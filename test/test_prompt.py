# -*- coding: utf-8 -*-

import os
import time

import sidekick.tools as T
from sidekick.apis import qdrant, oai
from sidekick.sources.local import ingest
from sidekick.chat import format_context


def update_modification_time(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            current_time = time.time()
            os.utime(file_path, (current_time, current_time))


def test_prompt():
    q_client = qdrant.get_qdrant_client()

    config = T.get_config('qdrant')
    q_client.delete_collection(collection_name=config['qdrant_collection'])
    qdrant.create_collection()

    source_config = T.get_source_config('local')

    test_dir = source_config[1]['directory']
    update_modification_time(test_dir)

    ingest(only_in_directory=test_dir)
    assert qdrant.count() == 1

    all_context = qdrant.search(oai.get_embeddings(['Spain'])[0], limit=1)
    assert len(all_context) == 1


    assert set(all_context[0].keys()) == set(['author',
                                              'body',
                                              'fact_type',
                                              'headings',
                                              'metadata',
                                              'source',
                                              'source_unit_id',
                                              'timestamp',
                                              'uri'])

    timestamp = T.timestamp_as_utc().isoformat()
    all_context[0]['timestamp'] = timestamp

    assert format_context(all_context[0]) == (
        '```\n'
        'url_or_file: /Users/juanre/prj/sidekick/res/test/local/short/galicia.md\n'
        'source: local:altair.home\n'
        'author: John Doe\n'
        'fact_type: historical\n'
        f'timestamp: {timestamp}\n'
        'breadcrumbs: Galicia > Introduction\n'
        'body: It is the north-western corner of the Iberian Peninsula. Great food, '
        'nice people, and amazing views.\n'
        '```')
