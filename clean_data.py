#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from constants import TEXT_FIELD_NAME
from messages import load_message_data, save_message_data

def clean_message_data(df, field):
    field = df[field]
    # remove outer quotes
    pattern = r'^"(.*)"$'
    replacement = r'\1'
    replace_pattern(field, pattern, replacement)
    # remove duplicated quote characters
    pattern = r'""'
    replacement = r'"'
    replace_pattern(field, pattern, replacement)
    # normalise white space
    pattern = r'\s+'
    replacement = r' '
    replace_pattern(field, pattern, replacement)
    # remove white space at start and end
    pattern = r'(^ +)|( +$)'
    replacement = r''
    replace_pattern(field, pattern, replacement)
    return df

# replace the given pattern in the field data
def replace_pattern(field, pattern, replacement, regex=True):
    field.replace(pattern, replacement, regex=regex, inplace=True)

def main():
    parser = argparse.ArgumentParser(description='Clean data')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('output_file', metavar='output-file', help='Output CSV file')
    parser.add_argument('--field', default=TEXT_FIELD_NAME, help='Name of field to clean')
    args = parser.parse_args()

    df = load_message_data(args.input_file)
    df = clean_message_data(df, args.field)
    save_message_data(df, args.output_file)


if __name__ == '__main__':
    # execute only if run as a script
    main()
