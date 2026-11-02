# EIDORA downloads and releases

[Downloads](https://www.eidora.org/#downloads) lists availability and system
requirements for each platform. [Release history](https://www.eidora.org/releases/)
provides notes, checksums, installation instructions, and downloads for all
published versions, including clearly labelled prototypes and previews. The old
`/download/` URL redirects to the homepage downloads section.

Early builds also appear at `/experimental/`, reached through the
“Experimental builds” link in the footer. When no stable installers
are available, the homepage offers the latest experimental builds labelled
Prototype on each download card. The `/experimental/` page warns that builds
are experimental and untested and requests `noindex, nofollow` from search engines.
It is publicly accessible to anyone with the URL; this is not access control.
Public GitHub release assets and this repository also remain discoverable.

The public release history begins with **EIDORA 0.2.4**, the first public release,
labelled Prototype. Its release notes introduce the software and available
workflows rather than describe changes from internal builds. Pre-launch versions
are excluded from the website catalog and release history.

Downloads include signed and notarized DMGs for Apple Silicon and Intel Macs,
AppImage and DEB installers for Linux x64, and Windows x64 through
[Microsoft Store](https://apps.microsoft.com/detail/9P0WFNT5DZS5) (Store package
version 1.2.5.0). The experimental page groups downloads under the 0.2 series
and shows the latest full version for each platform.

All platform packaged tests passed, including UMAP and video-thumbnail checks.
Signed Mac tests passed on Apple Silicon and under Rosetta. Fresh manual
installation checks on Intel hardware and Linux
remain unverified for 0.2.4. Linux packages were built and
self-tested on Ubuntu 24.04; broader distribution support is not claimed.
The 0.2.5 Mac/Linux update fixes macOS cursor crashes, model-download
responsiveness, welcome-tour resets, and update-version messages. Both signed
Mac architectures passed offscreen and native Cocoa runtime checks; Intel ran
under Rosetta. Manual installation checks remain separate.

Mac/Linux downloads include their size and expandable SHA-256 checksum.
Microsoft Store manages Windows installation and updates; the MSIX is not hosted
as a direct website download. The Microsoft Store button uses Microsoft’s
`ms-windows-store` product link to request the native Store app on Windows.
“View in browser” opens the Store website in a new tab. Store acceptance does not replace separately
recorded installed-Windows QA or WACK evidence.

## Download formats

| Platform | Distribution |
| --- | --- |
| macOS · Apple Silicon and Intel | DMG installers hosted in the [EIDORA releases](https://github.com/eidora-desktop/EIDORA/releases) |
| Windows · x64 | Microsoft Store |
| Linux · x64 | AppImage and DEB packages hosted in the [EIDORA releases](https://github.com/eidora-desktop/EIDORA/releases) |

Availability may differ by platform. Microsoft Store links lead to the current
Store version, rather than historical Windows packages. Mac and Linux downloads
identify a specific version and include file sizes and SHA-256 checksums.

## Update catalog

The public [update catalog](https://www.eidora.org/updates.json) provides
machine-readable recommendations for the desktop application. Its schema remains
unchanged; no application code changes are needed. The feed uses the source
catalog's explicit `latest` entries and includes their referenced release records,
regardless of whether they are labelled prototype, preview, or stable. Currently,
All four platforms recommend 0.2.5, retaining its Prototype label.
The maintainer confirmed Windows Store availability on 2026-11-02.
Adding a release record alone does not offer an update: update `latest` for each intended platform.
Unrecommended historical records stay in website release history, outside the feed.
The homepage prefers stable downloads, falling back to experimental builds while
stable installers are unavailable. This display choice does not control app updates.
For each channel group, the build uses the recommended version when it belongs
to that group, or the highest available matching version for that platform.

| Field | Meaning |
| --- | --- |
| `schema_version` | Catalog format version, currently `1` |
| `latest` | Recommended version for each platform, or `null` when none is available |
| `releases` | Release records keyed by `MAJOR.MINOR.PATCH` version |
| `channel` | Release designation: `prototype`, `preview`, or `stable` |
| `published_at` | Publication date in `YYYY-MM-DD` format |
| `notes` | Plain-text release notes |
| `platforms` | Available platforms and their requirements |
| `requirements` | Operating-system and runtime requirements for a build |
| `downloads` | Mac/Linux installer format, filename, URL, byte size, and SHA-256 checksum |
| `store_url` | Windows application listing in Microsoft Store |

Platform identifiers are `macos-arm64`, `macos-x86_64`, `windows-x86_64`, and
`linux-x86_64`. Recommended versions can differ between platforms.

## Publishing a new release on the website

Run these steps in the website repository. No EIDORA application code changes or
rebuild are needed to publish an update recommendation using the existing schema.
Edit the source `updates.json`, never `_site/updates.json`: `_site/` is regenerated
on every build and is not committed.

### 1. Publish and verify the application distributions

Publish the application GitHub release at tag `vMAJOR.MINOR.PATCH` (not a draft).
Use these exact asset names, replacing `VERSION` with the application version:

- `EIDORA-VERSION-macos-arm64.dmg`
- `EIDORA-VERSION-macos-x86_64.dmg`
- `EIDORA-VERSION-linux-x86_64.AppImage`
- `EIDORA-VERSION-linux-x86_64.deb`

Confirm the assets are downloadable and their requirements and release notes are
accurate. Keep published installer contents immutable; changed binaries need a new
version. For Windows, confirm that the intended version is available in Microsoft
Store before recommending it. Store submission alone is not publication.

### 2. Import each available Mac/Linux platform

For example, for a future **0.2.5** prototype (substitute the actual version and
verified requirements):

```sh
python3 scripts/prepare_release.py --version 0.2.5 --platform macos-arm64 \
  --requirements "macOS 15 or later" --channel prototype
python3 scripts/prepare_release.py --version 0.2.5 --platform macos-x86_64 \
  --requirements "macOS 15 or later" --channel prototype
python3 scripts/prepare_release.py --version 0.2.5 --platform linux-x86_64 \
  --requirements "Linux x64 (tested on Ubuntu 24.04)" --channel prototype
```

The importer reads the date, release notes, asset URLs, sizes, and SHA-256 digests
from GitHub. **Each invocation also sets `latest[platform]` to the imported
version**, making that platform an app-update recommendation once deployed.
Only run imports for platforms ready to publish; leave other recommendations at
their previous working versions. To archive a release without recommending it,
restore that platform's previous `latest` value before committing.

Use `prototype`, `preview`, or `stable` according to the release designation.
A GitHub prerelease cannot be imported as stable. Prototype and preview releases
can be recommended to the app; do not relabel them stable just to populate the feed.
If imports report differing release metadata, review the existing record and the
GitHub notes/date/channel before reconciling them. Import all available platforms
before making any intentional website-specific edits to the shared release notes.

### 3. Add Windows when the Store version is available

The importer does not handle Windows. In the new release's `platforms` object,
add the verified Windows entry:

```json
"windows-x86_64": {
  "requirements": "Windows 10 or 11 · x64",
  "store_url": "https://apps.microsoft.com/detail/9P0WFNT5DZS5"
}
```

Then set `latest["windows-x86_64"]` to the application version, such as `"0.2.5"`.
Use the EIDORA application version, not the Store package version (for example,
0.2.4 rather than 1.2.4.0). Do not add a `downloads` array or an MSIX asset.
If Windows ships first, create its release record with `published_at`, `channel`,
`notes`, and `platforms`; later Mac/Linux imports must agree with that metadata.

### 4. Review recommendations and generated pages

Keep public release records from 0.2.4 onward for website history; do not reintroduce
pre-launch versions. Future notes may describe changes since the preceding public
release. Each non-null `latest` entry
must reference a release that actually contains that platform. The public feed
includes exactly the release records referenced by `latest`, preserving their
channel labels. It does not automatically recommend every new experimental build.

When intentionally replacing 0.2.4 as the recommendation, update the explicit
publication regression in `tests/test_site.py`
(`test_published_feed_recommends_025_for_every_platform`), including its name and
expected per-platform versions. For staggered releases, assert the intended mixed
recommendations instead of requiring every platform to have the same version.

Regenerate the checked-in homepage cards for local file previews:

```sh
python3 - <<'PYCODE'
import json
import sys
from pathlib import Path
sys.path.insert(0, "scripts")
from build_site import catalog_for_channels, render_landing_downloads
catalog = json.loads(Path("updates.json").read_text())
page = Path("index.html")
page.write_text(render_landing_downloads(
    page.read_text(),
    catalog_for_channels(catalog, {"stable"}),
    catalog_for_channels(catalog, {"prototype", "preview"}),
))
PYCODE
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py
python3 -m json.tool _site/updates.json
git diff --check
```

Check that the generated feed has the intended recommendations and that each
referenced record has the correct notes, platform requirements, and distributions.
Preview `_site/` with `python3 -m http.server 8000 --directory _site`:

- `/`: current download cards and working installer/Store links.
- `/releases/#vVERSION`: new version, channel label, notes, and checksums.
- `/experimental/`: prototype/preview downloads, when applicable.
- `/download/`: redirects to the homepage downloads section, including when opened
  by the app with a platform fragment.

Homepage selection is independent of the update feed: it prefers stable releases
and only falls back to experimental releases when no stable downloads exist.
Review this distinction when publishing a preview newer than the stable version.

### 5. Deploy and verify the live feed

Commit the reviewed source catalog, regenerated `index.html`, relevant test updates,
and documentation. Push a branch, open a pull request, and merge after its checks
pass. The `Validate and deploy website` workflow deploys GitHub Pages on pushes to
`main`; a branch push or successful PR build alone does not publish the feed.

After the deployment succeeds, fetch the exact URL used by the application:

```sh
curl -fsSL https://eidora.org/updates.json -o /tmp/eidora-live-updates.json
python3 -m json.tool /tmp/eidora-live-updates.json
```

Compare its `latest` entries and referenced records with `_site/updates.json`.
Verify the live release-note anchors and download links too. An older application
version should offer the recommended newer version; the recommended version should
report that it is current. This can be checked with the existing application
`application_info.service.parse_release` function without editing application code,
or using Check for Updates in the installed app. Windows installation and updates
continue to be managed by Microsoft Store.

If a recommendation must be withdrawn, restore only the affected `latest` entries
to the previous available versions (or `null` if none), validate, and redeploy.
Keep historical records and never silently replace already published binaries.
