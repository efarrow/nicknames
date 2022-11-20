#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from constants import SESSION_FIELD_NAME, TIME_FIELD_NAME, TOPIC_FIELD_NAME
from messages import load_message_data, save_message_data

# sort messages
def sort_messages(df):
    # sort within sessions by topic thread and then by time
    df = df.sort_values(by=[SESSION_FIELD_NAME, TOPIC_FIELD_NAME, TIME_FIELD_NAME])
    return df

def main():
    parser = argparse.ArgumentParser(description='Sort data')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('output_file', metavar='output-file', help='Output CSV file')
    args = parser.parse_args()

    df = load_message_data(args.input_file)
    df = sort_messages(df)
    save_message_data(df, args.output_file)

if __name__ == '__main__':
    # execute only if run as a script
    main()
