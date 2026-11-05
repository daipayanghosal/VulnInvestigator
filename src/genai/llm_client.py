"""
src/genai/llm_client.py
~~~~~~~~~~~~~~~~~~~~~~~
Unified LLM client interface supporting OpenAI, Ollama, and Google Gemini backends.

Design
------
- ``LLMClient`` is an abstract base class defining the ``complete()`` contract.
- Concrete implementations handle backend-specific API calls and retry logic.
- ``get_llm_client()`` is a factory function that instantiates the correct
  backend based on a string identifier.

All clients retry up to 3 times with exponential back-off on transient errors.

Environment variables read by each backend
------------------------------------------
OpenAI  : OPENAI_API_KEY
Ollama  : OLLAMA_BASE_URL  (default: http://localhost:11434)
Gemini  : GEMINI_API_KEY   (or GOOGLE_API_KEY as fallback)
"""

from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 2.0  # seconds; doubles each retry


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class LLMClient(ABC):
    """Abstract LLM client.  All backends must implement :meth:`complete`."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send a chat completion request and return the assistant's reply.

        Parameters
        ----------
        system_prompt:
            Instruction / persona text for the system role.
        user_prompt:
            User turn content (the actual question / task).

        Returns
        -------
        str
            The model's text response.

        Raises
        ------
        RuntimeError
            If all retries are exhausted.
        """


# ---------------------------------------------------------------------------
# OpenAI backend
# ---------------------------------------------------------------------------

class OpenAIClient(LLMClient):
    """LLM client backed by the OpenAI Chat Completions API.

    Parameters
    ----------
    model:
        Model name, e.g. ``"gpt-4o"`` or ``"gpt-4-turbo"``.
    temperature:
        Sampling temperature (0–2).
    max_tokens:
        Maximum completion tokens.
    api_key:
        Overrides the ``OPENAI_API_KEY`` environment variable.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        api_key: str | None = None,
    ) -> None:
        import openai  # type: ignore

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        resolved_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._client = openai.OpenAI(api_key=resolved_key)
        logger.info("OpenAIClient: model=%s", model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Call the OpenAI Chat Completions endpoint with retry logic."""
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                wait = _RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "OpenAIClient: attempt %d/%d failed — %s. Retrying in %.1f s",
                    attempt, _MAX_RETRIES, exc, wait,
                )
                time.sleep(wait)
        raise RuntimeError(
            f"OpenAIClient: all {_MAX_RETRIES} retries exhausted. Last error: {last_exc}"
        )


# ---------------------------------------------------------------------------
# Ollama backend
# ---------------------------------------------------------------------------

class OllamaClient(LLMClient):
    """LLM client backed by a local Ollama instance.

    Parameters
    ----------
    model:
        Ollama model tag, e.g. ``"llama3:8b"`` or ``"mistral"``.
    temperature:
        Sampling temperature.
    host:
        Ollama API base URL (overrides ``OLLAMA_BASE_URL`` env var).
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        temperature: float = 0.2,
        host: str | None = None,
    ) -> None:
        import ollama  # type: ignore

        self.model = model
        self.temperature = temperature
        resolved_host = host or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._client = ollama.Client(host=resolved_host)
        logger.info("OllamaClient: model=%s host=%s", model, resolved_host)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Call the Ollama chat endpoint with retry logic."""
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self._client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    options={"temperature": self.temperature},
                )
                return response["message"]["content"]  # type: ignore[index]
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                wait = _RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "OllamaClient: attempt %d/%d failed — %s. Retrying in %.1f s",
                    attempt, _MAX_RETRIES, exc, wait,
                )
                time.sleep(wait)
        raise RuntimeError(
            f"OllamaClient: all {_MAX_RETRIES} retries exhausted. Last error: {last_exc}"
        )


# ---------------------------------------------------------------------------
# Google Gemini backend
# ---------------------------------------------------------------------------

class GeminiClient(LLMClient):
    """LLM client backed by the Google Gemini API (using modern google-genai SDK).

    Parameters
    ----------
    model:
        Gemini model name, e.g. ``"gemini-3.5-flash"``.
    temperature:
        Sampling temperature (0–1 for Gemini).
    max_tokens:
        Maximum output tokens.
    api_key:
        Overrides the ``GEMINI_API_KEY`` / ``GOOGLE_API_KEY`` environment variable.
    """

    def __init__(
        self,
        model: str = "gemini-3.5-flash",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        api_key: str | None = None,
    ) -> None:
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except ImportError as exc:
            raise ImportError("Please install google-genai: pip install google-genai") from exc

        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        st_key = ""
        try:
            import streamlit as st  # type: ignore
            st_key = str(st.secrets.get("GEMINI_API_KEY", "") or st.secrets.get("GOOGLE_API_KEY", ""))
        except Exception:
            pass

        resolved_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or st_key
            or ""
        )
        self._client = genai.Client(api_key=resolved_key)
        self._types = types
        logger.info("GeminiClient: model=%s (google-genai)", model)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Call the Gemini GenerateContent API via modern google-genai SDK."""
        last_exc: Exception | None = None
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                config = self._types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=config,
                )
                return response.text or ""
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                wait = _RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "GeminiClient: attempt %d/%d failed — %s. Retrying in %.1f s",
                    attempt, _MAX_RETRIES, exc, wait,
                )
                time.sleep(wait)
        raise RuntimeError(
            f"GeminiClient: all {_MAX_RETRIES} retries exhausted. Last error: {last_exc}"
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_llm_client(backend: str, model: str, **kwargs: Any) -> LLMClient:
    """Instantiate and return the correct LLM client for *backend*.

    Parameters
    ----------
    backend:
        Backend identifier — one of ``"openai"``, ``"ollama"``, ``"gemini"``.
    model:
        Model name passed to the backend constructor.
    **kwargs:
        Additional keyword arguments forwarded to the backend constructor
        (e.g. ``temperature``, ``max_tokens``, ``api_key``).

    Returns
    -------
    LLMClient

    Raises
    ------
    ValueError
        If *backend* is not recognised.
    """
    backend_lower = backend.lower().strip()
    if backend_lower == "openai":
        return OpenAIClient(model=model, **kwargs)
    elif backend_lower == "ollama":
        return OllamaClient(model=model, **kwargs)
    elif backend_lower in ("gemini", "google"):
        return GeminiClient(model=model, **kwargs)
    else:
        raise ValueError(
            f"Unknown LLM backend: '{backend}'. Choose from: openai, ollama, gemini"
        )
