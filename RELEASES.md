# EIDORA downloads and releases

[Downloads](https://www.eidora.org/download/) lists availability and system
requirements for each platform. [Release history](https://www.eidora.org/releases/)
provides version notes and links to stable installers.

Early builds appear separately at `/experimental/`, reached through the small
“Experimental builds” link in the homepage footer. This page warns that builds
are experimental and untested and requests `noindex, nofollow` from search engines.
It is publicly accessible to anyone with the URL; this is not access control.
Public GitHub release assets and this repository also remain discoverable.

Stable application downloads are coming soon. The experimental downloads offer
0.2.3 signed and notarized DMGs for Apple Silicon and Intel Macs, plus AppImage
and DEB installers for Linux x64. Windows remains unavailable. Earlier release
listings and assets are retired after local archival; Git tags and source history
remain available. The page groups downloads under the 0.2 series and
shows the latest full version for each platform.

All platform packaged tests passed. Signed Mac tests passed on Apple Silicon
and under Rosetta. Fresh manual installation checks on Intel hardware and Linux
remain unverified for 0.2.3. Linux packages were built and
self-tested on Ubuntu 24.04; broader distribution support is not claimed.
Every download includes its size and expandable SHA-256 checksum.

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
machine-readable stable release information for the desktop application. The same
stable data appears on the main download and release pages. The source
`updates.json` also holds prototype and preview records; the build routes these
only to the experimental page and excludes them from the published update feed.
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

## Adding an experimental installer

Publish the installer as a GitHub prerelease in the application repository, using
the versioned asset names required by the catalog (for example,
`EIDORA-0.2.0-macos-arm64.dmg`). Import its verified metadata with:

```sh
python scripts/prepare_release.py --version 0.2.0 --platform macos-arm64 \
  --requirements "macOS 15 or later" --channel prototype
```

Use the actual version, platform, and verified requirements for your build.
The importer obtains the asset URL, size, and checksum from GitHub. Commit the
updated catalog with the website changes; the normal Pages build generates the
experimental downloads. `preview` also goes to this page. Only use `stable` when
you intend a release to appear in the main downloads and public update feed.

Run `python -m unittest discover -s tests -v` and
`python scripts/build_site.py` to check the catalog and generated pages locally.
