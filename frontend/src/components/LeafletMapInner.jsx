"use client";

import { useEffect, useRef } from "react";
import { useMap, useMapEvents } from "react-leaflet";
import { Circle, CircleMarker, GeoJSON, MapContainer, TileLayer, Tooltip } from "react-leaflet";

const ALERT_ZONES = {
  cyclone: polygonFeature("Cyclone watch", "weather_alert", [
    [86.7, 19.1],
    [88.9, 19.1],
    [88.9, 21.1],
    [86.7, 21.1],
    [86.7, 19.1],
  ]),
  geofence: polygonFeature("Protected coastal restriction", "weather_alert", [
    [87.8, 19.6],
    [88.6, 19.6],
    [88.6, 20.2],
    [87.8, 20.2],
    [87.8, 19.6],
  ]),
};

const RESTRICTED_BOUNDARIES = {
  type: "FeatureCollection",
  features: [
    polygonFeature("Seasonal fishing ban boundary", "restricted_boundary", [
      [88.95, 19.7],
      [89.45, 19.7],
      [89.45, 20.85],
      [88.95, 20.85],
      [88.95, 19.7],
    ]),
  ],
};

function polygonFeature(name, zoneType, coordinates) {
  return {
    type: "Feature",
    properties: { name, zone_type: zoneType },
    geometry: { type: "Polygon", coordinates: [coordinates] },
  };
}

function alertCollection(alerts) {
  return {
    type: "FeatureCollection",
    features: alerts.map((alert) => ({
      ...(ALERT_ZONES[alert.type] || ALERT_ZONES.cyclone),
      properties: {
        ...alert,
        name: alert.message || alert.type,
        zone_type: "weather_alert",
      },
    })),
  };
}

function styleFeature(feature, cached) {
  const zoneType = feature?.properties?.zone_type;
  const cachedStyle = cached ? { opacity: 0.68, fillOpacity: 0.18, weight: 2, dashArray: "7 5" } : {};
  if (zoneType === "potential_fishing_zone") {
    return { color: "#15803d", fillColor: "#22c55e", fillOpacity: 0.28, weight: 2, ...cachedStyle };
  }
  if (zoneType === "weather_alert") {
    return { color: "#b45309", fillColor: "#f59e0b", fillOpacity: 0.22, weight: 2, ...cachedStyle };
  }
  return { color: "#1d4ed8", fillColor: "#60a5fa", fillOpacity: 0.12, weight: 2, dashArray: "6 4", ...cachedStyle };
}

function bindPopup(feature, layer) {
  const props = feature.properties || {};
  layer.bindPopup(`<strong>${props.name || props.zone_type || "Marine zone"}</strong>`);
}

function MapStateSaver({ onMapChange }) {
  useMapEvents({
    moveend(event) {
      const map = event.target;
      const center = map.getCenter();
      onMapChange?.({ center: [center.lat, center.lng], zoom: map.getZoom() });
    },
  });
  return null;
}

function MapStateRestorer({ mapState }) {
  const map = useMap();
  useEffect(() => {
    if (!mapState) return;
    const center = map.getCenter();
    if (center.lat !== mapState.center[0] || center.lng !== mapState.center[1] || map.getZoom() !== mapState.zoom) {
      map.setView(mapState.center, mapState.zoom, { animate: false });
    }
  }, [map, mapState]);
  return null;
}

function MapSizeObserver() {
  const map = useMap();
  const containerRef = useRef(null);

  useEffect(() => {
    const container = map.getContainer();
    const resize = () => map.invalidateSize({ pan: false, animate: false });
    containerRef.current = container;
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(container);
    return () => observer.disconnect();
  }, [map]);

  return null;
}

function CurrentLocationMarker({ location }) {
  const map = useMap();
  const centeredRef = useRef(false);

  useEffect(() => {
    if (!location || centeredRef.current) return;
    centeredRef.current = true;
    map.setView([location.latitude, location.longitude], Math.max(map.getZoom(), 8), { animate: false });
  }, [location, map]);

  if (!location) return null;
  const center = [location.latitude, location.longitude];
  return <><Circle center={center} radius={location.accuracy} pathOptions={{ color: "#0e7490", fillColor: "#67e8f9", fillOpacity: 0.12, weight: 1, dashArray: "4 4" }} /><CircleMarker center={center} radius={8} pathOptions={{ color: "#fff", fillColor: "#0e7490", fillOpacity: 1, weight: 3 }}><Tooltip permanent direction="top" offset={[0, -8]}>Current location</Tooltip></CircleMarker></>;
}

function prefetchTiles(center, zoom) {
  const scale = 2 ** zoom;
  const x = Math.floor(((center[1] + 180) / 360) * scale);
  const y = Math.floor(((1 - Math.asinh(Math.tan((center[0] * Math.PI) / 180)) / Math.PI) / 2) * scale);
  const urls = [];
  for (let offsetX = -1; offsetX <= 1; offsetX += 1) {
    for (let offsetY = -1; offsetY <= 1; offsetY += 1) {
      const tileX = (x + offsetX + scale) % scale;
      const tileY = Math.max(0, Math.min(scale - 1, y + offsetY));
      urls.push(`https://${["a", "b", "c"][urls.length % 3]}.tile.openstreetmap.org/${zoom}/${tileX}/${tileY}.png`);
    }
  }
  urls.forEach((url) => fetch(url).catch(() => null));
}

function MapTilePrefetcher({ mapState, cached }) {
  const prefetchedRef = useRef(false);

  useEffect(() => {
    if (cached || prefetchedRef.current || !mapState) return;
    prefetchedRef.current = true;
    prefetchTiles(mapState.center, mapState.zoom);
  }, [cached, mapState]);

  return null;
}

export default function LeafletMapInner({ pfz, alerts, mapState, cached, currentLocation, onMapChange }) {
  const activeAlerts = alertCollection(alerts);

  return (
    <MapContainer
      center={mapState?.center || [20.25, 88.45]}
      zoom={mapState?.zoom || 8}
      scrollWheelZoom
      className="h-full min-h-[360px] w-full"
      maxBounds={[
        [5, 66],
        [24, 99],
      ]}
      maxBoundsViscosity={0.6}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapSizeObserver />
      <MapTilePrefetcher mapState={mapState} cached={cached} />
      <CurrentLocationMarker location={currentLocation} />
      <MapStateRestorer mapState={mapState} />
      <MapStateSaver onMapChange={onMapChange} />
      {pfz?.features?.length ? (
        <GeoJSON data={pfz} style={(feature) => styleFeature(feature, cached)} onEachFeature={bindPopup} />
      ) : null}
      <GeoJSON data={activeAlerts} style={(feature) => styleFeature(feature, cached)} onEachFeature={bindPopup} />
      <GeoJSON data={RESTRICTED_BOUNDARIES} style={(feature) => styleFeature(feature, cached)} onEachFeature={bindPopup} />
    </MapContainer>
  );
}
