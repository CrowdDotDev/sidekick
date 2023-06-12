# -*- coding: utf-8 -*-

import sidekick.embed as E
import sidekick.tools as T
from sidekick.apis import qdrant
from sidekick.payload import Payload
from sidekick.apis.oai import get_embeddings


def test_get_embeddings():
    embeddings = get_embeddings(['hola que tal',
                                 'como estas'])
    assert len(embeddings) == 2


def test_chunks(tokenizer):

    tk, txt = list(zip(*E.chunks('hola que tal. Esto es una prueba de chunk',
                                 4, tokenizer)))
    assert txt[0] == 'hola que tal.'
    assert tokenizer.encode(txt[0]) == tk[0]
    assert tokenizer.encode(txt[-1]) == tk[-1]


def test_embed():
    q_client = qdrant.get_qdrant_client()
    config = T.get_config('qdrant')

    q_client.delete_collection(collection_name=config['qdrant_collection'])
    qdrant.create_collection()

    with open('res/test/local/org/wands.org', encoding='utf-8') as wands_in:
        with open('res/test/local/org/trees.org', encoding='utf-8') as trees_in:
            txt = wands_in.read() + trees_in.read()
            # txt = trees_in.read()
            payload = Payload(txt,
                              uri='file://uri_to_file_path',
                              headings=['Wands', 'Wand composition'])

            points = E.embed_source_unit([payload], source_unit_id='1')

            assert points[1].payload['body'] == (
                'Pine trees are evergreen, coniferous resinous trees in the genus '
                'Pinus. They are known for their distinctive pine cones and are '
                'often associated with Christmas.\n'
                '*** Characteristics\n'
                'Pine trees can be identified by their needle-like leaves, which are '
                'bundled in clusters of 2-5. The bark of most pines is thick and '
                'scaly, but some species have thin, flaky bark.\n'
                '** Willow Tree\n'
                '*** Overview\n'
                'Willow trees, part of the genus Salix, are known for their '
                'flexibility and their association with water and wetlands.\n'
                '*** Characteristics\n'
                'Willow trees are usually fast-growing but relatively short-lived. '
                'They have slender branches and large, fibrous, often stoloniferous '
                'roots. The leaves are typically elongated, but may also be round to '
                'oval.\n'
            )

            assert qdrant.count() == 2

            # If we embed again the same source_unit_id it should first delete the
            # previous version
            E.embed_source_unit([payload], source_unit_id='1')
            assert qdrant.count() == 2

            # But if we embed it with a different source_unit_id it should make new
            # points
            points = E.embed_source_unit([payload], source_unit_id='2')
            assert len(points) == 2
            assert qdrant.count() == 4