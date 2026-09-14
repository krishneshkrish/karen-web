<script lang="ts">
	import { appState } from '$lib/state.svelte';
	import { api, setStoredToken } from '$lib/api';
	import Orb from '$lib/components/Orb.svelte';
	import { Mail, Lock, ArrowRight, ShieldCheck } from 'lucide-svelte';

	let mode = $state<'login' | 'register'>('register');
	let email = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		if (!email || !password) {
			error = 'Please fill in both email and password.';
			return;
		}

		loading = true;
		try {
			let res;
			if (mode === 'register') {
				res = await api.register(email, password);
			} else {
				res = await api.login(email, password);
			}

			if (res.access_token) {
				setStoredToken(res.access_token);
				appState.userEmail = email;
				appState.setScreen('space-transition');
			}
		} catch (err: any) {
			error = err.message || 'An error occurred during authentication.';
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex flex-col items-center justify-between min-h-[85vh] p-6 screen-fade-drift max-w-sm mx-auto">
	<div class="pt-4 flex flex-col items-center">
		<Orb size="md" interactive={false} />
		<h2 class="text-xl font-light text-white mt-4">Welcome to Karen</h2>
		<p class="text-xs text-gray-400 mt-1">A quiet, personal space created for you</p>
	</div>

	<!-- Auth Form -->
	<div class="w-full glass-card rounded-3xl p-6 border border-white/10 shadow-2xl space-y-5 my-auto">
		<!-- Mode Toggle -->
		<div class="flex p-1 rounded-xl bg-black/40 border border-white/5">
			<button
				type="button"
				onclick={() => { mode = 'register'; error = null; }}
				class="flex-1 py-2 text-xs font-medium rounded-lg transition-all {mode === 'register' ? 'bg-purple-600/50 text-white shadow' : 'text-gray-400 hover:text-gray-200'}"
			>
				Create Space
			</button>
			<button
				type="button"
				onclick={() => { mode = 'login'; error = null; }}
				class="flex-1 py-2 text-xs font-medium rounded-lg transition-all {mode === 'login' ? 'bg-purple-600/50 text-white shadow' : 'text-gray-400 hover:text-gray-200'}"
			>
				Sign In
			</button>
		</div>

		{#if error}
			<div class="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300 text-center">
				{error}
			</div>
		{/if}

		<form onsubmit={handleSubmit} class="space-y-4">
			<div>
				<label for="auth-email" class="block text-xs text-gray-400 mb-1 pl-1">Email Address</label>
				<div class="relative">
					<Mail size={16} class="absolute left-3.5 top-3.5 text-gray-400" />
					<input
						id="auth-email"
						type="email"
						bind:value={email}
						placeholder="you@example.com"
						required
						class="w-full pl-10 pr-4 py-3 rounded-xl glass-input text-sm text-white placeholder-gray-500 focus:outline-none"
					/>
				</div>
			</div>

			<div>
				<label for="auth-password" class="block text-xs text-gray-400 mb-1 pl-1">Password</label>
				<div class="relative">
					<Lock size={16} class="absolute left-3.5 top-3.5 text-gray-400" />
					<input
						id="auth-password"
						type="password"
						bind:value={password}
						placeholder="••••••••"
						required
						class="w-full pl-10 pr-4 py-3 rounded-xl glass-input text-sm text-white placeholder-gray-500 focus:outline-none"
					/>
				</div>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-purple-600/70 to-indigo-600/70 hover:from-purple-600 hover:to-indigo-600 text-white text-sm font-medium transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
			>
				{#if loading}
					<span class="animate-pulse">Connecting...</span>
				{:else}
					<span>{mode === 'register' ? 'Create My Space' : 'Enter My Space'}</span>
					<ArrowRight size={16} />
				{/if}
			</button>
		</form>
	</div>

	<div class="pb-4 flex items-center justify-center gap-2 text-xs text-gray-500">
		<ShieldCheck size={14} class="text-teal-400" />
		<span>Zero cookies used • JWT stored locally</span>
	</div>
</div>
