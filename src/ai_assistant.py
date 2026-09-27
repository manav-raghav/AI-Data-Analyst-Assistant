"""AI provider helper for the AI Data Analyst Assistant."""

import os
import time

import requests
from dotenv import load_dotenv
from google import genai


load_dotenv()


MODEL = "gemini-3.6-flash"  
OLLAMA_MODEL = "qwen3:4b"
OLLAMA_URL = "http://localhost:11434/api/generate"
RETRY_DELAY_SECONDS = 1
OLLAMA_TIMEOUT_SECONDS = 90


def _get_gemini_response(prompt: str, api_key: str) -> str:
    """Send one request to Gemini and return its generated text."""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


def _get_ollama_response(prompt: str) -> str:
    """Send a prompt to the local Ollama server and return its generated text."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
               "temperature": 0.2
            },
        },
        timeout=OLLAMA_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    ollama_response = response.json().get("response")
    if not isinstance(ollama_response, str) or not ollama_response.strip():
        raise RuntimeError("Ollama returned an empty response.")

    return ollama_response


def get_ai_response(prompt: str, fallback_prompt: str | None = None) -> str:
    """Return an AI response using Gemini first, then local Ollama if needed."""
    if not isinstance(prompt, str) or not prompt.strip():
        return "Error: Please provide a non-empty prompt."

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY is not set."

    # Gemini is the primary provider. Retry once because temporary 503 and
    # network errors can often recover after a short pause.
    try:
        return _get_gemini_response(prompt, api_key)
    except Exception:
        time.sleep(RETRY_DELAY_SECONDS)

    try:
        return _get_gemini_response(prompt, api_key)
    except Exception:
        pass

    # Gemini did not respond after the retry, so use the local Ollama model.
    try:
        ollama_prompt = fallback_prompt if fallback_prompt is not None else prompt
        ollama_response = _get_ollama_response(ollama_prompt)
        return (
            "\u26a0\ufe0f Gemini is temporarily unavailable. "
            "Using local AI fallback (Ollama).\n\n"
            f"{ollama_response}"
        )
    except Exception:
        return "AI services are temporarily unavailable. Please try again in a moment."
