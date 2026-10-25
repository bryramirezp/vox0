import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { resolve, join } from 'node:path';
import test from 'node:test';

const out = resolve('dist');
const release = JSON.parse(readFileSync('src/data/release.json', 'utf8'));
const preview = process.env.VERCEL_ENV && process.env.VERCEL_ENV !== 'production';
const routes = ['/', '/install/', '/privacy/'];
const pages = routes.map((route) => readFileSync(join(out, route, 'index.html'), 'utf8'));
const attributes = (tag) => Object.fromEntries([...tag.matchAll(/([\w:-]+)="([^"]*)"/g)].map((m) => [m[1], m[2]]));
const tags = (html, name) => [...html.matchAll(new RegExp(`<${name}\\b[^>]*>`, 'g'))].map((m) => attributes(m[0]));
const metadata = (html, key) => tags(html, 'meta').find((m) => m.name === key || m.property === key)?.content;

test('pages have distinct search metadata, production canonicals and accessible landmarks', () => {
  assert.notEqual(pages[0].match(/<title>(.*?)<\/title>/s)?.[1], pages[1].match(/<title>(.*?)<\/title>/s)?.[1]);
  assert.notEqual(metadata(pages[0], 'description'), metadata(pages[1], 'description'));
  for (const [i, html] of pages.entries()) {
    const canonical = `https://vox0.app${routes[i]}`;
    assert.equal(tags(html, 'link').find((m) => m.rel === 'canonical')?.href, canonical);
    assert.equal(metadata(html, 'og:url'), canonical);
    assert.equal(metadata(html, 'og:image'), 'https://vox0.app/images/social-preview.png');
    assert.equal(metadata(html, 'twitter:card'), 'summary_large_image');
    assert.equal(metadata(html, 'robots').includes('noindex'), Boolean(preview));
    assert.match(html, /<html\b[^>]*lang="en"/);
    assert.equal([...html.matchAll(/<h1\b/g)].length, 1);
    assert.equal(tags(html, 'main').filter((m) => m.id === 'main').length, 1);
    assert.doesNotMatch(html, /bryramirezp\.github\.io|\.astro\b|docs\/src/);
  }
});

test('download links and structured data describe the published release', () => {
  const prefix = `https://github.com/bryramirezp/vox0/releases/download/v${release.version}/`;
  const installer = release.gpuInstaller || `${release.brand}-Setup-${release.version}.exe`;
  for (const html of pages.slice(0, 2)) {
    const downloads = tags(html, 'a').map((a) => a.href).filter((url) => url?.endsWith('.exe'));
    assert(downloads.includes(prefix + installer));
    assert(downloads.every((url) => url === prefix + installer));
    const schema = [...html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>(.*?)<\/script>/gs)].map((m) => JSON.parse(m[1]));
    assert(schema.length > 0);
    const app = schema.find((s) => s['@type'] === 'SoftwareApplication');
    if (app) {
      assert.equal(app.softwareVersion, release.version);
      assert.equal(app.downloadUrl, prefix + installer);
      assert.equal(app.offers.price, '0');
      assert(!app.aggregateRating);
    }
  }
  assert(pages[1].replaceAll('&quot;', '"').includes(`Get-FileHash "$HOME\\Downloads\\${installer}" -Algorithm SHA256`));
  const heroDownload = pages[0].match(/<div class="pick">(.*?)<\/div>/s)?.[1];
  assert(heroDownload);
  assert.equal(tags(heroDownload, 'a').length, 1);
  assert.match(heroDownload, /Download for Windows/);
  assert.match(heroDownload, /NVIDIA graphics card needed for GPU acceleration/);
  assert(!heroDownload.includes('CPU edition'));
});

test('local links, anchors, images and bundles resolve inside the build', () => {
  for (const [i, html] of pages.entries()) {
    for (const tag of [...tags(html, 'a'), ...tags(html, 'link'), ...tags(html, 'img'), ...tags(html, 'script')]) {
      const value = tag.href || tag.src;
      if (!value || /^(https?:|mailto:|data:)/.test(value)) continue;
      const url = new URL(value, `https://vox0.app${routes[i]}`);
      const file = join(out, url.pathname, url.pathname.endsWith('/') ? 'index.html' : '');
      assert(existsSync(file), `${routes[i]} links to missing ${value}`);
      if (url.hash) {
        assert.match(readFileSync(file, 'utf8'), new RegExp(`id="${url.hash.slice(1)}"`));
      }
    }
    for (const img of tags(html, 'img')) {
      assert('alt' in img);
      const png = readFileSync(join(out, img.src));
      assert(Number(img.width) > 0 && Number(img.height) > 0, img.src);
      assert.equal(Number(img.width) / Number(img.height), png.readUInt32BE(16) / png.readUInt32BE(20), img.src);
    }
  }
});

test('sitemap and robots expose only canonical content; 404 stays excluded', () => {
  const index = readFileSync(join(out, 'sitemap-index.xml'), 'utf8');
  assert(index.includes('https://vox0.app/sitemap-0.xml'));
  const sitemap = readFileSync(join(out, 'sitemap-0.xml'), 'utf8');
  assert.deepEqual([...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map((m) => m[1]).sort(), routes.map((r) => `https://vox0.app${r}`).sort());
  assert(!sitemap.includes('<lastmod>'));
  assert.match(readFileSync(join(out, 'robots.txt'), 'utf8'), /Sitemap: https:\/\/vox0\.app\/sitemap-index\.xml/);
  assert.match(metadata(readFileSync(join(out, '404.html'), 'utf8'), 'robots'), /noindex/);
  assert(existsSync(join(out, 'googlece489537988ffecf.html')));
});

test('legacy URLs redirect to their matching page', () => {
  const config = JSON.parse(readFileSync('vercel.json', 'utf8'));
  for (const [source, destination] of [['/index.html', '/'], ['/install.html', '/install/'], ['/vox0/install.html', '/install/']]) {
    assert(config.redirects.some((r) => r.source === source && r.destination === destination && r.permanent));
  }
  assert.equal(config.outputDirectory, 'dist');
});
