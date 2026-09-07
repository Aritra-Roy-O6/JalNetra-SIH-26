"""FastAPI entry point for the JalNetra prototype API."""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.orchestrator import graph
from app.language import normalize_language
from app.pfz_model import MODEL_FEATURES, current_pfz_prediction, load_pfz_model
from services.sarvam_service import SarvamServiceError, speech_to_text, text_to_speech


app = FastAPI(title="JalNetra API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
PFZ_MODEL = load_pfz_model()


class QueryRequest(BaseModel):
    """Natural-language query submitted to the prototype assistant."""

    query: str
    language: str = "en-IN"
    user_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_to_coast_km: float | None = None


@app.get("/api/v1/pfz")
def get_pfz(latitude: float | None = None, longitude: float | None = None, distance_to_coast_km: float | None = None) -> dict:
    """Return a model-backed PFZ prediction and feature provenance."""
    prediction = current_pfz_prediction(latitude, longitude, distance_to_coast_km, PFZ_MODEL)
    return {"model_features": MODEL_FEATURES, "prediction": prediction}


@app.get("/api/v1/alerts")
def get_alerts() -> list[dict]:
    """Return live alerts when an ingestion service is configured."""
    return []


def run_query(query: str, language: str = "en-IN", latitude: float | None = None, longitude: float | None = None, distance_to_coast_km: float | None = None) -> dict:
    """Run the LangGraph workflow and return its structured response."""
    requested_language = normalize_language(language)
    location = None if latitude is None or longitude is None else {"latitude": latitude, "longitude": longitude, "distance_to_coast_km": distance_to_coast_km}
    result = graph.invoke({"query": query, "original_query": query, "requested_language": requested_language, "location": location})
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
    return run_query(request.query, request.language, request.latitude, request.longitude, request.distance_to_coast_km)


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
