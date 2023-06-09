import requests
import datetime
from apis.qdrant import upsert
from apis.openai import generate_embeddings
from tqdm import tqdm
import dotenv
import os


# Replace YOUR_API_KEY with your Linear API key
api_key = os.environ.get("LINEAR_API_KEY")
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

# Set the date after which you want to retrieve issues
# One day ago in this format (YYYY-MM-DDTHH:mm:ss.sssZ)
# date_filter = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
date_filter = "2023-01-01T00:00:00.000Z"

# Convert the date string to a datetime object
date_filter = datetime.datetime.fromisoformat(date_filter.replace("Z", "+00:00"))

query = """
query($cursor: String, $pageSize: Int) {
  issues(first: $pageSize, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    nodes {
      id
      title
      description
      state {
        name
      }
      estimate
      priorityLabel
      creator {
        name
      }
      assignee {
        name
      }
      labels {
        nodes {
          name
        }
      }
      cycle {
        name
      }
      createdAt
      startedAt
      completedAt
      canceledAt
      parent {
        id
      }
      updatedAt
      url
    }
  }
}
"""


def get_issues(date_filter, cursor=None, page_size=50):
    query = """
    query GetIssues($cursor: String, $pageSize: Int, $updatedAfter: DateTime) {
        issues(first: $pageSize, after: $cursor, filter: {updatedAt:{ gt: $updatedAfter}}) {
            nodes {
              id
              title
              description
              state {
                name
              }
              estimate
              priorityLabel
              creator {
                name
              }
              assignee {
                name
              }
              labels {
                nodes {
                  name
                }
              }
              cycle {
                name
              }
              createdAt
              startedAt
              completedAt
              canceledAt
              parent {
                id
              }
              updatedAt
              url
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
    """

    variables = {
        "cursor": cursor,
        "pageSize": page_size,
        "updatedAfter": date_filter.isoformat(),
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
    )
    data = response.json()

    if response.status_code == 200:
        issues = data["data"]["issues"]["nodes"]
        end_cursor = data["data"]["issues"]["pageInfo"]["endCursor"]
        has_next_page = data["data"]["issues"]["pageInfo"]["hasNextPage"]

        if has_next_page:
            return issues + get_issues(
                date_filter, cursor=end_cursor, page_size=page_size
            )
        else:
            return issues
    else:
        raise Exception(f'Error fetching issues: {data.get("errors", "")}')


def main():
    try:
        issues = get_issues(date_filter)
        for issue in tqdm(issues, total=len(issues)):
            print(issue)
            labels = ", ".join([label["name"] for label in issue["labels"]["nodes"]])
            creator = issue["creator"]["name"] if issue["creator"] else "N/A"
            assignee = issue["assignee"]["name"] if issue["assignee"] else "N/A"
            parent_id = issue["parent"]["id"] if issue["parent"] else "N/A"

            payload = {
                "url": issue["url"],
                "timestamp": issue["updatedAt"],
                "title": issue["title"],
                "body": issue["description"] if issue["description"] else "",
                "platform": "linear",
                "member": creator,
                "attributes": {
                    "status": issue["state"]["name"],
                    "estimate": issue["estimate"],
                    "priority": issue["priorityLabel"],
                    "labels": labels,
                    "cycle": issue["cycle"]["name"] if issue["cycle"] else "N/A",
                    "created": issue["createdAt"],
                    "assignee": assignee,
                    "parent": parent_id,
                },
            }

            print(payload)

            embed = generate_embeddings(payload["title"] + "\n" + payload["body"])

            if embed:
                upsert([abs(hash(str(issue["id"])))], [payload], [embed])

    except Exception as e:
        print(e)
        raise e


if __name__ == "__main__":
    main()
