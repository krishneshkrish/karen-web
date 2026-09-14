<script lang="ts">
	import { onMount } from 'svelte';
	import { appState } from '$lib/state.svelte';
	import {
		getLocalSessionMessages,
		getLocalSessionMeta,
		type ChatMessage,
		type SessionMeta
	} from '$lib/db';
	import { api, type ReportResponse, type ChatMessagePayload } from '$lib/api';
	import Orb from '$lib/components/Orb.svelte';
	import { ArrowLeft, Download, Sparkles, CheckCircle2, ShieldCheck, Heart } from 'lucide-svelte';
	import jsPDF from 'jspdf';

	let report = $state<ReportResponse | null>(null);
	let sessionMeta = $state<SessionMeta | null>(null);
	let loading = $state(true);

	onMount(async () => {
		const targetId = appState.selectedReportSessionId || appState.currentSessionId;
		if (!targetId) {
			appState.setScreen('chat');
			return;
		}

		try {
			const msgs = await getLocalSessionMessages(targetId);
			sessionMeta = (await getLocalSessionMeta(targetId)) || null;

			const payload: ChatMessagePayload[] = msgs.map((m) => ({
				role: m.sender === 'user' ? 'user' : 'assistant',
				content: m.content
			}));

			const res = await api.generateReport({
				session_id: targetId,
				messages: payload,
				emotion_arc: appState.emotionArc,
				topic: sessionMeta?.topic,
				final_severity: sessionMeta?.final_severity
			});

			report = res;
		} catch (err) {
			console.warn('Report generation error:', err);
		} finally {
			loading = false;
		}
	});

	function downloadPDF() {
		if (!report) return;

		const doc = new jsPDF();

		// Header theme setup
		doc.setFillColor(13, 13, 26);
		doc.rect(0, 0, 210, 297, 'F');

		doc.setTextColor(167, 139, 250);
		doc.setFontSize(22);
		doc.text('Karen — Emotional Support Summary', 20, 25);

		doc.setFontSize(10);
		doc.setTextColor(156, 163, 175);
		doc.text(`Generated on: ${new Date(report.created_at).toLocaleString()}`, 20, 33);
		doc.text(`Session ID: ${report.session_id}`, 20, 39);

		doc.setDrawColor(255, 255, 255, 0.2);
		doc.line(20, 45, 190, 45);

		// Core Topic & Severity
		doc.setFontSize(14);
		doc.setTextColor(255, 255, 255);
		doc.text(`Primary Theme: ${report.topic}`, 20, 57);

		doc.setFontSize(11);
		doc.setTextColor(20, 184, 166);
		doc.text(`Emotional State: ${report.final_severity}`, 20, 65);

		// Journey Summary
		doc.setFontSize(12);
		doc.setTextColor(167, 139, 250);
		doc.text('Emotional Journey Summary:', 20, 80);

		doc.setFontSize(10);
		doc.setTextColor(229, 231, 235);
		const splitSummary = doc.splitTextToSize(report.emotional_journey_summary, 170);
		doc.text(splitSummary, 20, 88);

		let y = 88 + splitSummary.length * 6 + 10;

		// Key Insights
		doc.setFontSize(12);
		doc.setTextColor(167, 139, 250);
		doc.text('Key Insights & Reflections:', 20, y);
		y += 8;

		doc.setFontSize(10);
		doc.setTextColor(229, 231, 235);
		report.key_takeaways.forEach((item) => {
			doc.text(`• ${item}`, 24, y);
			y += 7;
		});

		y += 6;

		// Recommended Practices
		doc.setFontSize(12);
		doc.setTextColor(167, 139, 250);
		doc.text('Recommended Mindful Practices:', 20, y);
		y += 8;

		doc.setFontSize(10);
		doc.setTextColor(229, 231, 235);
		report.recommended_practices.forEach((item) => {
			doc.text(`• ${item}`, 24, y);
			y += 7;
		});

		// Footer note
		y += 15;
		doc.setFontSize(9);
		doc.setTextColor(156, 163, 175);
		doc.text('Confidential Client Report. Transcripts were stored exclusively on device.', 20, y);

		doc.save(`Karen_Session_Report_${report.session_id.substring(0, 8)}.pdf`);
	}
</script>

<div class="flex flex-col min-h-[100dvh] max-w-md mx-auto relative screen-fade-drift p-4 pb-8">
	<!-- Header -->
	<header class="flex items-center justify-between py-3 mb-4 border-b border-white/10 shrink-0">
		<button
			type="button"
			onclick={() => appState.setScreen('history')}
			class="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-300 transition-colors flex items-center gap-1.5 text-xs font-medium"
		>
			<ArrowLeft size={16} />
			<span>History</span>
		</button>
		<h1 class="text-sm font-semibold text-white">Session Insights</h1>
		<div class="w-8"></div>
	</header>

	{#if loading}
		<div class="flex-1 flex flex-col items-center justify-center space-y-4 text-center">
			<Orb size="md" interactive={false} />
			<div class="text-sm text-gray-300">Synthesizing your gentle insights...</div>
		</div>
	{:else if report}
		<div class="space-y-4 flex-1">
			<!-- Main Insight Card -->
			<div class="glass-card rounded-3xl p-6 border border-purple-500/20 shadow-2xl space-y-4">
				<div class="flex items-center justify-between">
					<div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-medium">
						<Sparkles size={14} />
						<span>{report.topic}</span>
					</div>
					<span class="text-xs font-medium text-teal-400">{report.final_severity}</span>
				</div>

				<div class="space-y-2 pt-1">
					<h2 class="text-base font-semibold text-white">Emotional Journey</h2>
					<p class="text-xs text-gray-300 leading-relaxed">
						{report.emotional_journey_summary}
					</p>
				</div>
			</div>

			<!-- Key Insights -->
			<div class="glass-card rounded-3xl p-6 border border-white/10 space-y-3">
				<h3 class="text-sm font-semibold text-purple-200">Key Takeaways</h3>
				<ul class="space-y-2.5">
					{#each report.key_takeaways as item}
						<li class="flex items-start gap-2.5 text-xs text-gray-300">
							<CheckCircle2 size={16} class="text-teal-400 shrink-0 mt-0.5" />
							<span class="leading-normal">{item}</span>
						</li>
					{/each}
				</ul>
			</div>

			<!-- Recommended Practices -->
			<div class="glass-card rounded-3xl p-6 border border-white/10 space-y-3">
				<h3 class="text-sm font-semibold text-teal-300">Gentle Grounding Practices</h3>
				<ul class="space-y-2.5">
					{#each report.recommended_practices as item}
						<li class="flex items-start gap-2.5 text-xs text-gray-300">
							<Heart size={15} class="text-purple-400 shrink-0 mt-0.5" />
							<span class="leading-normal">{item}</span>
						</li>
					{/each}
				</ul>
			</div>

			<!-- Download PDF Action -->
			<button
				type="button"
				onclick={downloadPDF}
				class="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-purple-600/70 to-indigo-600/70 hover:from-purple-600 hover:to-indigo-600 text-white font-medium text-sm shadow-xl border border-purple-400/30 transition-all flex items-center justify-center gap-2"
			>
				<Download size={18} />
				<span>Download PDF Summary</span>
			</button>

			<div class="flex items-center justify-center gap-2 text-[11px] text-gray-500 pt-2">
				<ShieldCheck size={14} class="text-teal-400" />
				<span>PDF generated entirely client-side (jsPDF)</span>
			</div>
		</div>
	{/if}
</div>
