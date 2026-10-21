# Domain-root robots.txt

Vox0's project site is served from `main:/docs` at
`https://bryramirezp.github.io/kara/`. Crawlers consult robots.txt at the host
root, not at `/kara/robots.txt`.

Publish the adjacent `robots.txt` at the root of the public repository
`bryramirezp/bryramirezp.github.io`, then enable GitHub Pages from that branch's
root. Do not replace an existing root robots.txt without preserving its rules
and other sitemap declarations.

Verify that `https://bryramirezp.github.io/robots.txt` returns HTTP 200 and
contains the Vox0 sitemap URL. The sitemap must also return HTTP 200.
The copy in Vox0's `docs/` is not a host-root crawler configuration.

Until the root file is published, submit
`https://bryramirezp.github.io/kara/sitemap.xml` directly in Google Search
Console. A missing root robots.txt does not block crawling.
