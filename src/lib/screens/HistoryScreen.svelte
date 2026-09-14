<script lang="ts">
	import { onMount } from 'svelte';
	import { appState } from '$lib/state.svelte';
	import { getLocalSessions, type SessionMeta } from '$lib/db';
	import { api } from '$lib/api';
	import Orb from '$lib/components/Orb.svelte';
	import { ArrowLeft, Calendar, MessageSquare, ChevronRight, Sparkles } from 'lucide-svelte';

	let sessions = $state<SessionMeta[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			// Local IndexedDB metadata session list
			sessions = await getLocalSessions();

			// Also attempt backend sync for session metadata if available
			const remoteSessions = await api.getHistorySessions();
			if (remoteSessions && remoteSessions.length > 0) {
				// Combine/merge metadata only
			}
		} catch (e) {
			console.warn('History fetch error', e);
		} finally {
			loading = false;
		}
	});

	function formatDate(iso: string) {
		const d = new Date(iso);
		return d.toLocaleDateString(undefined, {
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		});
	}
</script>

<div class="flex flex-col h-[100dvh] max-w-md mx-auto relative screen-fade-drift p-4">
	<!-- Top Bar -->
	<header class="flex items-center justify-between py-3 mb-4 border-b border-white/10 shrink-0">
		<button
			type="button"
			onclick={() => appState.setScreen('chat')}
			class="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition-colors flex items-center gap-1.5 text-xs font-medium"
		>
			<ArrowLeft size={16} />
			<span>Back to Space</span>
		</button>
		<h1 class="text-sm font-semibold text-white">Past Sessions</h1>
		<div class="w-8"></div>
	</header>

	<!-- Session List -->
	<div class="flex-1 overflow-y-auto space-y-3 pr-1">
		{#if loading}
			<div class="text-center py-12 text-sm text-gray-400">Loading your quiet spaces...</div>
		{:else if sessions.length === 0}
			<div class="text-center py-16 space-y-4 glass-card rounded-3xl p-8 border border-white/10">
				<Orb size="md" interactive={false} />
				<h2 class="text-base font-medium text-white">No sessions saved yet</h2>
				<p class="text-xs text-gray-400">Every conversation you start will be safely remembered here on your device.</p>
				<button
					type="button"
					onclick={() => {
						appState.startNewSession();
						appState.setScreen('space-transition');
					}}
					class="py-2.5 px-4 rounded-xl bg-purple-600/40 hover:bg-purple-600/60 text-white text-xs font-medium transition-colors inline-block"
				>
					Begin First Session
				</button>
			</div>
		{:else}
			{#each sessions as s (s.id)}
				<button
					type="button"
					onclick={() => {
						appState.selectedReportSessionId = s.id;
						appState.setScreen('report');
					}}
					class="w-full text-left glass-card rounded-2xl p-4 border border-white/10 hover:border-purple-400/40 hover:bg-white/10 transition-all flex items-center justify-between group"
				>
					<div class="space-y-1.5">
						<div class="flex items-center gap-2 text-xs text-purple-300 font-medium">
							<Calendar size={13} />
							<span>{formatDate(s.start_time)}</span>
						</div>
						<div class="text-sm font-semibold text-white">
							{s.topic || 'Emotional Grounding & Support'}
						</div>
						<div class="flex items-center gap-3 text-xs text-gray-400">
							<span class="flex items-center gap-1">
								<MessageSquare size={12} />
								{s.message_count || 0} messages
							</span>
							{#if s.dominant_emotion}
								<span class="px-2 py-0.5 rounded-full bg-white/10 text-[10px] uppercase tracking-wider text-teal-300">
									{s.dominant_emotion}
								</span>
							{/if}
						</div>
					</div>
					<ChevronRight size={18} class="text-gray-500 group-hover:text-purple-300 group-hover:translate-x-0.5 transition-all" />
				</button>
			{/each}
		{/if}
	</div>
</div>
