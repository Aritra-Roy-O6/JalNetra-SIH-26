"""Small async Redis cache and single-flight helper for external data calls."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import date
import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)
_redis: Redis | None = None
_redis_loop: asyncio.AbstractEventLoop | None = None
_locks: dict[str, asyncio.Lock] = {}
_recent_results: dict[str, tuple[float, dict]] = {}
_SINGLE_FLIGHT_WINDOW_SECONDS = 5.0


def cache_key(source: str, variable: str, lat: float, lon: float, day: date | str | None = None) -> str:
    day_value = day.isoformat() if isinstance(day, date) else (day or date.today().isoformat())
    return f"{source}:{variable}:{round(lat, 2)}:{round(lon, 2)}:{day_value}"


def _client() -> Redis:
    global _redis, _redis_loop
    loop = asyncio.get_running_loop()
    if _redis is None or _redis_loop is not loop:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=0.5, socket_timeout=0.5)
        _redis_loop = loop
    return _redis


async def get_cached(key: str) -> dict | None:
    try:
        value = await _client().get(key)
        if value is None:
            logger.info("cache MISS %s", key)
            return None
        logger.info("cache HIT %s", key)
        return json.loads(value)
    except Exception as error:
        logger.warning("Redis read failed for %s: %s", key, error)
        return None


async def set_cached(key: str, value: dict, ttl_seconds: int = 1800) -> None:
    try:
        await _client().setex(key, ttl_seconds, json.dumps(value, default=str))
    except Exception as error:
        logger.warning("Redis write failed for %s: %s", key, error)


async def fetch_with_cache_and_fallback(
    primary_fn: Callable[[], Awaitable[dict]],
    fallback_fn: Callable[[], Awaitable[dict]] | None,
    cache_key_value: str,
    ttl: int = 1800,
) -> dict:
    cached = await get_cached(cache_key_value)
    if cached is not None:
        return {**cached, "stale": False}
    recent = _recent_results.get(cache_key_value)
    if recent is not None and asyncio.get_running_loop().time() - recent[0] < _SINGLE_FLIGHT_WINDOW_SECONDS:
        return recent[1]

    lock = _locks.setdefault(cache_key_value, asyncio.Lock())
    async with lock:
        cached = await get_cached(cache_key_value)
        if cached is not None:
            return {**cached, "stale": False}
        recent = _recent_results.get(cache_key_value)
        if recent is not None and asyncio.get_running_loop().time() - recent[0] < _SINGLE_FLIGHT_WINDOW_SECONDS:
            return recent[1]
        try:
            result = await primary_fn()
            await set_cached(cache_key_value, result, ttl)
            response = {**result, "stale": False}
            _recent_results[cache_key_value] = (asyncio.get_running_loop().time(), response)
            return response
        except Exception as primary_error:
            logger.warning("Primary provider failed for %s: %s", cache_key_value, primary_error)
            if fallback_fn is not None:
                try:
                    result = await fallback_fn()
                    await set_cached(cache_key_value, result, ttl)
                    response = {**result, "stale": False, "fallback": True}
                    _recent_results[cache_key_value] = (asyncio.get_running_loop().time(), response)
                    return response
                except Exception as fallback_error:
                    logger.warning("Fallback provider failed for %s: %s", cache_key_value, fallback_error)
            stale = await get_cached(cache_key_value)
            if stale is not None:
                response = {**stale, "stale": True}
            else:
                response = {"available": False, "stale": True, "error": "External data providers are unavailable."}
            _recent_results[cache_key_value] = (asyncio.get_running_loop().time(), response)
            return response
