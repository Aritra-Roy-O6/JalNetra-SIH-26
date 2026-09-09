import asyncio
import math
import os
import time
from datetime import datetime, timedelta, UTC
from pathlib import Path
from dotenv import load_dotenv
import httpx
import copernicusmarine

load_dotenv(Path(__file__).resolve().parents[0] / ".env")

INCOIS_SST_DATASET = "incois_argo_sst_weekly"
INCOIS_CHL_DATASET = "IRS_chlorophyll_datasets"
BASE_URL = os.getenv("INCOIS_ERDDAP_BASE_URL", "https://erddap.incois.gov.in/erddap").rstrip("/")
username = os.getenv("COPERNICUS_MARINE_USERNAME")
password = os.getenv("COPERNICUS_MARINE_PASSWORD")

def get_bbox(lat: float, lon: float, radius: float = 0.5):
    return lon - radius, lat - radius, lon + radius, lat + radius

def score_pfz_grid(sst_grid, chlorophyll_grid):
    chlorophyll_by_cell = {(round(item["lat"], 6), round(item["lon"], 6)): item["value"] for item in chlorophyll_grid}
    cells = []
    for sst in sst_grid:
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

async def check_incois_grid(lat: float, lon: float, radius: float = 0.5):
    min_lon, min_lat, max_lon, max_lat = get_bbox(lat, lon, radius)
    def expression(variable: str) -> str:
        return f"{variable}[(last)][({min_lat}):({max_lat})][({min_lon}):({max_lon})]"

    sst_url = f"{BASE_URL}/griddap/{INCOIS_SST_DATASET}.json?{expression('ASST')}"
    chl_url = f"{BASE_URL}/griddap/{INCOIS_CHL_DATASET}.json?{expression('CHLOROPHYLL')}"
    
    async with httpx.AsyncClient(verify=False, timeout=15) as client:
        try:
            sst_res, chl_res = await asyncio.gather(client.get(sst_url), client.get(chl_url))
            sst_rows = sst_res.json().get("table", {}).get("rows", []) if sst_res.status_code == 200 else []
            chl_rows = chl_res.json().get("table", {}).get("rows", []) if chl_res.status_code == 200 else []
        except Exception:
            return {"valid_chl": 0, "null_ratio": 1.0, "sst_grid": [], "chl_grid": []}

    valid_chl_rows = []
    for r in chl_rows:
        try:
            val = float(r[3])
            if math.isfinite(val) and val > -1e20:
                valid_chl_rows.append(r)
        except Exception:
            pass

    total_chl = len(chl_rows)
    valid_count = len(valid_chl_rows)
    null_ratio = 1.0 - (valid_count / total_chl) if total_chl > 0 else 1.0

    sst_grid = []
    chl_grid = []
    if null_ratio <= 0.70 and valid_chl_rows:
        for sst_row in sst_rows:
            try:
                sst_lat, sst_lon, sst_value = float(sst_row[1]), float(sst_row[2]), float(sst_row[3])
                if sst_value <= -1e20:
                    continue
                nearest = min(valid_chl_rows, key=lambda row: abs(float(row[1]) - sst_lat) + abs(float(row[2]) - sst_lon))
                chl_val = float(nearest[3])
                if chl_val <= -1e20:
                    continue
                sst_grid.append({"lat": sst_lat, "lon": sst_lon, "value": sst_value})
                chl_grid.append({"lat": sst_lat, "lon": sst_lon, "value": chl_val})
            except Exception:
                continue

    return {
        "valid_chl": valid_count,
        "total_chl": total_chl,
        "null_ratio": null_ratio,
        "sst_grid": sst_grid,
        "chl_grid": chl_grid,
    }

def check_copernicus_grid(lat: float, lon: float, radius: float = 0.5):
    min_lon, min_lat = lon - radius, lat - radius
    max_lon, max_lat = lon + radius, lat + radius
    now = datetime.now(UTC)
    start_str = (now - timedelta(days=5)).isoformat()
    end_str = now.isoformat()
    
    try:
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

        if not chl_points:
            return {"sst_grid": [], "chl_grid": [], "valid_chl": 0}

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

        return {"sst_grid": sst_grid, "chl_grid": chl_grid, "valid_chl": len(chl_points)}
    except Exception as e:
        print(f"Copernicus fetch error: {e}")
        return {"sst_grid": [], "chl_grid": [], "valid_chl": 0}

async def test_full_pipeline(name: str, lat: float, lon: float):
    print(f"\n--- Testing Pipeline for {name} ({lat}, {lon}) ---")
    # Step 1: Check INCOIS at radius 0.5
    inc05 = await check_incois_grid(lat, lon, 0.5)
    print(f"INCOIS radius=0.5: valid chl={inc05['valid_chl']}/{inc05.get('total_chl',0)} (null={inc05['null_ratio']*100:.1f}%)")
    
    source_used = None
    data_availability = "no_data"
    cells = []

    if inc05["null_ratio"] <= 0.70 and inc05["valid_chl"] > 0:
        cells = score_pfz_grid(inc05["sst_grid"], inc05["chl_grid"])
        if cells:
            data_availability = "full"
            source_used = "INCOIS ERDDAP"

    # Fallback to Copernicus at radius 0.5
    if not cells:
        print("Attempting Copernicus radius=0.5...")
        cop05 = check_copernicus_grid(lat, lon, 0.5)
        print(f"Copernicus radius=0.5: valid chl={cop05['valid_chl']}")
        if cop05["valid_chl"] > 0:
            cells = score_pfz_grid(cop05["sst_grid"], cop05["chl_grid"])
            if cells:
                data_availability = "full"
                source_used = "Copernicus Marine"

    # Progressive bbox widening to radius=1.0
    if not cells:
        print("Attempting Progressive Widening (radius=1.0)...")
        inc10 = await check_incois_grid(lat, lon, 1.0)
        print(f"INCOIS radius=1.0: valid chl={inc10['valid_chl']}/{inc10.get('total_chl',0)} (null={inc10['null_ratio']*100:.1f}%)")
        if inc10["null_ratio"] <= 0.70 and inc10["valid_chl"] > 0:
            cells = score_pfz_grid(inc10["sst_grid"], inc10["chl_grid"])
            if cells:
                data_availability = "widened"
                source_used = "INCOIS ERDDAP (+/-1.0° widened)"

        if not cells:
            print("Attempting Copernicus radius=1.0...")
            cop10 = check_copernicus_grid(lat, lon, 1.0)
            print(f"Copernicus radius=1.0: valid chl={cop10['valid_chl']}")
            if cop10["valid_chl"] > 0:
                cells = score_pfz_grid(cop10["sst_grid"], cop10["chl_grid"])
                if cells:
                    data_availability = "widened"
                    source_used = "Copernicus Marine (+/-1.0° widened)"

    print(f"RESULT [{name}]: availability='{data_availability}', source='{source_used}', features={len(cells)}")

async def main():
    locations = [
        ("Kochi", 9.9312, 76.2673),
        ("Vizag", 17.6868, 83.2185),
        ("Chennai", 13.0827, 80.2707),
        ("Digha", 21.6266, 87.5074),
    ]
    for name, lat, lon in locations:
        await test_full_pipeline(name, lat, lon)

if __name__ == "__main__":
    asyncio.run(main())
