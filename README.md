# EIDORA website

GitHub Pages hosts the existing homepage, platform downloads, release history,
and the desktop application's update catalog. Installers live in GitHub Releases;
Windows links to Microsoft Store. The site uses HTML, CSS, and a Python
standard-library build, with no browser JavaScript or third-party build packages.

## Edit and preview

Run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 -m http.server 8000 --directory _site
```

Open <http://localhost:8000>. Rebuild after editing; stop the server with Ctrl+C.
Check `/download/`, `/releases/`, and `/updates.json` as well as the homepage.

`updates.json` owns all public release information. See [RELEASES.md](RELEASES.md)
for verified artifacts, per-platform availability, checksums, Microsoft Store,
and the release preparation command. Do not advertise unpublished packages.

## Landing-page integration

The new landing page is being prepared separately on `landing_page`. This
infrastructure can ship while the existing homepage remains in use. Keep the
current access form, root logo, and `CNAME` unchanged.

The generated download and history pages use `styles.css`, `release-pages.css`,
and the approved artwork in `assets/brand/`. They share the new landing page's
styles so the eventual launch does not need a separate release-page redesign.

To include live download cards in the future homepage, link both stylesheets
and put these markers around its download cards:

```html
<!-- EIDORA DOWNLOADS START -->
<!-- EIDORA DOWNLOADS END -->
```

The build replaces only the content between that single ordered marker pair.
Without markers, it copies the homepage unchanged. Partial or repeated markers
fail validation. Preserve `/download/`, `/releases/`, `/updates.json`, platform
anchors, and release anchors when changing the homepage.

No application screenshots are included in this infrastructure branch.

## Brand assets

The SVG logos, wordmark, icon, PNG icon, and color reference in `assets/brand/`
are approved artwork copied unchanged from the EIDORA design workspace. The
16 px and 32 px favicons use its corresponding Windows PNG icons. Keep the
simplified 16 px mark rather than regenerating both sizes from the large icon.
The color reference's original relative links refer to the design workspace.

## Publish

Pull requests run tests and build the site. Merging reviewed changes into `main`
deploys `_site/` through GitHub Actions and the existing `github-pages` environment.
Feature and landing-page branches do not deploy. See [RELEASES.md](RELEASES.md)
for the existing domain, HTTPS, and environment settings.
