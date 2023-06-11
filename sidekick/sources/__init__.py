# -*- coding: utf-8 -*-

import os
import sys
import json


SourceConfig = {}


def load_config():
    # Define potential locations for `sources.json`
    config_locations = [
        os.path.join(os.path.dirname(__file__), '..', 'sources.json'),  # Repository
        os.environ.get('SIDEKICK_SOURCES_CONFIG'),  # Environment variable
        os.path.expanduser('~/.sidekick/sources.json')  # User's home directory
    ]

    # Find the first existing configuration file in the list
    config_path = next((path for path in config_locations
                        if path and os.path.isfile(path)), None)

    if config_path is None:
        if 'pytest' in sys.argv[0]:
            return
        raise FileNotFoundError('No sources configuration file found.')

    with open(config_path, 'r', encoding='utf-8') as f:
        global SourceConfig
        SourceConfig = json.load(f)


load_config()


def combine_headings(headings, text):
    return ' > '.join(headings) + '\n\n' + text
