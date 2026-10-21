---
name: seo
description: Improve a website's search discovery with technical SEO, accurate metadata, structured data, content and competitor comparisons. Use for SEO audits, indexability, sitemap or robots checks, and search-focused website edits in this project.
license: MIT
metadata:
  source: https://github.com/AgriciDaniel/claude-seo
  upstream-version: "2.4.2"
  upstream-commit: c167521da73bf560660b1dbb0a7650f7b37b1eb5
---

# SEO for Vox0

Project-local Codex adaptation of AgriciDaniel's Claude SEO v2.4.2. The upstream
MIT license is in [LICENSE.txt](LICENSE.txt). This installation retains the
analysis references; Claude Code commands, agents, hooks, Python runtime and
paid integrations are not installed. Use the available source, web and browser
tools. No additional Python packages are needed for these workflows.

## Project context

- The public site is static HTML in `docs/`, served at
  `https://bryramirezp.github.io/kara/`. `docs/index.html` is the landing page and
  `docs/install.html` is the installation guide. `README.md` repeats product copy.
- Position Vox0 as free, open source offline Whisper dictation for Windows:
  hold a key, speak, release, and insert text into the active app. Transcription
  runs locally after a one-time model download; no account or subscription.
- The source app and modules use Vox0 (`vox0.py`, `vox0i18n.py`, `vox0text.py`).
  Installers through 0.3.5 use Kara; 0.3.6 uses Vox0. Preserve legacy data paths
  and immutable historical artifact URLs when updating the current release.
- Wispr Flow is the relevant comparison for dictating into apps. Use its correct
  name, verify claims against current official sources and date comparisons.
  Distinguish local transcription from AI rewriting and cross-device features;
  do not imply feature parity or affiliation. Do not add unrelated competitors
  just to target their names.
- Follow the repository's `AGENTS.md`. Keep versioned download links intact.
  SEO maintenance belongs in the technical report, not product release notes.

## Workflow

1. Establish the page, intended audience and search intent. Inspect the current
   HTML, README, robots.txt, sitemap and relevant local changes before editing.
2. Review live HTTP responses when available: status, redirects, canonical URL,
   indexability and discoverable internal links. Crawlers consult `/robots.txt`
   at the host root, not the project path. A missing robots.txt does not itself
   block crawling. The root deployment instructions are in
   `packaging/github-pages-root/README.md`.
3. Keep titles, descriptions, headings, visible answers and JSON-LD consistent.
   Prefer useful descriptive copy over keyword repetition. Keep the first model
   download explicit wherever making an offline claim. Use original screenshots
   and accurate product capabilities; never invent ratings, users or benchmarks.
4. For comparisons, read [competitor-pages.md](references/competitor-pages.md).
   Link official sources for competitor claims. Treat numeric title lengths,
   keyword density and word counts as heuristics, not ranking requirements.
5. Read only references relevant to the task: [schema types](references/schema-types.md),
   [content quality](references/eeat-framework.md),
   [quality gates](references/quality-gates.md), or
   [Core Web Vitals](references/cwv-thresholds.md).
   Verify dated search-engine policies in current official documentation before
   acting on the bundled references. Structured data must match visible content;
   FAQ markup alone is not evidence of rich-result eligibility.
6. Validate edited HTML, JSON-LD, local links, mobile layout and download URLs.
   `python tools/stamp_docs.py --check` checks release facts and sitemap dates;
   its sitemap dates come from Git commits, so do not stamp a new date for an
   uncommitted edit. Preserve that release workflow.
7. Report confirmed findings with file/line evidence, changes, checks and any
   unverified live state. Do not invent SEO scores, traffic or measured Core Web
   Vitals. Installing this skill does not submit a site to search engines or
   guarantee indexing; distinguish local changes from published results.
