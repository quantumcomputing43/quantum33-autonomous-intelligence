from urllib.parse import quote
from .github_adapter import GitHubAdapter

class GitHubService:
    """GitHub service; reads are automatic, writes are explicit and runtime-gated."""
    def __init__(self, token: str):
        self.api=GitHubAdapter(token)
        self.current_repository=None

    def _ctx(self, full_name):
        if "/" not in full_name or full_name.count("/") != 1:
            raise ValueError("repository must be owner/name")
        owner,repo=full_name.split("/",1)
        self.current_repository=full_name
        return owner,repo

    def repository(self, full_name):
        owner,repo=self._ctx(full_name); return self.api.get_repository(owner,repo)

    def file(self, full_name,path,ref=None):
        owner,repo=self._ctx(full_name); return self.api.get_file(owner,repo,path,ref)

    def tree(self, full_name,ref="HEAD"):
        owner,repo=self._ctx(full_name)
        return self.api.request("GET",f"/repos/{owner}/{repo}/git/trees/{quote(ref,safe='')}?recursive=1")

    def commits(self, full_name,per_page=20):
        owner,repo=self._ctx(full_name)
        return self.api.request("GET",f"/repos/{owner}/{repo}/commits?per_page={int(per_page)}")

    def workflow_runs(self, full_name,per_page=20):
        owner,repo=self._ctx(full_name)
        return self.api.request("GET",f"/repos/{owner}/{repo}/actions/runs?per_page={int(per_page)}")

    def workflow_dispatch(self, full_name, workflow, ref="main", inputs=None):
        owner,repo=self._ctx(full_name)
        path=f"/repos/{owner}/{repo}/actions/workflows/{quote(workflow,safe='')}/dispatches"
        body={"ref":ref}
        if inputs: body["inputs"]=inputs
        return self.api.request("POST",path,body)

    def create_file(self, full_name, path, content, message, branch="main"):
        owner,repo=self._ctx(full_name)
        return self.api.request("PUT",f"/repos/{owner}/{repo}/contents/{path}",
            {"message":message,"content":__import__("base64").b64encode(content.encode()).decode(),"branch":branch})

    def update_file(self, full_name, path, content, message, sha, branch="main"):
        owner,repo=self._ctx(full_name)
        return self.api.request("PUT",f"/repos/{owner}/repos/{repo}/contents/{path}",
            {"message":message,"content":__import__("base64").b64encode(content.encode()).decode(),
             "sha":sha,"branch":branch})
