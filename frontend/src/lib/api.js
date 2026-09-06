const API_BASE = "";

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function requestJson(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(`Backend returned ${response.status}`, response.status);
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Backend is unavailable. Start FastAPI on port 8000.");
  }
}

function withParams(path, params = {}) {
  const query = new URLSearchParams();
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value) {
      query.set(key, value);
    }
  });

  const suffix = query.toString();
  return suffix ? `${path}?${suffix}` : path;
}

export function fetchPFZ(params) {
  return requestJson(withParams("/api/v1/pfz", params));
}

export function fetchAlerts(params) {
  return requestJson(withParams("/api/v1/alerts", params));
}

export function postQuery(query) {
  return requestJson("/api/v1/query", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
}
