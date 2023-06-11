# -*- coding: utf-8 -*-

import os

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from sidekick import load_environment, Config

C = Config['qdrant']

QClient = None


def get_qdrant_client():
    global QClient
    if QClient is None:
        load_environment()
        if C['QDRANT_LOCAL_DB']:
            client_pars = {'path': C['QDRANT_LOCAL_DB']}
        elif C['QDRANT_URL']:
            client_pars = {'url': C['QDRANT_LOCAL_DB'],
                           'api_key': os.environ['QDRANT_API_KEY']}
        else:
            raise RuntimeError('Need either QDRANT_LOCAL_DB or '
                               'QDRANT_LOCAL_DB in config')

        QClient = QdrantClient(**client_pars)

    return QClient


def create_collection():
    client = get_qdrant_client()
    client.recreate_collection(
        collection_name=C['QDRANT_COLLECTION'],
        vectors_config=VectorParams(size=Config['openai']['OAI_EMBEDDING_DIMENSIONS'],
                                    distance=Distance.COSINE))

    client.create_payload_index(collection_name=C['QDRANT_COLLECTION'],
                                field_name=C['QDRANT_SUID_FIELD'],
                                field_schema="keyword")


def count():
    client = get_qdrant_client()
    return client.count(collection_name=C['QDRANT_COLLECTION'],
                        exact=True).count


def search(query_vector, limit=5):
    client = get_qdrant_client()
    out = client.search(collection_name=C['QDRANT_COLLECTION'],
                        query_vector=query_vector,
                        limit=limit)
    return [r.payload for r in out]


def clean_source_unit(source_unit_id):
    # We assume that when a source unit is embedded it will replace
    # any previous version of the same unit, so we first need to
    # delete all the points belonging to this source_unit_id if any
    # exists
    client = get_qdrant_client()
    client.delete(collection_name=C['QDRANT_COLLECTION'],
                  points_selector=Filter(must=[
                      FieldCondition(key=C['QDRANT_SUID_FIELD'],
                                     match=MatchValue(value=source_unit_id))]))
