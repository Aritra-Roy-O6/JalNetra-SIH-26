"""FastAPI entry point for the JalNetra prototype API."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.agent_orchestrator import graph
from pfz_heuristics import generate_mock_pfz


app = FastAPI(title="JalNetra API", version="0.1.0")


class QueryRequest(BaseModel):
    """Natural-language query submitted to the prototype assistant."""

    query: str


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


@app.post("/api/v1/query")
def submit_query(request: QueryRequest) -> dict:
    """Run the LangGraph workflow and return its structured response."""
    result = graph.invoke({"query": request.query})
    return {
        "query": request.query,
        "intent": result["intent"],
        "answer": result["response"],
        "visual_trace": result["visual_trace"],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)