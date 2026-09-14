<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { openDB } from 'idb';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	let step = $state<'confirm' | 'reflection'>('confirm');
	let loading = $state(false);

	let sessionId = $state('');
	let topic = $state('General Reflection');
	let finalSeverity = $state('Mild');

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

	function handleStayLonger() {
		goto('/chat');
	}

	async function handleEndForNow() {
		loading = true;
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		try {
			await fetch(`${PUBLIC_API_URL}/api/v1/chat/end-session`, {
				method: 'POST',
				headers,
				body: JSON.stringify({
					session_id: sessionId,
					topic,
					final_severity: finalSeverity
				})
			});
		} catch (err) {
			// Fail-soft if network unavailable
		} finally {
			loading = false;
			step = 'reflection';
		}
	}

	async function handleSaveReflection() {
		loading = true;
		let messagesPayload: Array<{ role: string; content: string }> = [];
		let emotionArcPayload: string[] = [];

		try {
			const db = await getDB();
			const sessionData = await db.get('sessions', sessionId);
			if (sessionData) {
				if (sessionData.messages && Array.isArray(sessionData.messages)) {
					messagesPayload = sessionData.messages.map((m: any) => ({
						role: m.sender === 'user' ? 'user' : 'assistant',
						content: m.content
					}));
				}
				if (sessionData.emotion_arc && Array.isArray(sessionData.emotion_arc)) {
					emotionArcPayload = sessionData.emotion_arc;
				}
			}
		} catch (err) {
			// Fail-soft
		}

		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/report/generate`, {
				method: 'POST',
				headers,
				body: JSON.stringify({
					session_id: sessionId,
					messages: messagesPayload,
					emotion_arc: emotionArcPayload,
					topic,
					final_severity: finalSeverity
				})
			});

			if (res.ok) {
				const reportData = await res.json();
				const db = await getDB();
				await db.put('reports', reportData);
			}
		} catch (err) {
			// Generate fallback reflection if offline
			const db = await getDB();
			await db.put('reports', {
				session_id: sessionId,
				topic,
				final_severity: finalSeverity,
				emotional_journey_summary: 'You navigated through this session with courage and vulnerability.',
				key_takeaways: [
					'Acknowledged current emotional state without judgment',
					'Practiced steady breathing and mindful grounding'
				],
				recommended_practices: ['5-4-3-2-1 Sensory Grounding', 'Evening reflective check-in'],
				created_at: new Date().toISOString()
			});
		} finally {
			loading = false;
			goto('/report');
		}
	}

	function handleNoReflection() {
		goto('/complete');
	}

	onMount(() => {
		sessionId = sessionStorage.getItem('karen_session_id') || '';
		topic = sessionStorage.getItem('karen_session_topic') || 'General Reflection';
		finalSeverity = sessionStorage.getItem('karen_session_severity') || 'Mild';
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col items-center justify-between bg-[#0d0d1a] px-6 py-12 text-white select-none overflow-hidden"
>
	<!-- Ambient Outer Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-80 w-80 rounded-full bg-purple-950/20 blur-[100px]"></div>
	</div>

	<!-- Top Space Header -->
	<header class="z-10 pt-4 flex flex-col items-center">
		<div class="relative flex items-center justify-center">
			<div class="orb-end"></div>
		</div>
	</header>

	<!-- Main Content Area with Smooth Step Transition -->
	<main class="z-10 my-auto w-full max-w-[390px] text-center px-4">
		{#if step === 'confirm'}
			<!-- Step 1: Confirmation -->
			<div class="space-y-8 transition-opacity duration-400">
				<div class="space-y-3">
					<h1 class="font-serif text-2xl font-extralight leading-relaxed text-purple-50 sm:text-3xl">
						I'm glad you told me how you were feeling.
					</h1>
					<p class="text-sm font-light text-purple-200/60 leading-relaxed pt-2">
						Would you like to leave this conversation here for now?
					</p>
				</div>

				<div class="flex flex-col items-center space-y-5 pt-4">
					<!-- Option 2: "End for now" (Pill Button) -->
					<button
						type="button"
						onclick={handleEndForNow}
						disabled={loading}
						class="w-full group relative inline-flex items-center justify-center rounded-full bg-purple-950/40 px-8 py-3.5 text-sm font-medium tracking-wider text-purple-100/90 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/40 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] active:scale-95 disabled:opacity-50"
					>
						{#if loading}
							<span class="animate-pulse">Concluding...</span>
						{:else}
							<span>End for now</span>
						{/if}
					</button>

					<!-- Option 1: "Stay a little longer" (Quiet text link) -->
					<button
						type="button"
						onclick={handleStayLonger}
						disabled={loading}
						class="text-xs font-light text-purple-300/50 hover:text-purple-200 py-1 transition-colors focus:outline-none"
					>
						Stay a little longer
					</button>
				</div>
			</div>
		{:else}
			<!-- Step 2: Reflection Request -->
			<div class="space-y-8 transition-opacity duration-400">
				<div class="space-y-3">
					<h2 class="font-serif text-2xl font-extralight leading-relaxed text-purple-50 sm:text-3xl">
						Would you like a reflection of this conversation?
					</h2>
					<p class="text-xs font-light text-purple-200/50 leading-relaxed pt-1">
						A gentle summary of your emotional journey and helpful insights.
					</p>
				</div>

				<div class="flex flex-col items-center space-y-4 pt-4">
					<!-- "Save reflection" -->
					<button
						type="button"
						onclick={handleSaveReflection}
						disabled={loading}
						class="w-full group relative inline-flex items-center justify-center rounded-full bg-purple-950/40 px-8 py-3.5 text-sm font-medium tracking-wider text-purple-100/90 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/40 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] active:scale-95 disabled:opacity-50"
					>
						{#if loading}
							<span class="animate-pulse">Preparing reflection...</span>
						{:else}
							<span>Save reflection</span>
						{/if}
					</button>

					<!-- "No, thank you" -->
					<button
						type="button"
						onclick={handleNoReflection}
						disabled={loading}
						class="text-xs font-light text-purple-300/50 hover:text-purple-200 py-2 transition-colors focus:outline-none"
					>
						No, thank you
					</button>
				</div>
			</div>
		{/if}
	</main>

	<!-- Footer Note -->
	<footer class="z-10 text-center text-xs font-light tracking-wide text-purple-200/30">
		Take all the time you need.
	</footer>
</div>

<style>
	.orb-end {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(180, 160, 255, 0.3);
		box-shadow:
			0 0 30px rgba(140, 100, 255, 0.2),
			0 0 60px rgba(140, 100, 255, 0.05);
		animation: breathe 4s ease-in-out infinite;
	}

	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
			opacity: 0.5;
		}
		50% {
			transform: scale(1.08);
			opacity: 0.8;
		}
	}
</style>
