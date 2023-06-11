# -*- coding: utf-8 -*-


def test_get_embeddings():
    from sidekick.apis.oai import get_embeddings

    embeddings = get_embeddings(['hola que tal',
                                 'como estas'])
    assert len(embeddings) == 2


def test_chunks(tokenizer):
    import sidekick.embed as E

    tk, txt = list(zip(*E.chunks('hola que tal. Esto es una prueba de chunk',
                                 4, tokenizer)))
    assert txt[0] == 'hola que tal.'
    assert tokenizer.encode(txt[0]) == tk[0]
    assert tokenizer.encode(txt[-1]) == tk[-1]


def test_embed():
    from sidekick import Config
    import sidekick.embed as E
    from sidekick.apis import qdrant

    q_client = qdrant.get_qdrant_client()
    q_client.delete_collection(collection_name=Config['qdrant']['QDRANT_COLLECTION'])
    qdrant.create_collection()


    with open('res/test/local/org/wands.org', encoding='utf-8') as fin:
        txt = fin.read()

        E.embed(txt, source_unit_id='1')
        assert qdrant.count() == 3

        # If we embed again the same source_unit_id it should first delete the
        # previous version
        E.embed(txt, source_unit_id='1')
        assert qdrant.count() == 3

        # But if we embed it with a different source_unit_id it should make new
        # points
        text_embeddings = E.embed(txt, source_unit_id='2')
        assert qdrant.count() == 6

        assert len(text_embeddings) == 3
