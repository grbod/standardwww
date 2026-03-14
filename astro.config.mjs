import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://bodynutrition.com',
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
    },
  },
});
