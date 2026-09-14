/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				karen: {
					bg: '#0d0d1a',
					orb: '#8b5cf6',
					card: 'rgba(255, 255, 255, 0.05)',
					border: 'rgba(255, 255, 255, 0.1)',
					userBubble: 'rgba(139, 92, 246, 0.25)',
					karenBubble: 'rgba(255, 255, 255, 0.07)',
					text: '#f3f4f6',
					subtext: '#9ca3af'
				}
			},
			animation: {
				breathe: 'breathe 8s ease-in-out infinite',
				'breathe-fast': 'breathe 4s ease-in-out infinite',
				drift: 'driftUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards'
			},
			keyframes: {
				breathe: {
					'0%, 100%': { transform: 'scale(1)', opacity: '0.85', filter: 'blur(30px) brightness(1)' },
					'50%': { transform: 'scale(1.15)', opacity: '1', filter: 'blur(45px) brightness(1.2)' }
				},
				driftUp: {
					'0%': { opacity: '0', transform: 'translateY(12px)' },
					'100%': { opacity: '1', transform: 'translateY(0)' }
				}
			}
		}
	},
	plugins: []
};
