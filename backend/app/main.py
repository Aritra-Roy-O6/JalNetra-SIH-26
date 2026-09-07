"""Compatibility entry point for ``uvicorn app.main:app``.

The dashboard uses the root FastAPI application; re-export it here so both
common Uvicorn commands serve the same contract.
"""

from main import app
