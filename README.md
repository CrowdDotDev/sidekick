# Sidekick

## Running and configuration

### Environment variables

Some environment variables are always needed

- `OPENAI_API_KEY`
- `QDRANT_HOST`
- `QDRANT_COLLECTION`
- `QDRANT_API_KEY`

### Running the Slack bot

To run the Slack bot, create your own app using the manifest (in the code). Then install your app in the workspace, and add the following environment variables:

- `SLACK_BOT_TOKEN`
- `SLACK_APP_TOKEN`

Then run `bot.py`.

### Ingesting data

To get data from Slack (through [crowd.dev](https://crowd.dev)), add the following environment variables
- `CROWDDEV_TENANT_ID`
- `CROWDDEV_API_KEY`

and run `crowddev.py`

To get data from Notion, add the following environment variable
- `NOTION_API_KEY`

and run `notion.py`.

To get data from Linear, add the following environment variable
- `LINEAR_API_KEY`

and run `linear.py`. 