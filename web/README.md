# Vox0 website

The Microsoft Store privacy page lives at `/privacy/`. Its source is
`src/pages/privacy.astro`. Verify the public URL after each authorized deployment
before using it in the Store submission. Store listing
copy and remaining submission work are in `../packaging/store-listing.md`.
Do not advance public download links while the MSIX trial is in progress.

Astro generates the landing page and privacy policy as static HTML for
`https://vox0.app/`. The desktop application remains at the repository root.
The website builds into `web/dist/`; the root `dist/` contains Windows installers
and must never be used as Vercel's output directory. The old installation guide
has been removed; `/install/` and its legacy URLs redirect to the home page.

## Local development

Use Node.js 24 (Astro 7 requires a recent Node release):

```powershell
cd web
npm ci
npm run dev
```

`npm run build` checks Astro and TypeScript, builds the site, and checks generated
HTML, structured data, download versions, assets, anchors and sitemaps.
`npm run preview` serves the production build locally.
From the repository root, `npm run dev:site`, `npm run build:site` and
`npm run preview:site` delegate to these commands after installing `web/` dependencies.

The layout owns search and social metadata. Pages own their visible content and
JSON-LD. Keep both consistent. Images have explicit aspect ratios, screenshots
below the fold load lazily, and the demo respects reduced motion. The site uses
system fonts and has no analytics or external JavaScript.

## Public releases

`src/data/release.json` describes the **published** installer, independently of
the unreleased version in `vox0.py`. At migration time the published version is
0.3.6, with separate immutable CPU and NVIDIA installers. The website offers one
download: the NVIDIA installer, which includes CPU fallback. MSIX 1.0.2 is in
Store certification and is not a public download yet. Switch the download button
to the verified Microsoft Store listing when installation becomes available.

After the Microsoft Store listing is live and verified, update the website's
download link and release metadata to that Store listing with authorization.
The existing `tools/stamp_docs.py --web-release` workflow maintains historical
EXE releases; do not use it to invent a GitHub EXE URL for an MSIX release.
Normal application builds leave the public website's manifest unchanged.
`tools/capture_demo.py`, `tools/screenshots.py`
and `tools/make_logo.py` update both the Astro assets and legacy Pages assets during
the transition. Review captured content and images before publishing.

## Vercel

Import `bryramirezp/vox0` with **Root Directory = `web`**. `vercel.json` sets Astro,
`npm ci`, `npm run build`, and output `dist`. GitHub is the source of truth:
push approved website source to `main`, then deploy that exact Git commit to the
existing Vercel project. Use its Git source rather than direct file uploads.
The user
authorized the privacy-page deployment on October 25, 2026 after testing MSIX
1.0.2. Keep public download links on the published EXE until the Store listing
is certified, live and verified.

Add `vox0.app` as the production domain and `www.vox0.app` as a permanent redirect
to it. Use the DNS targets shown by Vercel for this project; keep existing mail
and verification records. Verify HTTPS and both hostnames after propagation.

Astro uses `https://vox0.app` for all canonical, sitemap and social URLs.
Vercel previews include `noindex, follow` in page metadata; production pages are
indexable. Robots allows crawling so the preview's `noindex` can be observed.
The 404 page is always excluded from indexing and from the sitemap.
Sitemaps omit `lastmod` rather than claiming every build changed the content.

## Move from GitHub Pages

The new domain passed its HTTPS checks. Local changes in `docs/index.html` and
`docs/install.html` preserve legacy content and add immediate refresh with matching
canonical URLs. These changes have not been pushed. The user has chosen to retire
the old Pages website after the installer test and GitHub-to-Vercel cutover;
disable Pages hosting at that point, keeping repository history and assets used
by the README. Until then GitHub Pages continues serving `main:/docs`.
Do not point Pages or Vercel at the desktop application's compiled payload.

| Previous URL | New URL |
| --- | --- |
| `https://bryramirezp.github.io/vox0/` | `https://vox0.app/` |
| `https://bryramirezp.github.io/vox0/index.html` | `https://vox0.app/` |
| `https://bryramirezp.github.io/vox0/install.html` | `https://vox0.app/` |

Vercel redirects legacy `.html` and `/vox0` paths arriving on the new host.
Those rules cannot redirect requests received by GitHub Pages. The old host uses
immediate HTML refresh and matching canonical URLs because Pages does not provide
per-path HTTP redirect configuration. This is not an HTTP 301 or 308 response.

Verify the new domain in Google Search Console using the domain's DNS. The
preserved HTML verification file does not itself verify ownership of the new
domain. Submit `https://vox0.app/sitemap-index.xml`, inspect the home and privacy URLs,
and monitor the old and new properties. Indexing and field performance require
post-deployment observation; a passing local build does not establish either.

## Astro Docs MCP

The project's `.codex/config.toml` registers `astro-docs` with the HTTP URL
`https://mcp.docs.astro.build/mcp`. Reload the MCP connection or start a new Codex
session to load newly configured tools. The endpoint was checked with MCP
`initialize`, `tools/list` and a `search_astro_docs` call over HTTP.

References: [Astro on Vercel](https://docs.astro.build/en/guides/deploy/vercel/),
[Astro sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/),
[Astro Docs MCP](https://docs.astro.build/en/guides/build-with-ai/),
[Vercel domains](https://vercel.com/docs/domains/working-with-domains/add-a-domain),
[Google site moves](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes).
