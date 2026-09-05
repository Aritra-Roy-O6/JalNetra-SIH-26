"""Synthesizing and Visual Reasoning Agent."""

from app.llm import invoke_text
from app.state import AgentState


def synthesizing_agent(state: AgentState) -> AgentState:
    """Merge agent evidence into the frontend answer and visual trace."""
    intent = state.get("intent", "Weather")
    evidence_id, evidence_label, fallback = {
        "PFZ": (
            "pfz-mock-01",
            "Potential Fishing Zone",
            "A mock potential fishing zone was identified off the Indian coast.",
        ),
        "Weather": (
            "alert-cyclone-01",
            "Cyclone Warning",
            "Active mock marine alerts were found. Review cyclone conditions before sailing.",
        ),
        "Regulation": (
            "Seasonal_Ban",
            "Seasonal Fishing Regulation",
            "The maritime knowledge graph found applicable boundary and regulation relationships.",
        ),
        "Route": (
            "route-mock-01",
            "Safe Route",
            "A mock risk-aware route was calculated around active hazards.",
        ),
    }.get(intent, ("evidence-mock-01", "Marine Evidence", "Marine evidence was collected for this query."))
    answer = invoke_text(f"Answer briefly using this marine evidence. Query: {state['query']}") or fallback
    return {
        "response": answer,
        "visual_trace": {
            "nodes": [
                {"id": "user_query", "label": "Query", "type": "input"},
                {"id": "intent_agent", "label": f"Intent: {intent}", "type": "agent"},
                {"id": evidence_id, "label": evidence_label, "type": "database_record"},
                {"id": "synthesis_agent", "label": "Final Response", "type": "agent"},
            ],
            "edges": [
                {"source": "user_query", "target": "intent_agent", "label": "classified"},
                {"source": "intent_agent", "target": evidence_id, "label": "queried"},
                {"source": evidence_id, "target": "synthesis_agent", "label": "synthesized"},
            ],
        },
    }
