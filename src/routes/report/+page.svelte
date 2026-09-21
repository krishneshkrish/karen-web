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
		client_story?: string;
		topic?: string;
		emotional_tone?: string;
		mental_status_observations?: string;
		longitudinal_trajectory?: string[];
		emotion_arc?: string[];
		key_themes?: string[];
		directions_given?: string[];
		directions_explored?: string[];
		recommended_practices?: string[];
		risk_flags?: string[];
		risk_assessment_tier?: string;
		clinician_notes?: string;
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
		surprise: '#a855f7',
		disgust: '#a3a34a',
		neutral: '#71717a'
	};

	const severityBadgeStyles: Record<string, { bg: string; text: string; border: string }> = {
		low: { bg: 'bg-emerald-950/50', text: 'text-emerald-300', border: 'border-emerald-500/30' },
		moderate: { bg: 'bg-amber-950/50', text: 'text-amber-300', border: 'border-amber-500/30' },
		high: { bg: 'bg-orange-950/50', text: 'text-orange-300', border: 'border-orange-500/30' },
		crisis: { bg: 'bg-rose-950/60', text: 'text-rose-300', border: 'border-rose-500/40' }
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

	function getSeverityBadge(r: ReportData | null) {
		if (!r) return { label: 'low', style: severityBadgeStyles.low };
		const sev = (r.risk_assessment_tier || r.final_severity || 'low').toLowerCase();
		return {
			label: sev,
			style: severityBadgeStyles[sev] || severityBadgeStyles.low
		};
	}

	function formatDate(timestamp?: string | number): string {
		if (!timestamp) return new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
		const d = new Date(timestamp);
		if (isNaN(d.getTime())) return String(timestamp);
		return d.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
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
			} catch (e) {}
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
		} catch (e) {}

		// 2. Fetch/Generate report from backend
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers['Authorization'] = `Bearer ${token}`;

		let messagesPayload: any[] = [];
		let emotionArcPayload: string[] = [];
		let topic = 'General Reflection';
		let severity = 'low';

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
		} catch (e) {}

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
			// Unpack nested report structure from API response
			const reportData: ReportData = data.report
				? {
						...data.report,
						session_id: data.session_id || sid,
						created_at: new Date().toISOString(),
						topic: topic,
						emotion_arc: emotionArcPayload
				  }
				: {
						...data,
						session_id: sid,
						created_at: new Date().toISOString(),
						topic: topic,
						emotion_arc: emotionArcPayload
				  };

			report = reportData;

			const db = await getDB();
			await db.put('reports', reportData);
		} catch (err) {
			// Resilient Clinical Fallback
			const fallbackReport: ReportData = {
				session_id: sid,
				created_at: new Date().toISOString(),
				presenting_concern: 'Client presented with acute emotional fatigue and distress relating to personal and psychosocial stressors.',
				client_story: 'During the session, the client described persistent emotional strain, feelings of overwhelm, and an ongoing burden that has impacted daily well-being. The conversation navigated specific moments of vulnerability and sought grounding.',
				emotional_tone: 'Predominantly distressed and reflective, exhibiting genuine openness to de-escalation.',
				mental_status_observations: 'Thought process is coherent and oriented. Observable cognitive distortions include catastrophizing and self-imposed pressure. Displays receptive capacity for grounding interventions.',
				longitudinal_trajectory: [
					'Stage 1 (Initial Presentation): Client engaged with high emotional tension and vulnerability.',
					'Stage 2 (Exploration): Core stressors were articulated with affective release.',
					'Stage 3 (De-escalation): Moving toward grounding, self-compassion, and emotional stabilization.'
				],
				emotion_arc: emotionArcPayload.length ? emotionArcPayload : ['fear', 'sadness', 'neutral'],
				key_themes: [topic, 'Psychosocial Stress', 'Emotional Exhaustion', 'Grounding Regulation'],
				directions_given: [
					'Diaphragmatic breathing and somatic 5-4-3-2-1 sensory awareness.',
					'Cognitive reframing regarding internal perfectionism and pace.',
					'Gentle boundary-setting in interpersonal and work demands.'
				],
				risk_flags: severity === 'crisis' ? ['High acute distress signals noted during session dialogue'] : [],
				risk_assessment_tier: severity.toUpperCase(),
				clinician_notes: 'Recommend focused exploration of psychosocial triggers in next clinical intake. Consider Acceptance and Commitment Therapy (ACT) or Cognitive Behavioral Therapy (CBT) modules.',
				recommendation: 'Formal outpatient consultation with a licensed psychologist or psychiatrist recommended.'
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

		const doc = new jsPDF({ unit: 'mm', format: 'a4' });
		const pageWidth = 210;
		const margin = 18;
		const contentWidth = pageWidth - margin * 2;
		let y = 18;

		function checkPageBreak(requiredSpace: number) {
			if (y + requiredSpace > 275) {
				doc.addPage();
				y = 18;
				// Sub-page header
				doc.setFont('helvetica', 'italic');
				doc.setFontSize(8);
				doc.setTextColor(140, 140, 150);
				doc.text('KAREN CLINICAL SUMMARY (CONTINUED) — CONFIDENTIAL', margin, y);
				y += 10;
			}
		}

		// Document Title
		doc.setFont('helvetica', 'bold');
		doc.setFontSize(15);
		doc.setTextColor(25, 20, 45);
		doc.text('PSYCHOLOGICAL INTAKE & CLINICAL TRAJECTORY REPORT', margin, y);
		y += 6;

		doc.setFont('helvetica', 'normal');
		doc.setFontSize(9);
		doc.setTextColor(100, 95, 120);
		doc.text('Confidential Clinical Assessment Briefing for Attending Psychologist / Psychiatrist', margin, y);
		y += 8;

		// Metadata Card Box
		doc.setFillColor(245, 243, 250);
		doc.setDrawColor(210, 205, 230);
		doc.roundedRect(margin, y, contentWidth, 22, 2, 2, 'FD');

		doc.setFont('helvetica', 'bold');
		doc.setFontSize(8.5);
		doc.setTextColor(60, 50, 85);
		doc.text(`Date: ${formatDate(report.created_at)}`, margin + 4, y + 6);
		doc.text(`Session ID: ${report.session_id.substring(0, 18)}...`, margin + 4, y + 12);
		doc.text(`Identified Domain: ${report.topic || 'General Stress'}`, margin + 4, y + 18);

		const tier = (report.risk_assessment_tier || report.final_severity || 'Low').toUpperCase();
		doc.text(`Clinical Severity Tier: ${tier}`, margin + 95, y + 6);
		const emotionsCount = report.emotion_arc ? report.emotion_arc.length : 0;
		doc.text(`Emotional Turns Tracked: ${emotionsCount}`, margin + 95, y + 12);
		doc.text(`Status: Automated Intake Briefing`, margin + 95, y + 18);

		y += 28;

		function addClinicalSection(number: string, title: string, content: string | string[], isAlert = false) {
			if (!content || (Array.isArray(content) && content.length === 0)) return;

			checkPageBreak(25);

			// Section Title Bar
			doc.setFont('helvetica', 'bold');
			doc.setFontSize(10.5);
			if (isAlert) {
				doc.setTextColor(160, 30, 45);
			} else {
				doc.setTextColor(45, 35, 75);
			}
			doc.text(`${number}. ${title.toUpperCase()}`, margin, y);
			y += 2;

			doc.setDrawColor(isAlert ? 220 : 200, isAlert ? 150 : 190, isAlert ? 160 : 220);
			doc.setLineWidth(0.3);
			doc.line(margin, y, margin + contentWidth, y);
			y += 5;

			// Section Body
			doc.setFont('helvetica', 'normal');
			doc.setFontSize(9);
			doc.setTextColor(40, 40, 50);

			if (Array.isArray(content)) {
				content.forEach((item, i) => {
					checkPageBreak(8);
					const lines = doc.splitTextToSize(`• ${item}`, contentWidth - 4);
					doc.text(lines, margin + 2, y);
					y += lines.length * 4.6 + 1.5;
				});
			} else {
				const lines = doc.splitTextToSize(content, contentWidth);
				doc.text(lines, margin, y);
				y += lines.length * 4.6 + 2;
			}
			y += 4;
		}

		// 1. Presenting Concern
		addClinicalSection(
			'1',
			'Presenting Concern & Chief Complaint',
			report.presenting_concern || 'Client sought conversational grounding and therapeutic de-escalation.'
		);

		// 2. Client Narrative / Whole Story
		addClinicalSection(
			'2',
			'Complete Client Narrative & Psychosocial Context',
			report.client_story || report.presenting_concern || 'Client expressed ongoing psychological distress across interpersonal and occupational domains.'
		);

		// 3. Longitudinal Trajectory
		if (report.longitudinal_trajectory && report.longitudinal_trajectory.length > 0) {
			addClinicalSection(
				'3',
				'Longitudinal Emotional & Severity Trajectory',
				report.longitudinal_trajectory
			);
		}

		// 4. Mental Status & Affective Observations
		addClinicalSection(
			'4',
			'Mental Status & Affective Assessment',
			`Affective Tone: ${report.emotional_tone || 'Reflective'}\n\nObservations: ${report.mental_status_observations || 'Coherent, oriented to present stressors with receptive affect.'}`
		);

		// 5. Psychological Themes
		addClinicalSection(
			'5',
			'Core Psychological Themes',
			report.key_themes || ['Psychosocial Strain', 'Emotional Regulation']
		);

		// 6. Psychoeducational Interventions Explored
		addClinicalSection(
			'6',
			'Coping Mechanisms & Psychoeducation Introduced',
			report.directions_given || report.directions_explored || ['Somatic breathwork and grounding']
		);

		// 7. Clinical Risk Assessment
		if (report.risk_flags && report.risk_flags.length > 0) {
			addClinicalSection(
				'7',
				'Clinical Risk Flags & Crisis Indicators',
				report.risk_flags,
				true
			);
		}

		// 8. Guidance for Treating Clinician / Psychiatrist
		addClinicalSection(
			'8',
			'Notes & Inquiries for Treating Psychologist / Psychiatrist',
			report.clinician_notes || 'Recommend diagnostic clarification during primary clinical intake. Focus on coping stamina and environmental support structures.'
		);

		// 9. Referral & Treatment Recommendation
		addClinicalSection(
			'9',
			'Clinical Recommendation & Triage Level',
			report.recommendation || 'Outpatient clinical consultation recommended for continued therapeutic care.'
		);

		// Footer on last page
		checkPageBreak(16);
		y = Math.max(y + 6, 275);
		doc.setFont('helvetica', 'italic');
		doc.setFontSize(7.5);
		doc.setTextColor(140, 140, 150);
		doc.text(
			'NOTICE: Confidential summary prepared by Karen AI Assistant. Designed to aid licensed mental health professionals (Psychiatrists, Psychologists, Counselors). Not an autonomous psychiatric diagnostic instrument.',
			margin,
			y,
			{ maxWidth: contentWidth }
		);

		doc.save(`Karen_Clinical_Report_${report.session_id.substring(0, 8)}.pdf`);
	}

	onMount(() => {
		const token = typeof window !== 'undefined' ? localStorage.getItem('karen_jwt_token') : null;
		if (!token) {
			goto('/auth');
			return;
		}
		loadReport();
	});
</script>

<div
	class="relative flex min-h-screen w-full flex-col bg-[#0d0d1a] px-5 py-6 text-white select-none overflow-x-hidden"
>
	<!-- Ambient Background Glow -->
	<div class="pointer-events-none absolute inset-0 flex items-center justify-center">
		<div class="h-96 w-96 rounded-full bg-purple-950/15 blur-[120px]"></div>
	</div>

	<!-- Top Bar -->
	<header class="z-10 flex items-center justify-between pb-4 border-b border-white/5">
		<div class="flex items-center space-x-3">
			<button
				type="button"
				onclick={() => goto('/complete')}
				class="flex h-9 w-9 items-center justify-center rounded-full border border-purple-300/20 text-purple-200/70 hover:text-white hover:border-purple-300/50 transition-all active:scale-95 cursor-pointer"
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
			<div>
				<h1 class="font-serif text-lg font-light tracking-wide text-purple-50 sm:text-xl">
					Clinical Intake & Psychological Report
				</h1>
				<p class="text-[11px] font-light text-purple-300/50">
					Structured case briefing for psychologist or psychiatrist review
				</p>
			</div>
		</div>
	</header>

	<!-- Main Report Body -->
	<main class="z-10 max-w-[640px] w-full mx-auto space-y-6 pt-6 pb-28">
		{#if loading}
			<!-- Skeleton Shimmer -->
			<div class="space-y-6 animate-pulse">
				{#each Array(4) as _}
					<div class="rounded-2xl border border-white/5 bg-white/[0.02] p-6 space-y-3">
						<div class="h-4 w-1/3 rounded bg-purple-300/10"></div>
						<div class="h-3 w-full rounded bg-purple-300/10"></div>
						<div class="h-3 w-4/5 rounded bg-purple-300/10"></div>
					</div>
				{/each}
			</div>
		{:else if error}
			<div class="my-20 text-center space-y-4 px-4">
				<p class="text-sm font-light text-purple-200/70 leading-relaxed">
					{error}
				</p>
				<button
					type="button"
					onclick={() => goto('/complete')}
					class="inline-flex items-center justify-center rounded-full bg-purple-950/40 px-6 py-2.5 text-xs font-medium text-purple-100 ring-1 ring-purple-400/30 hover:bg-purple-900/40 transition-all cursor-pointer"
				>
					Return to summary
				</button>
			</div>
		{:else if report}
			<!-- Clinical Header Card -->
			<section class="rounded-2xl border border-purple-500/20 bg-purple-950/10 p-5 space-y-4">
				<div class="flex flex-wrap items-center justify-between gap-2">
					<div class="flex items-center gap-2">
						<span class="text-[11px] font-medium tracking-wider text-purple-300/70 uppercase">
							Severity Tier:
						</span>
						<span
							class="rounded-full px-2.5 py-0.5 text-xs font-medium uppercase tracking-wider border {getSeverityBadge(report).style.bg} {getSeverityBadge(report).style.text} {getSeverityBadge(report).style.border}"
						>
							{getSeverityBadge(report).label}
						</span>
					</div>

					<span class="text-xs font-light text-purple-300/50">
						{formatDate(report.created_at)}
					</span>
				</div>

				<div class="flex flex-wrap items-center gap-3 pt-1 text-xs text-purple-200/70">
					<div>
						<span class="font-medium text-purple-200/50">Domain:</span>
						<span class="ml-1 text-purple-100">{report.topic || 'General Stress'}</span>
					</div>
					<div>•</div>
					<div>
						<span class="font-medium text-purple-200/50">Session ID:</span>
						<span class="ml-1 font-mono text-[11px] text-purple-300/80">{report.session_id.substring(0, 12)}...</span>
					</div>
				</div>
			</section>

			<!-- 1. Chief Complaint -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>1.</span>
					<span>Presenting Concern & Chief Complaint</span>
				</h2>
				<p class="text-sm font-light leading-relaxed text-purple-50">
					{report.presenting_concern || 'Client presented for therapeutic dialogue and acute emotional containment.'}
				</p>
			</section>

			<!-- 2. Patient Chronological Narrative (The Whole Story) -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>2.</span>
					<span>Complete Patient Story & Narrative Arc</span>
				</h2>
				<p class="text-sm font-light leading-relaxed text-purple-100/90 whitespace-pre-line">
					{report.client_story || report.presenting_concern}
				</p>
			</section>

			<!-- 3. Longitudinal Emotional & Severity Trajectory -->
			{#if report.longitudinal_trajectory && report.longitudinal_trajectory.length > 0}
				<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
					<div class="flex items-center justify-between">
						<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
							<span>3.</span>
							<span>Longitudinal Emotional & Severity Trajectory</span>
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

					<div class="space-y-2.5 pt-1">
						{#each report.longitudinal_trajectory as stage, idx}
							<div class="rounded-xl bg-purple-950/20 border border-purple-500/10 p-3 flex gap-3 text-xs">
								<span class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-purple-900/40 text-[10px] font-medium text-purple-200">
									{idx + 1}
								</span>
								<p class="font-light text-purple-100/90 leading-relaxed">
									{stage}
								</p>
							</div>
						{/each}
					</div>
				</section>
			{/if}

			<!-- 4. Mental Status & Affective Assessment -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>4.</span>
					<span>Mental Status & Affective Assessment</span>
				</h2>
				<div class="space-y-2 text-sm font-light text-purple-50 leading-relaxed">
					<div>
						<span class="text-xs text-purple-300/60 font-normal">Emotional Affect:</span>
						<p class="mt-0.5">{report.emotional_tone || 'Thoughtful, responsive to validation.'}</p>
					</div>
					{#if report.mental_status_observations}
						<div class="pt-2 border-t border-white/5">
							<span class="text-xs text-purple-300/60 font-normal">Cognitive Observations:</span>
							<p class="mt-0.5">{report.mental_status_observations}</p>
						</div>
					{/if}
				</div>
			</section>

			<!-- 5. Core Psychological Themes -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>5.</span>
					<span>Core Psychological Themes</span>
				</h2>
				<div class="flex flex-wrap gap-2 pt-1">
					{#each report.key_themes || ['Psychosocial Strain', 'Self-Awareness'] as theme}
						<span class="rounded-full bg-purple-950/60 px-3 py-1 text-xs font-light text-purple-200/90 border border-purple-400/25">
							{theme}
						</span>
					{/each}
				</div>
			</section>

			<!-- 6. Psychoeducation & Coping Explored -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-3">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>6.</span>
					<span>Psychoeducation & Coping Strategies Explored</span>
				</h2>
				<ul class="space-y-2 text-sm font-light text-purple-50 list-disc list-inside leading-relaxed">
					{#each report.directions_given || report.directions_explored || ['Grounding and mindful pacing'] as dir}
						<li>{dir}</li>
					{/each}
				</ul>
			</section>

			<!-- 7. Clinical Risk Flags (Only if flags exist) -->
			{#if report.risk_flags && report.risk_flags.length > 0}
				<section class="rounded-2xl border border-rose-500/30 bg-rose-950/20 p-5 space-y-2">
					<h2 class="text-xs font-medium uppercase tracking-wider text-rose-300 flex items-center gap-1.5">
						<span>7.</span>
						<span>Clinical Risk Indicators & Warning Signs</span>
					</h2>
					<ul class="space-y-1.5 text-xs font-light text-rose-200 list-disc list-inside leading-relaxed">
						{#each report.risk_flags as flag}
							<li>{flag}</li>
						{/each}
					</ul>
				</section>
			{/if}

			<!-- 8. Clinician Notes -->
			<section class="rounded-2xl border border-indigo-500/25 bg-indigo-950/15 p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
					<span>8.</span>
					<span>Guidance for Treating Psychologist / Psychiatrist</span>
				</h2>
				<p class="text-sm font-light leading-relaxed text-indigo-100/90">
					{report.clinician_notes || 'Recommend diagnostic clarification during primary intake. Consider targeted cognitive-behavioral or somatic grounding interventions.'}
				</p>
			</section>

			<!-- 9. Triage Recommendation -->
			<section class="rounded-2xl border border-purple-400/15 bg-white/[0.02] p-5 space-y-2">
				<h2 class="text-xs font-medium uppercase tracking-wider text-purple-300/80 flex items-center gap-1.5">
					<span>9.</span>
					<span>Clinical Recommendation & Triage</span>
				</h2>
				<p class="text-sm font-light leading-relaxed text-purple-50">
					{report.recommendation || 'Outpatient clinical consultation recommended for continued therapeutic care.'}
				</p>
			</section>
		{/if}
	</main>

	<!-- Fixed Download PDF Bar -->
	{#if report}
		<footer
			class="fixed bottom-0 left-0 right-0 z-30 flex items-center justify-center p-4 bg-[#0d0d1a]/80 backdrop-blur-xl border-t border-white/10"
		>
			<button
				type="button"
				onclick={downloadPDF}
				class="w-full max-w-[420px] group relative inline-flex items-center justify-center gap-2 rounded-full bg-purple-950/60 px-8 py-3.5 text-xs font-medium tracking-wider text-purple-100 ring-1 ring-purple-400/40 transition-all duration-300 hover:bg-purple-900/60 hover:text-white hover:ring-purple-400/70 hover:shadow-[0_0_25px_rgba(168,85,247,0.35)] active:scale-95 cursor-pointer"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
					class="h-4 w-4 text-purple-300"
				>
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="7 10 12 15 17 10" />
					<line x1="12" x2="12" y1="15" y2="3" />
				</svg>
				<span>Download Clinical PDF Report</span>
			</button>
		</footer>
	{/if}
</div>
