#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse
import re
import sys

from collections import defaultdict

from constants import ADDITIONAL_PSEUDONYMS, PSEUDONYM_ANON, SESSION_FIELD_NAME, TEXT_FIELD_NAME, TOPIC_FIELD_NAME, USER_FIELD_NAME
from messages import load_message_data, save_message_data
from names import combine_counters, create_counter, load_names, sort_names, update_counter, write_names

GROUP_BY_NONE = 'none'
GROUP_BY_TOPIC = 'topic'
GROUP_BY_SESSION = 'session'
GROUP_BY_CHOICES = [GROUP_BY_TOPIC, GROUP_BY_SESSION, GROUP_BY_NONE]

# find the pseudonyms present in this data
def find_pseudonyms(df):
    # add additional pseudonyms for users added manually
    return sorted(df[USER_FIELD_NAME].astype(str).unique()) + ADDITIONAL_PSEUDONYMS

# replace names using the mapping
def replace_names(df, mapping, *, group_by=None, count_upper_bounds=False, **kwargs):
    all_conflicts = set()
    all_counts = create_counter()
    temp_field_name = None
    if count_upper_bounds or group_by is None or group_by == GROUP_BY_NONE:
        # create a temporary field for grouping
        temp_field_name = get_temp_field_name(df)
        df[temp_field_name] = 1
        field_name = temp_field_name
    elif group_by == GROUP_BY_TOPIC:
        field_name = TOPIC_FIELD_NAME
    elif group_by == GROUP_BY_SESSION:
        field_name = SESSION_FIELD_NAME
    for group_name, group in df.groupby(field_name, sort=False, as_index=False, group_keys=False):
        pseudonyms = find_pseudonyms(group)
        if count_upper_bounds:
            # treat each pseudonym independently, ignoring conflicts (counts are upper bounds)
            for pseudonym in pseudonyms:
                replacements = make_replacements({pseudonym: mapping[pseudonym]}, **kwargs)
                _, counts = perform_substitutions(group[TEXT_FIELD_NAME], replacements)
                combine_counters(all_counts, counts)
        else:
            replacements = make_replacements(mapping, valid_pseudonyms=pseudonyms, **kwargs)
            substituted, counts = perform_substitutions(group[TEXT_FIELD_NAME], replacements)
            df.loc[df[field_name] == group_name, TEXT_FIELD_NAME] = substituted
            combine_counters(all_counts, counts)
            # find name conflicts in this group
            all_conflicts.update(find_conflicts(replacements))
    if temp_field_name:
        df.drop(columns=temp_field_name, inplace=True)
    # report name conflicts
    for conflict in sorted(all_conflicts):
        name, repl_new, repl_orig = conflict
        print(f'WARNING: skipping duplicate name {name} for {repl_new} -- already mapped to {repl_orig}', file=sys.stderr)
    if all_conflicts:
        print(f'WARNING: found {len(all_conflicts)} duplicates in total', file=sys.stderr)
    return all_counts

# create the mapping from names to replacements and pseudonyms
def make_replacements(mapping, *, valid_pseudonyms=None, anon_only=False, verbose=False, **kwargs):
    replacements = defaultdict(list)
    for pseudonym, names in mapping.items():
        if valid_pseudonyms and pseudonym not in valid_pseudonyms:
            continue
        repl = PSEUDONYM_ANON if anon_only else pseudonym
        for name in names:
            replacements[name].append((pseudonym, repl))
            if verbose:
                print(f'INFO: replacing name {name} with {repl}', file=sys.stderr)
    return replacements

# perform the substitutions
def perform_substitutions(series, replacements):
    counts = create_counter()
    # sort the mapping so we handle multi-word strings correctly
    for name in sort_names(replacements):
        pattern = rf'\b({re.escape(name)})\b'
        # replace one name at a time, so we can count the replacements
        n_matches = series.str.count(pattern).sum()
        if n_matches > 0:
            # replace each name with the first matching entry
            pseudonym, repl = replacements[name][0]
            series = series.replace(regex={pattern: repl})
            update_counter(counts[pseudonym], name, count=n_matches)
    return series, counts

# find duplicated names
def find_conflicts(replacements):
    conflicts = set()
    for name, entries in replacements.items():
        if len(entries) > 1:
            orig = entries[0]
            for entry in entries[1:]:
                conflicts.add((name, entry[0], orig[0]))
    return conflicts

# generate an unused field name
def get_temp_field_name(df, base_name='tmp'):
    counter = 1
    tmp_field_name = base_name
    while tmp_field_name in df.columns:
        tmp_field_name = f'{base_name}{counter}'
        counter += 1
    return tmp_field_name

def main():
    parser = argparse.ArgumentParser(description='Replace names with pseudonyms and return substitution counts')
    parser.add_argument('input_file', metavar='input-file', help='Input CSV file')
    parser.add_argument('names_file', metavar='names-file', help='Input text file with with names for each pseudonym')
    parser.add_argument('output_file', metavar='output-file', nargs='?', help='Output CSV file (optional)')
    parser.add_argument('--used-names', help='Output text file (optional)')
    parser.add_argument('--by', help='Grouping option', choices=GROUP_BY_CHOICES, default=GROUP_BY_SESSION)
    parser.add_argument('--anon', help='Use the same pseudonym for every name', action='store_true')
    parser.add_argument('-q', help='Sort names by frequency', action='store_true')
    parser.add_argument('-c', help='Output counts', action='store_true')
    parser.add_argument('-v', help='Verbose output', action='store_true')
    args = parser.parse_args()

    names = load_names(args.names_file)
    df = load_message_data(args.input_file)
    names = replace_names(df, names, group_by=args.by, anon_only=args.anon, verbose=args.v)
    if args.output_file:
        save_message_data(df, args.output_file)
    if args.used_names:
        write_names(args.used_names, names, by_frequency=args.q, with_counts=args.c, verbose=args.v)

if __name__ == '__main__':
    # execute only if run as a script
    main()
