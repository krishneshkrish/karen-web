<script lang="ts">
	import { appState } from '$lib/state.svelte';
	import { api } from '$lib/api';
	import Orb from '$lib/components/Orb.svelte';
	import { Heart, Sparkles } from 'lucide-svelte';

	let loading = $state(false);

	async function handleLeave() {
		loading = true;
		try {
			if (appState.currentSessionId) {
				await api.endSession(appState.currentSessionId);
			}
		} catch (e) {
			console.warn('End session call error', e);
		} finally {
			loading = false;
			appState.setScreen('session-complete');
		}
	}
</script>

<div class="flex flex-col items-center justify-center min-h-[85vh] p-6 text-center screen-fade-drift max-w-sm mx-auto">
	<div class="glass-card rounded-3xl p-8 border border-white/10 shadow-2xl space-y-6 w-full">
		<Orb size="md" interactive={false} />

		<div class="space-y-2">
			<h2 class="text-xl font-light text-white leading-snug">
				Would you like to leave this conversation?
			</h2>
			<p class="text-xs text-gray-400 leading-relaxed">
				Your space will be preserved safely in your local device storage.
			</p>
		</div>

		<div class="space-y-3 pt-2">
			<button
				type="button"
				disabled={loading}
				onclick={handleLeave}
				class="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-purple-600/70 to-indigo-600/70 hover:from-purple-600 hover:to-indigo-600 text-white text-sm font-medium transition-all shadow-md flex items-center justify-center gap-2"
			>
				<Heart size={16} class="text-purple-200 fill-purple-200/40" />
				<span>{loading ? 'Closing space...' : 'Yes, finish for now'}</span>
			</button>

			<button
				type="button"
				onclick={() => appState.setScreen('chat')}
				class="w-full py-3 px-4 rounded-xl bg-white/5 hover:bg-white/10 text-xs text-gray-300 font-medium transition-colors"
			>
				Stay in conversation
			</button>
		</div>
	</div>
</div>
