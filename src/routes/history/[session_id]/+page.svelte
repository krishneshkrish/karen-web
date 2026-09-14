<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { openDB } from 'idb';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	interface Message {
		id?: string;
		sender: 'user' | 'karen';
		content: string;
		timestamp?: string;
		created_at?: string | number;
	}

	interface SessionMeta {
		session_id: string;
		started_at?: number | string;
		topic?: string;
		final_severity?: string;
		emotion_arc?: string[];
	}

	let sessionId = $derived(page.params.session_id);

	let messages = $state<Message[]>([]);
	let sessionMeta = $state<SessionMeta | null>(null);
	let reportExists = $state<boolean>(false);
	let loading = $state<boolean>(true);
	let generatingReport = $state<boolean>(false);

	let mainContainer: HTMLElement | null = $state(null);
	let showJumpToTop = $state<boolean>(false);

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
		if (!timestamp) return 'Past session';
		const d = new Date(timestamp);
		if (isNaN(d.getTime())) return String(timestamp);
		return d.toLocaleDateString('en-US', {
			weekday: 'short',
			day: 'numeric',
			month: 'short',
			hour: 'numeric',
			minute: '2-digit'
		});
	}

	function handleScroll() {
		if (mainContainer) {
			const maxScroll = mainContainer.scrollHeight - mainContainer.clientHeight;
			showJumpToTop = mainContainer.scrollTop < maxScroll - 300;
		}
	}

	function scrollToTop() {
		if (mainContainer) {
			mainContainer.scrollTo({ top: 0, behavior: 'smooth' });
		}
	}

	async function loadSessionDetail() {
		loading = true;
		const sid = sessionId || '';
		if (!sid) {
			loading = false;
			return;
		}

		// 1. Fetch remote session metadata if available
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		let remoteMeta: any = null;
		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/history/sessions/${sid}`, { headers });
			if (res.ok) {
				remoteMeta = await res.json();
			}
		} catch (err) {
			// Fail soft
		}

		// 2. Fetch full transcript and local session metadata from IndexedDB
		try {
			const db = await getDB();
			const localSession = await db.get('sessions', sid);
			const existingReport = await db.get('reports', sid);

			if (existingReport) {
				reportExists = true;
			}

			if (localSession) {
				sessionMeta = {
					session_id: sid,
					started_at: localSession.started_at || remoteMeta?.started_at || Date.now(),
					topic: localSession.topic || remoteMeta?.topic || 'Emotional Reflection',
					final_severity: localSession.final_severity || remoteMeta?.final_severity,
					emotion_arc: localSession.emotion_arc || remoteMeta?.emotion_arc || []
				};
				if (localSession.messages && Array.isArray(localSession.messages)) {
					messages = localSession.messages;
				}
			} else if (remoteMeta) {
				sessionMeta = {
					session_id: sid,
					started_at: remoteMeta.started_at || Date.now(),
					topic: remoteMeta.topic || 'Emotional Reflection',
					final_severity: remoteMeta.final_severity,
					emotion_arc: remoteMeta.emotion_arc || []
				};
				if (remoteMeta.messages) {
					messages = remoteMeta.messages;
				}
			}
		} catch (err) {
			// Fail soft
		}

		loading = false;

		tick().then(() => {
			if (mainContainer) {
				mainContainer.scrollTop = mainContainer.scrollHeight;
			}
		});
	}

	async function handleGenerateReport() {
		generatingReport = true;
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		const payloadMessages = messages.map((m) => ({
			role: m.sender === 'user' ? 'user' : 'assistant',
			content: m.content
		}));

		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/report/generate`, {
				method: 'POST',
				headers,
				body: JSON.stringify({
					session_id: sessionId,
					messages: payloadMessages,
					emotion_arc: sessionMeta?.emotion_arc || [],
					topic: sessionMeta?.topic || 'Emotional Reflection',
					final_severity: sessionMeta?.final_severity
				})
			});

			if (res.ok) {
				const reportData = await res.json();
				const db = await getDB();
				await db.put('reports', reportData);
			}
		} catch (err) {
			// Fallback offline report
			const db = await getDB();
			await db.put('reports', {
				session_id: sessionId,
				topic: sessionMeta?.topic || 'Emotional Reflection',
				final_severity: sessionMeta?.final_severity || 'Mild',
				emotional_journey_summary: 'A quiet processing session saved locally on your device.',
				key_takeaways: ['Navigated feelings without judgment', 'Took time to ground and reflect'],
				recommended_practices: ['5-4-3-2-1 Grounding', 'Mindful breathing'],
				created_at: new Date().toISOString()
			});
		} finally {
			generatingReport = false;
			goto(`/report?session_id=${sessionId}`);
		}
	}

	onMount(() => {
		loadSessionDetail();
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col bg-[#0d0d1a] text-white select-none overflow-hidden"
>
	<!-- Top Bar -->
	<header
		class="sticky top-0 z-30 flex h-16 w-full items-center justify-between px-4 bg-[#0d0d1a]/80 backdrop-blur-md border-b border-white/5"
	>
		<button
			type="button"
			onclick={() => goto('/history')}
			class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/70 hover:text-white hover:border-purple-300/50 transition-all active:scale-95"
			aria-label="Back to history"
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

		<div class="text-xs font-light text-purple-200/80">
			{formatDate(sessionMeta?.started_at)}
		</div>

		<button
			type="button"
			onclick={() => goto(reportExists ? `/report?session_id=${sessionId}` : `/history/${sessionId}`)}
			class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/70 hover:text-white hover:border-purple-300/50 transition-all active:scale-95"
			aria-label="Reflection options"
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
				<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
				<polyline points="7 10 12 15 17 10" />
				<line x1="12" y1="15" x2="12" y2="3" />
			</svg>
		</button>
	</header>

	<!-- Metadata Strip (Topic Pill + Emotion Arc Dots) -->
	<div
		class="z-20 flex items-center justify-between px-6 py-2.5 bg-purple-950/20 border-b border-purple-500/10 text-xs"
	>
		<span class="rounded-full bg-purple-900/40 px-3 py-0.5 text-purple-200/80 border border-purple-400/20 font-light">
			{sessionMeta?.topic || 'Emotional Processing'}
		</span>

		{#if sessionMeta?.emotion_arc && sessionMeta.emotion_arc.length > 0}
			<div class="flex items-center space-x-1.5">
				{#each sessionMeta.emotion_arc as emotion}
					<div
						class="h-2 w-2 rounded-full"
						style="background-color: {emotionColors[emotion] || emotionColors.neutral}"
						title={emotion}
					></div>
				{/each}
			</div>
		{/if}
	</div>

	<!-- Soft Top Banner -->
	<div class="z-20 bg-purple-950/30 px-6 py-2 text-center text-[11px] font-light text-purple-200/50 border-b border-white/5">
		This is a record of your conversation on {formatDate(sessionMeta?.started_at)}. It lives only on this device.
	</div>

	<!-- Main Chat Replay Area -->
	<main
		bind:this={mainContainer}
		onscroll={handleScroll}
		class="z-10 flex-1 overflow-y-auto px-4 pt-6 pb-20 space-y-6 max-w-[390px] w-full mx-auto"
	>
		{#if loading}
			<div class="mt-20 text-center text-xs font-light text-purple-200/50 animate-pulse">
				Retrieving journal record...
			</div>
		{:else if messages.length === 0}
			<div class="mt-20 text-center text-xs font-light text-purple-200/50">
				No recorded messages in this session.
			</div>
		{:else}
			{#each messages as msg (msg.id || msg.content)}
				<div class="flex flex-col">
					{#if msg.sender === 'karen'}
						<!-- Karen Message Bubble (Left-aligned, floating text, left border accent) -->
						<div class="max-w-[85%] self-start pl-3 border-l-2 border-purple-300/20 py-1 space-y-1">
							<p class="font-light text-sm leading-[1.7] text-purple-50">
								{msg.content}
							</p>
							{#if msg.timestamp || msg.created_at}
								<span class="block text-[10px] font-light text-purple-200/40">
									{msg.timestamp || formatDate(msg.created_at)}
								</span>
							{/if}
						</div>
					{:else}
						<!-- User Message Bubble (Right-aligned, muted purple pill) -->
						<div class="max-w-[75%] self-end space-y-1">
							<div class="rounded-2xl bg-[rgba(100,80,180,0.25)] px-4 py-3 text-sm font-light leading-relaxed text-purple-50">
								{msg.content}
							</div>
							{#if msg.timestamp || msg.created_at}
								<span class="block text-right text-[10px] font-light text-purple-200/40 pr-1">
									{msg.timestamp || formatDate(msg.created_at)}
								</span>
							{/if}
						</div>
					{/if}
				</div>
			{/each}
		{/if}

		<!-- Reflection Section at Bottom -->
		{#if !loading && messages.length > 0}
			<div class="pt-8 pb-4 text-center border-t border-white/5 space-y-3">
				{#if reportExists}
					<p class="text-xs font-light text-purple-200/70">You saved a reflection from this session.</p>
					<button
						type="button"
						onclick={() => goto(`/report?session_id=${sessionId}`)}
						class="inline-flex items-center justify-center rounded-full bg-purple-950/40 px-6 py-2.5 text-xs font-medium text-purple-100 ring-1 ring-purple-400/30 hover:bg-purple-900/40 hover:text-white transition-all active:scale-95"
					>
						View reflection
					</button>
				{:else}
					<p class="text-xs font-light text-purple-200/60">Would you like a reflection of this conversation?</p>
					<button
						type="button"
						onclick={handleGenerateReport}
						disabled={generatingReport}
						class="inline-flex items-center justify-center rounded-full bg-purple-950/40 px-6 py-2.5 text-xs font-medium text-purple-100 ring-1 ring-purple-400/30 hover:bg-purple-900/40 hover:text-white transition-all active:scale-95 disabled:opacity-50"
					>
						{#if generatingReport}
							<span class="animate-pulse">Generating reflection...</span>
						{:else}
							<span>Generate reflection</span>
						{/if}
					</button>
				{/if}
			</div>
		{/if}
	</main>

	<!-- Jump to Top Floating Button -->
	{#if showJumpToTop}
		<button
			type="button"
			onclick={scrollToTop}
			class="fixed bottom-6 right-6 z-30 flex h-9 w-9 items-center justify-center rounded-full bg-purple-950/80 border border-purple-400/30 text-purple-200 shadow-lg hover:text-white transition-all active:scale-95"
			aria-label="Jump to top"
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
				<path d="m18 15-6-6-6 6" />
			</svg>
		</button>
	{/if}
</div>
