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

## Distribution status

Downloads are paused while EIDORA 0.3.0 is prepared as the first official release.
The homepage, `/releases/`, and `/experimental/` show “Coming soon” without
installer or Microsoft Store links. `/download/` still redirects to the homepage.
The schema-1 update feed has `null` recommendations for every platform and no
release records, so it does not offer withdrawn versions to installed apps.

Previous application releases and version tags are being withdrawn from GitHub.
The separate starter datasets are not application releases. Removing website
Store links does not unpublish the Microsoft Store listing.

Follow [Publishing a new release](RELEASES.md#publishing-a-new-release-on-the-website)
when 0.3.0 is ready. Do not restore pre-launch versions to the catalog.

## About this repository

The website uses HTML and CSS, with a Python standard-library build that generates
download and release pages from [the update catalog](updates.json).
[Release information](RELEASES.md) describes the available download formats and
catalog fields. The [brand reference](assets/brand/eidora_colors.md) lists the
website's colors and artwork.
