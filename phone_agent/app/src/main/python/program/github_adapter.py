import json
from urllib.request import Request, urlopen

class GitHubAdapter:
    """Provider-neutral GitHub REST adapter. Credentials are supplied at runtime, never stored in source."""

    def __init__(self, token: str, api_base: str = "https://api.github.com"):
        if not token:
            raise ValueError("GitHub token is required")
        self.token = token
        self.api_base = api_base.rstrip("/")

    def request(self, method: str, path: str, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = Request(
            self.api_base + path,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else None

    def get_repository(self, owner: str, repo: str):
        return self.request("GET", f"/repos/{owner}/{repo}")

    def get_file(self, owner: str, repo: str, path: str, ref=None):
        suffix = "" if ref is None else f"?ref={ref}"
        return self.request("GET", f"/repos/{owner}/{repo}/contents/{path}{suffix}")
