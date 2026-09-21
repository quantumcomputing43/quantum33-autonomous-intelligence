from urllib.parse import quote
from .github_adapter import GitHubAdapter

class GitHubService:
    """Read-heavy GitHub service. Mutations are explicit and separately authorized."""
    def __init__(self, token: str):
        self.api = GitHubAdapter(token)

    def repository(self, full_name: str):
        owner, repo = full_name.split("/", 1)
        return self.api.get_repository(owner, repo)

    def file(self, full_name: str, path: str, ref=None):
        owner, repo = full_name.split("/", 1)
        return self.api.get_file(owner, repo, path, ref)

    def tree(self, full_name: str, ref="HEAD"):
        owner, repo = full_name.split("/", 1)
        return self.api.request("GET", f"/repos/{owner}/{repo}/git/trees/{quote(ref, safe='')}?recursive=1")

    def commits(self, full_name: str, per_page=20):
        owner, repo = full_name.split("/", 1)
        return self.api.request("GET", f"/repos/{owner}/{repo}/commits?per_page={int(per_page)}")

    def workflow_runs(self, full_name: str, per_page=20):
        owner, repo = full_name.split("/", 1)
        return self.api.request("GET", f"/repos/{owner}/{repo}/actions/runs?per_page={int(per_page)}")
