import os
import datetime

import pytz
import requests
from apis.openai import generate_embeddings
from apis.qdrant import upsert
import tqdm


DATABASES = [
    "482fa260a9394a4aa20a93508acd659d",  # Shared notes
    "a85e95936d02431ab41b0f71eb701658",  # Employee Directory
    "fe8851a21893481193f1f9de9c3e5184",  # User research notes
]

PAGES = [
    "2b6281823fc747108b957b3968937248",  # What is crowd.dev
    "c91a1adde6864c6385fa7607900cf80f",  # Mission
    "b043987017804f98a742509872ccdb28",  # Ways of working
    "c50d6e854c5e4174b61e545ce59738f8",  # Tools
    "25175a4e7f23410a876105b54f7bb83d",  # Admin information
    "ce89b0b2de6443488a9f8ecc4c8611b7",  # Vacation and Sick days
    "2d75482a29824aaabebc89b3427e6d56",  # Expenses
    "e4877da4c71e43408a2c0a6fac95bef9",  # Benefits
    "6ab2dc24f72743d3af8d936a6628e6d1",  # Employee Option Plan
    "9f5e3c5810f54f3cb452d05b26736be0",  # First line customer support
]


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

        response = requests.post(url, headers=get_headers(api_key), json=data)

        if response.status_code != 200:
            raise RuntimeError(f"Request failed with status code {response.status_code}")

        result = response.json()
        all_pages.extend(result["results"])
        has_more = result.get("has_more", False)
        next_cursor = result.get("next_cursor", None)

    return all_pages


# Define a function to get a single page's content


def get_page_content(page_id, api_key):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=get_headers(api_key))

    if response.status_code != 200:
        print(response)
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()["results"]


def get_page(page_id, api_key):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=get_headers(api_key))

    if response.status_code != 200:
        print(response)
        raise Exception(f"Request failed with status code {response.status_code}")

    return response.json()


def embed_pages(unfiltered_pages, filterP, api_key):
    if isinstance(unfiltered_pages[0], str):
        unfiltered_pages = [get_page(page_id, api_key) for page_id in unfiltered_pages]

    now = datetime.datetime.now(datetime.timezone.utc)
    one_day_ago = now - datetime.timedelta(days=1)

    if filterP:
        pages = []
        for item in unfiltered_pages:
            time_str = item["last_edited_time"]
            time = datetime.datetime.fromisoformat(time_str[:-1]).replace(
                tzinfo=pytz.UTC
            )
            if one_day_ago <= time <= now:
                pages.append(item)
    else:
        pages = unfiltered_pages

    for page in tqdm.tqdm(pages, total=len(pages)):
        key = "Name" if "Name" in page["properties"] else "title"
        try:
            title = page["properties"][key]["title"][0]["plain_text"]
        except:  # noqa
            continue

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
