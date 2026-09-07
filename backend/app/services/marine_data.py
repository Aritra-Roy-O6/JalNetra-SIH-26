"""Small live-data adapters for Copernicus Marine and INCOIS ERDDAP."""

from __future__ import annotations

import csv
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import math
import os
from threading import Lock
import time
from datetime import UTC, datetime, timedelta
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv

try:
    import truststore
except ModuleNotFoundError:  # deployment still reports a clear provider error
    truststore = None
else:
    truststore.inject_into_ssl()

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SEA_LEVEL_DATASET = "cmems_mod_glo_phy_anfc_0.083deg_P1D-m"
TEMPERATURE_DATASET = "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m"
CURRENT_DATASET = "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m"
BGC_DATASET = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
WIND_DATASET = "cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H"
INCOIS_DATASET = "ascat_daily_datasets"
MAX_INCOIS_AGE_DAYS = 7
LIVE_SNAPSHOT_TTL_SECONDS = 300
LIVE_PROVIDER_TIMEOUT_SECONDS = 20
_live_snapshot_cache: dict[tuple[float, float, float | None], tuple[float, dict[str, Any]]] = {}
_live_snapshot_lock = Lock()
_live_provider_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="marine-provider")


class MarineDataError(RuntimeError):
    """An upstream marine provider could not supply a trustworthy value."""


def _coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise MarineDataError("Latitude must be between -90 and 90 and longitude between -180 and 180.")
    return float(latitude), float(longitude)


def _scalar(value: Any) -> float:
    return float(value.squeeze().values.item())


def _point_dataset(
    toolbox: Any,
    dataset_id: str,
    variables: list[str],
    latitude: float,
    longitude: float,
    start: datetime | None = None,
) -> Any:
    now = datetime.now(UTC)
    return toolbox.open_dataset(
        dataset_id=dataset_id,
        username=os.environ["COPERNICUS_MARINE_USERNAME"],
        password=os.environ["COPERNICUS_MARINE_PASSWORD"],
        variables=variables,
        minimum_longitude=longitude,
        maximum_longitude=longitude,
        minimum_latitude=latitude,
        maximum_latitude=latitude,
        start_datetime=(start or now - timedelta(days=2)).isoformat(),
        end_datetime=now.isoformat(),
    ).sel(latitude=latitude, longitude=longitude, method="nearest")


def fetch_copernicus_wind(latitude: float, longitude: float) -> dict[str, Any]:
    """Return current CMEMS L4 10 m wind components as RF-ready features."""
    latitude, longitude = _coordinates(latitude, longitude)
    if not os.getenv("COPERNICUS_MARINE_USERNAME") or not os.getenv("COPERNICUS_MARINE_PASSWORD"):
        raise MarineDataError("Copernicus Marine credentials are not configured.")
    try:
        toolbox = import_module("copernicusmarine")
        wind = _point_dataset(toolbox, WIND_DATASET, ["eastward_wind", "northward_wind"], latitude, longitude).isel(time=-1)
        eastward = _scalar(wind["eastward_wind"])
        northward = _scalar(wind["northward_wind"])
    except Exception as error:
        raise MarineDataError(f"Copernicus Marine wind request failed: {error}") from error
    return {
        "wind_speed": math.hypot(eastward, northward),
        "wind_direction_deg": (math.degrees(math.atan2(eastward, northward)) + 360) % 360,
        "observed_at": str(wind["time"].values),
        "source": "Copernicus Marine WIND_GLO_PHY_L4_NRT_012_004",
    }


def _copernicus_point(latitude: float, longitude: float) -> dict[str, Any]:
    username = os.getenv("COPERNICUS_MARINE_USERNAME")
    password = os.getenv("COPERNICUS_MARINE_PASSWORD")
    if not username or not password:
        raise MarineDataError("Copernicus Marine credentials are not configured.")
    try:
        toolbox = import_module("copernicusmarine")
    except ModuleNotFoundError as error:
        raise MarineDataError("Copernicus Marine Toolbox is not installed. Install backend requirements.") from error

    try:
        baseline_start = datetime.now(UTC) - timedelta(days=35)
        temperature = _point_dataset(toolbox, TEMPERATURE_DATASET, ["thetao"], latitude, longitude, baseline_start).isel(depth=0)
        current = _point_dataset(toolbox, CURRENT_DATASET, ["uo", "vo"], latitude, longitude, baseline_start).isel(depth=0)
        sea_level = _point_dataset(toolbox, SEA_LEVEL_DATASET, ["zos"], latitude, longitude, baseline_start)
        surface_level = sea_level["zos"]
        latest_level = _scalar(surface_level.isel(time=-1))
        baseline = _scalar(surface_level.isel(time=slice(-31, -1)).mean())
        latest_temperature = temperature.isel(time=-1)
        latest_current = current.isel(time=-1)
        biogeochemistry = _point_dataset(toolbox, BGC_DATASET, ["chl"], latitude, longitude, baseline_start).isel(depth=0, time=-1)
        chlorophyll = _scalar(biogeochemistry["chl"])
        wind = fetch_copernicus_wind(latitude, longitude)
    except Exception as error:  # provider exceptions differ between toolbox releases
        raise MarineDataError(f"Copernicus Marine request failed: {error}") from error

    return {
        "sst": _scalar(latest_temperature["thetao"]),
        "chlorophyll": chlorophyll,
        "chlorophyll_log": math.log1p(chlorophyll),
        "ssh": latest_level,
        "ssh_anomaly": latest_level - baseline,
        "current_u": _scalar(latest_current["uo"]),
        "current_v": _scalar(latest_current["vo"]),
        "wind_speed": wind["wind_speed"],
        "wind_direction_deg": wind["wind_direction_deg"],
        "depth": _scalar(temperature["depth"]),
        "observed_at": str(latest_temperature["time"].values),
        "wind_observed_at": wind["observed_at"],
        "source": "Copernicus Marine global analysis and forecast datasets",
        "wind_source": wind["source"],
    }


def fetch_incois_wind(latitude: float, longitude: float) -> dict[str, Any]:
    """Read the latest official INCOIS ASCAT wind observation at a map point."""
    latitude, longitude = _coordinates(latitude, longitude)
    base_url = os.getenv("INCOIS_ERDDAP_BASE_URL", "").rstrip("/")
    if not base_url:
        raise MarineDataError("INCOIS_ERDDAP_BASE_URL is not configured.")

    dimensions = f"[(last)][(10.0)][({latitude})][({longitude})]"
    constraint = ",".join(f"{name}{dimensions}" for name in ("wind_speed", "eastward_wind", "northward_wind"))
    url = f"{base_url}/griddap/{INCOIS_DATASET}.csv?{quote(constraint, safe='[](),')}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        rows = list(csv.DictReader(StringIO(response.text)))
        row = rows[-1]
        observed_at = datetime.fromisoformat(row["time"].replace("Z", "+00:00"))
        speed = float(row["wind_speed"])
        eastward = float(row["eastward_wind"])
        northward = float(row["northward_wind"])
    except (IndexError, KeyError, TypeError, ValueError, requests.RequestException) as error:
        raise MarineDataError(f"INCOIS ERDDAP request failed: {error}") from error

    age_days = (datetime.now(UTC) - observed_at).total_seconds() / 86400
    return {
        "wind_speed": speed,
        "wind_direction_deg": (math.degrees(math.atan2(eastward, northward)) + 360) % 360,
        "observed_at": observed_at.isoformat(),
        "age_days": round(age_days, 1),
        "fresh": 0 <= age_days <= MAX_INCOIS_AGE_DAYS,
        "source": "INCOIS ERDDAP ASCAT daily wind field",
    }


def _load_live_pfz_features(latitude: float, longitude: float, distance_to_coast_km: float | None) -> dict[str, Any]:
    """Collect only observed/modelled values; never substitute a demo snapshot."""
    latitude, longitude = _coordinates(latitude, longitude)
    providers: dict[str, Any] = {}
    features: dict[str, float] = {}
    errors: list[str] = []
    warnings: list[str] = []

    try:
        copernicus = _copernicus_point(latitude, longitude)
        providers["copernicus"] = {"available": True, "observed_at": copernicus.pop("observed_at"), "source": copernicus.pop("source")}
        providers["copernicus_wind"] = {"available": True, "observed_at": copernicus.pop("wind_observed_at"), "source": copernicus.pop("wind_source")}
        features.update(copernicus)
    except MarineDataError as error:
        providers["copernicus"] = {"available": False, "error": str(error)}
        errors.append(str(error))

    # BYPASS: INCOIS ASCAT ends in 2023, so it must never supply live RF features.
    providers["incois"] = {"available": False, "used_for_prediction": False, "reason": "Bypassed stale INCOIS ASCAT; CMEMS L4 NRT wind is used instead."}
    warnings.append("INCOIS ASCAT is bypassed for live predictions because its configured dataset is stale.")

    if distance_to_coast_km is not None:
        if distance_to_coast_km < 0:
            errors.append("distance_to_coast_km cannot be negative.")
        else:
            features["distance_to_coast_km"] = float(distance_to_coast_km)

    return {"features": features, "providers": providers, "errors": errors, "warnings": warnings, "location": {"latitude": latitude, "longitude": longitude}}


def live_pfz_features(latitude: float, longitude: float, distance_to_coast_km: float | None = None) -> dict[str, Any]:
    """Return a short-lived shared snapshot so concurrent UI requests reuse providers."""
    latitude, longitude = _coordinates(latitude, longitude)
    key = (latitude, longitude, distance_to_coast_km)
    now = time.monotonic()
    with _live_snapshot_lock:
        cached = _live_snapshot_cache.get(key)
        if cached and now - cached[0] < LIVE_SNAPSHOT_TTL_SECONDS:
            return cached[1]
        future = _live_provider_executor.submit(_load_live_pfz_features, latitude, longitude, distance_to_coast_km)
        try:
            snapshot = future.result(timeout=LIVE_PROVIDER_TIMEOUT_SECONDS)
        except FutureTimeoutError:
            snapshot = {
                "features": {},
                "providers": {},
                "errors": [f"Live marine providers did not respond within {LIVE_PROVIDER_TIMEOUT_SECONDS} seconds."],
                "warnings": [],
                "location": {"latitude": latitude, "longitude": longitude},
            }
        _live_snapshot_cache[key] = (time.monotonic(), snapshot)
    return snapshot
