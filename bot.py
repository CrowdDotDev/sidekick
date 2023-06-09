import os
import re
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import dotenv
import requests


from apis.openai import generate_embeddings, chat

SYSTEM_PROMPT = """
You are an assistant for our company. Our employees will ask you questions.
You will have access to some context,
and your goal is to provide the best answer possible given the context.

The context can come from one of three places:
Notion, Slack, or Linear. All context pieces will have:

- url: link to the context
- timestamp: date of last modification
- title: title of the context
- body (optional): body of the context
- platform: linear, slack, or notion. Shows you which one of the three it is
- member: name of the person that created the context
- attributes: these are platform-specific, but important for each case

## Notion
It has internal documents and notes.

## Slack
It has our internal communication and messages.

## Linear
Our issue tracking software.

Attributes:
- status: if something is done or not. Can be Done (finished),
In Review (finished but not deployed),
In progress (being done), Todo (planned) and Backlog (not planned or started)
- priority: how important the issue is
- labels: can be either Feature, Bug, Improvement, Design, or empty.
- asignee: person in charge of doing the issue. Can be empty

You can use these attributes to anser about the state of an issue if you need.


## Your instructions

- Give an answer as specific as possible, and try to
derive aconclusion from the context.
- Always reference back to the URLs of the contexts,
we should be able to find information from your reply.
- Use attributes, especially for Linear, to know the
status of tasks.
- Use timestamps to know the timeline of things.
- There will probably me more than one context related to a topic.
Use them all, giving more weight to the most recent ones.
- If there are multiple relevant contexts, use them all,
but give more weight to the most recent ones.


## Formatting
- Write using Markdown
- Display links like this: <http://www.example.com|This message is a link>
- Referencing messages depends on the platform: 
  - for Slack and Notion, provide it like this: "
    <http://www.example.com|(source)>"
  - for linear, always add the title as a link.
    For example: <https://linear.app/linear/issue/XXX|Issue name>.
`
"""


app = App(token=os.environ["SLACK_BOT_TOKEN"])


def process_question(body, say):
    channel = body["channel"]
    event_ts = body["ts"]
    question = body["text"].strip().replace("<@(.*?)>", "", re.IGNORECASE)

    app.client.reactions_add(channel=channel, name="brain", timestamp=event_ts)

    try:
        embeddings = generate_embeddings(question)
        # Get answers from qdrant
        qdrant_data = {
            "vector": embeddings,
            "limit": 5,
            "params": {"hnsw_ef": 128, "exact": False},
            "with_vectors": False,
            "with_payload": True,
        }

        qdrant_headers = {
            "Content-Type": "application/json",
            "api-key": os.environ["QDRANT_API_KEY"],
        }

        url = f"{os.environ['QDRANT_HOST']}/collections/{os.environ['QDRANT_COLLECTION']}/points/search"
        qdrant_response = requests.post(url, json=qdrant_data, headers=qdrant_headers)
        qdrant_result = qdrant_response.json()["result"]

        if len(qdrant_result) == 0:
            app.client.chat_postMessage(
                channel=channel,
                text=":x: There are no results for your question. Please try different one.",
                thread_ts=event_ts,
            )
            return

        # Format qdrant_results
        context_data = [entry["payload"] for entry in qdrant_result]

        response = chat(
            SYSTEM_PROMPT, f"Question:\n{question}\n Context:\n{context_data}"
        )

        # Remove reaction
        app.client.reactions_remove(channel=channel, name="brain", timestamp=event_ts)
        app.client.chat_postMessage(channel=channel, text=response, thread_ts=event_ts)

    except Exception as err:
        print(f"Error: {err}")
        app.client.chat_postMessage(
            channel=channel,
            text=":x: An error occurred while fetching the answer. Please try again later.",
            thread_ts=event_ts,
        )


@app.event("message")
def handle_message(body, say):
    from pprint import pprint as pp

    if body["event"]["channel_type"] != "im":
        return
    process_question(body["event"], say)


@app.event("app_mention")
def handle_app_mention(body, say):
    process_question(body, say)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
    print("⚡️ Crowd assistant app is running!")
