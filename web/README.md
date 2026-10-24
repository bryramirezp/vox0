# Vox0 website

Astro generates the landing page and installation guide as static HTML for
`https://vox0.app/`. The desktop application remains at the repository root.
The website builds into `web/dist/`; the root `dist/` contains Windows installers
and must never be used as Vercel's output directory.

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
download: the NVIDIA installer, which includes CPU fallback. The local 0.3.7 build
is not a public download. Do not publish links to an installer before it exists.

After a new release and its assets have been published and verified, run from
the repository root, using the actual released version:

```powershell
.venv/Scripts/python.exe tools/stamp_docs.py --web-release 0.3.7
.venv/Scripts/python.exe tools/stamp_docs.py --check --web-release 0.3.7
npm run build:site
```

This updates the manifest along with the existing release documentation. Releases
after 0.3.6 use the single versioned installer. Normal application builds leave the
public website's manifest unchanged. `tools/capture_demo.py`, `tools/screenshots.py`
and `tools/make_logo.py` update both the Astro assets and legacy Pages assets during
the transition. Review captured content and images before publishing.

## Vercel

Import `bryramirezp/vox0` with **Root Directory = `web`**. `vercel.json` sets Astro,
`npm ci`, `npm run build`, and output `dist`. Production should use `main` once the
website source is committed. Deployments uploaded directly from local files do
not establish a Git integration; connect the repository only after those files
exist remotely.

Add `vox0.app` as the production domain and `www.vox0.app` as a permanent redirect
to it. Use the DNS targets shown by Vercel for this project; keep existing mail
and verification records. Verify HTTPS and both hostnames after propagation.

Astro uses `https://vox0.app` for all canonical, sitemap and social URLs.
Vercel previews include `noindex, follow` in page metadata; production pages are
indexable. Robots allows crawling so the preview's `noindex` can be observed.
The 404 page is always excluded from indexing and from the sitemap.
Sitemaps omit `lastmod` rather than claiming every build changed the content.

## Move from GitHub Pages

The new domain passed its HTTPS checks. `docs/index.html` and `docs/install.html`
now keep their legacy content and use immediate refresh with canonical URLs to
send visitors and crawlers to the matching Astro page. GitHub Pages continues
serving `main:/docs`; it is not a second Astro source directory.
Do not point Pages or Vercel at the desktop application's compiled payload.

| Previous URL | New URL |
| --- | --- |
| `https://bryramirezp.github.io/vox0/` | `https://vox0.app/` |
| `https://bryramirezp.github.io/vox0/index.html` | `https://vox0.app/` |
| `https://bryramirezp.github.io/vox0/install.html` | `https://vox0.app/install/` |

Vercel redirects legacy `.html` and `/vox0` paths arriving on the new host.
Those rules cannot redirect requests received by GitHub Pages. The old host uses
immediate HTML refresh and matching canonical URLs because Pages does not provide
per-path HTTP redirect configuration. This is not an HTTP 301 or 308 response.

Verify the new domain in Google Search Console using the domain's DNS. The
preserved HTML verification file does not itself verify ownership of the new
domain. Submit `https://vox0.app/sitemap-index.xml`, inspect the home and guide URLs,
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
