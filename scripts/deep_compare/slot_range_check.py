import os
import sys
import warnings
import psycopg2
import pandas as pd
import pandas_gbq
from datetime import datetime, timezone, timedelta
from google.oauth2 import service_account

warnings.filterwarnings('ignore', message='A progress bar was requested.*tqdm', category=UserWarning)
warnings.filterwarnings('ignore', message='pandas only supports SQLAlchemy connectable', category=UserWarning)

from slot_range_queries import bq_slot_range_query, pg_slot_range_query


def get_pg_connection():
    try:
        return psycopg2.connect(
            dbname=os.environ['PGDATABASE'], host=os.environ['PGHOST'],
            port=os.environ['PGPORT'], password=os.environ['PGPASSWORD'],
            user=os.environ['PGUSER'])
    except Exception as e:
        print(f"Failed connecting to database: {e}")
        sys.exit(1)


def get_local_pg_connection():
    try:
        return psycopg2.connect(
            dbname=os.environ['PGDATABASE'], host='localhost',
            port='5432', password=os.environ['PGPASSWORD'],
            user=os.environ['PGUSER'])
    except Exception as e:
        print(f"Failed connecting to local database: {e}")
        sys.exit(1)


def get_bq(creds, query):
    proj_id = os.environ['BQ_PROJECT']
    location = os.environ['BQ_REGION']
    return pandas_gbq.read_gbq(query, project_id=proj_id, location=location, credentials=creds)


def get_pg(pg_conn, query):
    return pd.DataFrame(pd.read_sql_query(query, pg_conn))


def run_pg(pg_con, query):
    with pg_con.cursor() as cur:
        cur.execute(query)


def compute_slot_window(duration_s: int = 3600):
    """Return (start_time, end_time) for a safe comparison window.

    end_time   = current UTC hour at :20:00
    start_time = end_time - duration_s seconds (default 3600 = 1 hour)

    The BQ sync runs at ~x:34, so anchoring end_time at x:20 ensures
    the window falls within fully-synced data on both sides.
    """
    now = datetime.now(timezone.utc)
    end_time = now.replace(minute=20, second=0, microsecond=0)
    start_time = end_time - timedelta(seconds=duration_s)
    return start_time, end_time


def get_slot_range(credentials, bq_project, start_time, end_time):
    # block_time is DATETIME in BQ (no timezone); strip tz for the literal
    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S')
    query = f"""
SELECT MIN(slot_no) AS min_slot, MAX(slot_no) AS max_slot
FROM `{bq_project}.cardano_mainnet.block`
WHERE block_time BETWEEN DATETIME('{start_str}') AND DATETIME('{end_str}')
"""
    df = get_bq(credentials, query)
    min_slot = int(df['min_slot'][0])
    max_slot = int(df['max_slot'][0])
    return min_slot, max_slot


def log_results(pg_local_con, run_time, slot_min, slot_max, merged_df):
    rows = []
    for _, row in merged_df.iterrows():
        bq_hash = row['hash_bq'] if pd.notna(row.get('hash_bq')) else 'empty'
        pg_hash = row['hash_pg'] if pd.notna(row.get('hash_pg')) else 'empty'
        row_count_bq = int(row['row_count_bq']) if pd.notna(row.get('row_count_bq')) else 0
        row_count_pg = int(row['row_count_pg']) if pd.notna(row.get('row_count_pg')) else 0
        rows.append(
            f"('{run_time.isoformat()}', {slot_min}, {slot_max},"
            f" '{row['table_name']}', {row_count_bq}, {row_count_pg},"
            f" '{bq_hash}', '{pg_hash}')"
        )
    values = ", ".join(rows)
    query = (
        "INSERT INTO analytics.log_slot_range_comparison "
        "(run_time, slot_min, slot_max, table_name, row_count_bq, row_count_pg, bq_hash, pg_hash) "
        f"VALUES {values};"
    )
    run_pg(pg_local_con, query)


def main():
    bq_project = os.environ['BQ_PROJECT']
    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(os.path.dirname(current_script_path))
    # keyfile_path = f"{parent_directory}/key.json"
    keyfile_path = os.environ['BQ_KEY_FILE']
    credentials = service_account.Credentials.from_service_account_file(keyfile_path)

    pg_con = get_pg_connection()
    # pg_local_con = get_local_pg_connection()

    duration_s = int(os.environ.get('SLOT_WINDOW_DURATION_S', 3600))
    start_time, end_time = compute_slot_window(duration_s)
    print(f"Slot window: {start_time.isoformat()} → {end_time.isoformat()}")

    min_slot, max_slot = get_slot_range(credentials, bq_project, start_time, end_time)
    print(f"Slot range: {min_slot} – {max_slot}")

    run_time = datetime.now(timezone.utc)

    bq_sql = bq_slot_range_query(min_slot, max_slot, bq_project)
    pg_sql = pg_slot_range_query(min_slot, max_slot)

    print("Running BQ query...")
    bq_df = get_bq(credentials, bq_sql)
    bq_df = bq_df.rename(columns={'row_count': 'row_count_bq', 'hash_val': 'hash_bq'})

    print("Running PG query...")
    pg_df = get_pg(pg_con, pg_sql)
    pg_df = pg_df.rename(columns={'row_count': 'row_count_pg', 'hash_val': 'hash_pg'})

    merged = pd.merge(bq_df, pg_df, on='table_name', how='outer')
    merged['match'] = (merged['hash_bq'].fillna('__empty__') == merged['hash_pg'].fillna('__empty__'))

    mismatches = merged[~merged['match']]
    print(f"\nResults: {len(merged)} tables, {len(mismatches)} mismatches")

    #msg_file = f"slot_range_msg-{end_time.isoformat()}.txt"
    msg_file = "slot_range_msg.txt"
    with open(msg_file, 'w') as f:
        f.write(f"Slot range check: {start_time.isoformat()} → {end_time.isoformat()}\n")
        f.write(f"Slots: {min_slot} – {max_slot}\n\n")
        for _, row in merged.iterrows():
            status = "OK" if row['match'] else "MISMATCH"
            f.write(
                f"[{status}] {row['table_name']}"
                f"  BQ={row.get('row_count_bq', 0)} rows"
                f"  PG={row.get('row_count_pg', 0)} rows\n"
            )
            if not row['match']:
                f.write(f"  BQ hash: {row.get('hash_bq', 'empty')}\n")
                f.write(f"  PG hash: {row.get('hash_pg', 'empty')}\n")

    # log_results(pg_local_con, run_time, min_slot, max_slot, merged)
    # pg_local_con.commit()
    # pg_local_con.close()
    pg_con.close()

    print(f"Done. Results written to {msg_file}")
    if len(mismatches) > 0:
        print("MISMATCHES DETECTED:")
        for _, row in mismatches.iterrows():
            print(f"  {row['table_name']}: BQ={row.get('hash_bq','empty')}  PG={row.get('hash_pg','empty')}")


if __name__ == '__main__':
    main()
