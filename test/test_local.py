# -*- coding: utf-8 -*-

import os
import time

import sidekick.tools as T
from sidekick.apis import qdrant
from sidekick.sources.local import ingest


def update_modification_time(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            current_time = time.time()
            os.utime(file_path, (current_time, current_time))


def test_local():
    q_client = qdrant.get_qdrant_client()

    config = T.get_config('qdrant')
    q_client.delete_collection(collection_name=config['qdrant_collection'])
    qdrant.create_collection()

    source_config = T.get_source_config('local')
    update_modification_time(source_config[0]['directory'])

    embedded = ingest()
    assert qdrant.count() == 39  # A long payload has been divided in two
    assert len(embedded) == 38

    time.sleep(1.1)

    embedded = ingest()
    assert qdrant.count() == 39
    assert len(embedded) == 0