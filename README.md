# EIDORA website

The post-release landing page is developed on `landing_page`. The current
GitHub Pages site on `main` stays live until this branch is merged for launch.
The download infrastructure is available separately on
`feature/release-download-infrastructure` (website PR #1), based on the current
placeholder. Merge it into this branch before the landing-page launch.
The build accepts a placeholder without download markers and replaces the cards
when the landing page supplies one ordered marker pair.

The site is plain HTML and CSS. A small Python build generates release pages from
`updates.json`; no third-party packages or browser JavaScript are required.

## Edit and preview

- `index.html` contains the landing-page copy and resources. Keep its download
  markers so the build can insert the current catalog without changing the design.
- `updates.json` owns release information; see [release infrastructure](RELEASES.md).
- `styles.css` contains layout and named brand colors, with tablet and mobile rules at the end.
- `assets/brand/` contains approved artwork and its color reference.
- `assets/images/discovery-preview.png` is the temporary July 2026 application screenshot.

From this directory, run `python3 scripts/build_site.py`, then
`python3 -m http.server 8000 --directory _site` and open <http://localhost:8000>.
Rebuild after editing. Stop the server with Ctrl+C.

## Update downloads

Edit `updates.json`, then build and preview. The landing-page download section,
`/download/`, `/releases/`, and the public JSON are generated together. Do not
maintain separate version labels or download URLs in `index.html`.

Follow [RELEASES.md](RELEASES.md) for the catalog contract, preparation command,
Windows Store availability, checksums, validation, and GitHub Pages launch setup.
Installer files remain in GitHub Releases; Windows links to Microsoft Store.

## Update the screenshot and resources

Replace the preview with a current, uncropped screenshot. Update both image links,
the image's intrinsic width and height, its alt text, and the dated caption together.
Keep the full-size image available. Review example data and attribution before launch.

Getting-started and citation resources are explicitly unavailable. When ready,
replace their non-clickable articles with links using the existing resource-card
pattern, update their availability text, and check each destination. Do not invent
a publication, DOI, or installation requirements.

## Brand asset provenance

The following assets were copied unchanged from `/Users/yr38osif/Documents/eidora/design`:

- `eidora_logo.svg`, `eidora_wordmark.svg`, `eidora_icon.svg`, `eidora_icon.png`, and
  `eidora_colors.md` → `assets/brand/` with the same names.
- `icons/Windows/png/eidora_icon_16.png` → `assets/brand/favicon-16.png`.
- `icons/Windows/png/eidora_icon_32.png` → `assets/brand/favicon-32.png`.

The 16 px favicon is the approved simplified small mark; the 32 px favicon retains
the instrument. Do not regenerate both from a single large icon. The color reference
is an unchanged design document; its original relative links refer to the design
workspace, not this website.

The screenshot was copied unchanged from
`/Users/yr38osif/Documents/eidora/paper/figures/screenshot_eidora.png`.
The navigation rings around the hero logo are decorative CSS; they do not alter
or become part of the approved artwork.

## Review and publish

Check the page at 320, 390, 768, and 1440 px widths, keyboard navigation, visible
focus, expanded FAQ answers, text contrast, and operation with JavaScript disabled.
Verify all internal links, images, and enabled release links. Replace or explicitly
review every remaining availability label before launch.

Keep `request-access.html`, the root `EIDORA_logo.svg` it uses, and `CNAME` unchanged.
No changes to the existing access form or its external service are needed.

When ready to launch, follow the reviewed GitHub Pages launch procedure in
[RELEASES.md](RELEASES.md), retain the GitHub Actions Pages configuration, and merge
`landing_page` into `main`. The workflow tests and builds the static site before
publishing `_site/`. Preserve `CNAME` (`www.eidora.org`). Development alone does
not publish the new landing page. Leave work uncommitted until reviewed.
