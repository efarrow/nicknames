# © All rights reserved. Elaine Farrow, University of Edinburgh, United Kingdom, 2022

import json
import os

# load config file from script directory
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(f'{dir_path}/config.json') as f:
    CONFIG = json.load(f)

FIELDS = CONFIG['message_fields']
CSV_FIELDS = CONFIG['csv_name_fields']
VALUES = CONFIG['values']

# field names in the message data
POST_FIELD_NAME = FIELDS['post_id']
PARENT_FIELD_NAME = FIELDS['parent_post_id']
USER_ID_FIELD_NAME = FIELDS['user_id']
USER_FIELD_NAME = FIELDS['pseudonym']
PARENT_USER_FIELD_NAME = FIELDS['parent_pseudonym']
SESSION_FIELD_NAME = FIELDS['session_id']
TOPIC_FIELD_NAME = FIELDS['topic_id']
TIME_FIELD_NAME = FIELDS['time']
TEXT_FIELD_NAME = FIELDS['text']

# column names in the CSV files of student names
CSV_NAME_LABEL = CSV_FIELDS['name']
CSV_PSEUDONYM_LABEL = CSV_FIELDS['pseudonym']

# additional pseudonyms for users added manually
ADDITIONAL_PSEUDONYMS = VALUES['additional_pseudonyms']

# parent pseudonym for messages with no parent
NO_PARENT_VALUE = VALUES['pseudonym_no_parent']

# pseudonyms for all anon entries
PSEUDONYM_ANON = VALUES['pseudonym_anon']
