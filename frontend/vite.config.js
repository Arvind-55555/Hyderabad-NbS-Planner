import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Use root path for Vercel, or /Hyderabad-NbS-Planner/ for GitHub Pages
  base: process.env.VERCEL ? '/' : '/Hyderabad-NbS-Planner/',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    port: 3000,
    open: true,
  },
});

