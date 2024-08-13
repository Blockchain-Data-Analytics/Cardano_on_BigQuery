import csv, sys
import json
import tempfile
import os
import datetime

def main():
    args = ParseArgs()
    input_file = args.file
    max_digits = int(args.max_int_length)
    json_field_idx = int(args.index)
    csv.field_size_limit(sys.maxsize)
    with tempfile.NamedTemporaryFile(mode='w', newline='', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        # Read the input file and process each row
        with open(input_file, mode='r', newline='') as infile:
            print(f"{datetime.datetime.now()}: Processing file: {input_file}")
            reader = csv.reader(infile)
            fix_json_numbers(reader, writer, json_field_idx, max_digits)
            os.replace(temp_file.name, input_file)
            print(f"{datetime.datetime.now()}: File processed successfully")


def process_json_field(json_field, max_digits=15):
    def wrap_large_numbers(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "int" and isinstance(value, int) and len(str(value)) > max_digits:
                    print(f"Wrapping large number: {value}")
                    obj[key] = str(value)
                else:
                    wrap_large_numbers(value)
        elif isinstance(obj, list):
            for item in obj:
                wrap_large_numbers(item)
    
    json_data = json.loads(json_field)
    wrap_large_numbers(json_data)
    return json.dumps(json_data)


def fix_json_numbers(reader, writer, json_field_idx, max_digits=15):
    for row in reader:
        if row:  # Check if row is not empty
            last_field = row[json_field_idx]
            try:
                modified_json = process_json_field(last_field, max_digits)
                row[json_field_idx] = modified_json
            except json.JSONDecodeError:
                print(f"Invalid JSON field in line: {','.join(row)}")
        writer.writerow(row)


def ParseArgs():
    ''' Parse the arguments '''
    import argparse
    parser = argparse.ArgumentParser(
            description=f'Take as input a csv file with a field that is a json. Every `int` property of that json that is a number ' \
                         'bigger than a certain threshold, gets wrapped in double quotes',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-m', '--max_int_length', help='Maximum list length', default=15)
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-i', '--index', help='The index of the json field (zero based)', required=True)
    requiredNamed.add_argument('-f', '--file', help='CSV file to be edited',
                               required=True)
    args = parser.parse_args()
    return args


# %%
if __name__ == '__main__':
    main()
