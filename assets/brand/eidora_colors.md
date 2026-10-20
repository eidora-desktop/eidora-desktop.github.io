# EIDORA color codes

Color space: sRGB. HEX values are the digital reference.

Last verified against [EIDORA_logo.svg](EIDORA_logo.svg): **28 September 2026**. All 32 explicit SVG color codes are documented here, including the latest patina and gold highlights.

The full-logo SVG palette is matched to the approved [balanced teal rendering](../photo/EIDORA_logo_modern_nebra_balanced_teal.png). Representative material midtones from that image were adapted to native SVG gradients and restrained mineral shading: balanced blue-green teal, pale gold scale markings, warm gold fittings and smoky brown bronze. The 512 × 512 canvas and transparent background are preserved. The C-ring now has fine continuous mineral grain and inset gold edges; the right objective rim has rounded shoulders, a recessed connecting neck and a light-catching front face. The telescope uses cylindrical shading and shaded end collars, with the horizontal engraved line retained near the bottom of the barrel.

## Full logo — approved balanced teal palette

### Main fills and outlines

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Balanced Teal | `#426F6E` | 66, 111, 110 | Central tone of the large C-ring patina gradient. |
| Scale Gold | `#E9C17D` | 233, 193, 125 | C-ring scale arc and markers, including their stroke. |
| Hanger Gold | `#C19758` | 193, 151, 88 | Warm midtone in the hanger mount and telescope clamp gradients. |
| Smoky Bronze | `#756446` | 117, 100, 70 | Main midtone of the telescope barrel gradient. |
| Holder Gold | `#C49B5C` | 196, 155, 92 | Main tone of the shaded curved holder below the telescope. |
| Fitting Gold | `#C59C5C` | 197, 156, 92 | Base gold in the shaded clamp, eyepiece collar and right-hand objective rings. |
| Mount Bronze | `#B68D4F` | 182, 141, 79 | Main tone of the shaded round hanger mount. |
| Focus Charcoal | `#50463F` | 80, 70, 63 | Large focus-knob face. |
| Hardware Ink | `#302A21` | 48, 42, 33 | Telescope barrel outline, knob body and grip stroke, and lower telescope engraving. |
| Patina Ink | `#2C4D4A` | 44, 77, 74 | Large C-ring outline. |
| Hanger Outline | `#5F4F36` | 95, 79, 54 | Top hanger-ring outline. |
| Mount Outline | `#615036` | 97, 80, 54 | Round hanger-mount outline. |
| Lens Ink | `#1F3437` | 31, 52, 55 | Lens outline. |
| Eyepiece Outline | `#55452E` | 85, 69, 46 | Eyepiece collar outline. |
| Clamp Outline | `#4C3E2A` | 76, 62, 42 | Telescope clamp outline. |
| Objective Outline | `#4B3F2C` | 75, 63, 44 | Objective collar outline. |
| Rim Outline | `#4C402E` | 76, 64, 46 | Right objective rim outline. |

### Texture and detail colors

These are source colors. Semi-transparent overlays blend with the underlying fill; they are not separate flat color blocks. Keep the patina variation subtle and continuous, with no new green patches.

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Deep Teal | `#315655` | 49, 86, 85 | C-ring mottling, inner shading and concentric engraving. |
| Soft Verdigris | `#588B82` | 88, 139, 130 | Quiet green-teal variation within the C-ring. |
| Patina Edge | `#8FABAA` | 143, 171, 170 | C-ring outer edge highlight at 42% opacity. |
| Hanger Shade | `#95743F` | 149, 116, 63 | Warm shadow within the hanger and fitting gradients; the hanger edge highlight uses Scale Gold at 55% opacity. |
| Metal Light | `#D4B57E` | 212, 181, 126 | Bronze texture and soft gold reflections across the hanger, holder, clamp and objective rim. |
| Bronze Shade | `#745B35` | 116, 91, 53 | Bronze texture and holder inner shading at 30% opacity. |
| Holder Engraving | `#947340` | 148, 115, 64 | Curved holder engraving at 16% opacity. |

### Telescope cylinder shading

The barrel uses the vertical barrel gradient (`g7`) across its diameter, with a broad upper reflection and a dark underside. It replaces the former flat highlight band. The horizontal lower engraving remains in Hardware Ink `#302A21`, with a fine Metal Light `#D4B57E` edge at 30% opacity to suggest a recessed groove. The eyepiece collar and both objective end rings use aligned vertical gradients (`g9` for the eyepiece, `g12` and `g13` for the objective). A rounded objective lip, recessed neck and clipped curved front face define the telescope end.

| Barrel stop | HEX | RGB |
| --- | --- | --- |
| 0% | `#51452F` | 81, 69, 47 |
| 10% | `#756446` | 117, 100, 70 |
| 25% | `#B39A6B` | 179, 154, 107 |
| 32% | `#BDA574` | 189, 165, 116 |
| 49% | `#8F7B56` | 143, 123, 86 |
| 70% | `#756446` | 117, 100, 70 |
| 91% | `#51452F` | 81, 69, 47 |
| 100% | `#302A21` | 48, 42, 33 |

Eyepiece collar gradient stops: 0% `#745B35`, 16% `#C59C5C`, 31% `#D4B57E`, 51% `#C59C5C`, 78% `#95743F`, 100% `#745B35`. All gradient stops are opaque. These shading tones derive from the approved bronze and gold palette.

### Lens gradient

The lens uses an opaque horizontal linear gradient from left to right (`g8` in the SVG).

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Lens Light | `#D8E9E8` | 216, 233, 232 | First gradient stop at 0%. |
| Lens Depth | `#28595A` | 40, 89, 90 | Second gradient stop at 73%; this color continues to the end. |

### Mineral patina and gold reflections

The C-ring uses a diagonal gradient from `#457774` (69, 119, 116) through Balanced Teal `#426F6E` to `#396260` (57, 98, 96). A native SVG `feTurbulence` filter adds fine, continuous teal mineral grain, with 60% base color and 40% tinted grain. It is bounded by the original C-ring alpha; no raster texture is embedded. The older broad mottling is reduced so no separate green patches dominate.

The inset gold edge gradient uses Scale Gold `#E9C17D`, Metal Light `#D4B57E` and Hanger Shade `#95743F`. Edge opacity is 80% on the C-ring and 65% on the holder and clamp. The hanger's upper edge uses Scale Gold at 55% opacity.

The objective collar and rounded rim use these vertical stops: 0% `#745B35`, 14% `#C59C5C`, 28% `#E9C17D`, 43% `#D4B57E`, 63% `#C59C5C`, 83% `#95743F`, 100% `#51452F`. A recessed bronze neck connects the rim to the collar. The front-face highlight uses `#C59C5C`, `#E9C17D`, `#D4B57E` and `#745B35`.

The top hanger uses a concentric radial gradient (`g1`), centered at (250, 63) with radius 31. Soft bronze edges surround a broad, muted gold face. The reduced contrast and flatter highlight give the ring shallow depth while preserving the opening.

Exact stops for the remaining material gradients (all stops are opaque; edge path opacity is applied separately):

| SVG gradient | Stops: position and HEX |
| --- | --- |
| `g3` | 0% `#457774`; 42% `#426F6E`; 100% `#396260` |
| `g4 / g6 / g15` | 0% `#E9C17D`; 38% `#D4B57E`; 65% `#95743F`; 100% `#D4B57E` |
| `g1` (radial hanger) | 0% and 61% `#95743F`; 69% `#B68D4F`; 77% and 90% `#C59C5C`; 96% `#B68D4F`; 100% `#95743F` |
| `g2` | 0% `#D4B57E`; 30% `#C19758`; 70% `#B68D4F`; 100% `#95743F` |
| `g5` | 0% `#D4B57E`; 22% `#C49B5C`; 65% `#C59C5C`; 100% `#B68D4F` |
| `g10` | 0% `#D4B57E`; 15% `#C59C5C`; 72% `#C19758`; 100% `#95743F` |
| `g14` | 0% `#C59C5C`; 25% `#E9C17D`; 55% `#D4B57E`; 100% `#745B35` |
| `g11` | 0% `#745B35`; 30% `#B68D4F`; 65% `#95743F`; 100% `#51452F` |

### Texture opacity

Preserve the existing nested group opacities and path opacities. Effective values below describe each individual overlay; overlapping layers composite together.

| Surface | Path opacity | Group opacity | Effective individual opacity |
| --- | --- | --- | --- |
| C-ring, Deep Teal layers | 13% / 26% | 10% | 1.30% / 2.60% |
| C-ring, Soft Verdigris layers | 16% / 38% | 10% | 1.60% / 3.80% |
| Curved holder, Bronze Shade / Metal Light | 9% / 16% | 53% × 55% | 2.62% / 4.66% |
| Telescope tube, Bronze Shade / Metal Light | 9% / 16% | 51% × 65% | 2.98% / 5.30% |

C-ring inner shading uses Deep Teal at 50% opacity; concentric engraving uses it at 10%. The scale uses Scale Gold for both fill and its 0.5-unit stroke. The hanger, mount, holder, clamp and end collars use coordinated gold gradients. The knob mounting plate is a wider rounded rectangle covering the telescope sliding element, with a consistent inset outline and gold edge; its vertical gradient (`g10`) follows the new plate bounds. The C-ring and holder have thin gold edge reflections clipped inside their silhouettes.

### Asset reference

- **Vector master:** [EIDORA_logo.svg](EIDORA_logo.svg). Its exact editable colors are listed above.
- **Approved material and color reference:** [EIDORA_logo_modern_nebra_balanced_teal.png](../photo/EIDORA_logo_modern_nebra_balanced_teal.png). Lighting and material variation produce a range of pixel colors; the SVG uses representative tones rather than reproducing every photographic highlight.
- **Inscription lockup:** [EIDORA_inscription_lockup.svg](EIDORA_inscription_lockup.svg) embeds the approved balanced teal PNG, with its existing wordmark and sub-line. Its instrument is a raster image inside an SVG container. [The PNG preview](EIDORA_inscription_preview.png) uses the same layout.
- **Inscription wordmark:** [EIDORA_inscription_wordmark.svg](EIDORA_inscription_wordmark.svg) remains a separate asset.
- **App icons and interface:** the existing palettes documented below remain unchanged and separate from the full-logo palette.

## Existing app icon and interface brand palette

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Hellenic Green | `#71816A` | 113, 129, 106 | C-ring in the Hellenic Bronze app icon; muted brand fields. |
| Stone Sage | `#92988B` | 146, 152, 139 | Suspension details in the Hellenic Bronze app icon; muted brand fields. |
| Quiet Bronze | `#A3947C` | 163, 148, 124 | Secondary brand accent; tube and holder in the Hellenic Bronze app icon. |
| Limestone | `#CEC5AE` | 206, 197, 174 | Pale metal fittings, dark-section accents and inverse links. |
| Chalk | `#E6E1D2` | 230, 225, 210 | App icon highlights and pale decorative accents. |
| Olive Ink | `#303830` | 48, 56, 48 | Primary text, monochrome marks and dark brand backgrounds. |

## Surfaces

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Paper | `#F5F3EB` | 245, 243, 235 | Default page, document and slide background; inverse text on Olive Ink. |
| Porcelain | `#FCFBF7` | 252, 251, 247 | Cards, sheets, inputs and raised surfaces. |
| Sage Mist | `#E8E9E0` | 232, 233, 224 | Alternate sections, quiet panels and secondary button backgrounds. |
| Soft Rule | `#D3D5CA` | 211, 213, 202 | Decorative dividers, table rules and nonessential separators. |

## Text & controls

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Stone Edge | `#7D8576` | 125, 133, 118 | Input boundaries and essential UI outlines on the light surfaces. |
| Moss Gray | `#596153` | 89, 97, 83 | Secondary text, summaries and supporting labels. |
| Ash Olive | `#636B5D` | 99, 107, 93 | Captions, metadata and placeholder text on light surfaces. |
| Deep Sage | `#535E4C` | 83, 94, 76 | Primary buttons, underlined text links, focus rings and active icons. |
| Forest Shade | `#424D3C` | 66, 77, 60 | Hover and pressed states for primary buttons and links. |
| Bronze Ink | `#766449` | 118, 100, 73 | Readable bronze emphasis, visited links and small accent text. |

## Status

| Color | HEX | RGB | Use |
| --- | --- | --- | --- |
| Laurel | `#52664B` | 82, 102, 75 | Success text, icon and border; pair with Success Wash. |
| Success Wash | `#E6EBDD` | 230, 235, 221 | Background for success and completion messages. |
| Ochre | `#806535` | 128, 101, 53 | Warning text, icon and border; pair with Warning Wash. |
| Warning Wash | `#F1E8D5` | 241, 232, 213 | Background for caution and review messages. |
| Terracotta Ink | `#8A5348` | 138, 83, 72 | Error text, icon and border; pair with Error Wash. |
| Error Wash | `#F2E3DE` | 242, 227, 222 | Background for errors and destructive-action explanations. |
| Slate Blue | `#536971` | 83, 105, 113 | Informational text, icon and border; pair with Info Wash. |
| Info Wash | `#E3EAEB` | 227, 234, 235 | Background for neutral information and guidance. |

## Common combinations

| Element | Foreground | Background / state |
| --- | --- | --- |
| Page | Olive Ink `#303830` | Paper `#F5F3EB` |
| Card / input | Olive Ink `#303830` | Porcelain `#FCFBF7` |
| Alternate section | Olive Ink `#303830` | Sage Mist `#E8E9E0` |
| Supporting text | Moss Gray `#596153` | Any of the three light surfaces |
| Captions / placeholders | Ash Olive `#636B5D` | Any of the three light surfaces |
| Primary button | Paper `#F5F3EB` | Deep Sage `#535E4C`; hover / pressed `#424D3C` |
| Secondary button | Olive Ink `#303830` | Sage Mist `#E8E9E0`; border `#7D8576` |
| Disabled control | Ash Olive `#636B5D` | Sage Mist `#E8E9E0`; border `#D3D5CA` |
| Underlined link | Deep Sage `#535E4C` | Hover `#424D3C`; visited `#766449` |
| Selected text | Olive Ink `#303830` | Limestone `#CEC5AE` |
| Dark brand section | Paper `#F5F3EB` | Olive Ink `#303830` |
| Dark-section secondary text / link | Limestone `#CEC5AE` | Olive Ink `#303830`; link hover `#E6E1D2` |
| Dark-section button | Olive Ink `#303830` | Limestone `#CEC5AE`; hover `#E6E1D2` |

Use a 2 px Deep Sage `#535E4C` focus ring with a 3 px offset on light surfaces; use Limestone `#CEC5AE` on Olive Ink backgrounds. Soft Rule is for decorative separators; use Stone Edge for essential control boundaries.

Keep Hellenic Green, Stone Sage and Quiet Bronze as decorative brand colors. Use the darker text and action colors for small copy and controls. Pair status colors with their named washes and a written label or icon.

The specified normal-size text pairings meet 4.5:1 contrast; essential control borders meet 3:1 on the three light surfaces. See [W3C text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

For print, convert these sRGB colors using the production printer’s ICC profile and proof on the chosen stock.

## App icon variants

All desktop icons use a 1024 × 1024 canvas with an opaque rounded background tile. The original instrument paths are placed at 100% scale, with the C-ring center offset 36 pixels right and 44 pixels down from the tile center for visual balance; the area outside the tile stays transparent. The standalone transparent marks are retained in `../app_icon/marks/`.

| SVG in `../app_icon/` | Colors and intended surface |
| --- | --- |
| `EIDORA_app_icon_dark.svg` | Main `#2B261F`, secondary `#5A5249`; Paper background `#F5F3EB`, Limestone edge `#CEC5AE` at 60% opacity. |
| `EIDORA_app_icon_light.svg` | Main Paper `#F5F3EB`, suspension and holder Limestone `#CEC5AE`; Olive Ink background `#303830`, Moss Gray edge `#596153` at 60% opacity. |
| `EIDORA_app_icon_hellenic_bronze.svg` | C-ring `#71816A`; suspension `#92988B`; tube and holder `#A3947C`; fittings `#CEC5AE`; Paper background `#F5F3EB`, Limestone edge `#CEC5AE` at 60% opacity. |
