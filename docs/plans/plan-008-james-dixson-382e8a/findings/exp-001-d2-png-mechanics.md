# EXP-001 — d2 PNG export mechanics & white-background guarantee

**Question:** How does d2 produce PNGs? Does the default produce a light-mode,
white-background PNG suitable for local/desktop rendering? What deps does each path carry?

## Findings (tested firsthand, d2 v0.7.1, macOS arm64)

### Two render paths exist

| Path | Command | Speed | Background | Hidden dependency |
|------|---------|-------|------------|-------------------|
| **d2-native PNG** | `d2 in.d2 out.png` | slow first run | opaque white `srgba(255,255,255,1)` | **downloads ~140MB playwright Chromium** to `~/Library/Caches/ms-playwright` on first PNG; network-dependent (timed out once, succeeded on retry) |
| **SVG → rasterize** | `d2 in.d2 out.svg` + `rsvg-convert -b white out.svg -o out.png` | ~20ms + ~0.1s | forced white via `-b white`, opaque RGB | `librsvg` (`rsvg-convert`) — already installed, brew cross-platform |

### Key facts
- **d2 SVG export is native Go** — 18ms, no browser, no network. SVG root rect is
  `fill="#FFFFFF"` under default theme 0 (light/Neutral).
- **d2 PNG export shells out to a bundled playwright Chromium** — this is the heavy,
  surprising cost. ~140MB one-time download; fails offline on a cold cache.
- Default theme `0` = light mode. `--theme`, `--dark-theme`, `--layout` (dagre|elk),
  `--pad`, `--scale`, `--sketch` are the relevant flags.
- Local SVG→PNG rasterizers already present: `rsvg-convert`, ImageMagick (`magick`/`convert`).
  `resvg`, `cairosvg`, `inkscape` absent.
- Both paths verified to yield opaque white backgrounds (sampled corner+center pixels).

### Implication for the skill
The PNG rendering backend is the central design fork. The SVG→`rsvg-convert -b white`
path is faster, browser-free, offline-capable, and gives explicit white-background
control — at the cost of one extra (already-installed, cross-platform) dependency.
The d2-native path is a single command and needs no rasterizer, but carries a 140MB
Chromium download and a network requirement on first use, which conflicts with the
portability/preflight goals. Preflight must check for `d2` plus whichever rasterizer
the chosen backend needs.
