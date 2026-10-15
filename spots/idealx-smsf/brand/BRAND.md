# IdealX brand guide

Working guide for the SMSF Start landing page and campaign material. Every value here was read from idealx.com's published stylesheet and markup on 14 and 15 October 2026, except where marked **derived**. Confirm against IdealX's own brand assets before print or paid media.

## 1. Logo

### The mark

Two shapes on a 212 x 212 grid: a tall indigo bar on the left, and two ink blocks on the right. The upper block has one large rounded corner (radius 52) at the top right; everything else uses a radius of 8.

```svg
<svg viewBox="0 0 212 212" fill="none">
  <rect x="0" y="0" width="80" height="212" rx="8" fill="#5158F6"/>
  <path d="M98 0H160C188.719 0 212 23.281 212 52V92C212 96.418 208.418 100 204 100H98C93.582 100 90 96.418 90 92V8C90 3.582 93.582 0 98 0Z" fill="currentColor"/>
  <rect x="90" y="112" width="122" height="100" rx="8" fill="currentColor"/>
</svg>
```

The indigo bar never changes colour. The two blocks take the text colour of their surface: ink on light backgrounds, white on dark backgrounds.

| File | Use |
|---|---|
| `logo/idealx-mark.svg` | Mark on white or light backgrounds (ink blocks) |
| `logo/idealx-mark-on-dark.svg` | Mark on ink or dark backgrounds (white blocks) |
| `logo/idealx-mark-mono-ink.svg` | Single-colour ink, for embossing, fax-grade print or one-colour stamps |
| `logo/idealx-mark-mono-white.svg` | Single-colour white, for photography and video overlays |
| `logo/idealx-lockup.svg` | Mark with the IDEALX wordmark, light backgrounds |
| `logo/idealx-lockup-on-dark.svg` | Mark with the IDEALX wordmark, dark backgrounds |
| `logo/site-icon-source.svg` | The app icon as served by idealx.com: the mark at 60% inside an ink rounded square (radius 56 on 256) |
| `logo/png/` | PNG exports of each at 1024 px for decks and ad platforms |

### The wordmark

IDEALX set in Inter Semibold (600), all capitals, letter-spacing 0.18 em. On the site it sits at 15 px beside a 24 px mark. In the lockup files the wordmark starts 56 units to the right of the mark and is optically centred on it.

### Clear space and minimum size

- Clear space on every side equals the width of the indigo bar (80 units, or 38% of the mark's width).
- Minimum size: 16 px on screen, 5 mm in print. The site itself uses the mark at 16, 24, 48 and 96 px.
- Do not rotate, outline, add a shadow or gradient, change the indigo, or recolour the blocks to anything but ink or white.

## 2. Colour

Tokens as named in the site's stylesheet.

| Token | Hex | Role |
|---|---|---|
| `--indigo` | `#5158F6` | The one accent: links, underlines, focus rings, the logo bar, the footer rule |
| `--indigo-600` | `#3F46E0` | Accent hover and pressed states |
| `--indigo-tint` | `#EEEFFE` | Soft accent fill behind selected items |
| `--ink` | `#0D0D0F` | Text on light surfaces; primary buttons; the dark page in dark mode |
| `--ink-2` | `#16161A` | Secondary dark surface; the lighter end of the footer gradient |
| `--slate` | `#5B5B63` | Muted text |
| `--mist` | `#E7E7EA` | Hairlines and input borders |
| `--cloud` | `#F0F0F0` | Card and panel fill on light pages |
| `--white` | `#FFFFFF` | Page background |
| `--positive-tint` | `#E6F3EA` | Success fill |
| `--warn` / `--warn-tint` | `#8A5300` / `#FBF1DE` | Warning text and fill |
| `--danger` / `--danger-tint` | `#B4232A` / `#FBE9EA` | Error text and fill |
| `--page-muted` | `#0D0D0F` at 64% | Muted text as the site actually sets it |
| `--page-line` | `#0D0D0F` at 10% | Hairlines as the site actually sets it |

Opacities the site uses on dark surfaces: white at 3%, 4%, 14%, 22%, 28%; indigo at 16%, 25%, 35%.

**Rule of one accent.** Indigo is the only hue. Success, warning and danger colours carry meaning and never decorate. Buttons are ink, not indigo.

### Derived values (not on the site)

Used in the prototype's dark theme and the two exploration themes. Replace if IdealX publishes its own.

| Use | Hex | Note |
|---|---|---|
| Dark theme muted text | `#A3A3AA` | Near white at 64% on ink |
| Dark theme accent hover | `#8B90F9` | Indigo lightened so it reads on ink |
| Dark theme lines | `#FFFFFF` at 14% and 28% | The site's own opacities |
| Positive text on light | `#1F7A45` | Pairs with the site's positive tint |

### Contrast

Ink on white and white on ink exceed 15:1. Indigo `#5158F6` on white is about 4.9:1, enough for text at any size. Slate on white is about 6.6:1. Indigo on cloud is about 4.4:1, so keep indigo text at 16 px or larger on cloud cards, or use it for underlines and rules rather than words.

## 3. Typography

| Role | Face | Weight | Notes |
|---|---|---|---|
| Headlines | Inter | 300 Light | Letter-spacing -0.03 em, line-height 1.04 |
| Accent word in a headline | Instrument Serif | 400 Regular | Upright, not italic. About 6% larger than the Inter around it. Underlined in indigo, thickness 0.09 em, offset 0.14 em |
| Body and UI | Inter | 400 and 500 | 16 px base, line-height 1.5 |
| Wordmark and emphasis | Inter | 600 Semibold | |
| Eyebrow labels | Inter | 500 | 11.5 px, uppercase, letter-spacing 0.14 em |
| Data and codes | System monospace | 400 | `ui-monospace, SF Mono, Menlo, monospace`, tabular numerals |

Both faces are served from Google Fonts on the site:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap">
```

### Type scale (prototype)

| Element | Size |
|---|---|
| H1 | clamp(2.5 rem, 6 vw, 4.1 rem) |
| H2 | clamp(1.9 rem, 4.2 vw, 2.8 rem) |
| H3 | 1.45 rem |
| Lede | 1.1 rem, slate |
| Body | 1 rem |
| Small | 0.875 rem |
| Eyebrow | 0.72 rem |

### The accent word

Every headline carries exactly one word in Instrument Serif, chosen for meaning, not position: the word the sentence turns on. "Hand it to a *person* at any point." "Where can we *reach* you?" "No room at this *address*." Never two words, never the whole line.

## 4. Treatments

**Eyebrow.** An indigo code in tabular capitals, a 40 px hairline in indigo at 55% opacity, then a slate label in small capitals. The site writes `404 —— PAGE NOT FOUND`; the form writes `01 —— SECTION 1 OF 5`.

**Primary button.** Ink fill, white text, 12 px radius, 44 px tall, 20 px side padding, with a trailing arrow (→) that nudges right on hover. On dark surfaces the button inverts: white fill, ink text.

**Secondary button.** White fill, mist border, ink text, same geometry, no arrow. Hover darkens the border to ink.

**Cards.** Cloud fill, no border, 24 px radius, 24 px padding. Titles in Inter Regular, body in slate. A selected card gains a 1 px indigo border and the indigo tint as its fill.

**Inputs.** White fill, mist border, 10 px radius, 46 px tall. Hover darkens the border; focus shows a 2 px indigo ring with a 2 px offset.

**Hairline rules.** Mist, or ink at 10%.

**Footer.** A dark band with a 3 px indigo top rule, a vertical gradient from ink-2 to ink, a large light headline with a serif accent word ("Where your SMSF *lives*."), and three columns under small-capital headings: The platform, Company, Legal.

**Radius tokens.** 10 px on controls (`--radius`), 14 px on panels (`--radius-lg`), 24 px on cards and sheets (`--radius-xl`). The app icon uses 56 on 256.

**Motion.** `--ease-out: cubic-bezier(.22, 1, .36, 1)` for things arriving; `--ease-in-out: cubic-bezier(.65, 0, .35, 1)` for things moving. Durations around 300 ms. Hero words on the site fade and rise in sequence with a 50 ms stagger. Respect `prefers-reduced-motion`.

## 5. Voice

Short, direct, plain. Headings often read as slogans: "One home. One door. Every room." "Where your SMSF lives." Say what happens, not how the system works. No exclamation marks, no emoji, no "please note". Error messages say what went wrong and how to fix it: "Postcodes are 4 digits. Fix it or leave it blank."

Financial copy stays general. Never "suits you", "best for you" or "we recommend". The landing page carries a general advice line and the footer carries the licence.

## 6. Themes in the prototype

| Theme | Page | Accent | Source |
|---|---|---|---|
| IdealX Light | `#FFFFFF` | `#5158F6` | The site as published |
| IdealX Dark | `#0D0D0F` | `#5158F6` | Derived: the same palette inverted |
| Indigo Tint | `#EEEFFE` | `#5158F6` | Derived: the site's indigo tint as the page |
| Cloud | `#F0F0F0` | `#5158F6` | Derived: the site's cloud as the page |

The footer stays dark in every theme, as it does on the site.

## 7. CSS tokens, ready to paste

```css
:root{
  --indigo:#5158F6; --indigo-600:#3F46E0; --indigo-tint:#EEEFFE;
  --ink:#0D0D0F; --ink-2:#16161A; --slate:#5B5B63; --mist:#E7E7EA; --cloud:#F0F0F0; --white:#FFFFFF;
  --positive-tint:#E6F3EA; --warn:#8A5300; --warn-tint:#FBF1DE; --danger:#B4232A; --danger-tint:#FBE9EA;
  --page-bg:var(--white); --page-fg:var(--ink); --page-muted:#0D0D0FA3; --page-line:#0D0D0F1A;
  --radius:10px; --radius-lg:14px; --radius-xl:24px;
  --ease-out:cubic-bezier(.22,1,.36,1); --ease-in-out:cubic-bezier(.65,0,.35,1);
  --font-sans:'Inter',ui-sans-serif,system-ui,sans-serif;
  --font-serif:'Instrument Serif',Georgia,serif;
  --font-mono:ui-monospace,'SF Mono',Menlo,monospace;
}
```

## 8. Sources

- https://www.idealx.com/ (markup: logo SVG, wordmark styling, footer, hero copy)
- https://www.idealx.com/_next/static/immutable/chunks/3ayne5o3frdem.css (`:root` tokens, font faces, easing)
- https://www.idealx.com/icon.svg (app icon)
- https://legal.idealx.com/agreements/privacy (entity names used in the footer)
