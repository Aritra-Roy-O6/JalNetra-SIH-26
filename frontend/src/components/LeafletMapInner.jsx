"use client";

import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";

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

function styleFeature(feature) {
  const zoneType = feature?.properties?.zone_type;
  if (zoneType === "potential_fishing_zone") {
    return { color: "#15803d", fillColor: "#22c55e", fillOpacity: 0.28, weight: 2 };
  }
  if (zoneType === "weather_alert") {
    return { color: "#b45309", fillColor: "#f59e0b", fillOpacity: 0.22, weight: 2 };
  }
  return { color: "#1d4ed8", fillColor: "#60a5fa", fillOpacity: 0.12, weight: 2, dashArray: "6 4" };
}

function bindPopup(feature, layer) {
  const props = feature.properties || {};
  layer.bindPopup(`<strong>${props.name || props.zone_type || "Marine zone"}</strong>`);
}

export default function LeafletMapInner({ pfz, alerts }) {
  const activeAlerts = alertCollection(alerts);

  return (
    <MapContainer
      center={[20.25, 88.45]}
      zoom={8}
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
      {pfz?.features?.length ? (
        <GeoJSON data={pfz} style={styleFeature} onEachFeature={bindPopup} />
      ) : null}
      <GeoJSON data={activeAlerts} style={styleFeature} onEachFeature={bindPopup} />
      <GeoJSON data={RESTRICTED_BOUNDARIES} style={styleFeature} onEachFeature={bindPopup} />
    </MapContainer>
  );
}
