# -*- coding: utf-8 -*-

import os
import sys
import configparser
from dotenv import load_dotenv


Config = {}

def load_config():
    # Creating a ConfigParser object
    config = configparser.ConfigParser()

    # Define potential locations for `config.ini`
    config_locations = [
        os.path.join(os.path.dirname(__file__), '..', 'config.ini'),  # Repository
        os.environ.get('SIDEKICK_CONFIG'),  # Environment variable
        os.path.expanduser('~/.sidekick/config.ini')  # User's home directory
    ]

    # Find the first existing configuration file in the list
    config_path = next((path for path in config_locations
                        if path and os.path.isfile(path)), None)

    if config_path is None:
        if 'pytest' in sys.argv[0]:
            return {}
        raise FileNotFoundError('No configuration file found.')

    config.read(config_path)

    global Config
    Config = {
        'state': {
            'LAST_SEEN_DB': config.get('state', 'LAST_SEEN_DB')
        },
        'qdrant': {
            'QDRANT_COLLECTION': config.get('qdrant', 'QDRANT_COLLECTION'),
            'QDRANT_LOCAL_DB': config.get('qdrant', 'QDRANT_LOCAL_DB', fallback=None),
            'QDRANT_URL': config.get('qdrant', 'QDRANT_URL', fallback=None),
            'QDRANT_SUID_FIELD': config.get('qdrant', 'QDRANT_SUID_FIELD'),
            'QDRANT_TEXT_FIELD': config.get('qdrant', 'QDRANT_TEXT_FIELD')
        },
        'openai': {
            'OAI_EMBEDDING_DIMENSIONS': config.getint('openai',
                                                      'OAI_EMBEDDING_DIMENSIONS'),
            'OAI_EMBEDDING_MODEL': config.get('openai',
                                              'OAI_EMBEDDING_MODEL'),
            'OAI_EMBEDDING_CTX_LENGTH': config.getint('openai',
                                                      'OAI_EMBEDDING_CTX_LENGTH'),
            'OAI_EMBEDDING_ENCODING': config.get('openai',
                                                 'OAI_EMBEDDING_ENCODING'),
            'OAI_EMBEDDING_CHUNK_SIZE': config.getint('openai',
                                                      'OAI_EMBEDDING_CHUNK_SIZE'),
            'OAI_MAX_TEXTS_TO_EMBED_BATCH_SIZE': config.getint(
                'openai', 'OAI_MAX_TEXTS_TO_EMBED_BATCH_SIZE'),
            'OAI_MODEL': config.get('openai', 'OAI_MODEL'),
            'OAI_SYSTEM_PROMPT': config.get('openai', 'OAI_SYSTEM_PROMPT')
        }
    }
    return Config


load_config()


def load_environment():
    load_dotenv('.env.testing' if 'pytest' in sys.argv[0] else '.env')
