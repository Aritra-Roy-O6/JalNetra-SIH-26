"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import nearestPoint from "@turf/nearest-point";
import distance from "@turf/distance";
import { point } from "@turf/helpers";
import coastlineSource from "../../public/data/india_coastline.geojson";
import validPortsSource from "../../public/data/valid_ports.geojson";
import { clearUserLocation, loadUserLocation, saveUserLocation } from "./db";

const LocationContext = createContext(null);
const coastlinePayload = coastlineSource?.default || coastlineSource;
const coastline = typeof coastlinePayload === "string" ? JSON.parse(coastlinePayload) : coastlinePayload;

const DEFAULT_PORTS_COLLECTION = {
  type: "FeatureCollection",
  features: [
    { type: "Feature", properties: { name: "Digha" }, geometry: { type: "Point", coordinates: [87.52, 21.62] } },
    { type: "Feature", properties: { name: "Kakdwip" }, geometry: { type: "Point", coordinates: [88.18, 21.87] } },
    { type: "Feature", properties: { name: "Frazerganj" }, geometry: { type: "Point", coordinates: [88.25, 21.58] } },
    { type: "Feature", properties: { name: "Namkhana" }, geometry: { type: "Point", coordinates: [88.23, 21.77] } },
    { type: "Feature", properties: { name: "Paradip" }, geometry: { type: "Point", coordinates: [86.70, 20.31] } },
    { type: "Feature", properties: { name: "Visakhapatnam" }, geometry: { type: "Point", coordinates: [83.29, 17.69] } },
    { type: "Feature", properties: { name: "Chennai" }, geometry: { type: "Point", coordinates: [80.29, 13.08] } },
    { type: "Feature", properties: { name: "Kochi" }, geometry: { type: "Point", coordinates: [76.28, 9.97] } },
    { type: "Feature", properties: { name: "Goa" }, geometry: { type: "Point", coordinates: [73.81, 15.46] } },
    { type: "Feature", properties: { name: "Mumbai" }, geometry: { type: "Point", coordinates: [72.95, 18.95] } },
    { type: "Feature", properties: { name: "Veraval" }, geometry: { type: "Point", coordinates: [70.37, 20.90] } },
  ],
};

function parseGeoJson(source) {
  if (!source) return DEFAULT_PORTS_COLLECTION;
  const payload = source?.default || source;
  if (typeof payload === "string") {
    try { return JSON.parse(payload); } catch { return DEFAULT_PORTS_COLLECTION; }
  }
  return payload?.features ? payload : DEFAULT_PORTS_COLLECTION;
}

const validPorts = parseGeoJson(validPortsSource);

export const MANUAL_REGIONS = (validPorts.features || []).map((f) => ({
  name: f.properties.name,
  lat: f.geometry.coordinates[1],
  lon: f.geometry.coordinates[0],
}));

function nearestCoastalLocation(latitude, longitude) {
  const userPt = point([longitude, latitude]);
  const nearestPortFeature = nearestPoint(userPt, validPorts);
  const portName = nearestPortFeature.properties.name || "Coastal Port";
  const [portLon, portLat] = nearestPortFeature.geometry.coordinates;
  const distKm = distance(userPt, nearestPortFeature, { units: "kilometers" });

  if (distKm <= 5) {
    return { lat: latitude, lon: longitude, distanceKm: distKm, portName, isNearCoast: true };
  }
  return { lat: portLat, lon: portLon, distanceKm: distKm, portName, isNearCoast: false };
}

export function ResolvedLocationProvider({ children }) {
  const [location, setLocation] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [toastMessage, setToastMessage] = useState("");

  async function chooseManual(region) {
    const resolved = { lat: region.lat, lon: region.lon, resolvedAt: Date.now(), source: "manual", name: region.name };
    await saveUserLocation(resolved);
    setLocation(resolved);
    setStatus("resolved");
    setError("");
    setToastMessage("");
  }

  function requestLocation() {
    if (!navigator.geolocation) {
      setError("Location is not supported by this browser.");
      setStatus("manual");
      return;
    }
    setStatus("resolving");
    setError("");
    setToastMessage("");
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        try {
          const coastal = nearestCoastalLocation(coords.latitude, coords.longitude);
          const resolved = {
            lat: coastal.lat,
            lon: coastal.lon,
            resolvedAt: Date.now(),
            source: coastal.isNearCoast ? "auto" : "nearest_port",
            name: coastal.portName,
            distanceKm: coastal.distanceKm,
          };
          await saveUserLocation(resolved);
          setLocation(resolved);
          setStatus("resolved");

          if (!coastal.isNearCoast) {
            setToastMessage(`Located inland (${coastal.distanceKm.toFixed(1)} km). Defaulting to nearest coastal port: ${coastal.portName}.`);
          }
        } catch {
          setError("Coastline location could not be calculated. Choose a coastal region below.");
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
    toastMessage,
    regions: MANUAL_REGIONS,
    chooseManual,
    changeLocation: async () => { await clearUserLocation(); setLocation(null); setStatus("manual"); setError(""); setToastMessage(""); requestLocation(); },
    requestLocation,
  }), [location, status, error, toastMessage]);

  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useResolvedLocation() {
  const context = useContext(LocationContext);
  if (!context) throw new Error("useResolvedLocation must be used inside ResolvedLocationProvider");
  return context;
}
