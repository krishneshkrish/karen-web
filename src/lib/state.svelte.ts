import { getStoredToken, setStoredToken, clearStoredToken } from '$lib/api';
import { getLocalSessions } from '$lib/db';

export type ScreenState =
	| 'splash'
	| 'auth'
	| 'space-transition'
	| 'chat'
	| 'end-session'
	| 'session-complete'
	| 'history'
	| 'report';

export type EmotionState = 'neutral' | 'anxiety' | 'sadness' | 'calm';

// Svelte 5 Runes app state implementation
class AppState {
	currentScreen = $state<ScreenState>('splash');
	currentEmotion = $state<EmotionState>('neutral');
	emotionArc = $state<EmotionState[]>(['neutral']);
	currentSessionId = $state<string | null>(null);
	selectedReportSessionId = $state<string | null>(null);
	isCrisisOpen = $state<boolean>(false);
	isDrawerOpen = $state<boolean>(false);
	userEmail = $state<string | null>(null);

	// Derived values
	greetingTagline = $derived.by(() => {
		const hour = new Date().getHours();
		if (hour >= 23 || hour < 5) return 'Quiet • Still • Deep';
		if (hour >= 5 && hour < 12) return 'Soft • Gentle • Fresh';
		if (hour >= 12 && hour < 17) return 'Warm • Calm • Grounded';
		return 'Serene • Quiet • Present';
	});

	dominantEmotion = $derived.by(() => {
		if (!this.emotionArc.length) return 'neutral';
		const counts: Record<string, number> = {};
		for (const em of this.emotionArc) {
			counts[em] = (counts[em] || 0) + 1;
		}
		let maxCount = 0;
		let dominant: EmotionState = 'neutral';
		for (const [em, cnt] of Object.entries(counts)) {
			if (cnt >= maxCount) {
				maxCount = cnt;
				dominant = em as EmotionState;
			}
		}
		return dominant;
	});

	constructor() {
		// Init check
		if (typeof window !== 'undefined') {
			const token = getStoredToken();
			if (token) {
				this.userEmail = 'user@karen.space';
			}
		}
	}

	setScreen(screen: ScreenState) {
		this.currentScreen = screen;
	}

	setEmotion(emotion: string) {
		const validEmotions: EmotionState[] = ['neutral', 'anxiety', 'sadness', 'calm'];
		const normalized = validEmotions.includes(emotion as EmotionState)
			? (emotion as EmotionState)
			: 'neutral';

		this.currentEmotion = normalized;
		this.emotionArc.push(normalized);
	}

	startNewSession(): string {
		const id = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7);
		this.currentSessionId = id;
		this.currentEmotion = 'neutral';
		this.emotionArc = ['neutral'];
		return id;
	}

	toggleCrisis(open?: boolean) {
		this.isCrisisOpen = open !== undefined ? open : !this.isCrisisOpen;
	}

	toggleDrawer(open?: boolean) {
		this.isDrawerOpen = open !== undefined ? open : !this.isDrawerOpen;
	}

	logout() {
		clearStoredToken();
		this.userEmail = null;
		this.currentSessionId = null;
		this.currentScreen = 'auth';
	}
}

export const appState = new AppState();
