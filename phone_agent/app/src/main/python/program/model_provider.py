import json
from urllib.request import Request, urlopen

class OpenAICompatibleBackend:
    """Provider-neutral chat backend for OpenAI-compatible APIs.

    Endpoint, model, and API key are runtime configuration only.
    The response is treated as untrusted model output and is never command authority.
    """
    def __init__(self, endpoint: str, model: str, api_key: str, timeout: int = 60):
        if not endpoint or not model or not api_key:
            raise ValueError("endpoint, model and api_key are required")
        self.endpoint = endpoint.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete(self, system_prompt: str, user_input: str, context: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context + "\n\nUSER COMMAND:\n" + user_input},
            ],
        }
        req = Request(
            self.endpoint + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        with urlopen(req, timeout=self.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]
