#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse
import sys

from constants import CSV_NAME_LABEL, CSV_PSEUDONYM_LABEL
from names import create_counter, load_names, load_names_csv, normalise_counter, update_counter, write_names

def combine_names(filenames, args, *, subtract=False, **kwargs):
    orig_names = None
    known_names = set()
    names = create_counter()
    for filename in filenames:
        if filename.endswith('.txt'):
            load_names(filename, result=names, **kwargs)
        elif filename.endswith('.csv'):
            load_names_csv(filename, args.csv_pseudonym, args.csv_name, result=names, **kwargs)
        else:
            print(f'Ignoring unknown file type {filename}', file=sys.stderr)
        if subtract and orig_names is None:
            orig_names = names
            names = create_counter()

    if args.known_names:
        for mapping in load_names(args.known_names, **kwargs).values():
            known_names.update(mapping.keys())
        if orig_names is None:
            orig_names = names
            names = create_counter()

    if orig_names:
        # remove the unwanted name variants
        for pseudonym in list(orig_names):
            for name in names[pseudonym]:
                orig_names[pseudonym].pop(name, None)
            for name in known_names:
                orig_names[pseudonym].pop(name, None)
        names = orig_names

    return normalise_counter(names)

def main():
    parser = argparse.ArgumentParser(description='Combine names')
    parser.add_argument('filenames', metavar='FILE', nargs='+',
                        help='Files (text or CSV) with names for each pseudonym')
    parser.add_argument('--output-file', '-o', help='Output text file')
    parser.add_argument('--known-names', help='File with known names to remove from all entries')
    parser.add_argument('--top', type=int, default=None, help='Output only the top names, by frequency')
    parser.add_argument('--subtract', '-s', help='Output only the names from the first list that are not in the other list(s)', action='store_true')
    parser.add_argument('--split-multi', '-m', help='Split multi-part names', action='store_true')
    parser.add_argument('--drop-initials', help='Drop single letter names', action='store_true')
    parser.add_argument('--csv-pseudonym', default=CSV_PSEUDONYM_LABEL, help='Label of pseudonym field in CSV file')
    parser.add_argument('--csv-name', default=CSV_NAME_LABEL, help='Label of name field in CSV file')
    parser.add_argument('--prefix', default='', help='Optional prefix to add to the pseudonyms')
    parser.add_argument('-q', help='Sort names by frequency', action='store_true')
    parser.add_argument('-c', help='Output counts', action='store_true')
    parser.add_argument('-v', help='Verbose output', action='store_true')
    args = parser.parse_args()

    keep_initials = not args.drop_initials
    names = combine_names(args.filenames, args, subtract=args.subtract, divide=args.split_multi, initials=keep_initials, prefix=args.prefix)
    write_names(args.output_file, names, by_frequency=args.q, with_counts=args.c, top_n=args.top)

if __name__ == '__main__':
    # execute only if run as a script
    main()
