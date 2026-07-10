from __future__ import annotations

import os
from datetime import datetime, timezone

import psycopg2
import requests
from dotenv import load_dotenv


def fetch_repositories(owner: str, token: str | None) -> list[dict]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(
        f"https://api.github.com/users/{owner}/repos",
        params={"per_page": 100, "sort": "updated"},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    load_dotenv()
    owner = os.environ["GITHUB_OWNER"]
    repositories = fetch_repositories(owner, os.getenv("GITHUB_TOKEN"))
    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "github_bi"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )
    collected_at = datetime.now(timezone.utc)
    try:
        with connection, connection.cursor() as cursor:
            for repository in repositories:
                cursor.execute(
                    """
                    insert into raw.github_repositories (
                        repository_id, repository_name, repository_full_name,
                        description, language, stars, forks, open_issues,
                        is_archived, created_at, updated_at, collected_at
                    ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (repository_id) do update set
                        repository_name = excluded.repository_name,
                        description = excluded.description,
                        language = excluded.language,
                        stars = excluded.stars,
                        forks = excluded.forks,
                        open_issues = excluded.open_issues,
                        is_archived = excluded.is_archived,
                        updated_at = excluded.updated_at,
                        collected_at = excluded.collected_at
                    """,
                    (
                        repository["id"],
                        repository["name"],
                        repository["full_name"],
                        repository.get("description"),
                        repository.get("language"),
                        repository.get("stargazers_count", 0),
                        repository.get("forks_count", 0),
                        repository.get("open_issues_count", 0),
                        repository.get("archived", False),
                        repository.get("created_at"),
                        repository.get("updated_at"),
                        collected_at,
                    ),
                )
    finally:
        connection.close()
    print(f"Loaded {len(repositories)} repositories for {owner}.")


if __name__ == "__main__":
    main()
