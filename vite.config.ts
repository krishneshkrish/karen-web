import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5180,
		host: true,
		watch: {
			ignored: ['**/testsprite_tests/**', '**/.git/**']
		}
	}
});
