# -*- coding: utf-8 -*-

import os
import time
from typing import Dict, List, Callable, Tuple

import requests

import sidekick.tools as T
from sidekick.payload import Payload, FactType
from sidekick.embed import embed_source_unit
from sidekick.sources.state import State

SourceName = 'notion'
Timeout = 15


def get_headers():
    T.load_dotenv()
    api_key = os.environ.get('NOTION_API_KEY', '')
    if not api_key:
        raise RuntimeError('No NOTION_API_KEY found as an environment variable')

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def fetch_all_pages_in_database(database_id: str) -> List:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    has_more = True
    next_cursor = None

    all_pages = []
    while has_more:
        data = {
            "page_size": 20,  # Maximum allowed by the API
        }
        if next_cursor:
            data["start_cursor"] = next_cursor

        response = requests.post(url,
                                 headers=get_headers(),
                                 json=data,
                                 timeout=Timeout)

        if response.status_code != 200:
            raise RuntimeError(f"Request failed with status code {response.status_code}")

        result = response.json()
        all_pages.extend(result["results"])
        has_more = result.get("has_more", False)
        next_cursor = result.get("next_cursor", None)

    return all_pages


def fetch_page_content(page_id: str) -> List:
    """It returns the actual content of the page, in the form of a
    list of blocks.
    """
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=get_headers(), timeout=Timeout)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}")

    time.sleep(0.5)
    return response.json()["results"]


def fetch_page(page_id: str) -> Dict:
    """The page includes timestamps and user information, and a
    'properties' object with things like the title, but not the page
    contents.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    response = requests.get(url, headers=get_headers(), timeout=Timeout)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}")

    return response.json()


def extract_page_title(page: Dict) -> str:
    """The title will be a property with a title component:

    "Title": {
        "id": "title",
        "type": "title",
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Bug bash",
                    "link": null
                },
                "annotations": {
                    "bold": false,
                },
                "plain_text": "Bug bash",
                "href": null
            }
        ]
    }

    or

    "Name": {
      "title": [
        {
          "type": "text",
          "text": {
            "content": "The title"
          }
        }
      ]
    }

    https://developers.notion.com/reference/page
    https://developers.notion.com/reference/property-value-object#title-property-values
    """
    def _get_element_text(element):
        if 'plain_text' in element:
            return element['plain_text']
        if 'text' in element:
            return element['text'].get('content', '')
        return ''

    for prop in page['properties'].values():
        title = prop.get('title', [])
        if title:
            return ' '.join([
                _get_element_text(el) for el in title
            ])
    return ''


def fetch_user_data(user_id: str, sleeping: int = 0) -> str:
    response = requests.get(f"https://api.notion.com/v1/users/{user_id}",
                            headers=get_headers(),
                            timeout=Timeout)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed with status code {response.status_code}")

    user_data = response.json()

    if sleeping:
        time.sleep(sleeping)

    return user_data['name']


def fetch_page_authors(page: Dict, sleeping: int = 0) -> Tuple:
    created_by_id = page['created_by']['id']
    last_edited_by_id = (created_by_id if 'last_edited_by' not in page
                         else page['last_edited_by']['id'])

    created_by = fetch_user_data(created_by_id, sleeping)
    last_edited_by = (created_by if last_edited_by_id == created_by_id
                      else fetch_user_data(last_edited_by_id, sleeping))

    return created_by, last_edited_by, last_edited_by_id


def ingest_page(title: str,
                created_by: str,
                last_edited_by: str,
                last_edited_by_id: str,
                url: str,
                timestamp: str,
                content: List,
                fact_type: FactType):

    print('Ingesting', title)

    source_unit_id = url

    def _text_from_block(block):
        out = []
        if block['type'] in block:
            for rich_text in block[block['type']].get('rich_text', []):
                out.append(rich_text.get('plain_text'))
        return ' '.join(out)

    payloads = []
    current_heading_chain = []
    current_text = []
    current_heading_id = ''
    for block in content:
        if block["object"] == "block":
            if block["type"].startswith("heading"):

                text_so_far = '\n\n'.join(current_text).strip()
                if text_so_far:
                    block_last_edited_by_id = block["last_edited_by"]["id"]
                    block_last_edited_by = (last_edited_by
                                            if (block_last_edited_by_id ==
                                                last_edited_by_id)
                                            else
                                            fetch_user_data(block_last_edited_by_id))
                    payloads.append(
                        Payload(body=text_so_far,
                                source_unit_id=source_unit_id,
                                uri=url + (('#' + current_heading_id)
                                           if current_heading_id else ''),
                                # Extract heading texts from the stack
                                headings=[title] + [heading[1] for heading in
                                                    current_heading_chain],
                                created_by=created_by,
                                last_edited_by=block_last_edited_by,
                                source=SourceName,
                                fact_type=fact_type,
                                timestamp=timestamp))
                    current_text = []
                    current_heading_id = block['id'].replace('-', '')

                # Extract level from heading type (e.g. "heading_1" => 1)
                level = int(block["type"][-1])
                if current_heading_chain and level <= current_heading_chain[-1][0]:
                    # Pop headings from the stack until we reach the
                    # correct level
                    while (current_heading_chain and level <=
                           current_heading_chain[-1][0]):
                        current_heading_chain.pop()
                # Push the current heading onto the stack
                current_heading_chain.append((level, _text_from_block(block)))
            else:
                text = _text_from_block(block)
                if text:
                    current_text.append(text)

    embed_source_unit(payloads, source_unit_id=source_unit_id)


def process_page(page_id: str,
                 ingesting_function: Callable,
                 state: State,
                 fact_type: FactType,
                 recurse_subpages: bool = False,
                 visited_pages: set = None,
                 sleeping: int = 0):

    short_page_id = page_id.replace('-', '')

    visited = visited_pages or set([])
    if short_page_id in visited:
        return

    page = fetch_page(page_id)
    if sleeping:
        time.sleep(sleeping)

    page_content = fetch_page_content(page_id)

    last_edited_tm = T.timestamp_as_utc(page.get(
        'last_edited_time', page['created_time']))

    last_seen_dt = state.get_last_seen(SourceName, short_page_id)
    state.update_last_seen(SourceName, short_page_id)

    if (last_seen_dt is None) or (last_edited_tm > last_seen_dt):
        created_by, last_edited_by, last_edited_by_id = fetch_page_authors(page)
        ingesting_function(extract_page_title(page),
                           created_by=created_by,
                           last_edited_by=last_edited_by,
                           last_edited_by_id=last_edited_by_id,
                           url=page['url'],
                           timestamp=last_edited_tm,
                           content=page_content,
                           fact_type=fact_type)

    if recurse_subpages:
        visited.add(short_page_id)
        for block in page_content:
            if block['type'] == 'child_page':
                process_page(block['id'],
                             ingesting_function,
                             state=state,
                             fact_type=fact_type,
                             recurse_subpages=True,
                             visited_pages=visited,
                             sleeping=sleeping)


def ingest():
    sources = T.get_source_config(SourceName)

    page_id_fact_types = []
    for database in sources.get('databases', []):
        try:
            fact_type = FactType(database['fact_type'])
            page_id_fact_types.extend(
                [(page_id, fact_type) for page_id in
                 fetch_all_pages_in_database(database['id'])]
            )
        except:
            print('Error preparing database for ingestion: ' + str(database))

    for page in sources.get('pages', []):
        try:
            page_id_fact_types.append((page['id'],
                                        FactType(page['fact_type'])))
        except:
            print('Error preparing page for ingestion: ' + str(page))

    state = State()
    for (page_id, fact_type) in page_id_fact_types:
        process_page(page_id,
                     ingesting_function=ingest_page,
                     state=state,
                     fact_type=fact_type,
                     recurse_subpages=True,
                     sleeping=0.5)

def _check_qtc():
    # build_platform_page_id = 'bff67ad3178e4156be5153981f90ab5d'
    cr_page_id = 'f557ddee52244b0e81d63d68f90d8333'

    state = State()
    process_page(cr_page_id,
                 ingesting_function=ingest_page,
                 state=state,
                 fact_type=FactType.historical,
                 recurse_subpages=True,
                 sleeping=0.5)


if __name__ == "__main__":
    ingest()
