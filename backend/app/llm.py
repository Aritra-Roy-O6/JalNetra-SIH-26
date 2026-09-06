"""Shared optional LLM helpers for JalNetra agents."""

import os

from dotenv import load_dotenv

load_dotenv()


def build_llm():
    """Create the configured Gemini model, or return None for offline mode."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from langchain.chat_models import init_chat_model

        return init_chat_model(
            "gemini-2.0-flash",
            model_provider="google_genai",
            api_key=api_key,
            temperature=0,
            timeout=10,
            max_retries=0,
        )
    except (ImportError, TypeError, ValueError):
        return None


def invoke_text(prompt: str) -> str | None:
    """Invoke Gemini and return None on timeout, provider, or configuration errors."""
    llm = build_llm()
    if llm is None:
        return None
    try:
        result = llm.invoke(prompt)
        content = getattr(result, "content", str(result))
        return content.strip() if content else None
    except (TimeoutError, ConnectionError, OSError):
        return None
    except Exception:
        return None
