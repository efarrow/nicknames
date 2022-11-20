#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from constants import NO_PARENT_VALUE, PARENT_FIELD_NAME, PARENT_USER_FIELD_NAME, POST_FIELD_NAME, USER_FIELD_NAME
from messages import load_message_data, save_message_data

def generate_columns(df):
    if USER_FIELD_NAME not in df.columns:
        from constants import USER_ID_FIELD_NAME
        df.insert(df.columns.get_loc(USER_ID_FIELD_NAME), USER_FIELD_NAME, df[USER_ID_FIELD_NAME])
    mapping = {POST_FIELD_NAME: PARENT_FIELD_NAME, USER_FIELD_NAME: PARENT_USER_FIELD_NAME}
    parents = df[[POST_FIELD_NAME, USER_FIELD_NAME]].rename(columns=mapping)
    merged = df[[PARENT_FIELD_NAME]].merge(parents, on=PARENT_FIELD_NAME, how='left', sort=False, validate='many_to_one').fillna(NO_PARENT_VALUE, downcast='infer')
    # insert parent user name after post user name
    df.insert(df.columns.get_loc(USER_FIELD_NAME)+1, PARENT_USER_FIELD_NAME, merged[PARENT_USER_FIELD_NAME])
    return df

def main():
    parser = argparse.ArgumentParser(description='Generate additional column for parent user ID')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('output_file', metavar='output-file', help='Output CSV file')
    args = parser.parse_args()

    df = load_message_data(args.input_file)
    df = generate_columns(df)
    save_message_data(df, args.output_file)

if __name__ == '__main__':
    # execute only if run as a script
    main()
