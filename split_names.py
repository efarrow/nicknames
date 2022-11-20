#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from itertools import chain, combinations
from names import create_counter, load_names, update_counter, write_names

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def find_sub_names(names):
    for name in names:
        for n in powerset(name.split()):
            if n:
                yield ' '.join(n)
        if '-' in name:
            name = name.replace('-', ' ')
            for n in powerset(name.split()):
                if n:
                    yield ' '.join(n)

def split_names(names):
    result = create_counter()
    for pseudonym, candidates in names.items():
        for name in find_sub_names(candidates):
            update_counter(result[pseudonym], name)
    return result

def main():
    parser = argparse.ArgumentParser(description='Split the given multi-word names into valid subsets')
    parser.add_argument('input_file', metavar='input-file', help='Text file with names for each pseudonym')
    parser.add_argument('output_file', metavar='output-file', nargs='?', help='Output text file (optional)')
    args = parser.parse_args()

    names = load_names(args.input_file)
    names = split_names(names)
    write_names(args.output_file, names)

if __name__ == '__main__':
    # execute only if run as a script
    main()
