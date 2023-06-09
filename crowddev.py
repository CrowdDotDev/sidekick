import requests
from datetime import datetime, timedelta
from apis.openai import generate_embeddings
from apis.qdrant import upsert
import os
from tqdm import tqdm
import dotenv

dotenv.load_dotenv(".env")


def get_activities(lastTimestamp, offset):
    url = f"https://app.crowd.dev/api/tenant/{os.environ.get('CROWDDEV_TENANT_ID')}/activity/query"

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
        "authorization": f"Bearer {os.environ.get('CROWDDEV_API_KEY')}",
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


DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
# DATE = (datetime.now() - timedelta(days=17)).strftime('%Y-%m-%d')
embed_activities(DATE, start_offset=0)
