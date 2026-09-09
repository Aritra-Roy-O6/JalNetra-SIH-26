import asyncio
import math
import os
from pathlib import Path
from urllib.parse import quote
import httpx
import certifi
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[0] / ".env")

INCOIS_SST_DATASET = "incois_argo_sst_weekly"
INCOIS_CHL_DATASET = "IRS_chlorophyll_datasets"
BASE_URL = os.getenv("INCOIS_ERDDAP_BASE_URL", "https://erddap.incois.gov.in/erddap").rstrip("/")

def get_bbox(lat: float, lon: float, radius: float = 0.5):
    return lon - radius, lat - radius, lon + radius, lat + radius

async def test_incois_location(name: str, lat: float, lon: float, radius: float = 0.5):
    min_lon, min_lat, max_lon, max_lat = get_bbox(lat, lon, radius)
    def expression(variable: str) -> str:
        return quote(f"{variable}[(last)][({min_lat}):({max_lat})][({min_lon}):({max_lon})]", safe="(),:")

    sst_url = f"{BASE_URL}/griddap/{INCOIS_SST_DATASET}.json?{expression('ASST')}"
    chl_url = f"{BASE_URL}/griddap/{INCOIS_CHL_DATASET}.json?{expression('CHLOROPHYLL')}"
    
    async with httpx.AsyncClient(verify=False, timeout=20) as client:
        try:
            sst_res = await client.get(sst_url)
            chl_res = await client.get(chl_url)
            sst_rows = sst_res.json().get("table", {}).get("rows", []) if sst_res.status_code == 200 else []
            chl_rows = chl_res.json().get("table", {}).get("rows", []) if chl_res.status_code == 200 else []
        except Exception as e:
            print(f"[{name}] Exception fetching INCOIS: {e}")
            return

    valid_chl = []
    for r in chl_rows:
        try:
            val = float(r[3])
            if math.isfinite(val) and val > -1e20:
                valid_chl.append(val)
        except Exception:
            pass

    total_chl = len(chl_rows)
    valid_count = len(valid_chl)
    null_ratio = 1.0 - (valid_count / total_chl) if total_chl > 0 else 1.0
    print(f"[{name}] radius={radius}: SST rows={len(sst_rows)}, Chl rows={total_chl}, Valid Chl={valid_count}, Null %={null_ratio*100:.1f}%")

async def main():
    locations = [
        ("Kochi", 9.9312, 76.2673),
        ("Vizag", 17.6868, 83.2185),
        ("Chennai", 13.0827, 80.2707),
        ("Digha", 21.6266, 87.5074),
    ]
    for name, lat, lon in locations:
        await test_incois_location(name, lat, lon, radius=0.5)
        await test_incois_location(name, lat, lon, radius=1.0)

if __name__ == "__main__":
    asyncio.run(main())
