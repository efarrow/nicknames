# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import sys

from collections import defaultdict, Counter

from messages import load_csv, load_text, write_text

# load names and pseudonyms from CSV file
def load_names_csv(filename, pseudonym_field, name_field, *, prefix=None, result=None, **kwargs):
    if result is None:
        result = defaultdict(Counter)
    df = load_csv(filename)
    names = df[[pseudonym_field, name_field]]
    def read_entry(x):
        pseudonym, name = x
        if prefix and not pseudonym.startswith(prefix):
            pseudonym = f'{prefix}{pseudonym}'
        update_counter(result[pseudonym], name, **kwargs)
    names.apply(read_entry, axis=1)

# load names and pseudonyms from text file
def load_names(filename, *, prefix=None, result=None, **kwargs):
    if result is None:
        result = defaultdict(Counter)
    for line in load_text(filename):
        pseudonym, *names = line.split('|')
        pseudonym = pseudonym.strip()
        if prefix and not pseudonym.startswith(prefix):
            pseudonym = f'{prefix}{pseudonym}'
        # print(f'found {pseudonym}')
        for name in names:
            # handle files with frequency counts
            idx = name.find('[')
            if idx < 0:
                update_counter(result[pseudonym], name, **kwargs)
            else:
                count = int(name[idx+1:].strip()[:-1])
                update_counter(result[pseudonym], name[:idx], count=count, **kwargs)
    return result

# write names and pseudonyms to text file or stdout
def write_names(filename, names, **kwargs):
    if filename is None:
        print_names(names, **kwargs)
    else:
        write_text(filename, lambda x: print_names(names, file=x, **kwargs))

def create_counter():
    return defaultdict(Counter)

def update_counter(counter, name, *, divide=False, initials=True, count=1, **kwargs):
    if divide:
        # split name on whitespace
        for part in name.split():
            part = part.strip()
            # optionally ignore single initials
            if initials or len(part) > 1:
                counter[part] += count
    else:
        name = str(name).strip()
        if initials or len(name) > 1:
            counter[name] += count

def normalise_counter(counter):
    # drop zeros and empty entries
    return {k: Counter()+v for k, v in counter.items() if sum(v.values()) > 0}

def combine_counters(counter, *others):
    for c in others:
        for k, v in c.items():
            counter[k].update(v)

def sort_names(names):
    # sort by length (longest first) then alphabetically
    return sorted(list(names), key=lambda x: (-len(x), x))

def print_names(names, *, by_frequency=False, with_counts=False, top_n=None, verbose=False, file=sys.stdout, **kwargs):
    # sort by pseudonym
    for key in sorted(names):
        pairs = names[key].most_common(top_n)
        if by_frequency:
            # sort by frequency, then length, then alphabetically
            pairs.sort(key=lambda x: (-x[1], -len(x[0]), x[0]))
        else:
            # sort by length then alphabetically
            pairs.sort(key=lambda x: (-len(x[0]), x[0]))
        if with_counts:
            # combine names and counts
            entries = [f'{name} [{count}]' for name, count in pairs]
        else:
            entries = dict(pairs)
        values = ' | '.join(entries)
        print(f'{key} | {values}', file=file)
    if verbose:
        v = [sum(c.values()) for c in names.values()]
        print(f'Total connections: {sum(v)}', file=sys.stderr)
