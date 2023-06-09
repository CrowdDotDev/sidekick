from qdrant_client import QdrantClient
from qdrant_client.http import models

import os
import dotenv

dotenv.load_dotenv('.env')

qdrant_client = QdrantClient(
    url=os.environ.get('QDRANT_HOST'),
    api_key=os.environ.get('QDRANT_API_KEY'),
)


def upsert(ids, payloads, embeds):
    qdrant_client.upsert(
        collection_name='assistant',
        points=models.Batch(
            ids=ids,
            payloads=payloads,
            vectors=embeds
        )
    )
