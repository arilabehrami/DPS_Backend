import json
import os
import urllib.request

from openai import OpenAI


class LLMService:
    def __init__(self):
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "phi3")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")

    def generate(self, message: str, system_prompt: str | None = None, model: str | None = None) -> str:
        if os.getenv("OPENAI_API_KEY"):
            return self._generate_openai(message, system_prompt, model)

        try:
            return self._generate_ollama(message, system_prompt, model)
        except Exception:
            return (
                "AI service is configured, but no OpenAI key is set and Ollama is not reachable. "
                f"Your message was: {message}"
            )

    def _generate_openai(self, message: str, system_prompt: str | None, model: str | None) -> str:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=model or self.openai_model,
            messages=messages,
        )
        return response.choices[0].message.content or ""

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
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("message", {}).get("content", "")


llm_service = LLMService()
