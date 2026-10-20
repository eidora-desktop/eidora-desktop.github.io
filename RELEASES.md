# Website releases and application updates

The website is hosted by GitHub Pages in
`eidora-desktop/eidora-desktop.github.io`. Application installers belong to
GitHub Releases in `eidora-desktop/EIDORA`; Windows is distributed through
Microsoft Store. The website never hosts an EXE or a Store submission MSIX.

## Public URLs

- `https://eidora.org/download/`: platform downloads and installation instructions.
- `https://eidora.org/releases/`: notes and previous Mac/Linux versions.
- `https://eidora.org/updates.json`: versioned catalog consumed by EIDORA.

Keep the existing `www.eidora.org` CNAME. GitHub Pages redirects the apex domain
to www, including the requested path. Both names must continue to support HTTPS.
The desktop client accepts HTTPS redirects. Do not move these public paths when
redesigning the landing page.

## Catalog v1

`updates.json` is the sole publication catalog. The build validates it, generates
the download/history pages, and copies the identical JSON into the published
artifact. A landing page can also embed catalog-generated download cards using
the markers described in README.md; the current placeholder needs no markers.
Users can view
all downloads without browser JavaScript. No database or server application is
needed, and visitors do not call the GitHub API.

The initial catalog deliberately contains no application releases. The starter
collection release is a dataset and must not be offered as an application update.
A prepared source version is not evidence of public availability.

- `schema_version`: integer `1`. Coordinate changes with the desktop parser.
- `latest`: all four platform keys, each containing a recommended version or `null`.
  Keys: `macos-arm64`, `macos-x86_64`, `windows-x86_64`, `linux-x86_64`.
  A null means no public application release is available for that platform.
- `releases`: objects keyed by numeric `MAJOR.MINOR.PATCH` (without `v`). Each has:
  - `channel`: `prototype`, `preview`, or `stable`. The recommendation is explicit;
    prototype releases are not suppressed just because GitHub calls them prereleases.
  - `published_at`: actual release date in `YYYY-MM-DD` format.
  - `notes`: nonempty plain text, escaped during HTML generation.
  - `platforms`: only verified, available platforms for that release.
- Each platform has `requirements`: verified OS/runtime requirements as plain text.
- Mac/Linux platforms have `downloads`: one object per published installer with
  `format` (`dmg`, `deb`, or `AppImage`), `name`, exact versioned GitHub `url`,
  `size` in bytes, and lowercase hex `sha256`. These must describe final signed
  bytes where signing applies. Both Linux formats can be listed; either can be
  omitted if not published. Never mix versions within a platform entry.
- Windows has a verified `store_url` of the form
  `https://apps.microsoft.com/detail/PRODUCT_ID` and no `downloads`.
  Use the public application version, not the four-part MSIX submission version.

Latest pointers may differ by platform. For example, keep Windows on its currently
available version while a newer release is awaiting Store certification. Add the
Windows platform and move its pointer only after confirming actual Store availability.
Old Windows entries link to the live Store listing, not to historic installable packages;
the history page states this distinction.

Keep historical records when adding releases. Moving a latest pointer back after
a withdrawn release does not force installed applications to downgrade. The app
reports that the installed version is newer than the recommended release.

## Prepare a Mac/Linux release

Publish only after the existing private release validation, signing, and approval
process has completed. Upload final files to the public application release.

Run this for each platform that is actually available, substituting the approved
version and verified requirements (these placeholders are not release claims):

```sh
python3 scripts/prepare_release.py --version MAJOR.MINOR.PATCH \
  --platform macos-arm64 --channel prototype \
  --requirements 'Verified minimum macOS version and architecture'
```

The helper fetches the exact public `vMAJOR.MINOR.PATCH` release through GitHub's
API. It requires published, uploaded assets and GitHub SHA-256 digests, validates
filenames and URLs, and changes only the selected platform's recommendation.
It does not commit, push, or deploy. Review checksums against the approved private
release receipt and `SHA256SUMS`; API digests are integrity information, not a
separate signing authority. If a digest is unavailable, stop and verify it manually
before editing the catalog; never invent a checksum.

For Windows, edit the corresponding release's `platforms.windows-x86_64` with the
verified requirements and real Store URL, then update `latest.windows-x86_64`.
The Store publication can happen later than the release's original date.

Run:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 -m http.server 8000 --directory _site
```

Check the landing page, `/download/`, `/releases/`, and `/updates.json`. Test the
specific download links and compare the catalog to public platform availability.
Review changes before committing or merging. Published download URLs remain
version-specific; never overwrite an existing installer with changed contents.

## GitHub Pages setup and launch

The Pages workflow `.github/workflows/pages.yml` builds with Python's standard
library and publishes only `_site/`. It validates pull requests without deployment.
Pushes to `main` and manual runs on `main` can deploy through the `github-pages`
environment. Other branches, including `landing_page`, cannot deploy.
Actions are pinned to commit SHAs. The build has read-only repository access;
only the deployment job receives `pages: write` and `id-token: write`.
No personal token, release signing key, or private release-repository access is needed.

Pages is configured for **GitHub Actions**, with **Enforce HTTPS** enabled,
custom domain `www.eidora.org`, and the existing `github-pages` environment
restricted to `main`. Retain these settings. The previous placeholder remains
served until the reviewed website build is deployed. If recreating the site,
apply these same settings in Settings → Pages and Settings → Environments.

Merge the reviewed website changes into `main`, inspect the workflow's deployment
result, and verify both domain names and the three public paths. Do not merge the
unfinished landing-page work merely to publish infrastructure. Until this launch,
the placeholder may return 404 for updates.json; EIDORA reports that explicitly.

Do not upload `_site/` or test screenshots into Git. Installer binaries belong
in application release assets, never in the website checkout or Pages artifact.
The build copies only site files and assets; scripts, tests, and documentation
are excluded from the hosted site.
