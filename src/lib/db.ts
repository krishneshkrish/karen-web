import { openDB, type DBSchema, type IDBPDatabase } from 'idb';

export interface ChatMessage {
	id: string;
	session_id: string;
	sender: 'user' | 'karen';
	content: string;
	timestamp: string; // ISO String
	detected_emotion?: string;
}

export interface SessionMeta {
	id: string;
	start_time: string; // ISO string
	end_time?: string;
	message_count: number;
	dominant_emotion?: string;
	topic?: string;
	final_severity?: string;
	summary?: string;
}

interface KarenDB extends DBSchema {
	messages: {
		key: string;
		value: ChatMessage;
		indexes: { 'by-session': string };
	};
	sessions: {
		key: string;
		value: SessionMeta;
		indexes: { 'by-time': string };
	};
}

const DB_NAME = 'karen_transcript_db';
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<KarenDB>> | null = null;

export function getDB() {
	if (typeof window === 'undefined') return null;
	if (!dbPromise) {
		dbPromise = openDB<KarenDB>(DB_NAME, DB_VERSION, {
			upgrade(db) {
				const messageStore = db.createObjectStore('messages', { keyPath: 'id' });
				messageStore.createIndex('by-session', 'session_id');

				const sessionStore = db.createObjectStore('sessions', { keyPath: 'id' });
				sessionStore.createIndex('by-time', 'start_time');
			}
		});
	}
	return dbPromise;
}

// Save a single message to local IndexedDB (NEVER sent to server)
export async function saveLocalMessage(msg: ChatMessage): Promise<void> {
	const db = await getDB();
	if (!db) return;
	await db.put('messages', msg);
}

// Get all messages for a session from IndexedDB
export async function getLocalSessionMessages(sessionId: string): Promise<ChatMessage[]> {
	const db = await getDB();
	if (!db) return [];
	const messages = await db.getAllFromIndex('messages', 'by-session', sessionId);
	return messages.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
}

// Create or update local session metadata
export async function saveLocalSessionMeta(session: SessionMeta): Promise<void> {
	const db = await getDB();
	if (!db) return;
	await db.put('sessions', session);
}

// List all sessions stored locally
export async function getLocalSessions(): Promise<SessionMeta[]> {
	const db = await getDB();
	if (!db) return [];
	const sessions = await db.getAll('sessions');
	return sessions.sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
}

// Get single session meta
export async function getLocalSessionMeta(sessionId: string): Promise<SessionMeta | undefined> {
	const db = await getDB();
	if (!db) return undefined;
	return db.get('sessions', sessionId);
}
