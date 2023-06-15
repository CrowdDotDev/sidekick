# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Tuple

import requests

import sidekick.tools as T

from sidekick.payload import Payload, FactType
from sidekick.embed import embed_source_unit
from sidekick.sources.state import State


SourceName = 'crowddev'
Timeout = 15


def get_activities(from_timestamp: datetime, offset: int = 0):
    T.load_dotenv()
    tenant_id = os.environ.get('CROWDDEV_TENANT_ID')
    api_key = os.environ.get('CROWDDEV_API_KEY')
    if not tenant_id and api_key:
        return []

    url = f"https://app.crowd.dev/api/tenant/{tenant_id}/activity/query"

    payload = {
        "limit": 200,
        "offset": offset,
        "filter": {
            "timestamp": {"gte": "2022-09-01"},
        },
        "orderBy": "timestamp_DESC",
    }
    if from_timestamp is not None:
        payload['filter']['createdAt'] = {"gte": from_timestamp.strftime("%Y-%m-%d")}

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=Timeout)
    return response.json()["rows"]


def ingest_activities(activities: List[Dict]):
    payloads = []


def embed_activities(from_timestamp):
    rows = get_activities(lastTimestamp, start_offset=0)
    while len(rows) > 0:
        for row in tqdm(rows, total=len(rows)):
            payload = {
                "url": row["url"],
                "timestamp": row["createdAt"],
                "title": row["title"],
                "body": row["body"],
                "platform": row["platform"],
                "member": row["member"]["displayName"],
                # Everything except the above
                "attributes": row["attributes"],
            }
            embed = generate_embeddings(payload["title"] + "\n" + payload["body"])
            if embed:
                idd = abs(hash(str(row["id"])))

                upsert([idd], [payload], [embed])

        offset += 200
        rows = get_activities(lastTimestamp, offset)


def ingest():
    state = State()

    DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # DATE = (datetime.now() - timedelta(days=17)).strftime('%Y-%m-%d')
    embed_activities(DATE, start_offset=0)


if __name__ == '__main__':
    env_file = '.env'

    # We do not want to try to load .env when running as a github action
    if os.path.exists(env_file):
        import dotenv
        dotenv.load_dotenv(env_file)

    ingest()
