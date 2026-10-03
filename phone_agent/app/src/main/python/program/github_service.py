from urllib.parse import quote
from .github_adapter import GitHubAdapter

class GitHubService:
    """GitHub service; reads are automatic, mutations remain authorization-gated."""
    def __init__(self, token: str):
        self.api = GitHubAdapter(token)
        self.current_repository = None

    def repository(self, full_name):
        owner, repo = full_name.split("/",1); self.current_repository=full_name
        return self.api.get_repository(owner,repo)

    def file(self, full_name,path,ref=None):
        owner,repo=full_name.split("/",1); self.current_repository=full_name
        return self.api.get_file(owner,repo,path,ref)

    def tree(self, full_name,ref="HEAD"):
        owner,repo=full_name.split("/",1); self.current_repository=full_name
        return self.api.request("GET",f"/repos/{owner}/{repo}/git/trees/{quote(ref,safe='')}?recursive=1")

    def commits(self, full_name,per_page=20):
        owner,repo=full_name.split("/",1); self.current_repository=full_name
        return self.api.request("GET",f"/repos/{owner}/{repo}/commits?per_page={int(per_page)}")

    def workflow_runs(self, full_name,per_page=20):
        owner,repo=full_name.split("/",1); self.current_repository=full_name
        return self.api.request("GET",f"/repos/{owner}/{repo}/actions/runs?per_page={int(per_page)}")
