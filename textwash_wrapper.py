# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

# A wrapper around Textwash functionality, based on code
# at https://github.com/maximilianmozes/textwash

import os
import re
import sys
import torch

from collections import defaultdict, Counter

TEXTWASH_DIR = os.environ.get('TEXTWASH_DIR')
sys.path.insert(0, TEXTWASH_DIR)

from config import Config
from data_processor import DataProcessor
from bert_model import BERTModel
from anonymiser import Anonymiser
from utils import load_model

# A wrapper around Textwash functionality
class Washer:

    def __init__(self):
        oldwd = os.getcwd()
        os.chdir(TEXTWASH_DIR)
        config = Config()
        config.gpu = False
        data_processor = DataProcessor(config)
        config.num_classes = data_processor.label_count
        device = torch.device('cpu')
        bert_model = BERTModel(config)
        model = load_model(config.load_model_path, bert_model.model)
        self.config = config
        self.anonymiser = Anonymiser(config, model, data_processor, device, bert_model)
        os.chdir(oldwd)

    # Use the Textwash anonymiser directly to anonymise the text
    def wash(self, data):
        outputs = {}
        for idx, (k, text) in enumerate(data.items()):
            anonymised, orig_cut = self.anonymiser.anonymise(text)
            outputs[k] = {'orig': orig_cut, 'anon': anonymised}

            print(f'Anonymised {idx+1}/{len(data)}')
        return outputs

    # Use the Textwash BERT model to find names in the data
    def find_names(self, data_generator):
        result = defaultdict(Counter)
        for labels, text in data_generator:
            names = self.find_name_tokens(text)
            if isinstance(labels, int) or isinstance(labels, str):
                labels = [labels]
            for label in labels:
                result[label].update(names)
        return result

    # Replace all names found by the Textwash BERT model
    def replace_names(self, data):
        repl_map = self.make_replacement_map(self.find_names(data.items()))
        outputs = {}
        for idx, (k, text) in enumerate(data.items()):
            anonymised = self.anonymise(text, repl_map)
            outputs[k] = {'orig': text, 'anon': anonymised}

            print(f'Anonymised {idx+1}/{len(data)}')
        return outputs

    def find_name_tokens(self, text):
        tokens = self.get_tokens(text)
        names = set([k for k, v in tokens.items() if v.startswith('PERSON')])
        return names

    def get_tokens(self, text):
        def get_normalised_tokens(string):
            if string == self.config.unk_token:
                return
            if len(string) == 1 and not string.isalnum():
                return
            if string.startswith('.'):
                string = string[1:].strip()
            if string.endswith('.'):
                string = string[:-1].strip()
            for s in reformat_periods(string):
                if s in text:
                    yield s

        # selectively remove spacing before token-internal periods
        def reformat_periods(string, start=0):
            yield string
            for i in range(start, len(string)-1):
                if string[i:i+2] == ' .':
                    for p in reformat_periods(string[:i] + string[i+1:], i+1):
                        yield p

        entity_list = self.anonymiser.get_identifiable_tokens(text)
        result = {token: v for k, v in entity_list for token in get_normalised_tokens(k)}
        return result

    def anonymise(self, text, repl_map):
        # run through all the substitutions cumulatively
        for token, repl in repl_map.items():
            pattern = r'\b{}(\b|$)'.format(re.escape(token))
            text = re.sub(pattern, repl, text)
        return text

    # make one combined map from tokens to replacements
    def make_replacement_map(self, token_map):
        repl_map = {}
        for key in token_map:
            replacement = 'USER'
            for tok in token_map[key]:
                repl_map[tok] = replacement
        # sort the keys so we handle multi-word strings correctly
        result = {key: repl_map[key] for key in sort_names(repl_map)}
        return result

    def sort_names(names):
        # sort by length (longest first) then alphabetically
        return sorted(list(names), key=lambda x: (-len(x), x))
