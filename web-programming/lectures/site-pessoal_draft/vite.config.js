import { defineConfig } from 'vite';

export default defineConfig({
  base: '/site/', // '/your-repo-name/' for GitHub Pages
  build: {
    outDir: 'dist',
    assetsDir: 'public/images'
  }
});