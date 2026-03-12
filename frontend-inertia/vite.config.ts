import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig(({ command }) => ({
  plugins: [
    react({
      include: '**/*.{jsx,tsx}',
    }),
  ],
  base: command === 'build' ? '/static/dist/' : '/',
  resolve: {
    alias: {
      '@': resolve(fileURLToPath(new URL('./src', import.meta.url))),
      '@components': resolve(
        fileURLToPath(new URL('./src/components', import.meta.url)),
      ),
      '@styles': resolve(
        fileURLToPath(new URL('./src/styles', import.meta.url)),
      ),
      '@utils': resolve(fileURLToPath(new URL('./src/utils', import.meta.url))),
      '@types': resolve(fileURLToPath(new URL('./src/types', import.meta.url))),
      '@contexts': resolve(
        fileURLToPath(new URL('./src/contexts', import.meta.url)),
      ),
      '@layouts': resolve(
        fileURLToPath(new URL('./src/layouts', import.meta.url)),
      ),
      '@Pages': resolve(fileURLToPath(new URL('./src/Pages', import.meta.url))),
      '@hooks': resolve(fileURLToPath(new URL('./src/hooks', import.meta.url))),
      '@i18n': resolve(fileURLToPath(new URL('./src/i18n', import.meta.url))),
    },
  },
  build: {
    manifest: true,
    outDir: '../app/static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/main.tsx',
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    cors: true,
    hmr: false,
    watch: {
      usePolling: true,
      interval: 1000,
    },
  },
}));
