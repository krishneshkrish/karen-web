<script lang="ts">
	import { appState } from '$lib/state.svelte';
	import Orb from '$lib/components/Orb.svelte';
	import { Shield, Sparkles, Heart } from 'lucide-svelte';
</script>

<div class="flex flex-col items-center justify-between min-h-[85vh] p-6 text-center screen-fade-drift max-w-sm mx-auto">
	<!-- Top Spacer -->
	<div class="pt-8">
		<div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-medium mb-2">
			<Sparkles size={14} />
			<span>{appState.greetingTagline}</span>
		</div>
	</div>

	<!-- Center Core Hero: Orb & Name -->
	<div class="flex flex-col items-center space-y-6">
		<Orb size="xl" interactive={false} />

		<div class="space-y-2">
			<h1 class="text-3xl font-light tracking-wide text-white font-sans">Karen</h1>
			<p class="text-sm text-gray-400 max-w-[260px] leading-relaxed">
				A quiet, empathetic refuge for your thoughts and feelings.
			</p>
		</div>
	</div>

	<!-- Bottom Action & Privacy -->
	<div class="w-full space-y-6 pb-6">
		<button
			type="button"
			onclick={() => {
				if (!appState.userEmail) {
					appState.setScreen('auth');
				} else {
					appState.setScreen('space-transition');
				}
			}}
			class="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-purple-600/60 to-indigo-600/60 hover:from-purple-600/80 hover:to-indigo-600/80 text-white font-medium text-base shadow-lg shadow-purple-900/30 backdrop-blur-md border border-purple-400/30 transition-all duration-300 transform active:scale-98 flex items-center justify-center gap-2"
		>
			<span>Begin when ready</span>
			<Heart size={18} class="text-purple-200 fill-purple-200/40" />
		</button>

		<div class="flex items-center justify-center gap-2 text-xs text-gray-500">
			<Shield size={14} class="text-teal-400/80" />
			<span>Transcripts NEVER leave your device (IndexedDB only)</span>
		</div>
	</div>
</div>
