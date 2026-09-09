/** @type {import('next').NextConfig} */
import nextPWA from "@ducanh2912/next-pwa";

const nextConfig = {
  turbopack: {
    rules: {
      "*.geojson": { type: "raw" },
    },
  },
  /* config options here */
  reactCompiler: true,
  webpack(config) {
    config.module.rules.push({ test: /\.geojson$/, type: "asset/source" });
    return config;
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.API_BASE_URL || "http://127.0.0.1:8000"}/api/v1/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/api/v1/:path*",
        headers: [{ key: "x-accel-buffering", value: "no" }],
      },
    ];
  },
  httpAgentOptions: {
    keepAlive: true,
  },
  experimental: {
    proxyTimeout: 90_000,
  },
};

const withPWA = (nextPWA.default || nextPWA)({
  dest: "public",
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === "development",
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/.*\.tile\.openstreetmap\.org\/.*$/i,
      handler: "CacheFirst",
      options: {
        cacheName: "jalnetra-map-tiles",
        expiration: { maxEntries: 500, maxAgeSeconds: 30 * 24 * 60 * 60 },
        cacheableResponse: { statuses: [0, 200] },
      },
    },
  ],
});

export default withPWA(nextConfig);
