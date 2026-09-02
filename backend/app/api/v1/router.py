from fastapi import APIRouter
from app.api.v1.endpoints import query, pfz, routes, alerts, trace

api_router = APIRouter()

api_router.include_router(query.router, tags=["Reasoning Engine"])
api_router.include_router(pfz.router, tags=["Ocean Analytics"])
api_router.include_router(routes.router, tags=["Route Optimization"])
api_router.include_router(alerts.router, tags=["Weather & Safety"])
api_router.include_router(trace.router, tags=["Visual Trace UI"])