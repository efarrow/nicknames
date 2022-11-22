#!/usr/bin/python3

# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import argparse
import pandas as pd

import matplotlib as mpl
mpl.use('Agg') # headless mode
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

import seaborn
seaborn.set()

mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['blue', 'purple', 'teal', 'skyblue', 'turquoise', 'lime', 'lavender', 'darkgreen'])

from pathlib import Path    
from names import load_names, sort_names

NAMES = {
    'full': 'Full Registered Name',
    'subset': 'Subset of Full Name',
    'nicknames': 'Nickname',
    'misspelled': 'Misspelled Name',
}

def load_data(filenames, sort=False, total=False):
    data = {}
    for filename in filenames:
        names = load_names(filename)
        colname = Path(filename).name.replace('names_', '').replace('.txt', '')
        if colname in NAMES:
            colname = NAMES[colname]
        data[colname] = {n: len(c) for n, c in names.items()}
    df = pd.DataFrame(data=data)
    df = df.fillna(0, downcast='infer')
    if sort:
        sort_cols = df.columns.tolist()
        if total:
            df['total'] = df.sum(axis=1)
            sort_cols = ['total'] + sort_cols
        df = df.sort_values(by=sort_cols).reset_index(drop=True)
        if total:
            for v in sorted(df['total'].unique().tolist()):
                print(f'{v} name(s): ', df[df['total'] == v]['total'].count(), 'instances')
            df = df.drop(columns='total')
    return df

def savefig(fig, filename):
    fig.savefig(filename, dpi=300, bbox_inches='tight')

def plot_data(df, title=None, size=(4, 3)):
    fig = plt.figure(figsize=size)
    n_bins = df.max(axis=1).max()
    ax = fig.add_subplot(1, 1, 1)
    df.plot(kind='bar', width=1, stacked=True, ax=ax, legend=False, alpha=0.7)
    ax.grid(False)
    ax.set_facecolor('w')
    ax.set_ylabel('Names Used')
    ax.set_xlabel('Participant Number')
    ax.xaxis.set_tick_params(rotation=0)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    current_handles, _ = ax.get_legend_handles_labels()
    reversed_handles = reversed(current_handles)
    reversed_labels = reversed(df.columns)
    plt.legend(reversed_handles, reversed_labels)
    plt.setp(ax.patches, linewidth=0)
    if title is not None:
        plt.title(title)
    fig.tight_layout()
    return fig

def main():
    # seaborn.set_context('poster')
    seaborn.set_context('paper')

    parser = argparse.ArgumentParser(description='Plot distributions of names')
    parser.add_argument('output_dir', help='Output directory')
    parser.add_argument('input_data', nargs='+', help='Input CSV data files')
    args = parser.parse_args()

    df = load_data(args.input_data, sort=True, total=True)
    fig = plot_data(df, size=(6, 2))
    savefig(fig, f'{args.output_dir}/names.png')

if __name__ == '__main__':
    # execute only if run as a script
    main()
