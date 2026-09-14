<script lang="ts">
	import { appState } from '$lib/state.svelte';
	
	let { size = 'md', interactive = true, class: className = '' } = $props<{
		size?: 'sm' | 'md' | 'lg' | 'xl';
		interactive?: boolean;
		class?: string;
	}>();

	const sizeClasses = {
		sm: 'w-10 h-10',
		md: 'w-20 h-20',
		lg: 'w-32 h-32',
		xl: 'w-44 h-44'
	};

	const orbEmotionClass = $derived(`orb-${appState.currentEmotion}`);
</script>

<div class="relative flex items-center justify-center p-2 {className}">
	<!-- Ambient outer pulse ring -->
	<div
		class="absolute rounded-full pointer-events-none transition-all duration-[4000ms] ease-in-out opacity-40 animate-breathe
		{size === 'sm' ? 'w-14 h-14' : size === 'md' ? 'w-28 h-28' : size === 'lg' ? 'w-48 h-48' : 'w-64 h-64'}
		{appState.currentEmotion === 'anxiety' ? 'bg-amber-500/30' : appState.currentEmotion === 'sadness' ? 'bg-blue-500/30' : appState.currentEmotion === 'calm' ? 'bg-teal-500/30' : 'bg-purple-500/30'}"
	></div>

	<!-- Main Breathing Orb -->
	<button
		type="button"
		aria-label="Karen glowing identity orb"
		disabled={!interactive}
		onclick={() => {
			if (interactive) appState.toggleDrawer(true);
		}}
		class="karen-orb {sizeClasses[size]} {orbEmotionClass} animate-breathe transition-all duration-[4000ms] ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-400/50 rounded-full flex items-center justify-center cursor-pointer active:scale-95"
	>
		<!-- Subtle inner core shimmer -->
		<div class="w-1/3 h-1/3 rounded-full bg-white/40 blur-md animate-pulse"></div>
	</button>
</div>
