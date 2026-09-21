<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let mounted = $state(false);
	let timeGreeting = $state('');
	let isLoggedIn = $state(false);

	function updateGreeting() {
		const hour = new Date().getHours();
		if (hour >= 0 && hour < 6) {
			timeGreeting = 'Quiet • Still • Deep';
		} else if (hour >= 6 && hour < 12) {
			timeGreeting = 'Gentle • Present • Yours';
		} else if (hour >= 12 && hour < 18) {
			timeGreeting = 'Warm • Calm • Grounded';
		} else {
			timeGreeting = 'Easy • Unhurried • Safe';
		}
	}

	onMount(() => {
		updateGreeting();
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		isLoggedIn = !!token;
		// Trigger staggered fade-in animations after mount
		requestAnimationFrame(() => {
			mounted = true;
		});
	});

	function handleBegin() {
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		if (token) {
			goto('/enter');
		} else {
			goto('/auth');
		}
	}
</script>

<div
	class="relative flex min-h-screen w-full flex-col items-center justify-between bg-[#0d0d1a] px-6 py-10 text-white transition-opacity duration-1000 select-none overflow-hidden"
	class:opacity-0={!mounted}
	class:opacity-100={mounted}
>
	<!-- Ambient Background Glows -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-96 w-96 rounded-full bg-purple-900/10 blur-[100px]"></div>
	</div>

	<!-- Top Ambient Time-based Greeting & Auth State -->
	<header
		class="z-10 w-full flex items-center justify-between px-2 text-xs tracking-[0.25em] text-purple-200/60 uppercase transition-all duration-1000 delay-300"
		class:translate-y-2={!mounted}
		class:opacity-0={!mounted}
		class:translate-y-0={mounted}
		class:opacity-100={mounted}
	>
		<span class="w-16"></span>
		<span class="text-center">{timeGreeting}</span>
		<div class="w-16 flex justify-end">
			{#if isLoggedIn}
				<button
					type="button"
					onclick={() => goto('/enter')}
					class="text-[11px] lowercase tracking-wider text-purple-300/70 hover:text-white transition-colors cursor-pointer"
				>
					enter
				</button>
			{:else}
				<button
					type="button"
					onclick={() => goto('/auth')}
					class="text-[11px] lowercase tracking-wider text-purple-300/70 hover:text-white transition-colors cursor-pointer"
				>
					sign in
				</button>
			{/if}
		</div>
	</header>

	<!-- Center Content Area -->
	<main class="z-10 flex flex-col items-center justify-center text-center">
		<!-- Animated Breathing Orb -->
		<div
			class="relative mb-10 flex items-center justify-center transition-all duration-1000 delay-500"
			class:scale-95={!mounted}
			class:opacity-0={!mounted}
			class:scale-100={mounted}
			class:opacity-100={mounted}
		>
			<div class="orb-breathing"></div>
		</div>

		<!-- Title & Subtitles -->
		<div
			class="flex flex-col items-center space-y-3 transition-all duration-1000 delay-700"
			class:translate-y-4={!mounted}
			class:opacity-0={!mounted}
			class:translate-y-0={mounted}
			class:opacity-100={mounted}
		>
			<h1 class="font-serif text-5xl font-extralight tracking-wide text-purple-50/90 sm:text-6xl">
				Karen
			</h1>

			<p class="text-base font-light tracking-wide text-purple-200/75 sm:text-lg">
				A quiet place to talk.
			</p>

			<p class="max-w-xs text-xs font-light tracking-wider text-purple-200/60 sm:max-w-sm sm:text-sm">
				You don't have to explain everything at once.
			</p>
		</div>

		<!-- CTA Button -->
		<div
			class="mt-12 transition-all duration-1000 delay-1000"
			class:translate-y-4={!mounted}
			class:opacity-0={!mounted}
			class:translate-y-0={mounted}
			class:opacity-100={mounted}
		>
			<button
				onclick={handleBegin}
				class="group relative inline-flex items-center justify-center rounded-full bg-purple-950/40 px-8 py-3.5 text-sm font-medium tracking-wider text-purple-100/90 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/40 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] active:scale-95 cursor-pointer"
			>
				{isLoggedIn ? 'Continue when ready' : 'Begin when ready'}
			</button>
		</div>
	</main>

	<!-- Bottom Privacy Note -->
	<footer
		class="z-10 flex items-center justify-center space-x-2 text-xs tracking-wide text-purple-200/50 transition-all duration-1000 delay-1000"
		class:opacity-0={!mounted}
		class:opacity-100={mounted}
	>
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
		<span>Your conversations stay private on this device.</span>
	</footer>
</div>

<style>
	.orb-breathing {
		width: 120px;
		height: 120px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(180, 160, 255, 0.4);
		box-shadow:
			0 0 40px rgba(140, 100, 255, 0.3),
			0 0 80px rgba(140, 100, 255, 0.1);
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
