# -*- coding: utf-8 -*-

import os
import pytest
import tiktoken


@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['SIDEKICK_CONFIG'] = 'res/test/config.ini'
    os.environ['SIDEKICK_SOURCES_CONFIG'] = 'res/test/sources.json'

    from sidekick.sources import load_config as load_sources_config
    from sidekick import load_config

    load_config()
    load_sources_config()


@pytest.fixture(scope='session')
def tokenizer():
    os.environ['SIDEKICK_CONFIG'] = 'res/test/config.ini'
    from sidekick import load_config
    C = load_config()['openai']
    tk = tiktoken.get_encoding(C['OAI_EMBEDDING_ENCODING'])
    yield tk
