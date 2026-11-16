# EIDORA downloads and releases

## Distribution paused

EIDORA 0.3.0 will be the first official release. Until it is ready, the homepage,
`/releases/`, and `/experimental/` show “Coming soon” with no installer or Store
links. `/download/` redirects to the homepage downloads section.

The catalog is intentionally empty: every `latest` value is `null` and `releases`
is `{}`. This also withdraws all app-update recommendations without changing the
feed schema. Previous application GitHub releases are unpublished drafts; their assets and
version tags are preserved. Starter datasets remain separate. Website changes do not unpublish the
Microsoft Store listing or prevent Store-managed updates.

Do not restore withdrawn pre-launch releases. To resume distribution, publish and
verify 0.3.0, then follow the steps below. Catalog entries restore download cards
and release pages automatically; update the homepage resource card, this status,
the README, and the publication regression to reflect availability.

## Update catalog

The public [update catalog](https://www.eidora.org/updates.json) provides
machine-readable recommendations for the desktop application. Its schema remains
unchanged. Adding a release record alone does not recommend an app update:
set `latest` for each verified platform. The homepage prefers stable releases
and falls back to experimental builds when available, independently of the feed.
An empty catalog shows the coming-soon notice on every distribution page.

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

For example, for the first official **0.3.0** release (substitute the actual version and
verified requirements):

```sh
python3 scripts/prepare_release.py --version 0.3.0 --platform macos-arm64 \
  --requirements "macOS 15 or later" --channel stable
python3 scripts/prepare_release.py --version 0.3.0 --platform macos-x86_64 \
  --requirements "macOS 15 or later" --channel stable
python3 scripts/prepare_release.py --version 0.3.0 --platform linux-x86_64 \
  --requirements "Linux x64 (tested on Ubuntu 24.04)" --channel stable
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

Then set `latest["windows-x86_64"]` to the application version, such as `"0.3.0"`.
Use the EIDORA application version, not the Store package version (for example,
0.3.0 rather than its Store package version). Do not add a `downloads` array or an MSIX asset.
If Windows ships first, create its release record with `published_at`, `channel`,
`notes`, and `platforms`; later Mac/Linux imports must agree with that metadata.

### 4. Review recommendations and generated pages

Keep available public releases for website history. When the maintainer withdraws
a release, archive its metadata and validation evidence before removing its
download catalog record and public release. Do not reintroduce withdrawn or
pre-launch versions. Future notes may describe changes since the preceding public release. Each non-null `latest` entry
must reference a release that actually contains that platform. The public feed
includes exactly the release records referenced by `latest`, preserving their
channel labels. It does not automatically recommend every new experimental build.

When changing a platform recommendation, update the explicit
publication regression in `tests/test_site.py`
(`test_distribution_pause_removes_downloads_and_update_recommendations`), including its name and
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
