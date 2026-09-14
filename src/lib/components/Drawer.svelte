<script lang="ts">
	import { goto } from '$app/navigation';
	import { appState } from '$lib/state.svelte';
	import { X, History, Sparkles, LogOut, ShieldCheck, HeartHandshake } from 'lucide-svelte';
	import Orb from './Orb.svelte';
</script>

{#if appState.isDrawerOpen}
	<!-- Backdrop -->
	<div
		class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-300"
		onclick={() => appState.toggleDrawer(false)}
		aria-hidden="true"
	></div>

	<!-- Drawer -->
	<aside
		class="fixed top-0 left-0 bottom-0 z-50 w-72 max-w-[80vw] glass-card border-r border-white/10 p-6 flex flex-col justify-between shadow-2xl screen-fade-drift"
		aria-label="Navigation drawer"
	>
		<div>
			<div class="flex items-center justify-between mb-8">
				<div class="flex items-center gap-3">
					<Orb size="sm" interactive={false} />
					<div>
						<h2 class="font-semibold text-white tracking-wide">Karen</h2>
						<p class="text-xs text-purple-300/70">{appState.greetingTagline}</p>
					</div>
				</div>
				<button
					type="button"
					onclick={() => appState.toggleDrawer(false)}
					aria-label="Close menu drawer"
					class="p-2 rounded-full text-gray-400 hover:text-white hover:bg-white/10"
				>
					<X size={18} />
				</button>
			</div>

			<nav class="space-y-2">
				<button
					type="button"
					onclick={() => {
						appState.toggleDrawer(false);
						goto('/chat');
					}}
					class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl bg-white/5 hover:bg-white/10 text-sm text-white font-medium transition-all text-left"
				>
					<Sparkles size={18} class="text-purple-400" />
					<span>Active Space</span>
				</button>

				<button
					type="button"
					onclick={() => {
						appState.toggleDrawer(false);
						goto('/history');
					}}
					class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-white/10 text-sm text-gray-300 font-medium transition-all text-left"
				>
					<History size={18} class="text-blue-400" />
					<span>Past Sessions</span>
				</button>

				<button
					type="button"
					onclick={() => {
						appState.toggleDrawer(false);
						appState.toggleCrisis(true);
					}}
					class="w-full flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-amber-500/10 text-sm text-amber-300 font-medium transition-all text-left"
				>
					<HeartHandshake size={18} class="text-amber-400" />
					<span>Crisis Support</span>
				</button>
			</nav>
		</div>

		<div class="space-y-4 pt-6 border-t border-white/10">
			<div class="px-3 py-2 rounded-xl bg-white/5 text-[11px] text-gray-400 flex items-center gap-2">
				<ShieldCheck size={14} class="text-teal-400 shrink-0" />
				<span>Transcripts stored in local IndexedDB only.</span>
			</div>

			{#if appState.userEmail}
				<div class="text-xs text-gray-400 px-1 truncate">
					Logged in as: <span class="text-purple-300">{appState.userEmail}</span>
				</div>
				<button
					type="button"
					onclick={() => {
						appState.toggleDrawer(false);
						appState.logout();
						goto('/auth');
					}}
					class="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium transition-colors"
				>
					<LogOut size={14} />
					<span>Sign Out</span>
				</button>
			{:else}
				<button
					type="button"
					onclick={() => {
						appState.toggleDrawer(false);
						goto('/auth');
					}}
					class="w-full py-2.5 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-white text-xs font-medium transition-colors"
				>
					Sign In / Register
				</button>
			{/if}
		</div>
	</aside>
{/if}
