import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://vox0.app',
  output: 'static',
  trailingSlash: 'always',
  integrations: [sitemap()],
});
