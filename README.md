# EIDORA website

EIDORA is open-source desktop research software for the visual exploration of
embedding spaces in cultural data. Researchers can import or compute vector
embeddings, interactively explore their projections, and prepare figures in a
local research environment.

This repository contains the EIDORA website, including its landing page,
download listings, and release history.

- [Website](https://www.eidora.org/)
- [Downloads and system requirements](https://www.eidora.org/download/)
- [Release history](https://www.eidora.org/releases/)
- [EIDORA application source code](https://github.com/eidora-desktop/EIDORA)

## Platforms

| Platform | Requirements |
| --- | --- |
| macOS · Apple Silicon | macOS 15 or later |
| macOS · Intel | macOS 15 or later |
| Windows · x64 | Windows 10 or 11 |
| Linux · x64 | Requirements will accompany the public release |

Stable application downloads are coming soon. Experimental installers are available
for Apple Silicon and Intel Macs (0.2.0), plus Linux x64 as AppImage and DEB (0.2.1).
The Linux builds were built and self-tested on Ubuntu 24.04; other distributions
and native installation remain unverified. Availability is listed separately for
each platform.

Prototype and preview installers have a separate `/experimental/` page, linked
discreetly from the homepage footer and marked for search engines not to index.
It is publicly accessible, with a warning that builds are experimental and
untested. Only stable releases appear in the main downloads and public update
feed. See [release information](RELEASES.md) for how to add installer files.

## About this repository

The website uses HTML and CSS, with a Python standard-library build that generates
download and release pages from [the update catalog](updates.json).
[Release information](RELEASES.md) describes the available download formats and
catalog fields. The [brand reference](assets/brand/eidora_colors.md) lists the
website's colors and artwork.
