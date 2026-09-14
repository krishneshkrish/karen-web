<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { appState } from '$lib/state.svelte';
	import {
		saveLocalMessage,
		getLocalSessionMessages,
		saveLocalSessionMeta,
		type ChatMessage
	} from '$lib/db';
	import { api, type ChatMessagePayload } from '$lib/api';
	import Orb from '$lib/components/Orb.svelte';
	import { Send, Menu, HeartHandshake, LogOut, Clock } from 'lucide-svelte';

	let messages = $state<ChatMessage[]>([]);
	let inputValue = $state('');
	let isTyping = $state(false);
	let messagesContainer = $state<HTMLElement | null>(null);
	let activeTimestampId = $state<string | null>(null);

	onMount(async () => {
		if (!appState.currentSessionId) {
			appState.startNewSession();
		}

		const sessionId = appState.currentSessionId!;
		const existingMsgs = await getLocalSessionMessages(sessionId);

		if (existingMsgs.length > 0) {
			messages = existingMsgs;
		} else {
			// Welcome initial message from Karen
			const initMsg: ChatMessage = {
				id: 'msg_init_' + Date.now(),
				session_id: sessionId,
				sender: 'karen',
				content: `Hello. Take a deep breath. I'm right here with you. What is on your mind or heart right now?`,
				timestamp: new Date().toISOString(),
				detected_emotion: 'neutral'
			};
			messages = [initMsg];
			await saveLocalMessage(initMsg);
			await saveLocalSessionMeta({
				id: sessionId,
				start_time: new Date().toISOString(),
				message_count: 1
			});
		}

		await scrollToBottom();
	});

	async function scrollToBottom() {
		await tick();
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	async function handleSend() {
		const text = inputValue.trim();
		if (!text || isTyping) return;

		const sessionId = appState.currentSessionId!;
		inputValue = '';

		// 1. Create and store user message locally
		const userMsg: ChatMessage = {
			id: 'msg_usr_' + Date.now(),
			session_id: sessionId,
			sender: 'user',
			content: text,
			timestamp: new Date().toISOString()
		};

		messages = [...messages, userMsg];
		await saveLocalMessage(userMsg);
		await scrollToBottom();

		// 2. Prepare payload for Karen backend API
		isTyping = true;
		const payload: ChatMessagePayload[] = messages.map((m) => ({
			role: m.sender === 'user' ? 'user' : 'assistant',
			content: m.content
		}));

		try {
			const res = await api.sendMessage({
				session_id: sessionId,
				messages: payload,
				is_first_message: messages.length <= 2
			});

			if (res.detected_emotion) {
				appState.setEmotion(res.detected_emotion);
			}

			if (res.crisis_flag) {
				appState.toggleCrisis(true);
			}

			// 3. Save Karen's response locally
			const karenMsg: ChatMessage = {
				id: 'msg_krn_' + Date.now(),
				session_id: sessionId,
				sender: 'karen',
				content: res.reply,
				timestamp: new Date().toISOString(),
				detected_emotion: res.detected_emotion
			};

			messages = [...messages, karenMsg];
			await saveLocalMessage(karenMsg);

			await saveLocalSessionMeta({
				id: sessionId,
				start_time: messages[0].timestamp,
				message_count: messages.length,
				dominant_emotion: appState.dominantEmotion
			});
		} catch (err) {
			console.warn('Backend message error:', err);
		} finally {
			isTyping = false;
			await scrollToBottom();
		}
	}

	function formatTime(iso: string) {
		const d = new Date(iso);
		return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
	}

	function toggleTimestamp(id: string) {
		activeTimestampId = activeTimestampId === id ? null : id;
	}
</script>

<div class="flex flex-col h-[100dvh] max-w-md mx-auto relative screen-fade-drift overflow-hidden">
	<!-- Top Navigation Bar -->
	<header class="flex items-center justify-between px-4 py-3 border-b border-white/10 glass-card z-10 shrink-0">
		<div class="flex items-center gap-3">
			<button
				type="button"
				onclick={() => appState.toggleDrawer(true)}
				aria-label="Open menu drawer"
				class="p-1.5 rounded-full hover:bg-white/10 text-gray-300 transition-colors"
			>
				<Orb size="sm" interactive={false} />
			</button>

			<div>
				<h1 class="text-sm font-semibold text-white tracking-wide">Karen</h1>
				<div class="flex items-center gap-1.5 text-[11px] text-purple-300/80">
					<span class="w-1.5 h-1.5 rounded-full bg-teal-400 animate-pulse"></span>
					<span class="capitalize">{appState.currentEmotion} Space</span>
				</div>
			</div>
		</div>

		<div class="flex items-center gap-2">
			<button
				type="button"
				onclick={() => appState.toggleCrisis(true)}
				aria-label="Emergency Crisis Support"
				class="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 hover:bg-amber-500/20 transition-all text-xs font-medium flex items-center gap-1.5"
			>
				<HeartHandshake size={15} />
				<span class="hidden sm:inline">Crisis Support</span>
			</button>

			<button
				type="button"
				onclick={() => appState.setScreen('end-session')}
				aria-label="End conversation session"
				class="p-2 rounded-xl bg-white/5 border border-white/10 text-gray-300 hover:bg-white/10 transition-colors"
			>
				<LogOut size={16} />
			</button>
		</div>
	</header>

	<!-- Chat Messages Area -->
	<div
		bind:this={messagesContainer}
		class="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
	>
		{#each messages as msg (msg.id)}
			<div class="flex flex-col {msg.sender === 'user' ? 'items-end' : 'items-start'} space-y-1">
				<!-- Message Bubble -->
				<button
					type="button"
					onclick={() => toggleTimestamp(msg.id)}
					aria-label="Toggle timestamp reveal"
					class="max-w-[85%] text-left p-4 transition-all duration-200 {msg.sender === 'user'
						? 'rounded-3xl rounded-tr-sm bg-purple-900/40 text-purple-100 border border-purple-500/30 backdrop-blur-md shadow-md'
						: 'rounded-3xl rounded-tl-sm bg-white/7 text-gray-100 border border-white/10 backdrop-blur-md shadow-md'}"
				>
					<p class="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
				</button>

				<!-- 50% opacity small tap-to-reveal timestamp -->
				{#if activeTimestampId === msg.id}
					<div class="text-[10px] text-gray-400/80 px-2 flex items-center gap-1 screen-fade-drift">
						<Clock size={10} />
						<span>{formatTime(msg.timestamp)}</span>
					</div>
				{/if}
			</div>
		{/each}

		{#if isTyping}
			<div class="flex items-center gap-2 p-3.5 rounded-3xl rounded-tl-sm bg-white/5 border border-white/10 w-24">
				<span class="w-2 h-2 rounded-full bg-purple-400 animate-bounce"></span>
				<span class="w-2 h-2 rounded-full bg-purple-400 animate-bounce [animation-delay:0.2s]"></span>
				<span class="w-2 h-2 rounded-full bg-purple-400 animate-bounce [animation-delay:0.4s]"></span>
			</div>
		{/if}
	</div>

	<!-- Floating Input Bar -->
	<div class="p-4 border-t border-white/10 glass-card shrink-0">
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSend();
			}}
			class="flex items-center gap-2"
		>
			<div class="flex-1 relative rounded-2xl glass-input px-4 py-3 flex items-center">
				<input
					type="text"
					bind:value={inputValue}
					placeholder="Share what's on your heart..."
					aria-label="Message to Karen"
					class="w-full bg-transparent text-sm text-white placeholder-gray-400 focus:outline-none"
				/>
			</div>

			<!-- Floating soft glow send button (not solid filled) -->
			<button
				type="submit"
				disabled={!inputValue.trim() || isTyping}
				aria-label="Send message to Karen"
				class="p-3.5 rounded-2xl border border-purple-400/40 text-purple-300 hover:text-white hover:border-purple-400/80 hover:shadow-[0_0_20px_rgba(167,139,250,0.4)] bg-purple-500/10 transition-all duration-300 disabled:opacity-40 disabled:hover:shadow-none"
			>
				<Send size={18} />
			</button>
		</form>
	</div>
</div>
