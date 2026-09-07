import Dexie, { type Table } from "dexie";

export type MapState = { center: [number, number]; zoom: number };
export type ChatMessage = { query: string; answer: string; createdAt: number };

class JalNetraDb extends Dexie {
  mapState!: Table<MapState & { id: string }, string>;
  chatHistory!: Table<ChatMessage & { id?: number }, number>;

  constructor() {
    super("jalnetra");
    this.version(1).stores({ mapState: "id", chatHistory: "++id, createdAt" });
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
