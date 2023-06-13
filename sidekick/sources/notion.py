# -*- coding: utf-8 -*-

import os
import requests

import sidekick.tools as T
from sidekick.payload import Payload, FactType
from sidekick.embed import embed_source_unit

from sidekick.sources.state import State


def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def get_all_pages(database_id, api_key):
    all_pages = []
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    has_more = True
    next_cursor = None

    while has_more:
        data = {
            "page_size": 20,  # Maximum allowed by the API
        }
        if next_cursor:
            data["start_cursor"] = next_cursor

        response = requests.post(url,
                                 headers=get_headers(api_key),
                                 json=data,
                                 timeout=5)

        if response.status_code != 200:
            raise RuntimeError(f"Request failed with status code {response.status_code}")

        result = response.json()
        all_pages.extend(result["results"])
        has_more = result.get("has_more", False)
        next_cursor = result.get("next_cursor", None)

    return all_pages


def get_page_content(page_id, api_key):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=get_headers(api_key), timeout=5)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}")

    return response.json()["results"]


def get_page(page_id, api_key):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=get_headers(api_key), timeout=5)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}")

    return response.json()


def ingest_page(page_id, state, api_key):
    page = get_page(page_id, api_key)

    key = "Name" if "Name" in page["properties"] else "title"
    try:
        title = page["properties"][key]["title"][0]["plain_text"]
    except:
        print('Failed finding a title in page ' + page_id)

    payload = Payload(body='',
                      source_unit_id=page_id,
                      uri=page['url'],
                      headings)
    starting_payload = {
        "url": page["url"],
        "timestamp": page["last_edited_time"],
        "title": title,
        "platform": "notion",
    }
    try:
        content = get_page_content(page["id"], api_key)
        for block in content:
            if block["object"] == "block" and block["type"] == "paragraph":
                rich_texts = block["paragraph"]["rich_text"]
                for rich_text in rich_texts:
                    text = rich_text.get("text", {}).get("content", "")
                    if text:
                        embed = generate_embeddings(f"{title} \n {text}")
                        if embed:
                            payload = {
                                **starting_payload,
                                "body": text,
                            }

                            upsert([abs(hash(block["id"]))], [payload], [embed])
    except:
        print("Could not get content for page: ", page["url"])


def ingest():
    api_key = os.environ.get("NOTION_API_KEY")
    if not api_key:
        return

    filterP = True
    embed_pages(PAGES, filterP, api_key)
    for database_id in DATABASES:
        # Get all pages from the database and print their content
        pages = get_all_pages(database_id, api_key)
        embed_pages(pages, filterP, api_key)


if __name__ == "__main__":
    env_file = '.env'

    # We do not want to try to load .env when running as a github action
    if os.path.exists(env_file):
        import dotenv
        dotenv.load_dotenv(env_file)

    ingest()
