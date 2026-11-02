# EIDORA website colors and artwork

The website combines teal and gold accents with warm, light surfaces. All values
below use the sRGB color space and correspond to [the site stylesheet](../../styles.css).

## Website palette

| Color | HEX | Use |
| --- | --- | --- |
| Paper | `#F5F3EB` | Page background |
| Porcelain | `#FCFBF7` | Resource section and text on dark surfaces |
| Olive Ink | `#303830` | Primary text |
| Moss Gray | `#596153` | Supporting text |
| Teal | `#426F6E` | Accents and section labels |
| Deep Teal | `#254948` | Download cards, links, and focus outlines |
| Teal Hover | `#193B3A` | Dark teal variant |
| Gold | `#D4B57E` | Decorative accents and focus outlines on dark surfaces |
| Bronze Ink | `#766449` | Accent text |
| Sage Mist | `#E8E9E0` | Workflow section background |
| Soft Rule | `#D3D5CA` | Dividers and borders |
| Stone Edge | `#7D8576` | Border color variant |
| Inverse Muted | `#D5E1DA` | Supporting text on download cards |

## Artwork

- [Instrument logo](eidora_logo.svg)
- [Wordmark](eidora_wordmark.svg)
- [Application icon, SVG](eidora_icon.svg)
- [Application icon, PNG](eidora_icon.png)
- [16-pixel favicon](favicon-16.png)
- [32-pixel favicon](favicon-32.png)

The instrument logo uses teal patina, gold fittings, and bronze shading.
The 16-pixel favicon uses a simplified mark for legibility at small sizes.

## Typography

The hero headline uses Outfit Medium (500), and its introductory sentence uses
Outfit Regular (400). The EIDORA wordmark remains the original SVG artwork.
Body text uses system sans-serif fonts.

Outfit's variable WOFF2 files are hosted locally in `assets/fonts/`, with Latin
and extended Latin subsets. The Latin subset is preloaded; `font-display: swap`
and system/Arial fallbacks keep text visible while loading. No external font
service is required by the website.

Source: [Google Fonts Outfit](https://github.com/google/fonts/tree/main/ofl/outfit).
The SIL Open Font License is included in `assets/fonts/OFL-Outfit.txt`.
