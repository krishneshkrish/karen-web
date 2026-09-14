<script lang="ts">
	import { appState } from '$lib/state.svelte';
	import Orb from '$lib/components/Orb.svelte';
	import { FileText, Sparkles, PlusCircle } from 'lucide-svelte';
</script>

<div class="flex flex-col items-center justify-between min-h-[85vh] p-6 text-center screen-fade-drift max-w-sm mx-auto">
	<div class="pt-8">
		<Orb size="lg" interactive={false} />
	</div>

	<div class="space-y-4 my-auto">
		<h2 class="text-2xl font-light text-white tracking-wide">
			"You made space for yourself."
		</h2>
		<p class="text-sm text-purple-200/70 max-w-[280px] leading-relaxed mx-auto">
			Taking time to listen to your inner thoughts is an act of deep kindness.
		</p>
	</div>

	<div class="w-full space-y-3 pb-6">
		<button
			type="button"
			onclick={() => {
				appState.selectedReportSessionId = appState.currentSessionId;
				appState.setScreen('report');
			}}
			class="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-purple-600/70 to-indigo-600/70 hover:from-purple-600 hover:to-indigo-600 text-white font-medium text-sm shadow-lg border border-purple-400/30 transition-all flex items-center justify-center gap-2"
		>
			<FileText size={18} />
			<span>View Session Insights & Report</span>
		</button>

		<button
			type="button"
			onclick={() => {
				appState.startNewSession();
				appState.setScreen('space-transition');
			}}
			class="w-full py-3 px-6 rounded-2xl bg-white/5 hover:bg-white/10 text-gray-300 font-medium text-xs border border-white/10 transition-colors flex items-center justify-center gap-2"
		>
			<PlusCircle size={16} />
			<span>Start a New Session</span>
		</button>
	</div>
</div>
