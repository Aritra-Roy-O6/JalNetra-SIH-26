import Dexie, { type Table } from "dexie";

export type MapState = { center: [number, number]; zoom: number };
export type ChatMessage = { query: string; answer: string; createdAt: number };
export type CachedData = { key: string; data: unknown; savedAt: number };
export type UserLocation = { id: string; lat: number; lon: number; resolvedAt: number; source: "auto" | "manual"; name?: string; distanceKm?: number };

class JalNetraDb extends Dexie {
  mapState!: Table<MapState & { id: string }, string>;
  chatHistory!: Table<ChatMessage & { id?: number }, number>;
  cacheRecords!: Table<CachedData, string>;
  userLocation!: Table<UserLocation, string>;

  constructor() {
    super("jalnetra");
    this.version(1).stores({ mapState: "id", chatHistory: "++id, createdAt" });
    this.version(2).stores({ mapState: "id", chatHistory: "++id, createdAt", cacheRecords: "key, savedAt" });
    this.version(3).stores({ mapState: "id", chatHistory: "++id, createdAt", cacheRecords: "key, savedAt", userLocation: "id" });
  }
}

export const db = new JalNetraDb();

export async function saveMapState(mapState: MapState) {
  await db.mapState.put({ id: "last", ...mapState });
}

export async function loadMapState() {
  return db.mapState.get("last");
}

export async function saveChatMessage(query: string, answer: string) {
  await db.chatHistory.add({ query, answer, createdAt: Date.now() });
}

export async function loadLastChatMessage() {
  return db.chatHistory.orderBy("createdAt").last();
}

export async function loadRecentChatMessages() {
  return db.chatHistory.orderBy("createdAt").reverse().limit(3).toArray();
}

export async function clearChatHistory() {
  await db.chatHistory.clear();
}

export async function saveCachedData(key: string, data: unknown) {
  const record = { key, data, savedAt: Date.now() };
  await db.cacheRecords.put(record);
  return record;
}

export async function loadCachedData<T>(key: string) {
  return db.cacheRecords.get(key) as Promise<(CachedData & { data: T }) | undefined>;
}

export async function loadOfflineSnapshot() {
  const [pfz, alerts, route] = await Promise.all([
    loadCachedData("pfz"),
    loadCachedData("alerts"),
    loadCachedData("route"),
  ]);
  return { pfz, alerts, route };
}

export async function saveUserLocation(location: Omit<UserLocation, "id">) {
  await db.userLocation.put({ id: "resolved", ...location });
}

export async function loadUserLocation() {
  return db.userLocation.get("resolved");
}

export async function clearUserLocation() {
  await db.userLocation.delete("resolved");
}
