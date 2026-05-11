"""GitHub API client for GitSpy."""

import os
import sys

import requests


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token=None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitSpy",
        })
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        resp = self.session.get(url, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            print("GitHub API rate limit exceeded. Set GITHUB_TOKEN for higher limits.")
            sys.exit(1)
        if resp.status_code == 404:
            print(f"Not found: {endpoint}")
            sys.exit(1)
        resp.raise_for_status()
        return resp.json()

    def _get_paginated(self, endpoint, params=None, max_pages=5):
        params = params or {}
        params.setdefault("per_page", 100)
        results = []
        for page in range(1, max_pages + 1):
            params["page"] = page
            data = self._get(endpoint, params)
            if not data:
                break
            results.extend(data)
        return results

    def get_user(self, username):
        return self._get(f"/users/{username}")

    def get_repos(self, username, max_pages=3):
        return self._get_paginated(
            f"/users/{username}/repos",
            params={"sort": "updated"},
            max_pages=max_pages,
        )

    def get_events(self, username, max_pages=3):
        return self._get_paginated(
            f"/users/{username}/events/public",
            max_pages=max_pages,
        )

    def get_repo_commits(self, owner, repo, author=None, max_pages=2):
        params = {}
        if author:
            params["author"] = author
        return self._get_paginated(
            f"/repos/{owner}/{repo}/commits",
            params=params,
            max_pages=max_pages,
        )

    def get_orgs(self, username):
        return self._get(f"/users/{username}/orgs")

    def get_followers(self, username):
        return self._get_paginated(f"/users/{username}/followers", max_pages=2)

    def get_following(self, username):
        return self._get_paginated(f"/users/{username}/following", max_pages=2)

    def get_gists(self, username):
        return self._get_paginated(f"/users/{username}/gists", max_pages=2)

    def get_rate_limit(self):
        return self._get("/rate_limit")
