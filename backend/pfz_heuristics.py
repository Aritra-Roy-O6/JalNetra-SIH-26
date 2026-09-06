"""Deterministic PFZ heuristic stub for the JalNetra prototype."""

import numpy as np
import pandas as pd


def generate_mock_pfz() -> dict:
    """Return a deterministic GeoJSON FeatureCollection of mock PFZs.

    The arrays stand in for SST and chlorophyll raster cells. A cell is treated
    as favourable when both values clear the prototype thresholds.
    """
    sst_raster = np.array([[27.1, 28.2], [26.8, 27.8]])
    chlorophyll_raster = np.array([[0.22, 0.75], [0.18, 0.62]])
    coordinates = [
        [88.0, 20.0],
        [88.5, 20.0],
        [88.5, 20.5],
        [88.0, 20.5],
        [88.0, 20.0],
    ]

    raster_cells = pd.DataFrame(
        {
            "sst": sst_raster.ravel(),
            "chlorophyll": chlorophyll_raster.ravel(),
        }
    )
    favourable_cells = raster_cells[
        (raster_cells["sst"] >= 27.5)
        & (raster_cells["chlorophyll"] >= 0.5)
    ]
    confidence = round(
        float(
            favourable_cells["chlorophyll"].mean()
            / raster_cells["chlorophyll"].max()
        ),
        2,
    )

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "zone_type": "potential_fishing_zone",
                    "sst_celsius": 27.8,
                    "chlorophyll_mg_m3": 0.62,
                    "confidence": confidence,
                    "source": "deterministic_mock_heuristic",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates],
                },
            }
        ],
    }