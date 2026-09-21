<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { openDB } from 'idb';

	let step = $state<0 | 1 | 2 | 3 | 4>(0);

	async function initSessionAndDB() {
		const sessionId = crypto.randomUUID();
		sessionStorage.setItem('karen_session_id', sessionId);

		try {
			const db = await openDB('karen-db', 2, {
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

			await db.put('sessions', {
				session_id: sessionId,
				started_at: Date.now(),
				messages: [],
				emotion_arc: []
			});
		} catch (err) {
			// Fail-soft fallback if IndexedDB is blocked in constrained context
		}
	}

	onMount(() => {
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		if (!token) {
			goto('/auth');
			return;
		}

		// Initialize session and DB in parallel
		initSessionAndDB();

		// Animation Timings:
		requestAnimationFrame(() => {
			step = 1; // Screen fade in
		});

		const t1 = setTimeout(() => {
			step = 2;
		}, 400);

		const t2 = setTimeout(() => {
			step = 3;
		}, 900);

		const t3 = setTimeout(() => {
			step = 4;
		}, 1500);

		const t4 = setTimeout(() => {
			step = 0; // Fade to black
			setTimeout(() => {
				goto('/chat');
			}, 500);
		}, 2800);

		return () => {
			clearTimeout(t1);
			clearTimeout(t2);
			clearTimeout(t3);
			clearTimeout(t4);
		};
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col items-center justify-center bg-[#0d0d1a] px-6 text-white transition-opacity duration-500 select-none overflow-hidden"
	class:opacity-0={step === 0}
	class:opacity-100={step >= 1}
>
	<!-- Ambient Outer Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-[30rem] w-[30rem] rounded-full bg-purple-900/15 blur-[120px]"></div>
	</div>

	<!-- Center Content Container -->
	<div class="z-10 flex flex-col items-center text-center max-w-[390px] w-full">
		<!-- Larger 160px Brighter Orb -->
		<div
			class="relative mb-12 flex items-center justify-center transition-all duration-700 ease-out"
			class:opacity-0={step < 2}
			class:scale-90={step < 2}
			class:opacity-100={step >= 2}
			class:scale-100={step >= 2}
		>
			<div class="orb-large-bright"></div>
		</div>

		<!-- Centered Text Block -->
		<div class="flex flex-col items-center space-y-3">
			<h1
				class="font-serif text-3xl font-extralight tracking-wide text-purple-50 transition-all duration-700 ease-out sm:text-4xl"
				class:opacity-0={step < 3}
				class:translate-y-2.5={step < 3}
				class:opacity-100={step >= 3}
				class:translate-y-0={step >= 3}
			>
				I'm here with you.
			</h1>

			<p
				class="text-xs font-light tracking-wider text-purple-200/60 transition-all duration-700 ease-out sm:text-sm"
				class:opacity-0={step < 4}
				class:opacity-100={step >= 4}
			>
				You don't have to explain everything at once.
			</p>
		</div>
	</div>
</div>

<style>
	.orb-large-bright {
		width: 160px;
		height: 160px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(200, 180, 255, 0.6);
		box-shadow:
			0 0 50px rgba(160, 120, 255, 0.45),
			0 0 100px rgba(160, 120, 255, 0.2);
		animation: breathe 4s ease-in-out infinite;
	}

	@keyframes breathe {
		0%,
		100% {
			transform: scale(1);
			opacity: 0.75;
		}
		50% {
			transform: scale(1.08);
			opacity: 1;
		}
	}
</style>
