# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import pandas as pd

# import messages into pandas
def load_message_data(filename):
    df = pd.read_csv(filename)
    # print(f'read {len(df)} records')
    return df

# export messages to file
def save_message_data(df, filename):
    with open(filename, 'w') as f:
        df.to_csv(f, index=False)

# load records from CSV file
def load_csv(filename):
    df = pd.read_csv(filename, dtype=str)
    return df

# load records from text file
def load_text(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line

# write records to text file
def write_text(filename, write_fn):
    with open(filename, 'w') as f:
        write_fn(f)

# append records to text file
def append_text(filename, write_fn):
    with open(filename, 'a') as f:
        write_fn(f)
