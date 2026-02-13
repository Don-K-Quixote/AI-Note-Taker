"""
LLM Provider Abstraction Layer.

Supports Ollama (local) and OpenAI GPT models as interchangeable backends
for meeting summarization.
"""

import os
from abc import ABC, abstractmethod

import requests
from loguru import logger


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt.
            temperature: Sampling temperature (0.0-1.0).
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text response.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is ready to use."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...


class OllamaProvider(LLMProvider):
    """Wraps Ollama HTTP API for local LLM inference."""

    def __init__(self, model: str, url: str, context_window: int = 8192) -> None:
        self._model = model
        self._url = url
        self._context_window = context_window

    @property
    def name(self) -> str:
        return f"Ollama ({self._model})"

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """Generate text via Ollama HTTP API."""
        logger.info(f"Generating with {self.name}...")
        try:
            response = requests.post(
                self._url,
                json={
                    "model": self._model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_ctx": self._context_window,
                        "top_p": 0.9,
                    },
                },
                timeout=900,
            )
            response.raise_for_status()
            return response.json().get("response", "Error: No response from Ollama")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            return "Error: Cannot connect to Ollama. Make sure it's running (ollama serve)"
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Error: Ollama request timed out. Try a shorter transcript or increase timeout."
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return f"Error: {e}"

    def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            base_url = self._url.rsplit("/api", 1)[0]
            resp = requests.get(base_url, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


class OpenAIProvider(LLMProvider):
    """OpenAI GPT integration via openai package."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str = "") -> None:
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    @property
    def name(self) -> str:
        return f"OpenAI ({self._model})"

    def generate(self, prompt: str, temperature: float = 0.3, max_tokens: int = 4096) -> str:
        """Generate text via OpenAI Chat Completions API."""
        if not self._api_key:
            logger.error("OpenAI API key not set")
            return "Error: OpenAI API key not configured. Set OPENAI_API_KEY environment variable or add it to config.json."

        logger.info(f"Generating with {self.name}...")
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self._api_key)
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "You are a professional meeting note-taker and summarizer."},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or "Error: Empty response from OpenAI"
        except ImportError:
            logger.error("openai package not installed")
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return f"Error: {e}"

    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)


def get_provider(config: dict) -> LLMProvider:
    """Factory function: returns the right provider based on config.

    Args:
        config: Full application config dict (must contain 'llm', 'ollama', and optionally 'openai' keys).

    Returns:
        An initialized LLMProvider instance.
    """
    provider_name = config.get("llm", {}).get("provider", "ollama")

    if provider_name == "openai":
        openai_cfg = config.get("openai", {})
        api_key = os.environ.get("OPENAI_API_KEY", openai_cfg.get("api_key", ""))
        return OpenAIProvider(
            model=openai_cfg.get("model", "gpt-4o-mini"),
            api_key=api_key,
        )

    # Default to Ollama
    ollama_cfg = config.get("ollama", {})
    return OllamaProvider(
        model=ollama_cfg.get("model", "llama3.1:8b"),
        url=ollama_cfg.get("url", "http://localhost:11434/api/generate"),
        context_window=ollama_cfg.get("context_window", 8192),
    )
