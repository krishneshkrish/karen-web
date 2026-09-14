<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { env } from '$env/dynamic/public';
	import { openDB } from 'idb';
	import { jsPDF } from 'jspdf';

	const PUBLIC_API_URL = env.PUBLIC_API_URL || 'http://localhost:8000';

	interface ReportData {
		session_id: string;
		created_at?: string;
		presenting_concern?: string;
		topic?: string;
		emotional_tone?: string;
		emotional_journey_summary?: string;
		emotion_arc?: string[];
		key_themes?: string[];
		key_takeaways?: string[];
		directions_given?: string[];
		directions_explored?: string[];
		recommended_practices?: string[];
		risk_flags?: string[];
		recommendation?: string;
		final_severity?: string;
	}

	let report = $state<ReportData | null>(null);
	let loading = $state<boolean>(true);
	let error = $state<string>('');

	const emotionColors: Record<string, string> = {
		sadness: '#6b9bd2',
		fear: '#d4a853',
		anger: '#c47070',
		joy: '#6ba882',
		neutral: '#555566'
	};

	async function getDB() {
		return openDB('karen-db', 2, {
			upgrade(db, oldVersion) {
				if (oldVersion < 1) {
					if (!db.objectStoreNames.contains('sessions')) {
						db.createObjectStore('sessions', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('preferences')) {
						db.createObjectStore('preferences', { keyPath: 'key' });
					}
				}
				if (oldVersion < 2) {
					if (!db.objectStoreNames.contains('reports')) {
						db.createObjectStore('reports', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('sessions')) {
						db.createObjectStore('sessions', { keyPath: 'session_id' });
					}
					if (!db.objectStoreNames.contains('preferences')) {
						db.createObjectStore('preferences', { keyPath: 'key' });
					}
				}
			}
		});
	}

	function formatDate(timestamp?: string | number): string {
		if (!timestamp) return new Date().toLocaleDateString();
		const d = new Date(timestamp);
		if (isNaN(d.getTime())) return String(timestamp);
		return d.toLocaleDateString('en-US', {
			weekday: 'long',
			day: 'numeric',
			month: 'long',
			year: 'numeric'
		});
	}

	async function loadReport() {
		loading = true;
		error = '';

		let sid =
			page.url.searchParams.get('session_id') ||
			sessionStorage.getItem('karen_session_id') ||
			sessionStorage.getItem('karen_last_session_id') ||
			'';

		if (!sid) {
			try {
				const db = await getDB();
				const allReports = await db.getAll('reports');
				if (allReports.length > 0) {
					sid = allReports[allReports.length - 1].session_id;
				} else {
					const allSessions = await db.getAll('sessions');
					if (allSessions.length > 0) {
						sid = allSessions[allSessions.length - 1].session_id;
					}
				}
			} catch (e) {
				// Fail soft
			}
		}

		if (!sid) {
			sid = 'sess_' + Date.now();
		}

		// 1. Check IndexedDB reports store
		try {
			const db = await getDB();
			const cachedReport = await db.get('reports', sid);
			if (cachedReport) {
				report = cachedReport;
				loading = false;
				return;
			}
		} catch (e) {
			// Fail soft
		}

		// 2. Generate/fetch report from backend
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		let messagesPayload: any[] = [];
		let emotionArcPayload: string[] = [];
		let topic = 'General Reflection';
		let severity = 'Mild';

		try {
			const db = await getDB();
			const sessionData = await db.get('sessions', sid);
			if (sessionData) {
				if (sessionData.messages) {
					messagesPayload = sessionData.messages.map((m: any) => ({
						role: m.sender === 'user' ? 'user' : 'assistant',
						content: m.content
					}));
				}
				emotionArcPayload = sessionData.emotion_arc || [];
				topic = sessionData.topic || topic;
				severity = sessionData.final_severity || severity;
			}
		} catch (e) {
			// Fail soft
		}

		try {
			const res = await fetch(`${PUBLIC_API_URL}/api/v1/report/generate`, {
				method: 'POST',
				headers,
				body: JSON.stringify({
					session_id: sid,
					messages: messagesPayload,
					emotion_arc: emotionArcPayload,
					topic,
					final_severity: severity
				})
			});

			if (!res.ok) {
				throw new Error('Report generation failed');
			}

			const data = await res.json();
			report = data;

			const db = await getDB();
			await db.put('reports', data);
		} catch (err) {
			// Fallback local report
			const fallbackReport: ReportData = {
				session_id: sid,
				created_at: new Date().toISOString(),
				presenting_concern: 'Navigating personal thoughts and emotional processing.',
				emotional_tone: 'Thoughtful, open, and seeking grounding.',
				emotion_arc: emotionArcPayload.length ? emotionArcPayload : ['neutral', 'calm'],
				key_themes: [topic, 'Self-Reflection', 'Grounding'],
				directions_explored: [
					'Acknowledged emotional triggers without judgment.',
					'Explored steady breathing practices for emotional ease.'
				],
				recommendation: 'Continue daily check-ins and gentle grounding exercises.'
			};
			report = fallbackReport;

			try {
				const db = await getDB();
				await db.put('reports', fallbackReport);
			} catch (e) {}
		} finally {
			loading = false;
		}
	}

	function downloadPDF() {
		if (!report) return;

		const doc = new jsPDF();
		const margin = 20;
		let y = 20;

		// Title Header
		doc.setFont('helvetica', 'bold');
		doc.setFontSize(18);
		doc.setTextColor(30, 25, 50);
		doc.text('Karen — Session Reflection', margin, y);

		y += 8;
		doc.setFont('helvetica', 'normal');
		doc.setFontSize(10);
		doc.setTextColor(100, 100, 120);
		doc.text(`Date: ${formatDate(report.created_at)}`, margin, y);

		y += 12;

		function addSection(title: string, content: string | string[]) {
			if (!content || (Array.isArray(content) && content.length === 0)) return;

			if (y > 260) {
				doc.addPage();
				y = 20;
			}

			doc.setFont('helvetica', 'bold');
			doc.setFontSize(12);
			doc.setTextColor(60, 45, 90);
			doc.text(title, margin, y);
			y += 7;

			doc.setFont('helvetica', 'normal');
			doc.setFontSize(10);
			doc.setTextColor(40, 40, 50);

			if (Array.isArray(content)) {
				content.forEach((item, i) => {
					const lines = doc.splitTextToSize(`${i + 1}. ${item}`, 170);
					doc.text(lines, margin, y);
					y += lines.length * 6;
				});
			} else {
				const lines = doc.splitTextToSize(content, 170);
				doc.text(lines, margin, y);
				y += lines.length * 6;
			}
			y += 4;
		}

		addSection(
			'1. What brought you here',
			report.presenting_concern || report.topic || 'General emotional processing.'
		);
		addSection(
			'2. How you were feeling',
			report.emotional_tone || report.emotional_journey_summary || 'Self-reflective.'
		);
		addSection(
			'3. Themes that came up',
			report.key_themes || report.key_takeaways || ['Emotional awareness']
		);
		addSection(
			'4. Directions explored',
			report.directions_given || report.recommended_practices || ['Grounding & breathing']
		);

		if (report.risk_flags && report.risk_flags.length > 0) {
			addSection('5. Flags noted', report.risk_flags);
		}

		addSection(
			'6. Recommendation',
			report.recommendation || 'Continue gentle self-care and open dialogue.'
		);

		// Footer
		y = Math.max(y + 10, 275);
		doc.setFont('helvetica', 'italic');
		doc.setFontSize(9);
		doc.setTextColor(120, 120, 140);
		doc.text(
			'Generated by Karen. This is a personal reflection, not a clinical document.',
			margin,
			y
		);

		doc.save(`Karen_Reflection_${report.session_id.substring(0, 8)}.pdf`);
	}

	onMount(() => {
		loadReport();
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col bg-[#0d0d1a] px-5 py-6 text-white select-none overflow-x-hidden"
>
	<!-- Ambient Outer Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-96 w-96 rounded-full bg-purple-950/15 blur-[120px]"></div>
	</div>

	<!-- Top Bar -->
	<header class="z-10 flex items-center justify-between pb-4 border-b border-white/5">
		<div class="flex items-center space-x-3">
			<button
				type="button"
				onclick={() => goto('/complete')}
				class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/70 hover:text-white hover:border-purple-300/50 transition-all active:scale-95"
				aria-label="Back to completion page"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="h-4 w-4"
				>
					<path d="M19 12H5" />
					<path d="m12 19-7-7 7-7" />
				</svg>
			</button>
			<h1 class="font-serif text-xl font-light tracking-wide text-purple-50">Your reflection</h1>
		</div>
	</header>

	<div class="z-10 text-xs font-light text-purple-200/50 pt-2 pb-6">
		A summary of your conversation. Share this with a counsellor if helpful.
	</div>

	<!-- Main Report Content / Skeleton / Error State -->
	<main class="z-10 max-w-[390px] w-full mx-auto space-y-6 pb-28">
		{#if loading}
			<!-- Skeleton Shimmer -->
			<div class="space-y-6 animate-pulse">
				{#each Array(4) as _}
					<div class="rounded-2xl border border-white/5 bg-white/[0.02] p-5 space-y-3">
						<div class="h-4 w-1/3 rounded bg-purple-300/10"></div>
						<div class="h-3 w-full rounded bg-purple-300/10"></div>
						<div class="h-3 w-4/5 rounded bg-purple-300/10"></div>
					</div>
				{/each}
			</div>
		{:else if error}
			<!-- Soft Error State -->
			<div class="my-20 text-center space-y-4 px-4">
				<p class="text-sm font-light text-purple-200/70 leading-relaxed">
					{error}
				</p>
				<button
					type="button"
					onclick={() => goto('/complete')}
					class="inline-flex items-center justify-center rounded-full bg-purple-950/40 px-6 py-2.5 text-xs font-medium text-purple-100 ring-1 ring-purple-400/30 hover:bg-purple-900/40 transition-all"
				>
					Return to summary
				</button>
			</div>
		{:else if report}
			<!-- Section 1: What brought you here -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/70">
					1. What brought you here
				</h2>
				<p class="text-sm font-light leading-relaxed text-purple-50">
					{report.presenting_concern || report.topic || 'Navigating personal thoughts and emotions.'}
				</p>
			</section>

			<!-- Section 2: How you were feeling -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<div class="flex items-center justify-between">
					<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/70">
						2. How you were feeling
					</h2>
					{#if report.emotion_arc && report.emotion_arc.length > 0}
						<div class="flex items-center space-x-1.5">
							{#each report.emotion_arc as emotion}
								<div
									class="h-2 w-2 rounded-full"
									style="background-color: {emotionColors[emotion] || emotionColors.neutral}"
									title={emotion}
								></div>
							{/each}
						</div>
					{/if}
				</div>
				<p class="text-sm font-light leading-relaxed text-purple-50">
					{report.emotional_tone || report.emotional_journey_summary || 'Expressing open self-awareness and seeking emotional clarity.'}
				</p>
			</section>

			<!-- Section 3: Themes that came up -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/70">
					3. Themes that came up
				</h2>
				<div class="flex flex-wrap gap-2 pt-1">
					{#each report.key_themes || report.key_takeaways || ['Self-Reflection', 'Grounding'] as theme}
						<span class="rounded-full bg-purple-950/50 px-3 py-1 text-xs font-light text-purple-200/80 border border-purple-400/20">
							{theme}
						</span>
					{/each}
				</div>
			</section>

			<!-- Section 4: Directions explored -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/70">
					4. Directions explored
				</h2>
				<ol class="space-y-2 text-sm font-light text-purple-50 list-decimal list-inside leading-relaxed">
					{#each report.directions_given || report.recommended_practices || ['Mindful breathwork', 'Grounding techniques'] as dir}
						<li>{dir}</li>
					{/each}
				</ol>
			</section>

			<!-- Section 5: Flags noted (Only if risk_flags non-empty) -->
			{#if report.risk_flags && report.risk_flags.length > 0}
				<section class="rounded-2xl border border-amber-500/20 bg-amber-950/10 p-5 space-y-2">
					<h2 class="text-xs font-medium uppercase tracking-wider text-amber-300/80">
						5. Flags noted
					</h2>
					<ul class="space-y-1 text-xs font-light text-amber-200/90 list-disc list-inside leading-relaxed">
						{#each report.risk_flags as flag}
							<li>{flag}</li>
						{/each}
					</ul>
				</section>
			{/if}

			<!-- Section 6: Recommendation -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/70">
					6. Recommendation
				</h2>
				<p class="text-sm font-light leading-relaxed text-purple-50">
					{report.recommendation || 'Continue taking moments for quiet reflection and gentle grounding whenever needed.'}
				</p>
			</section>
		{/if}
	</main>

	<!-- Fixed Download PDF Bar -->
	{#if report}
		<footer
			class="fixed bottom-0 left-0 right-0 z-30 flex items-center justify-center p-4 bg-white/[0.04] backdrop-blur-xl border-t border-white/10"
		>
			<button
				type="button"
				onclick={downloadPDF}
				class="w-full max-w-[390px] group relative inline-flex items-center justify-center rounded-full bg-purple-950/50 px-8 py-3.5 text-xs font-medium tracking-wider text-purple-100 ring-1 ring-purple-400/30 transition-all duration-300 hover:bg-purple-900/50 hover:text-white hover:ring-purple-400/60 hover:shadow-[0_0_25px_rgba(168,85,247,0.3)] active:scale-95"
			>
				Download as PDF
			</button>
		</footer>
	{/if}
</div>
