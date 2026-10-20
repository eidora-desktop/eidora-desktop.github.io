# EIDORA downloads and releases

[Downloads](https://www.eidora.org/download/) lists availability and system
requirements for each platform. [Release history](https://www.eidora.org/releases/)
provides version notes and links to published installers.

Public application downloads are coming soon; the catalog currently contains no
releases.

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
machine-readable release information for the desktop application. The same data
appears on the download and release pages.

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
