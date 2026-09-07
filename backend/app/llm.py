"""Model integration seam, intentionally disabled for the deterministic demo."""


def build_llm():
    """Reserve this seam for the reviewed provider integration phase."""
    return None


def invoke_text(prompt: str) -> str | None:
    """Keep all pre-integration answers deterministic and offline-safe."""
    return None
