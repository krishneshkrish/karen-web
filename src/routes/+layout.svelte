<script lang="ts">
	import '../app.css';
	import { appState } from '$lib/state.svelte';
	import Drawer from '$lib/components/Drawer.svelte';
	import CrisisOverlay from '$lib/components/CrisisOverlay.svelte';

	let { children } = $props();

	// Emotion ambient background class string mapping
	const ambientClass = $derived(`ambient-${appState.currentEmotion}`);
</script>

<div class="relative min-h-[100dvh] w-full overflow-hidden text-gray-100 flex flex-col justify-between">
	<!-- Imperceptible 4-6 second background emotion transition layer -->
	<div class="ambient-bg {ambientClass}"></div>

	<!-- Main Screen Router Container -->
	<main class="relative z-10 w-full min-h-[100dvh]">
		{@render children?.()}
	</main>

	<!-- Global Drawers & Modals -->
	<Drawer />
	<CrisisOverlay visible={appState.isCrisisOpen} onDismiss={() => appState.toggleCrisis(false)} />
</div>
