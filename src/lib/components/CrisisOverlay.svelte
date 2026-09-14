<script lang="ts">
	import { onMount, tick } from 'svelte';

	interface Props {
		visible?: boolean;
		onDismiss?: () => void;
	}

	let { visible = false, onDismiss }: Props = $props();

	let cardRef: HTMLDivElement | null = $state(null);
	let previousActiveElement: HTMLElement | null = null;

	function handleDismiss() {
		if (onDismiss) {
			onDismiss();
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (!visible) return;

		if (e.key === 'Escape') {
			e.preventDefault();
			handleDismiss();
			return;
		}

		if (e.key === 'Tab' && cardRef) {
			const focusables = cardRef.querySelectorAll<HTMLElement>(
				'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
			);
			if (focusables.length === 0) return;

			const first = focusables[0];
			const last = focusables[focusables.length - 1];

			if (e.shiftKey && document.activeElement === first) {
				e.preventDefault();
				last.focus();
			} else if (!e.shiftKey && document.activeElement === last) {
				e.preventDefault();
				first.focus();
			}
		}
	}

	$effect(() => {
		if (visible) {
			previousActiveElement = document.activeElement as HTMLElement;
			tick().then(() => {
				if (cardRef) {
					const firstBtn = cardRef.querySelector<HTMLElement>('a, button');
					firstBtn?.focus();
				}
			});
		} else {
			if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
				previousActiveElement.focus();
			}
		}
	});
</script>

<svelte:window onkeydown={handleKeydown} />

{#if visible}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md transition-opacity duration-300 select-none overflow-y-auto"
		role="dialog"
		aria-modal="true"
		aria-labelledby="crisis-heading"
	>
		<!-- Centered Card -->
		<div
			bind:this={cardRef}
			class="w-full max-w-[340px] rounded-2xl bg-[#0d0d1a] border border-rose-400/20 p-6 text-purple-100 shadow-2xl transition-all duration-300 my-auto"
		>
			<!-- Top Heart Icon -->
			<div class="flex justify-center mb-3">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="currentColor"
					class="h-6 w-6 text-rose-400/70"
				>
					<path
						d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"
					/>
				</svg>
			</div>

			<!-- Heading & Body -->
			<div class="text-center space-y-2 mb-4">
				<h2 id="crisis-heading" class="font-serif text-2xl font-light text-purple-50 tracking-wide">
					I hear you.
				</h2>
				<p class="text-xs font-light leading-relaxed text-purple-200/75">
					What you're feeling right now is real. You deserve support from a real person — someone who can truly be there with you. If you are in immediate danger, please reach out to a 24/7 hotline below.
				</p>
			</div>

			<!-- Divider -->
			<div class="my-4 h-[1px] w-full bg-purple-500/10"></div>

			<!-- Support Cards -->
			<div class="space-y-2.5 mb-5">
				<!-- Find Support Now -->
				<div class="p-3 rounded-xl bg-purple-950/30 border border-purple-400/10 text-left">
					<div class="flex items-center gap-2 text-xs font-medium text-purple-100">
						<span>🫂</span>
						<span>Find support now</span>
					</div>
					<div class="mt-0.5 text-[11px] font-light text-purple-200/50">
						You don't have to go through this alone.
					</div>
				</div>

				<!-- 988 Lifeline -->
				<a
					href="tel:988"
					class="block p-3 rounded-xl bg-purple-950/30 border border-rose-400/20 hover:border-rose-400/40 hover:bg-purple-900/30 transition-all text-left group"
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2 text-xs font-medium text-rose-200">
							<span>📞</span>
							<span>Crisis & Suicide Lifeline</span>
						</div>
						<span class="text-[11px] font-light text-rose-300">Call 988</span>
					</div>
					<div class="mt-0.5 text-[11px] font-light text-purple-200/60">
						Free, confidential 24/7 support hotline
					</div>
				</a>

				<!-- iCall Helpline -->
				<a
					href="tel:9152987821"
					class="block p-3 rounded-xl bg-purple-950/30 border border-purple-400/10 hover:border-purple-400/30 hover:bg-purple-900/30 transition-all text-left group"
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2 text-xs font-medium text-purple-100">
							<span>📞</span>
							<span>iCall Helpline</span>
						</div>
						<span class="text-[11px] font-light text-rose-300/80">Call</span>
					</div>
					<div class="mt-0.5 text-[11px] font-light text-purple-200/60">
						9152987821
					</div>
				</a>

				<!-- Vandrevala Foundation -->
				<a
					href="tel:18602662345"
					class="block p-3 rounded-xl bg-purple-950/30 border border-purple-400/10 hover:border-purple-400/30 hover:bg-purple-900/30 transition-all text-left group"
				>
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-2 text-xs font-medium text-purple-100">
							<span>📞</span>
							<span>Vandrevala Foundation</span>
						</div>
						<span class="text-[11px] font-light text-rose-300/80">Call</span>
					</div>
					<div class="mt-0.5 text-[11px] font-light text-purple-200/60">
						1860-2662-345
					</div>
				</a>

				<!-- External Link -->
				<a
					href="https://icallhelpline.org"
					target="_blank"
					rel="noopener noreferrer"
					class="block p-3 rounded-xl bg-purple-950/30 border border-purple-400/10 hover:border-purple-400/30 hover:bg-purple-900/30 transition-all text-left"
				>
					<div class="flex items-center gap-2 text-xs font-medium text-purple-100">
						<span>🔗</span>
						<span>Call or text a support line</span>
					</div>
				</a>
			</div>

			<!-- Continuation note -->
			<p class="text-center text-[11px] font-light text-purple-200/40 mb-4">
				I'll be here when you're ready to continue.
			</p>

			<!-- Dismiss Buttons -->
			<div class="flex flex-col items-center gap-2">
				<button
					type="button"
					onclick={handleDismiss}
					class="w-full py-2.5 rounded-full bg-rose-950/50 ring-1 ring-rose-400/30 text-xs font-medium text-rose-100 hover:bg-rose-900/50 transition-all"
				>
					Return to conversation
				</button>
				<button
					type="button"
					onclick={handleDismiss}
					class="text-xs font-light text-purple-300/60 hover:text-purple-200 py-1 transition-colors focus:outline-none"
				>
					I'm okay for now
				</button>
			</div>
		</div>
	</div>
{/if}
