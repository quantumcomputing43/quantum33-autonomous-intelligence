from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import Request, urlopen
import json

@dataclass
class KnowledgeResult:
    query: str
    source: str
    content: str

class KnowledgeProvider:
    """Search-provider interface. Returned material is evidence and must be provenance-tagged."""

    def search(self, query: str):
        raise NotImplementedError

class GenericJsonSearchProvider(KnowledgeProvider):
    """Optional provider adapter. Endpoint and authentication are configured outside source."""

    def __init__(self, endpoint: str, headers=None):
        self.endpoint = endpoint.rstrip("/")
        self.headers = headers or {}

    def search(self, query: str):
        req = Request(
            self.endpoint + "?q=" + quote(query),
            headers={"Accept": "application/json", **self.headers},
        )
        with urlopen(req, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return payload
