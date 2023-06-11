# Sidekick

Sidekick is a GPT-powered information retrieval system that embeds pieces of information coming from several sources, stores the embeddings in a vector database, and enables querying based on the embeddings.

## Running and configuration

### Configuration options

Sidekick uses a `config.ini` file for most configuration options. You can provide this file in one of three ways:

1. Place it in the root of the repository.
2. Set the `SIDEKICK_CONFIG` environment variable to the path of your `config.ini` file.
3. Place it in `~/.sidekick/config.ini`.

Here is an example of a `config.ini` file:

```ini
[qdrant]
QDRANT_COLLECTION = sidekick
QDRANT_LOCAL_DB = res/test/local.qdrant
# If QDRANT_HOST is defined it will use it instead of the local db
# QDRANT_HOST =
[openai]
OAI_EMBEDDING_DIMENSIONS = 1536
OAI_EMBEDDING_MODEL = text-embedding-ada-002
OAI_EMBEDDING_CTX_LENGTH = 8191
OAI_EMBEDDING_ENCODING = cl100k_base
OAI_EMBEDDING_CHUNK_SIZE = 200
OAI_MAX_TEXTS_TO_EMBED_BATCH_SIZE = 100
```

### Environment variables

Some environment variables are always needed:

- `OPENAI_API_KEY`
- `QDRANT_API_KEY`

#### Running the Slack bot

To run the Slack bot, create your own app using the manifest (in the code). Then install your app in the workspace, and add the following environment variables:

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

Then run `bot.py`.

#### Ingesting data

To get data from Slack (through [crowd.dev](https://crowd.dev)), add the following environment variables:

- `CROWDDEV_TENANT_ID`
- `CROWDDEV_API_KEY`

and run `crowddev.py`.

To get data from Notion, add the following environment variable:

- `NOTION_API_KEY`

and run `notion.py`.

To get data from Linear, add the following environment variable:

- `LINEAR_API_KEY`

and run `linear.py`.

## Dev

```
mkdir ~/venv/sk && python -m venv ~/venv/sk
source ~/venv/sk/bin/activate
pip install --upgrade pip
pip install -e .
pip install ".[dev]"
```
