#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse

from collections import defaultdict, Counter

from names import load_names, sort_names

TP = 'true_positive'
FP = 'false_positive'
FN = 'false_negative'

# A class for comparing true names and found names
class Compare:

    def __init__(self, all_true_names, all_found_names):
        self.overall = Counter()
        self.names_true = []
        self.names_matching = []
        self.pseudonyms_missed = []
        self.n_substitutions_true = 0
        self.n_substitutions_found = 0
        self.names_missed_per_pseudonym = defaultdict(set)
        self.n_pseudonyms = len(all_true_names)
        for pseudonym in sorted(all_true_names):
            true_names = all_true_names[pseudonym]
            # ignore any counts in the found names
            found_names = set(all_found_names[pseudonym])
            if not found_names:
                self.pseudonyms_missed.append(pseudonym)
            missing_names = self.find_missing_names(true_names, found_names)
            if missing_names:
                self.names_missed_per_pseudonym[pseudonym] = missing_names
            matching_names = self.find_matching_names(true_names, found_names)
            self.names_true.extend(true_names)
            self.names_matching.extend(matching_names)
            self.overall[TP] += len(matching_names)
            self.overall[FP] += len(found_names - matching_names)
            self.overall[FN] += len(missing_names)
            self.n_substitutions_true += sum(true_names.values())
            self.n_substitutions_found += sum([true_names[name] for name in matching_names])

    def print_report(self, verbose=False):
        print(f'{self.format_overall_stats()}')
        if self.names_missed_per_pseudonym:
            print(f'  {self.format_missed_names()}')
            if verbose:
                for line in self.format_missed_names_per_pseudonym():
                    print(f'    {line}')
        print(f'  {self.format_coverage()}')
        print(f'  {self.format_found_names_unique()}')
        print(f'  {self.format_missed_connections()}')
        print(f'  {self.format_found_connections()}')
        if self.pseudonyms_missed:
            print(f'WARNING: {self.format_missed_pseudonyms()}')

    def print_latex_summary(self, style):
        line = self.format_summary(style)
        print(f'{line} \\\\'.replace('%', '\%'))

    def format_summary(self, style):
        result = []
        n_connections_true, n_connections_missed, n_connections_found = self.count_connections()
        if style == 1:
            n_total, _, n_complete = self.count_pseudonyms()
            precision, recall, f1 = self.calculate_p_r_f1()
            result.append(f'{n_complete / n_total:.1%}')
            result.append(f'{n_connections_missed}/{n_connections_true}')
            result.append(f'{recall:.1%}')
            result.append(f'{precision:.1%}')
            result.append(f'{f1:.1%}')
        elif style == 2:
            _, _, n_unique_names_found = self.count_unique_names()
            result.append(f'{n_unique_names_found}')
            result.append(f'{n_connections_found}')
            result.append(f'{n_connections_found/n_connections_true:.1%}')
            result.append(f'{self.n_substitutions_found:,}')
            result.append(f'{self.n_substitutions_found/self.n_substitutions_true:.1%}')
        return ' & '.join(result)

    def find_matching_names(self, true_names, found_names):
        return set(true_names) & set(found_names)

    def find_missing_names(self, true_names, found_names):
        return set(true_names) - set(found_names)

    def format_overall_stats(self):
        precision, recall, f1 = self.calculate_p_r_f1()
        return f'Overall: P={precision:.1%}, R={recall:.1%}, F1={f1:.3f}'

    def format_missed_names(self):
        n_total, n_incomplete, _ = self.count_pseudonyms()
        return f'Names missed for {n_incomplete} / {n_total} users'

    def format_missed_names_per_pseudonym(self):
        for k, v in self.names_missed_per_pseudonym.items():
            yield f'{k} : {self.format_names(v)}'

    def format_coverage(self):
        n_total, _, n_complete = self.count_pseudonyms()
        return f'Coverage: {self.format_ratio(n_complete, n_total)}'

    def format_found_names_unique(self):
        n_unique_true, _, n_unique_found = self.count_unique_names()
        found_names = self.format_ratio(n_unique_found, n_unique_true)
        instances = self.format_ratio(self.n_substitutions_found, self.n_substitutions_true)
        return f'Found names: {found_names} (instances: {instances})'

    def format_missed_connections(self):
        n_connections_true, n_connections_missed, _ = self.count_connections()
        connections = self.format_ratio(n_connections_missed, n_connections_true)
        return f'Missed connections: {connections}'

    def format_found_connections(self):
        n_connections_true, _, n_connections_found = self.count_connections()
        connections = self.format_ratio(n_connections_found, n_connections_true)
        return f'Found connections: {connections}'

    def format_missed_pseudonyms(self):
        missed = self.pseudonyms_missed
        return f'No names found for {len(missed)} users: {self.format_names(missed)}'

    def format_names(self, names):
        return ', '.join(sorted(names))

    def format_ratio(self, top, bottom):
        ratio = self.safe_divide(top, bottom)
        return f'{top} / {bottom}, {ratio:.1%}'

    def count_pseudonyms(self):
        n_incomplete = len(self.names_missed_per_pseudonym)
        return self.n_pseudonyms, n_incomplete, self.n_pseudonyms-n_incomplete

    def count_connections(self):
        n_true = len(self.names_true)
        n_missed = self.overall[FN]
        return n_true, n_missed, n_true - n_missed

    def count_unique_names(self):
        n_true = len(set(self.names_true))
        n_matched = len(set(self.names_matching))
        return n_true, n_true - n_matched, n_matched

    def calculate_p_r_f1(self):
        true_pos = self.overall[TP]
        false_pos = self.overall[FP]
        false_neg = self.overall[FN]
        precision = self.safe_divide(true_pos, true_pos + false_pos)
        recall = self.safe_divide(true_pos, true_pos + false_neg)
        f1 = self.safe_divide(2 * precision * recall, precision + recall)
        return precision, recall, f1

    def safe_divide(self, a, b):
        return a/b if b else 0

def main():
    parser = argparse.ArgumentParser(description='Compare collected names against true names')
    parser.add_argument('true_names', help='Text file with true names for each pseudonym')
    parser.add_argument('found_names', help='Text file with found names for each pseudonym')
    parser.add_argument('--report', help='Print a report as text', action='store_true')
    parser.add_argument('--summary', '-s', type=int, default=0, help='Print a LaTeX summary in a particular style')
    parser.add_argument('-v', help='Verbose output', action='store_true')
    args = parser.parse_args()

    if not (args.report or args.summary):
        args.report = True

    true_names = load_names(args.true_names)
    found_names = load_names(args.found_names)
    c = Compare(true_names, found_names)
    if args.report:
        c.print_report(verbose=args.v)
    if args.summary:
        c.print_latex_summary(args.summary)

if __name__ == '__main__':
    # execute only if run as a script
    main()
