<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { openDB } from 'idb';
	import CrisisOverlay from '$lib/components/CrisisOverlay.svelte';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	interface Message {
		id: string;
		sender: 'user' | 'karen';
		content: string;
		timestamp: string;
		showTime?: boolean;
		escalate?: boolean;
	}

	let messages = $state<Message[]>([]);
	let loading = $state(false);
	let dominantEmotion = $state<string>('neutral');
	let sessionId = $state<string>('');
	let isFirstMessage = $state<boolean>(true);
	let inputText = $state<string>('');

	let isDrawerOpen = $state<boolean>(false);
	let isAboutOpen = $state<boolean>(false);
	let showCrisisOverlay = $state<boolean>(false);

	let messagesContainer: HTMLElement | null = $state(null);
	let textareaRef: HTMLTextAreaElement | null = $state(null);

	// Emotion backgrounds
	const emotionBackgrounds: Record<string, string> = {
		neutral: '#0d0d1a',
		sadness: 'linear-gradient(135deg, #0a1020 0%, #0d0d1a 100%)',
		fear: 'linear-gradient(135deg, #1a1008 0%, #0d0d1a 100%)',
		anger: 'linear-gradient(135deg, #1a0808 0%, #0d0d1a 100%)',
		joy: 'linear-gradient(135deg, #081a10 0%, #0d0d1a 100%)'
	};

	let bgStyle = $derived(
		emotionBackgrounds[dominantEmotion] || emotionBackgrounds.neutral
	);

	// IndexedDB helper
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

	async function loadSessionData(sid: string) {
		try {
			const db = await getDB();
			const session = await db.get('sessions', sid);
			if (session) {
				if (session.messages && Array.isArray(session.messages)) {
					messages = session.messages;
					if (messages.length > 0) {
						isFirstMessage = false;
					}
				}
				if (session.emotion_arc && session.emotion_arc.length > 0) {
					dominantEmotion = session.emotion_arc[session.emotion_arc.length - 1];
				}
			}
		} catch (err) {
			// Fail-soft if storage unavailable
		}
	}

	async function saveSessionToDB(updatedMessages: Message[], emotion: string) {
		if (!sessionId) return;
		try {
			const db = await getDB();
			const existing = (await db.get('sessions', sessionId)) || {
				session_id: sessionId,
				started_at: Date.now(),
				messages: [],
				emotion_arc: []
			};

			const emotionArc = existing.emotion_arc || [];
			if (emotion && emotion !== 'neutral') {
				emotionArc.push(emotion);
			}

			await db.put('sessions', {
				...existing,
				messages: updatedMessages,
				emotion_arc: emotionArc
			});
		} catch (err) {
			// Storage save error ignored safely
		}
	}

	function scrollToBottom() {
		tick().then(() => {
			if (messagesContainer) {
				messagesContainer.scrollTop = messagesContainer.scrollHeight;
			}
		});
	}

	function adjustTextareaHeight() {
		if (textareaRef) {
			textareaRef.style.height = 'auto';
			const newHeight = Math.min(textareaRef.scrollHeight, 120);
			textareaRef.style.height = `${newHeight}px`;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}

	async function sendMessage() {
		const text = inputText.trim();
		if (!text || loading) return;

		const userMsg: Message = {
			id: crypto.randomUUID(),
			sender: 'user',
			content: text,
			timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
			showTime: false
		};

		messages = [...messages, userMsg];
		inputText = '';
		if (textareaRef) textareaRef.style.height = 'auto';
		loading = true;
		scrollToBottom();

		const lower = text.toLowerCase();
		if (
			lower.includes('suicide') ||
			lower.includes('end it all') ||
			lower.includes('kill myself') ||
			lower.includes('harm myself') ||
			lower.includes('hurt myself') ||
			lower.includes('harming myself') ||
			lower.includes('self-harm')
		) {
			showCrisisOverlay = true;
		}

		const payloadMessages = messages.slice(-10).map((m) => ({
			role: m.sender === 'user' ? 'user' : 'assistant',
			content: m.content
		}));

		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/chat/message`, {
				method: 'POST',
				headers,
				body: JSON.stringify({
					session_id: sessionId,
					messages: payloadMessages,
					is_first_message: isFirstMessage
				})
			});

			isFirstMessage = false;

			if (!res.ok) {
				throw new Error('API request failed');
			}

			const data = await res.json();
			const replyContent = data.reply || "I'm right here with you. Take your time.";
			const detectedEmotion = data.detected_emotion || data.ml_signals?.dominant_emotion || 'neutral';
			const isCrisis = data.crisis_flag || data.crisis === true;
			const isEscalate = data.escalate === true;

			const karenMsg: Message = {
				id: crypto.randomUUID(),
				sender: 'karen',
				content: replyContent,
				timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
				showTime: false,
				escalate: isEscalate
			};

			messages = [...messages, karenMsg];
			dominantEmotion = detectedEmotion;

			await saveSessionToDB(messages, detectedEmotion);

			if (isCrisis) {
				showCrisisOverlay = true;
			}
		} catch (err) {
			// Intelligent offline fallback response
			const karenMsg: Message = {
				id: crypto.randomUUID(),
				sender: 'karen',
				content: "I hear you, and I'm listening closely. Take a gentle breath with me.",
				timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
				showTime: false
			};
			messages = [...messages, karenMsg];
			isFirstMessage = false;
			await saveSessionToDB(messages, 'neutral');
		} finally {
			loading = false;
			scrollToBottom();
		}
	}

	function toggleTimestamp(id: string) {
		messages = messages.map((m) => (m.id === id ? { ...m, showTime: !m.showTime } : m));
	}

	onMount(() => {
		let sid = sessionStorage.getItem('karen_session_id');
		if (!sid) {
			sid = crypto.randomUUID();
			sessionStorage.setItem('karen_session_id', sid);
		}
		sessionId = sid;
		loadSessionData(sid);
	});
</script>

<!-- Screen Container with Smooth Emotion-Driven Background Transition -->
<div
	class="relative flex min-h-screen w-full flex-col justify-between text-white select-none overflow-hidden transition-all duration-[5000ms] ease-in-out"
	style="background: {bgStyle}"
>
	<!-- Top Bar -->
	<header
		class="sticky top-0 z-30 flex h-16 w-full items-center justify-between px-5 backdrop-blur-md bg-[#0d0d1a]/40 border-b border-white/5"
	>
		<!-- Left: 40px Orb Button (Opens Settings Drawer) -->
		<button
			type="button"
			onclick={() => (isDrawerOpen = true)}
			class="relative flex items-center justify-center p-1 focus:outline-none group active:scale-95 transition-transform"
			aria-label="Open settings menu"
		>
			<div class="orb-topbar"></div>
		</button>

		<!-- Center: Title -->
		<h1 class="font-serif text-lg font-light tracking-wide text-purple-100/90">Karen</h1>

		<div class="flex items-center gap-2">
			<!-- Emergency Crisis Support Button (TC002) -->
			<button
				type="button"
				onclick={() => (showCrisisOverlay = true)}
				aria-label="Emergency Crisis Support"
				class="px-2.5 py-1.5 rounded-full bg-rose-950/30 border border-rose-500/20 text-rose-300 hover:bg-rose-900/30 transition-all text-xs font-light flex items-center gap-1.5"
			>
				<span>Crisis Support</span>
			</button>

			<!-- Right: Circle Icon (Session End Trigger) -->
			<button
				type="button"
				onclick={() => goto('/end')}
				class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/60 hover:border-purple-300/50 hover:text-purple-100 hover:bg-purple-900/20 active:scale-95 transition-all"
				aria-label="End session"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					class="h-4 w-4"
				>
					<circle cx="12" cy="12" r="9" />
				</svg>
			</button>
		</div>
	</header>

	<!-- Messages Scroll Area -->
	<main
		bind:this={messagesContainer}
		class="z-10 flex-1 overflow-y-auto px-4 pt-6 pb-32 space-y-6 scrollbar-none"
	>
		{#if messages.length === 0 && !loading}
			<div class="mt-20 flex flex-col items-center justify-center text-center px-6">
				<p class="font-serif text-xl font-extralight text-purple-200/80">I'm right here with you.</p>
				<p class="mt-2 text-xs font-light text-purple-300/40">Say anything, or just begin whenever you're ready.</p>
			</div>
		{/if}

		{#each messages as msg (msg.id)}
			<div class="flex flex-col transition-all duration-300">
				{#if msg.sender === 'karen'}
					<!-- Karen Message (Left Aligned, Floating Text) -->
					<div
						class="group max-w-[85%] self-start pl-3 border-l-2 border-purple-300/20 py-1 transition-all"
					>
						<button
							type="button"
							onclick={() => toggleTimestamp(msg.id)}
							class="text-left font-light text-sm leading-[1.7] text-purple-50 focus:outline-none cursor-pointer"
						>
							{msg.content}
						</button>

						<!-- Escalation Note -->
						{#if msg.escalate}
							<div class="mt-2 text-xs font-light text-purple-300/70 italic">
								If things feel too heavy, remember it's okay to reach out to someone who can support you.
							</div>
						{/if}

						<!-- Timestamp on tap -->
						{#if msg.showTime}
							<div class="mt-1.5 text-[11px] font-light text-purple-200/45 transition-opacity">
								{msg.timestamp}
							</div>
						{/if}
					</div>
				{:else}
					<!-- User Message (Right Aligned Bubble) -->
					<div class="max-w-[75%] self-end">
						<button
							type="button"
							onclick={() => toggleTimestamp(msg.id)}
							class="rounded-2xl bg-[rgba(100,80,180,0.25)] px-4 py-3 text-sm font-light leading-relaxed text-purple-50 text-left focus:outline-none cursor-pointer"
						>
							{msg.content}
						</button>
						{#if msg.showTime}
							<div class="mt-1 text-right text-[11px] font-light text-purple-200/45 transition-opacity pr-1">
								{msg.timestamp}
							</div>
						{/if}
					</div>
				{/if}
			</div>
		{/each}

		<!-- Typing Indicator -->
		{#if loading}
			<div class="flex items-center space-x-1.5 self-start pl-3 py-2">
				<div class="h-2 w-2 rounded-full bg-purple-300/40 animate-pulse"></div>
				<div class="h-2 w-2 rounded-full bg-purple-300/40 animate-pulse delay-150"></div>
				<div class="h-2 w-2 rounded-full bg-purple-300/40 animate-pulse delay-300"></div>
			</div>
		{/if}
	</main>

	<!-- Fixed Input Bar -->
	<footer
		class="fixed bottom-0 left-0 right-0 z-30 flex items-end gap-3 px-4 py-3 border-t border-white/[0.08] bg-white/[0.05] backdrop-blur-[20px]"
	>
		<textarea
			bind:this={textareaRef}
			bind:value={inputText}
			oninput={adjustTextareaHeight}
			onkeydown={handleKeydown}
			placeholder="Type when you're ready..."
			rows="1"
			class="flex-1 resize-none bg-transparent py-2.5 text-sm font-light text-purple-50 placeholder-purple-200/40 focus:outline-none leading-relaxed max-h-32"
		></textarea>

		<button
			type="button"
			onclick={sendMessage}
			disabled={!inputText.trim() || loading}
			class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-950/40 ring-1 ring-purple-400/30 text-purple-200 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] active:scale-95 transition-all disabled:opacity-30 disabled:cursor-not-allowed mb-0.5"
			aria-label="Send message"
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
				<path d="M5 12h14" />
				<path d="m12 5 7 7-7 7" />
			</svg>
		</button>
	</footer>

	<!-- Settings Drawer (Slide from Left) -->
	{#if isDrawerOpen}
		<!-- Backdrop -->
		<div
			class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-300"
			onclick={() => (isDrawerOpen = false)}
			aria-hidden="true"
		></div>

		<!-- Drawer Panel -->
		<aside
			class="fixed top-0 left-0 bottom-0 z-50 w-72 max-w-[80vw] bg-[#0d0d1a] border-r border-white/10 p-6 flex flex-col justify-between shadow-2xl transition-transform duration-300"
		>
			<div class="space-y-6">
				<!-- Drawer Header -->
				<div class="flex items-center justify-between pb-4 border-b border-white/10">
					<div class="flex items-center gap-3">
						<div class="orb-topbar"></div>
						<span class="font-serif text-lg text-purple-100">Karen</span>
					</div>
					<button
						type="button"
						onclick={() => (isDrawerOpen = false)}
						class="text-purple-300/60 hover:text-white p-1"
						aria-label="Close menu"
					>
						✕
					</button>
				</div>

				<!-- Navigation Options -->
				<nav class="space-y-3">
					<button
						type="button"
						onclick={() => {
							isDrawerOpen = false;
							goto('/end');
						}}
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-purple-950/30 hover:bg-purple-900/40 text-sm font-light text-purple-100 transition-all text-left border border-purple-400/20"
					>
						<span>End session</span>
					</button>

					<button
						type="button"
						onclick={() => {
							isDrawerOpen = false;
							goto('/history');
						}}
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm font-light text-purple-200/80 transition-all text-left"
					>
						<span>Past sessions</span>
					</button>

					<button
						type="button"
						onclick={() => (isAboutOpen = true)}
						class="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 text-sm font-light text-purple-200/80 transition-all text-left"
					>
						<span>About Karen</span>
					</button>
				</nav>
			</div>

			<!-- Footer info in Drawer -->
			<div class="text-[11px] font-light text-purple-300/40 leading-relaxed border-t border-white/10 pt-4">
				Your space. Private & stored locally on this device.
			</div>
		</aside>
	{/if}

	<!-- About Karen Modal -->
	{#if isAboutOpen}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
		>
			<div class="w-full max-w-sm rounded-3xl bg-[#121226] p-6 border border-purple-500/20 text-purple-100 shadow-2xl">
				<h3 class="font-serif text-xl font-light text-purple-50 mb-3">About Karen</h3>
				<p class="text-xs font-light text-purple-200/70 leading-relaxed mb-4">
					Karen is a quiet, compassionate digital space designed for reflection, emotional grounding, and unhurried conversation.
				</p>
				<p class="text-xs font-light text-purple-200/50 leading-relaxed mb-6">
					Karen is an AI space created to listen without judgment. Karen is not a licensed therapist or medical professional and does not provide medical diagnoses or treatment.
				</p>
				<button
					type="button"
					onclick={() => (isAboutOpen = false)}
					class="w-full py-2.5 rounded-full bg-purple-950/60 ring-1 ring-purple-400/30 text-xs font-medium text-purple-100 hover:bg-purple-900/60 transition-all"
				>
					Close
				</button>
			</div>
		</div>
	{/if}

	<!-- Crisis Overlay Modal -->
	<CrisisOverlay visible={showCrisisOverlay} onDismiss={() => (showCrisisOverlay = false)} />
</div>

<style>
	.orb-topbar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(180, 160, 255, 0.4);
		box-shadow: 0 0 15px rgba(140, 100, 255, 0.25);
		animation: breathe 4s ease-in-out infinite;
	}

	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
			opacity: 0.6;
		}
		50% {
			transform: scale(1.08);
			opacity: 1;
		}
	}
</style>
