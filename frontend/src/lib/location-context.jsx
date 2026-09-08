"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import nearestPointOnLine from "@turf/nearest-point-on-line";
import { point } from "@turf/helpers";
import coastlineSource from "../../public/data/india_coastline.geojson";
import { clearUserLocation, loadUserLocation, saveUserLocation } from "./db";

const LocationContext = createContext(null);
const coastlinePayload = coastlineSource?.default || coastlineSource;
const coastline = typeof coastlinePayload === "string" ? JSON.parse(coastlinePayload) : coastlinePayload;

export const MANUAL_REGIONS = [
  { name: "Mumbai", lat: 18.95, lon: 72.95 },
  { name: "Veraval", lat: 20.90, lon: 70.37 },
  { name: "Kochi", lat: 9.97, lon: 76.28 },
  { name: "Chennai", lat: 13.08, lon: 80.29 },
  { name: "Visakhapatnam", lat: 17.69, lon: 83.29 },
  { name: "Digha", lat: 21.63, lon: 87.51 },
];

function nearestCoastalLocation(latitude, longitude) {
  const lines = coastline?.type === "Feature" && coastline.geometry?.type === "MultiLineString"
    ? { type: "FeatureCollection", features: coastline.geometry.coordinates.map((coordinates) => ({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates } })) }
    : coastline;
  const result = nearestPointOnLine(lines, point([longitude, latitude]), { units: "kilometers" });
  const [lon, lat] = result.geometry.coordinates;
  const distance = result.properties?.dist ?? Infinity;
  return { lat, lon, distanceKm: distance };
}

export function ResolvedLocationProvider({ children }) {
  const [location, setLocation] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");

  async function chooseManual(region) {
    const resolved = { lat: region.lat, lon: region.lon, resolvedAt: Date.now(), source: "manual", name: region.name };
    await saveUserLocation(resolved);
    setLocation(resolved);
    setStatus("resolved");
    setError("");
  }

  function requestLocation() {
    if (!navigator.geolocation) {
      setError("Location is not supported by this browser.");
      setStatus("manual");
      return;
    }
    setStatus("resolving");
    setError("");
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const coastal = nearestCoastalLocation(coords.latitude, coords.longitude);
          if (coastal.distanceKm > 50) {
            setError("You are more than 50 km from the coast. Choose your coastal region.");
            setStatus("manual");
            return;
          }
          const resolved = { lat: coastal.lat, lon: coastal.lon, resolvedAt: Date.now(), source: "auto", distanceKm: coastal.distanceKm };
          await saveUserLocation(resolved);
          setLocation(resolved);
          setStatus("resolved");
        } catch {
          setError("Coastline data could not be resolved. Choose your coastal region.");
          setStatus("manual");
        }
      },
      (geoError) => {
        const reason = geoError.code === geoError.PERMISSION_DENIED
          ? "Location permission was denied. Allow location for this site, then tap Change location."
          : geoError.code === geoError.TIMEOUT
            ? "Location request timed out. Check device location services, then tap Change location."
            : "Location is unavailable here. Use HTTPS or localhost, then tap Change location.";
        setError(`${reason} (${geoError.message || "geolocation error"})`);
        setStatus("manual");
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
  }

  useEffect(() => {
    let active = true;
    loadUserLocation().then((saved) => {
      if (!active) return;
      if (saved) {
        setLocation(saved);
        setStatus("resolved");
        return;
      }
      requestLocation();
    }).catch(() => {
      if (active) {
        setError("Saved location could not be loaded. Choose your coastal region.");
        setStatus("manual");
      }
    });
    return () => { active = false; };
  }, []);

  const value = useMemo(() => ({
    location,
    status,
    error,
    regions: MANUAL_REGIONS,
    chooseManual,
    changeLocation: async () => { await clearUserLocation(); setLocation(null); setStatus("manual"); setError(""); requestLocation(); },
    requestLocation,
  }), [location, status, error]);

  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useResolvedLocation() {
  const context = useContext(LocationContext);
  if (!context) throw new Error("useResolvedLocation must be used inside ResolvedLocationProvider");
  return context;
}
