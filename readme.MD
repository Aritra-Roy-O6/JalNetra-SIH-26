
# JalNetra (ORCA)

A multilingual, agentic AI conversational platform providing Indian fishermen, coastal authorities, and disaster-management agencies with explainable, evidence-based marine decision support.

## Overview

Built for the Smart India Hackathon (SIH) 2026 (Problem Statement 26176), JalNetra answers complex marine queries by reasoning over satellite, oceanographic, and regulatory data through a collaborating swarm of specialized AI agents. It prioritizes maritime safety, optimized navigation, and accessible intelligence for coastal communities.

## Core Capabilities

* **Visual Reasoning Trace:** A transparent, clickable node-edge graph demonstrating exactly how the AI arrived at its recommendation.
* **Hybrid GraphRAG Memory:** Combines `pgvector` for semantic search over unstructured marine advisories with an in-memory Knowledge Graph for deterministic regulatory boundaries and hazard geofencing.
* **Autonomous PFZ Prediction:** Predicts Potential Fishing Zones dynamically by analyzing raw SST and chlorophyll satellite rasters rather than relying solely on static advisories.
* **Coastal-First Delivery:** Features seamless multilingual support via Bhashini, an offline-capable PWA, and SMS/USSD fallbacks for low-connectivity environments.

## Technical Architecture

| Layer | Primary Technologies |
| --- | --- |
| **Frontend UI** | Next.js 16, React, Tailwind CSS, Leaflet/Mapbox |
| **Backend & Orchestration** | FastAPI, LangGraph, Celery |
| **Database & Memory** | PostgreSQL, pgvector, NetworkX, Redis |
| **Integrations** | MOSDAC, INCOIS, Open-Meteo, Bhashini SDK |

## Getting Started

### Prerequisites

* Node.js v20+
* Python 3.10+
* Docker & Docker Compose

### Local Setup

1. Clone the repository and navigate to the project root.
2. Spin up the Postgres and Redis infrastructure using `docker-compose up -d`.
3. Navigate to the `frontend` directory, run `npm install`, and start the development server using `npm run dev`.
4. Navigate to the `backend` directory, activate your Python virtual environment, and run `pip install -r requirements.txt`.
5. Populate your `.env` files in both the frontend and backend directories with the required API keys and database credentials.
6. Launch the FastAPI server using `uvicorn main:app --reload`.

---

By- Team Sixth Order