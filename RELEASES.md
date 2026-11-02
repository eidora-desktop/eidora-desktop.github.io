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

Stable application downloads are coming soon. The experimental downloads offer
0.2.4 signed and notarized DMGs for Apple Silicon and Intel Macs, plus AppImage
and DEB installers for Linux x64. Windows 0.2.4 is available through
[Microsoft Store](https://apps.microsoft.com/detail/9P0WFNT5DZS5), with accepted
package version 1.2.4.0 confirmed by the maintainer. The previous
0.2.3 release remains archived in the catalog and on GitHub. The page groups
downloads under the 0.2 series and
shows the latest full version for each platform.

All platform packaged tests passed, including UMAP and video-thumbnail checks.
Signed Mac tests passed on Apple Silicon and under Rosetta. Fresh manual
installation checks on Intel hardware and Linux
remain unverified for 0.2.4. Linux packages were built and
self-tested on Ubuntu 24.04; broader distribution support is not claimed.
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
all four platforms recommend 0.2.4, retaining its Prototype label. Adding a release
record alone does not offer an update: update `latest` for each intended platform.
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
experimental downloads and the homepage fallback. `preview` also goes to this page. Use `stable` only for releases designated stable. App-update publication is
controlled separately by the catalog’s explicit `latest` entries.

Run `python -m unittest discover -s tests -v` and
`python scripts/build_site.py` to check the catalog and generated pages locally.
