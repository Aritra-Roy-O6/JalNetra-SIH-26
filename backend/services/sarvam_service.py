"""Small, dependency-light client for Sarvam's synchronous voice APIs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import requests
from dotenv import load_dotenv

SARVAM_BASE_URL: Final = "https://api.sarvam.ai"
SUPPORTED_AUDIO_TYPES: Final = {"audio/webm", "audio/wav", "audio/mpeg"}

# Load the backend-local file regardless of whether Uvicorn starts from the
# repository root or the backend directory. Existing deployment variables win.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class SarvamServiceError(RuntimeError):
    """Raised when Sarvam cannot complete a voice request."""

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code


def _headers() -> dict[str, str]:
    api_key = os.getenv("SARVAM_API_KEY", "").strip()
    if not api_key:
        raise SarvamServiceError("Voice service is not configured. Set SARVAM_API_KEY.")
    return {"api-subscription-key": api_key}


def _normalized_audio_type(content_type: str) -> str:
    """Strip browser codec parameters and accept Sarvam's supported MIME types."""
    normalized = content_type.split(";", maxsplit=1)[0].strip().lower()
    normalized = {"audio/x-wav": "audio/wav", "audio/mp3": "audio/mpeg"}.get(normalized, normalized)
    if normalized not in SUPPORTED_AUDIO_TYPES:
        raise SarvamServiceError("Upload a short WebM, WAV, or MP3 recording.", 415)
    return normalized


def _request_error(error: requests.RequestException, operation: str) -> SarvamServiceError:
    """Turn an upstream failure into a safe, actionable API response."""
    response = getattr(error, "response", None)
    status_code = response.status_code if response is not None else 503
    provider_message = ""
    if response is not None:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                error_detail = payload.get("error", {})
                provider_message = (
                    error_detail.get("message", "") if isinstance(error_detail, dict) else ""
                ) or str(payload.get("message", ""))
        except ValueError:
            pass
    if status_code in (401, 403):
        return SarvamServiceError("Sarvam rejected the API key. Check SARVAM_API_KEY.", status_code)
    if status_code == 429:
        return SarvamServiceError("Sarvam voice quota is currently exhausted. Please type your question.", status_code)
    if status_code in (400, 413, 415, 422):
        detail = f" Provider detail: {provider_message}" if provider_message else ""
        return SarvamServiceError(
            f"Sarvam could not {operation} this audio. Use a short WebM, WAV, or MP3 recording.{detail}",
            status_code,
        )
    return SarvamServiceError(f"Sarvam {operation} is temporarily unavailable.", status_code)


def speech_to_text(
    audio_bytes: bytes,
    language_code: str = "hi-IN",
    *,
    filename: str = "recording.webm",
    content_type: str = "audio/webm",
) -> str:
    """Transcribe a short browser audio recording with Saaras v3.

    Sarvam's synchronous STT endpoint accepts WebM along with WAV and MP3. It
    is intended for short (up to 30-second) recordings, which the UI enforces.
    """
    if not audio_bytes:
        raise SarvamServiceError("The uploaded recording is empty.")

    try:
        normalized_content_type = _normalized_audio_type(content_type)
        response = requests.post(
            f"{SARVAM_BASE_URL}/speech-to-text",
            headers=_headers(),
            files={"file": (filename, audio_bytes, normalized_content_type)},
            data={
                "model": "saaras:v3",
                "mode": "transcribe",
                "language_code": language_code,
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        transcript = payload.get("transcript", "").strip() if isinstance(payload, dict) else ""
    except requests.RequestException as error:
        raise _request_error(error, "speech transcription") from error
    except (TypeError, ValueError) as error:
        raise SarvamServiceError("Speech transcription returned an invalid response.") from error

    if not transcript:
        raise SarvamServiceError("No speech was detected in the recording.")
    return transcript


def text_to_speech(text: str, language_code: str = "hi-IN") -> str:
    """Return Sarvam's base64-encoded WAV audio for a natural-language reply."""
    if not text.strip():
        raise SarvamServiceError("Cannot generate speech from an empty answer.")

    try:
        response = requests.post(
            f"{SARVAM_BASE_URL}/text-to-speech",
            headers={**_headers(), "Content-Type": "application/json"},
            json={
                "text": text[:2500],
                "language_code": language_code,
                "model": "bulbul:v3",
                "speaker": "shubh",
                "output_audio_codec": "wav",
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        audios = payload.get("audios", []) if isinstance(payload, dict) else []
    except requests.RequestException as error:
        raise _request_error(error, "speech playback") from error
    except (TypeError, ValueError) as error:
        raise SarvamServiceError("Speech playback returned an invalid response.") from error

    if not audios or not isinstance(audios[0], str):
        raise SarvamServiceError("Speech playback returned no audio.")
    return audios[0]
