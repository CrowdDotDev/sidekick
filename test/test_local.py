# -*- coding: utf-8 -*-

import os
import time


def update_modification_time(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            current_time = time.time()
            os.utime(file_path, (current_time, current_time))



def test_local():
    from sidekick import Config
    from sidekick.sources import SourceConfig

    from sidekick.apis import qdrant
    from sidekick.sources.local import ingest

    q_client = qdrant.get_qdrant_client()
    q_client.delete_collection(collection_name=Config['qdrant']['QDRANT_COLLECTION'])
    qdrant.create_collection()

    update_modification_time(SourceConfig['local'][0]['directory'])

    embedded = ingest()
    assert qdrant.count() == 14
    assert len(embedded) == 6

    embedded = ingest()
    assert qdrant.count() == 14
    assert len(embedded) == 0
