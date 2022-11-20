#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse
import re

from constants import NO_PARENT_VALUE, PARENT_USER_FIELD_NAME, TEXT_FIELD_NAME, USER_FIELD_NAME
from messages import load_message_data
from names import create_counter, update_counter, write_names

METHOD_REGEX = 'regex'
METHOD_TEXTWASH = 'textwash'
METHOD_CHOICES = [METHOD_REGEX, METHOD_TEXTWASH]

def find_names(df, find_to_names, find_from_names):
    names = create_counter()
    if find_to_names and PARENT_USER_FIELD_NAME in df.columns:
        posts = df[[TEXT_FIELD_NAME, PARENT_USER_FIELD_NAME]]
        patterns = [
            r'^"?[hH][iI]\W+(\w+(-\w+)?)',
        ]
        match_patterns(posts, patterns, names)
    if find_from_names:
        posts = df[[TEXT_FIELD_NAME, USER_FIELD_NAME]]
        patterns = [
            r'(\w+(-\w+)?(\s+\w\.?)?)"?$',
        ]
        match_patterns(posts, patterns, names)
    result = create_counter()
    for name, pseudonyms in names.items():
        if not re.fullmatch(r'\D+', name):
            # exclude names containing digits
            continue
        # collect all the names linked with this pseudonym
        for pseudonym, count in pseudonyms.most_common():
            # skip unattributed names
            if pseudonym != NO_PARENT_VALUE:
                update_counter(result[pseudonym], name, count=count)
    return result

def match_patterns(posts, patterns, names):
    # print(posts.columns)
    for pattern in patterns:
        for _, (body, pseudonym) in posts.iterrows():
            match = re.search(pattern, body)
            if match:
                # print(f'{match.group()}')
                name = match.group(1)
                # drop internal punctuation
                name = name.replace('.', '')
                # collect all the pseudonyms linked with this name
                update_counter(names[name], pseudonym)

# Use TextWash to find names in the data
def find_names_textwash(df, find_to_names, find_from_names):
    from textwash_wrapper import Washer
    columns = [TEXT_FIELD_NAME]
    if find_to_names and PARENT_USER_FIELD_NAME in df.columns:
        columns += [PARENT_USER_FIELD_NAME]
    if find_from_names:
        columns += [USER_FIELD_NAME]
    posts = df[columns]
    data = [(users, body) for _, (body, *users) in posts.iterrows()]
    return Washer().find_names(data)

def main():
    parser = argparse.ArgumentParser(description='Find personal names for each pseudonym')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('output_file', metavar='output-file', nargs='?', help='Output text file (optional)')
    parser.add_argument('-t', help="Find 'to' names", action='store_true')
    parser.add_argument('-f', help="Find 'from' names", action='store_true')
    parser.add_argument('-q', help='Sort names by frequency', action='store_true')
    parser.add_argument('-c', help='Output counts', action='store_true')
    parser.add_argument('-v', help='Verbose output', action='store_true')
    parser.add_argument('--method', default=METHOD_REGEX, help='Method to use for searching for names', choices=METHOD_CHOICES)
    parser.add_argument('--start', type=int, default=0, help='[DEBUG] First row to use')
    parser.add_argument('--limit', type=int, default=0, help='[DEBUG] Maximum number of rows to use')
    args = parser.parse_args()

    if not args.t and not args.f:
        args.t = True
        args.f = True

    df = load_message_data(args.input_file)
    if args.limit > 0:
        df = df[args.start:args.start+args.limit]
    if args.method == METHOD_REGEX:
        names = find_names(df, args.t, args.f)
    elif args.method == METHOD_TEXTWASH:
        names = find_names_textwash(df, args.t, args.f)
    write_names(args.output_file, names, by_frequency=args.q, with_counts=args.c, verbose=args.v)

if __name__ == '__main__':
    # execute only if run as a script
    main()
