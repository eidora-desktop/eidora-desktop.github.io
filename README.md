# EIDORA website

EIDORA is open-source desktop research software for the visual exploration of
embedding spaces in cultural data. Researchers can import or compute vector
embeddings, interactively explore their projections, and prepare figures in a
local research environment.

This repository contains the EIDORA website, including its landing page,
download listings, and release history.

- [Website](https://www.eidora.org/)
- [Downloads and system requirements](https://www.eidora.org/#downloads)
- [Release history](https://www.eidora.org/releases/)
- [EIDORA application source code](https://github.com/eidora-desktop/EIDORA)

## Platforms

| Platform | Requirements |
| --- | --- |
| macOS · Apple Silicon | macOS 15 or later |
| macOS · Intel | macOS 15 or later |
| Windows · x64 | Windows 10 or 11 |
| Linux · x64 | Tested on Ubuntu 24.04 |

The website release history starts with EIDORA 0.2.6, labelled Prototype. Installers are
available for Apple Silicon and Intel Macs, Windows x64 through Microsoft Store,
and Linux x64 as AppImage and DEB. Earlier versions are no longer listed on the website.
The Linux builds were built and self-tested on Ubuntu 24.04; other distributions
and native installation remain unverified. Availability is listed separately for
each platform.

While stable downloads are unavailable, the homepage shows the latest experimental
installers labelled Prototype on each download card. Their release notes, checksums,
and installation details appear at `/releases/`, alongside all published versions
with their release types clearly labelled. `/experimental/` remains available for
experimental builds and is marked for search engines not to index. `/download/`
redirects to the homepage downloads section; the obsolete access-request page has
been removed. The public update feed keeps its existing format and publishes explicitly
recommended releases from the catalog: 0.2.6 for all four platforms, including
the confirmed Microsoft Store version for Windows.
Prototype labels are preserved; no application rebuild is required.
Follow [Publishing a new release](RELEASES.md#publishing-a-new-release-on-the-website)
for importing installers, adding Windows Store availability, setting app-update
recommendations, validating, deploying, and checking the live feed.

## About this repository

The website uses HTML and CSS, with a Python standard-library build that generates
download and release pages from [the update catalog](updates.json).
[Release information](RELEASES.md) describes the available download formats and
catalog fields. The [brand reference](assets/brand/eidora_colors.md) lists the
website's colors and artwork.
