"""Strict Gemini client seam for model-assisted agent stages."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def build_llm():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required for model-assisted mode.")
    from langchain.chat_models import init_chat_model

    return init_chat_model(
        "gemini-2.0-flash",
        model_provider="google_genai",
        api_key=api_key,
        temperature=0,
        timeout=10,
        max_retries=0,
    )


def invoke_text(prompt: str) -> str:
    result = build_llm().invoke(prompt)
    content = getattr(result, "content", str(result))
    if not content:
        raise RuntimeError("Gemini returned an empty response.")
    return content.strip()
