import os
from datetime import datetime, timedelta

import requests
from apis.openai import generate_embeddings
from apis.qdrant import upsert
from tqdm import tqdm


def get_activities(lastTimestamp, offset):
    tenant_id = os.environ.get('CROWDDEV_TENANT_ID')
    api_key = os.environ.get('CROWDDEV_API_KEY')
    if not tenant_id and api_key:
        return []

    url = f"https://app.crowd.dev/api/tenant/{tenant_id}/activity/query"

    payload = {
        "limit": 200,
        "offset": offset,
        "filter": {
            "createdAt": {"gte": lastTimestamp},
            "timestamp": {"gte": "2022-09-01"},
        },
        "orderBy": "timestamp_DESC",
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}",
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()["rows"]


def embed_activities(lastTimestamp, start_offset=0):
    offset = start_offset
    rows = get_activities(lastTimestamp, start_offset)
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
