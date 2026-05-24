import json
import os
import urllib.request


class LLMService:
    UNREACHABLE_PREFIX = "Ollama AI service is not reachable."

    def __init__(self):
        self.ollama_model = os.getenv("OLLAMA_MODEL", "phi3:latest")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")

    def generate(self, message: str, system_prompt: str | None = None, model: str | None = None) -> str:
        try:
            return self._generate_ollama(message, system_prompt, model)
        except Exception:
            return (
                f"{self.UNREACHABLE_PREFIX} Start Ollama with `ollama run phi3`. "
                f"Your message was: {message}"
            )

    def is_unreachable_response(self, text: str) -> bool:
        return text.startswith(self.UNREACHABLE_PREFIX)

    def _generate_ollama(self, message: str, system_prompt: str | None, model: str | None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = json.dumps({
            "model": model or self.ollama_model,
            "messages": messages,
            "stream": False,
        }).encode("utf-8")

        request = urllib.request.Request(
            self.ollama_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("message", {}).get("content", "")


llm_service = LLMService()
