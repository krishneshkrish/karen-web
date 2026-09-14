<script lang="ts">
	import { onMount } from 'svelte';
	import { appState } from '$lib/state.svelte';
	import Orb from '$lib/components/Orb.svelte';

	onMount(() => {
		const timer = setTimeout(() => {
			appState.startNewSession();
			appState.setScreen('chat');
		}, 3200);

		return () => clearTimeout(timer);
	});
</script>

<div class="flex flex-col items-center justify-center min-h-[85vh] p-6 text-center screen-fade-drift max-w-sm mx-auto">
	<div class="space-y-8 flex flex-col items-center">
		<Orb size="lg" interactive={false} />

		<div class="space-y-3">
			<h2 class="text-2xl font-light text-white tracking-wide transition-opacity duration-1000">
				I'm here with you.
			</h2>
			<p class="text-xs text-purple-300/70 font-medium tracking-wider uppercase">
				Preparing your calm space
			</p>
		</div>

		<div class="w-32 h-1 bg-white/10 rounded-full overflow-hidden">
			<div class="h-full bg-gradient-to-r from-purple-500 to-teal-400 animate-pulse rounded-full w-full"></div>
		</div>
	</div>
</div>
