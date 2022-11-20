#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from messages import load_message_data, save_message_data
from names import load_names, write_names
from replace_names import replace_names

def main():
    parser = argparse.ArgumentParser(description='Remove names that do not appear in the data')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('names_file', metavar='names-file', help='Input text file with with names for each pseudonym')
    parser.add_argument('output_file', metavar='output-file', nargs='?', help='Output text file (optional)')
    parser.add_argument('-q', help='Sort names by frequency', action='store_true')
    parser.add_argument('-c', help='Output counts', action='store_true')
    parser.add_argument('-v', help='Verbose output', action='store_true')
    args = parser.parse_args()

    names = load_names(args.names_file)
    df = load_message_data(args.input_file)
    # count the upper bound of occurrences
    names = replace_names(df, names, count_upper_bounds=True, verbose=args.v)
    write_names(args.output_file, names, by_frequency=args.q, with_counts=args.c, verbose=args.v)

if __name__ == '__main__':
    # execute only if run as a script
    main()
