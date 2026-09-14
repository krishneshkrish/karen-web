<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { openDB } from 'idb';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	interface SessionItem {
		session_id: string;
		started_at?: number | string;
		topic?: string;
		final_severity?: string;
		emotion_arc?: string[];
		hasReport?: boolean;
	}

	let sessions = $state<SessionItem[]>([]);
	let loading = $state(true);

	const emotionColors: Record<string, string> = {
		sadness: '#6b9bd2',
		fear: '#d4a853',
		anger: '#c47070',
		joy: '#6ba882',
		neutral: '#555566'
	};

	async function getDB() {
		return openDB('karen-db', 2, {
			upgrade(db, oldVersion) {
				if (oldVersion < 1) {
					if (!db.objectStoreNames.contains('sessions')) {
						db.createObjectStore('sessions', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('preferences')) {
						db.createObjectStore('preferences', { keyPath: 'key' });
					}
				}
				if (oldVersion < 2) {
					if (!db.objectStoreNames.contains('reports')) {
						db.createObjectStore('reports', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('sessions')) {
						db.createObjectStore('sessions', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('preferences')) {
						db.createObjectStore('preferences', { keyPath: 'key' });
					}
				}
			}
		});
	}

	function formatDate(timestamp?: number | string): string {
		if (!timestamp) return 'Recent session';
		const d = new Date(timestamp);
		if (isNaN(d.getTime())) return String(timestamp);
		return d.toLocaleDateString('en-US', {
			weekday: 'long',
			day: 'numeric',
			month: 'short',
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	async function loadHistorySessions() {
		loading = true;

		// 1. Fetch remote metadata if available
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		let remoteMetaMap: Record<string, any> = {};
		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/history/sessions`, { headers });
			if (res.ok) {
				const remoteList = await res.json();
				if (Array.isArray(remoteList)) {
					remoteList.forEach((item) => {
						remoteMetaMap[item.session_id || item.id] = item;
					});
				}
			}
		} catch (err) {
			// Fail soft if server unreachable
		}

		// 2. Read local sessions from IndexedDB
		let combined: SessionItem[] = [];
		try {
			const db = await getDB();
			const localSessions = await db.getAll('sessions');
			const localReports = await db.getAll('reports');
			const reportIdSet = new Set(localReports.map((r: any) => r.session_id));

			const localMap: Record<string, any> = {};
			localSessions.forEach((s: any) => {
				localMap[s.session_id] = s;
			});

			// Merge remote and local session IDs
			const allIds = Array.from(new Set([...Object.keys(localMap), ...Object.keys(remoteMetaMap)]));

			combined = allIds.map((sid) => {
				const local = localMap[sid] || {};
				const remote = remoteMetaMap[sid] || {};

				return {
					session_id: sid,
					started_at: local.started_at || remote.created_at || remote.started_at || Date.now(),
					topic: local.topic || remote.topic || 'Emotional Grounding',
					final_severity: local.final_severity || remote.final_severity,
					emotion_arc: local.emotion_arc || remote.emotion_arc || ['neutral'],
					hasReport: reportIdSet.has(sid)
				};
			});

			combined.sort((a, b) => new Date(b.started_at || 0).getTime() - new Date(a.started_at || 0).getTime());
		} catch (err) {
			// Fail soft
		}

		sessions = combined;
		loading = false;
	}

	onMount(() => {
		loadHistorySessions();
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col bg-[#0d0d1a] px-5 py-6 text-white select-none overflow-x-hidden"
>
	<!-- Ambient Background Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-96 w-96 rounded-full bg-purple-950/15 blur-[120px]"></div>
	</div>

	<!-- Top Bar -->
	<header class="z-10 flex items-center justify-between pb-4 border-b border-white/5">
		<div class="flex items-center space-x-3">
			<button
				type="button"
				onclick={() => goto('/complete')}
				class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/70 hover:text-white hover:border-purple-300/50 transition-all active:scale-95"
				aria-label="Go back"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="h-4 w-4"
				>
					<path d="M19 12H5" />
					<path d="m12 19-7-7 7-7" />
				</svg>
			</button>
			<h1 class="font-serif text-xl font-light tracking-wide text-purple-50">Your sessions</h1>
		</div>

		<div class="flex items-center space-x-1.5 text-xs text-purple-200/50">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-3.5 w-3.5 text-purple-300/60"
			>
				<rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
				<path d="M7 11V7a5 5 0 0 1 10 0v4" />
			</svg>
			<span class="text-[11px] font-light">Saved privately on this device</span>
		</div>
	</header>

	<!-- Main Sessions List / Skeleton / Empty State -->
	<main class="z-10 my-auto py-6 max-w-[390px] w-full mx-auto space-y-4">
		{#if loading}
			<!-- Skeleton Shimmer Cards -->
			{#each Array(3) as _}
				<div class="rounded-2xl border border-white/5 bg-white/[0.02] p-4 space-y-3 animate-pulse">
					<div class="h-4 w-2/3 rounded bg-purple-300/10"></div>
					<div class="flex items-center justify-between">
						<div class="h-3 w-1/3 rounded bg-purple-300/10"></div>
						<div class="h-3 w-16 rounded-full bg-purple-300/10"></div>
					</div>
				</div>
			{/each}
		{:else if sessions.length === 0}
			<!-- Empty State -->
			<div class="my-24 flex flex-col items-center justify-center text-center space-y-4">
				<div class="orb-empty-dim"></div>
				<div class="space-y-1">
					<p class="font-serif text-lg font-extralight text-purple-200/80">Your sessions will appear here.</p>
					<p class="text-xs font-light text-purple-300/40">Each one stays on your device.</p>
				</div>
			</div>
		{:else}
			<!-- Session Cards -->
			{#each sessions as session (session.session_id)}
				<button
					type="button"
					onclick={() => goto(`/history/${session.session_id}`)}
					class="group w-full text-left rounded-2xl border border-purple-400/15 bg-white/[0.02] p-4 hover:bg-white/[0.05] hover:border-purple-400/30 transition-all duration-300 active:scale-[0.99] space-y-3"
				>
					<!-- Card Header: Date & Severity Badge -->
					<div class="flex items-center justify-between">
						<span class="text-xs font-light text-purple-200/80">
							{formatDate(session.started_at)}
						</span>

						{#if session.final_severity === 'high' || session.final_severity === 'High'}
							<span class="rounded-full bg-amber-500/15 px-2.5 py-0.5 text-[10px] font-light text-amber-300/90 border border-amber-500/20">
								High distress
							</span>
						{:else if session.final_severity === 'crisis' || session.final_severity === 'Crisis'}
							<span class="rounded-full bg-rose-500/15 px-2.5 py-0.5 text-[10px] font-light text-rose-300/90 border border-rose-500/20">
								Crisis
							</span>
						{/if}
					</div>

					<!-- Card Body: Topic Pill & Emotion Arc Dots -->
					<div class="flex items-center justify-between">
						{#if session.topic}
							<span class="rounded-full bg-purple-950/40 px-3 py-1 text-xs font-light text-purple-200/70 border border-purple-400/20">
								{session.topic}
							</span>
						{:else}
							<span></span>
						{/if}

						<!-- Emotion Arc Dots -->
						{#if session.emotion_arc && session.emotion_arc.length > 0}
							<div class="flex items-center space-x-1.5">
								{#each session.emotion_arc.slice(0, 6) as emotion}
									<div
										class="h-2 w-2 rounded-full"
										style="background-color: {emotionColors[emotion] || emotionColors.neutral}"
										title={emotion}
									></div>
								{/each}
							</div>
						{/if}
					</div>

					<!-- Card Footer Link: View Reflection -->
					{#if session.hasReport}
						<div class="pt-1 text-[11px] font-light text-purple-300/60 group-hover:text-purple-200 transition-colors flex items-center gap-1">
							<span>View reflection</span>
							<span>→</span>
						</div>
					{/if}
				</button>
			{/each}
		{/if}
	</main>
</div>

<style>
	.orb-empty-dim {
		width: 70px;
		height: 70px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(180, 160, 255, 0.2);
		box-shadow: 0 0 25px rgba(140, 100, 255, 0.1);
		animation: breathe 4s ease-in-out infinite;
	}

	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
			opacity: 0.4;
		}
		50% {
			transform: scale(1.08);
			opacity: 0.7;
		}
	}
</style>
