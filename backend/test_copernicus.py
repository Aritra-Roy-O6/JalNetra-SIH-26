import math
import os
import time
from datetime import datetime, timedelta, UTC
from pathlib import Path
from dotenv import load_dotenv
import copernicusmarine

load_dotenv(Path(__file__).resolve().parents[0] / ".env")

username = os.getenv("COPERNICUS_MARINE_USERNAME")
password = os.getenv("COPERNICUS_MARINE_PASSWORD")

def score_pfz_grid(sst_grid, chlorophyll_grid):
    chlorophyll_by_cell = {(round(item["lat"], 6), round(item["lon"], 6)): item["value"] for item in chlorophyll_grid}
    cells = []
    for index, sst in enumerate(sst_grid):
        key = (round(sst["lat"], 6), round(sst["lon"], 6))
        if key not in chlorophyll_by_cell:
            continue
        neighbors = [other["value"] for other in sst_grid if abs(other["lat"] - sst["lat"]) < 0.1 and abs(other["lon"] - sst["lon"]) > 0]
        gradient = max((abs(sst["value"] - value) for value in neighbors), default=0.0)
        cells.append({"lat": sst["lat"], "lon": sst["lon"], "sst_value": sst["value"], "chlorophyll_value": chlorophyll_by_cell[key], "gradient": gradient})
    if not cells:
        return []
    gradients = [cell["gradient"] for cell in cells]
    chlorophyll = [cell["chlorophyll_value"] for cell in cells]
    gradient_min, gradient_max = min(gradients), max(gradients)
    chl_min, chl_max = min(chlorophyll), max(chlorophyll)
    for cell in cells:
        gradient_norm = (cell["gradient"] - gradient_min) / (gradient_max - gradient_min) if gradient_max > gradient_min else 0.0
        chl_norm = (cell["chlorophyll_value"] - chl_min) / (chl_max - chl_min) if chl_max > chl_min else 0.0
        cell["confidence_score"] = round(0.5 * gradient_norm + 0.5 * chl_norm, 4)
    return [cell for cell in cells if cell["confidence_score"] >= 0.6]

def fetch_copernicus_grid(lat: float, lon: float, radius: float = 0.5):
    t0 = time.time()
    min_lon, min_lat = lon - radius, lat - radius
    max_lon, max_lat = lon + radius, lat + radius
    now = datetime.now(UTC)
    start_str = (now - timedelta(days=5)).isoformat()
    end_str = now.isoformat()
    
    ds_chl = copernicusmarine.open_dataset(
        dataset_id="cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m",
        username=username,
        password=password,
        variables=["chl"],
        minimum_longitude=min_lon,
        maximum_longitude=max_lon,
        minimum_latitude=min_lat,
        maximum_latitude=max_lat,
        start_datetime=start_str,
        end_datetime=end_str,
    )
    chl_sub = ds_chl.isel(depth=0, time=-1)["chl"]
    
    ds_sst = copernicusmarine.open_dataset(
        dataset_id="cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m",
        username=username,
        password=password,
        variables=["thetao"],
        minimum_longitude=min_lon,
        maximum_longitude=max_lon,
        minimum_latitude=min_lat,
        maximum_latitude=max_lat,
        start_datetime=start_str,
        end_datetime=end_str,
    )
    sst_sub = ds_sst.isel(depth=0, time=-1)["thetao"]

    chl_arr = chl_sub.values
    chl_lats = chl_sub.latitude.values
    chl_lons = chl_sub.longitude.values

    chl_points = []
    for i, clat in enumerate(chl_lats):
        for j, clon in enumerate(chl_lons):
            val = float(chl_arr[i, j])
            if math.isfinite(val) and val > -1e20 and not math.isnan(val):
                chl_points.append((float(clat), float(clon), val))

    print(f"Extracted {len(chl_points)} valid Chlorophyll grid points in {time.time() - t0:.2f}s")
    if not chl_points:
        return []

    sst_arr = sst_sub.values
    sst_lats = sst_sub.latitude.values
    sst_lons = sst_sub.longitude.values

    sst_grid = []
    chl_grid = []
    for i, slat in enumerate(sst_lats):
        for j, slon in enumerate(sst_lons):
            sst_val = float(sst_arr[i, j])
            if not math.isfinite(sst_val) or sst_val <= -1e20 or math.isnan(sst_val):
                continue
            if sst_val > 200:
                sst_val -= 273.15
            nearest_chl = min(chl_points, key=lambda p: abs(p[0] - slat) + abs(p[1] - slon))
            if abs(nearest_chl[0] - slat) + abs(nearest_chl[1] - slon) <= 0.4:
                sst_grid.append({"lat": float(slat), "lon": float(slon), "value": sst_val})
                chl_grid.append({"lat": float(slat), "lon": float(slon), "value": nearest_chl[2]})

    scored_cells = score_pfz_grid(sst_grid, chl_grid)
    print(f"Radius {radius}: Found {len(scored_cells)} scored PFZ cells in {time.time() - t0:.2f}s!")
    return scored_cells

if __name__ == "__main__":
    cells = fetch_copernicus_grid(13.0827, 80.2707, 0.5) # Chennai
    for c in cells[:5]:
        print(c)
