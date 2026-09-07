"""FastAPI entry point for the JalNetra prototype API."""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent_orchestrator import demo_query, graph
from app.language import normalize_language, translate_answer, translate_to_english
from pfz_heuristics import generate_mock_pfz
from services.sarvam_service import SarvamServiceError, speech_to_text, text_to_speech


app = FastAPI(title="JalNetra API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """Natural-language query submitted to the prototype assistant."""

    query: str
    language: str = "en-IN"
    user_id: str | None = None


class SmsRequest(BaseModel):
    phone: str | None = None
    message: str | None = None


MOCK_ALERTS = [
    {
        "id": "alert-cyclone-01",
        "type": "cyclone",
        "severity": "high",
        "message": "Mock cyclone advisory near the Odisha coast.",
        "source": "mock_weather_service",
    },
    {
        "id": "alert-geofence-01",
        "type": "geofence",
        "severity": "medium",
        "message": "Seasonal protected-area restriction is active.",
        "source": "mock_regulatory_graph",
    },
]


@app.get("/api/v1/pfz")
def get_pfz() -> dict:
    """Return deterministic Potential Fishing Zone GeoJSON."""
    return generate_mock_pfz()


@app.get("/api/v1/alerts")
def get_alerts() -> list[dict]:
    """Return active mock weather and geofence alerts."""
    return MOCK_ALERTS


def run_query(query: str, language: str = "en-IN") -> dict:
    """Run the LangGraph workflow and return its structured response."""
    requested_language = normalize_language(language)
    translated_query = translate_to_english(query, requested_language)
    if demo := demo_query(translated_query):
        demo_payload = dict(demo)
        demo_payload["answer"] = translate_answer(demo["intent"], requested_language, {
            "english": demo["answer"],
            "location": "Odisha coast",
            "confidence": "91%",
            "wave": "3.2",
            "threshold": "2.5",
            "zone": "Indian EEZ",
            "restriction": "Seasonal_Ban",
            "hazards": "active hazards",
        })
        return {
            "query": query,
            "original_query": query,
            "translated_query": translated_query,
            "language": requested_language,
            **demo_payload,
            "execution_log": [
                {"level": "info", "stage": "translation", "message": f"English context: {translated_query}"},
                {"level": "success", "stage": "demo", "message": "Returned cached pitch response."},
            ],
        }
    result = graph.invoke({"query": query, "original_query": query, "requested_language": requested_language})
    return {
        "query": query,
        "original_query": result.get("original_query", query),
        "translated_query": result.get("translated_query", query),
        "language": result.get("requested_language", requested_language),
        "intent": result["intent"],
        "answer": result["response"],
        "visual_trace": result["visual_trace"],
        "geojson": result.get("geojson"),
        "execution_log": result.get("execution_log", []),
    }


@app.post("/api/v1/query")
def submit_query(request: QueryRequest) -> dict:
    return run_query(request.query, request.language)


@app.post("/api/v1/sms")
def send_mock_sms(request: SmsRequest) -> dict:
    """Return the alert text that the prototype would send by SMS."""
    return {"status": "sent", "alert": "JalNetra: protected boundary nearby. Check route before sailing."}


@app.post("/api/v1/voice-query")
def submit_voice_query(
    audio: UploadFile = File(...),
    language: str = Form("hi-IN"),
) -> dict:
    """Transcribe audio, run ORCA, then return a spoken answer when available."""
    if not audio.content_type or not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=415, detail="Upload an audio file (WebM, WAV, or MP3).")

    try:
        transcribed_text = speech_to_text(
            audio.file.read(),
            language,
            filename=audio.filename or "recording.webm",
            content_type=audio.content_type,
        )
    except SarvamServiceError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error

    query_result = run_query(transcribed_text, language)
    audio_base64 = None
    voice_error = None
    try:
        audio_base64 = text_to_speech(query_result["answer"], language)
    except SarvamServiceError as error:
        # The text response remains useful if a quota/service error affects TTS.
        voice_error = str(error)
        query_result.setdefault("execution_log", []).append({
            "level": "error",
            "stage": "voice",
            "message": voice_error,
        })

    return {
        "transcribed_text": transcribed_text,
        "answer": query_result["answer"],
        "audio_base64": audio_base64,
        "audio_mime_type": "audio/wav" if audio_base64 else None,
        "visual_trace": query_result["visual_trace"],
        "execution_log": query_result.get("execution_log", []),
        "original_query": query_result.get("original_query", transcribed_text),
        "translated_query": query_result.get("translated_query", transcribed_text),
        "language": language,
        "voice_error": voice_error,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
