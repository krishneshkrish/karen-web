<script lang="ts">
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	let mode = $state<'login' | 'register'>('login');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');

	function switchTab(newMode: 'login' | 'register') {
		if (mode !== newMode) {
			mode = newMode;
			error = '';
		}
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = '';

		if (!email.trim() || !password) {
			error = 'Please enter both email and password.';
			return;
		}

		if (mode === 'register') {
			if (password !== confirmPassword) {
				error = 'Passwords do not match.';
				return;
			}
			if (password.length < 6) {
				error = 'Password should be at least 6 characters.';
				return;
			}
		}

		loading = true;

		const endpoint = mode === 'register' ? '/api/v1/auth/register' : '/api/v1/auth/login';

		try {
			const res = await fetch(`${PUBLIC_API_URL}${endpoint}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password })
			});

			const data = await res.json().catch(() => null);

			if (!res.ok) {
				if (res.status === 409) {
					error = 'An account with this email already exists.';
				} else if (res.status === 401) {
					error = 'Incorrect email or password.';
				} else {
					error = data?.message || data?.detail || 'Authentication failed. Please try again.';
				}
				loading = false;
				return;
			}

			const token = data?.access_token || data?.jwt || 'mock_jwt_token_' + Date.now();
			const userHash = data?.user_hash || data?.user?.id || 'usr_' + Math.random().toString(36).substring(2, 9);

			localStorage.setItem('karen_jwt_token', token);
			localStorage.setItem('karen_user_hash', userHash);

			goto('/enter');
		} catch (err) {
			// Soft network error fallback for offline/demo environment
			error = 'Unable to reach authentication server. Please check your connection.';
			loading = false;
		}
	}
</script>

<div
	class="relative flex min-h-screen w-full flex-col items-center justify-between bg-[#0d0d1a] px-6 py-10 text-white select-none overflow-hidden"
>
	<!-- Ambient Background Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-80 w-80 rounded-full bg-purple-950/20 blur-[100px]"></div>
	</div>

	<!-- Top Dimmed 60px Orb -->
	<header class="z-10 pt-4 flex flex-col items-center">
		<div class="relative flex items-center justify-center">
			<div class="orb-dimmed"></div>
		</div>
	</header>

	<!-- Auth Form Container -->
	<main class="z-10 my-auto w-full max-w-[390px] px-2">
		<!-- Tabs Header -->
		<div class="mb-8 flex justify-center space-x-8 border-b border-purple-500/10 pb-2">
			<button
				type="button"
				onclick={() => switchTab('login')}
				class="relative pb-2 text-sm font-medium tracking-wider transition-colors duration-300 ${mode === 'login' ? 'text-purple-100' : 'text-purple-300/40 hover:text-purple-200/70'}"
			>
				Sign in
				{#if mode === 'login'}
					<div class="absolute bottom-0 left-0 right-0 h-[2px] bg-purple-400/70 rounded-full"></div>
				{/if}
			</button>

			<button
				type="button"
				onclick={() => switchTab('register')}
				class="relative pb-2 text-sm font-medium tracking-wider transition-colors duration-300 ${mode === 'register' ? 'text-purple-100' : 'text-purple-300/40 hover:text-purple-200/70'}"
			>
				Create account
				{#if mode === 'register'}
					<div class="absolute bottom-0 left-0 right-0 h-[2px] bg-purple-400/70 rounded-full"></div>
				{/if}
			</button>
		</div>

		<!-- Form -->
		<form onsubmit={handleSubmit} class="space-y-6">
			<!-- Email Field -->
			<div class="space-y-1">
				<label for="email" class="block text-xs font-light tracking-wide text-purple-200/50">
					Email address
				</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					placeholder="your.name@example.com"
					required
					class="w-full bg-transparent border-b border-purple-300/20 py-2.5 text-sm text-purple-50 placeholder-purple-200/40 focus:border-purple-400/80 focus:outline-none transition-colors duration-300 font-light"
				/>
			</div>

			<!-- Password Field -->
			<div class="space-y-1">
				<label for="password" class="block text-xs font-light tracking-wide text-purple-200/50">
					Password
				</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					placeholder="••••••••"
					required
					class="w-full bg-transparent border-b border-purple-300/20 py-2.5 text-sm text-purple-50 placeholder-purple-200/40 focus:border-purple-400/80 focus:outline-none transition-colors duration-300 font-light"
				/>
			</div>

			<!-- Confirm Password (Register mode) -->
			{#if mode === 'register'}
				<div class="space-y-1 transition-all duration-300">
					<label for="confirmPassword" class="block text-xs font-light tracking-wide text-purple-200/50">
						Confirm password
					</label>
					<input
						id="confirmPassword"
						type="password"
						bind:value={confirmPassword}
						placeholder="••••••••"
						required
						class="w-full bg-transparent border-b border-purple-300/20 py-2.5 text-sm text-purple-50 placeholder-purple-200/40 focus:border-purple-400/80 focus:outline-none transition-colors duration-300 font-light"
					/>
				</div>
			{/if}

			<!-- Soft Error State -->
			{#if error}
				<div class="pt-1 text-xs text-rose-300/90 font-light tracking-wide text-center">
					{error}
				</div>
			{/if}

			<!-- Submit Button -->
			<div class="pt-4">
				<button
					type="submit"
					disabled={loading}
					class="w-full group relative inline-flex items-center justify-center rounded-full bg-purple-950/40 px-8 py-3.5 text-sm font-medium tracking-wider text-purple-100/90 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/40 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if loading}
						<span class="animate-pulse">Connecting...</span>
					{:else}
						<span>{mode === 'register' ? 'Create space' : 'Begin'}</span>
					{/if}
				</button>
			</div>
		</form>
	</main>

	<!-- Footer Note -->
	<footer class="z-10 pb-2 text-center text-xs font-light tracking-wide text-purple-200/40">
		Your conversations stay on this device.
	</footer>
</div>

<style>
	.orb-dimmed {
		width: 60px;
		height: 60px;
		border-radius: 50%;
		background: transparent;
		border: 1.5px solid rgba(180, 160, 255, 0.25);
		box-shadow:
			0 0 20px rgba(140, 100, 255, 0.15),
			0 0 40px rgba(140, 100, 255, 0.05);
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
			opacity: 0.75;
		}
	}
</style>
