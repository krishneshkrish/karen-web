<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { openDB } from 'idb';

	let mounted = $state(false);
	let timeSubtext = $state('');
	let hasSavedReflection = $state(false);

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

	function setTimeSubtext() {
		const hour = new Date().getHours();
		if (hour >= 5 && hour < 12) {
			timeSubtext = "That's a good way to start the day.";
		} else if (hour >= 12 && hour < 17) {
			timeSubtext = 'That took courage.';
		} else {
			timeSubtext = "That's enough for tonight.";
		}
	}

	async function checkReflectionStatus(sid: string) {
		if (!sid) return;
		try {
			const db = await getDB();
			const report = await db.get('reports', sid);
			if (report) {
				hasSavedReflection = true;
			}
		} catch (err) {
			// Fail soft
		}
	}

	function handleStartAgain() {
		sessionStorage.removeItem('karen_session_id');
		sessionStorage.removeItem('karen_session_topic');
		sessionStorage.removeItem('karen_session_severity');
		goto('/chat');
	}

	function handleGoToReport() {
		goto('/report');
	}

	onMount(() => {
		setTimeSubtext();
		const sid = sessionStorage.getItem('karen_session_id');
		if (sid) {
			sessionStorage.setItem('karen_last_session_id', sid);
			checkReflectionStatus(sid);
		}

		requestAnimationFrame(() => {
			mounted = true;
		});
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col items-center justify-between bg-[#0d0d1a] px-6 py-8 text-white transition-opacity duration-1000 select-none overflow-hidden"
	class:opacity-0={!mounted}
	class:opacity-100={mounted}
>
	<!-- Ambient Warm Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-96 w-96 rounded-full bg-amber-900/10 blur-[120px]"></div>
	</div>

	<!-- Top Blank Spacer -->
	<div class="h-8 z-10"></div>

	<!-- Center Content Block -->
	<main class="z-10 flex flex-col items-center text-center max-w-[390px] w-full my-auto">
		<!-- Warmer 100px Orb -->
		<div
			class="relative mb-10 flex items-center justify-center transition-all duration-1000 delay-300"
			class:scale-95={!mounted}
			class:opacity-0={!mounted}
			class:scale-100={mounted}
			class:opacity-100={mounted}
		>
			<div class="orb-complete-warmer"></div>
		</div>

		<!-- Staggered Text Sequence -->
		<div class="space-y-4">
			<!-- Large: "You made space for yourself." -->
			<h1
				class="font-serif text-3xl font-extralight tracking-wide text-purple-50 transition-all duration-1000 delay-500 sm:text-4xl"
				class:translate-y-3={!mounted}
				class:opacity-0={!mounted}
				class:translate-y-0={mounted}
				class:opacity-100={mounted}
			>
				You made space for yourself.
			</h1>

			<!-- Small: Time-based subtext -->
			<p
				class="text-sm font-light tracking-wide text-purple-200/70 transition-all duration-1000 delay-700 sm:text-base"
				class:translate-y-3={!mounted}
				class:opacity-0={!mounted}
				class:translate-y-0={mounted}
				class:opacity-100={mounted}
			>
				{timeSubtext}
			</p>

			<!-- Muted: Saved reflection note -->
			{#if hasSavedReflection}
				<p
					class="text-xs font-light text-purple-300/40 transition-all duration-1000 delay-1000 pt-2"
					class:opacity-0={!mounted}
					class:opacity-100={mounted}
				>
					Your reflection has been saved to your device.
				</p>
			{/if}
		</div>

		<!-- Subtle Action Buttons -->
		<div
			class="mt-10 flex flex-col items-center space-y-3 transition-all duration-1000 delay-1000 w-full"
			class:translate-y-3={!mounted}
			class:opacity-0={!mounted}
			class:translate-y-0={mounted}
			class:opacity-100={mounted}
		>
			{#if hasSavedReflection}
				<button
					type="button"
					onclick={handleGoToReport}
					class="w-full max-w-xs group relative inline-flex items-center justify-center rounded-full bg-purple-950/40 px-6 py-3 text-xs font-medium tracking-wider text-purple-100/90 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/40 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_20px_rgba(168,85,247,0.25)] active:scale-95"
				>
					View reflection
				</button>
			{/if}

			<button
				type="button"
				onclick={handleStartAgain}
				class="text-xs font-light text-purple-300/50 hover:text-purple-200 py-1.5 transition-colors focus:outline-none"
			>
				Start again
			</button>
		</div>
	</main>

	<!-- Bottom Navigation Bar (Appears for the first time) -->
	<footer
		class="z-20 w-full max-w-[390px] backdrop-blur-md bg-white/[0.03] border border-white/[0.08] rounded-full py-3 px-8 flex items-center justify-between transition-all duration-1000 delay-1000"
		class:opacity-0={!mounted}
		class:opacity-100={mounted}
	>
		<!-- Chat Icon (New session) -->
		<button
			type="button"
			onclick={handleStartAgain}
			class="flex flex-col items-center space-y-1 text-purple-300/60 hover:text-purple-100 transition-colors"
			aria-label="New chat session"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-5 w-5"
			>
				<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
			</svg>
			<span class="text-[10px] font-light tracking-wider">Chat</span>
		</button>

		<!-- Sessions Icon (Past Sessions / History) -->
		<button
			type="button"
			onclick={() => goto('/history')}
			class="flex flex-col items-center space-y-1 text-purple-300/60 hover:text-purple-100 transition-colors"
			aria-label="Past sessions history"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-5 w-5"
			>
				<circle cx="12" cy="12" r="10" />
				<polyline points="12 6 12 12 16 14" />
			</svg>
			<span class="text-[10px] font-light tracking-wider">History</span>
		</button>

		<!-- Space Icon (Enter Space) -->
		<button
			type="button"
			onclick={() => goto('/enter')}
			class="flex flex-col items-center space-y-1 text-purple-300/60 hover:text-purple-100 transition-colors"
			aria-label="Enter Space transition"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="1.5"
				stroke-linecap="round"
				stroke-linejoin="round"
				class="h-5 w-5"
			>
				<circle cx="12" cy="12" r="9" />
				<path d="M12 3a9 9 0 0 0 0 18" />
			</svg>
			<span class="text-[10px] font-light tracking-wider">Space</span>
		</button>
	</footer>
</div>

<style>
	.orb-complete-warmer {
		width: 100px;
		height: 100px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(220, 180, 240, 0.45);
		box-shadow:
			0 0 40px rgba(160, 110, 255, 0.35),
			0 0 70px rgba(255, 180, 80, 0.15);
		animation: breathe 4s ease-in-out infinite;
	}

	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
			opacity: 0.65;
		}
		50% {
			transform: scale(1.08);
			opacity: 1;
		}
	}
</style>
