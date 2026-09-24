"""Shared SVG primitives for the Cohesiq diagram set (diagram-design skill, `cohesiq` profile).

Every diagram module imports from here so palette, typography, connector
grammar and page chrome stay identical across files. Colours are the
`cohesiq` profile (~/.diagram-design/profiles/cohesiq.md), which maps
frontend/design/cohesiq.css onto the skill's semantic roles.
"""
from __future__ import annotations

import html
import math

# ── Semantic roles (cohesiq profile) ────────────────────────────────────────
PAPER = "#FAF8F5"        # n-50
PAPER2 = "#F3EFE9"       # n-100
INK = "#211D18"          # n-900
MUTED = "#4E483D"        # n-700
SOFT = "#6A6253"         # n-600
ACCENT = "#5B2BD9"       # brand-primary
LINK = "#ED4444"         # brand-secondary-strong
WHITE = "#ffffff"


def ink(a: float) -> str:
    return f"rgba(33,29,24,{a})"


def muted(a: float) -> str:
    return f"rgba(78,72,61,{a})"


def accent(a: float) -> str:
    return f"rgba(91,43,217,{a})"


def link(a: float) -> str:
    return f"rgba(237,68,68,{a})"


SANS = "'DM Sans', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
SERIF = "'Instrument Serif', 'Noto Serif', serif"
FONT_LINK = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
    "&family=DM+Sans:wght@400;500;600;700&family=Geist+Mono:wght@400;500;600&display=swap"
)

# fill, stroke, tag-stroke, tag-text, dash
KINDS = {
    "focal":    (accent(0.08), ACCENT, accent(0.50), ACCENT, None),
    "backend":  (WHITE, INK, ink(0.40), INK, None),
    "store":    (ink(0.05), MUTED, muted(0.50), MUTED, None),
    "external": (ink(0.03), ink(0.30), ink(0.22), SOFT, None),
    "input":    (muted(0.10), SOFT, muted(0.40), SOFT, None),
    "optional": (ink(0.02), ink(0.20), ink(0.22), SOFT, "4,3"),
}

ARROW = {"default": (MUTED, "arrow"), "accent": (ACCENT, "arrow-accent"), "link": (LINK, "arrow-link")}


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def ceil4(v: float) -> int:
    return int(math.ceil(v / 4.0) * 4)


def mono_w(text: str, size: float = 8, track: float = 0.06) -> float:
    return len(text) * size * (0.62 + track)


# ── Primitives ──────────────────────────────────────────────────────────────
def defs(extra: str = "") -> str:
    m = []
    for color, mid in ARROW.values():
        m.append(
            f'<marker id="{mid}" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
            f'<polygon points="0 0, 8 3, 0 6" fill="{color}"/></marker>'
        )
    m.append(
        '<marker id="arrow-open" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">'
        f'<polyline points="0 0, 8 3, 0 6" fill="none" stroke="{MUTED}" stroke-width="1.2"/></marker>'
    )
    return "<defs>" + "".join(m) + extra + "</defs>"


def orth(points, r: int = 8) -> str:
    """Orthogonal path through axis-aligned waypoints with quarter-arc corners."""
    (x0, y0) = points[0]
    d = [f"M {x0},{y0}"]
    for i in range(1, len(points) - 1):
        (px, py), (cx, cy), (nx, ny) = points[i - 1], points[i], points[i + 1]
        ix, iy = _sgn(cx - px), _sgn(cy - py)
        ox, oy = _sgn(nx - cx), _sgn(ny - cy)
        d.append(f"L {cx - ix * r},{cy - iy * r}")
        d.append(f"Q {cx},{cy} {cx + ox * r},{cy + oy * r}")
    xn, yn = points[-1]
    d.append(f"L {xn},{yn}")
    return " ".join(d)


def _sgn(v: float) -> int:
    return (v > 0) - (v < 0)


def arrow(points, kind: str = "default", dashed: bool = False, width: float | None = None,
          open_head: bool = False) -> str:
    color, marker = ARROW[kind]
    if open_head:
        marker = "arrow-open"
    w = width or (1.4 if kind == "accent" else (1 if dashed else 1.2))
    dash = ' stroke-dasharray="4,3"' if dashed else ""
    d = points if isinstance(points, str) else orth(points)
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}"{dash} '
            f'marker-end="url(#{marker})"/>')


def line(x1, y1, x2, y2, stroke=None, width=1, dash=None) -> str:
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke or ink(0.2)}" '
            f'stroke-width="{width}"{dd}/>')


def _label(x, y, w, text, color):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="{PAPER}"/>'
            f'<text x="{x + w / 2:g}" y="{y + 9}" fill="{color}" font-size="8" font-family="{MONO}" '
            f'text-anchor="middle" letter-spacing="0.06em">{esc(text)}</text>')


def label_above(cx, line_y, text, color=SOFT, gap=8):
    w = ceil4(mono_w(text) + 10)
    return _label(cx - w // 2, line_y - gap - 12, w, text, color)


def label_below(cx, line_y, text, color=SOFT, gap=8):
    w = ceil4(mono_w(text) + 10)
    return _label(cx - w // 2, line_y + gap, w, text, color)


def label_right(line_x, cy, text, color=SOFT, gap=8):
    w = ceil4(mono_w(text) + 10)
    return _label(line_x + gap, cy - 6, w, text, color)


def label_left(line_x, cy, text, color=SOFT, gap=8):
    w = ceil4(mono_w(text) + 10)
    return _label(line_x - gap - w, cy - 6, w, text, color)


def tag(x, y, text, stroke, color):
    w = ceil4(len(text) * 7 * 0.70 + 10)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="transparent" stroke="{stroke}" '
            f'stroke-width="0.8"/><text x="{x + w / 2:g}" y="{y + 9}" fill="{color}" font-size="7" '
            f'font-family="{MONO}" text-anchor="middle" letter-spacing="0.08em">{esc(text)}</text>')


def node(x, y, w, h, kind, tag_text, name, subs=(), num=None, rx=6) -> str:
    fill, stroke, tstroke, tcolor, dash = KINDS[kind]
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{PAPER}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" '
           f'stroke-width="1"{dd}/>']
    if tag_text:
        out.append(tag(x + 8, y + 6, tag_text, tstroke, tcolor))
    if num:
        numc = accent(0.12) if kind == "focal" else ink(0.07)
        out.append(f'<text x="{x + w - 8}" y="{y + h - 6}" fill="{numc}" font-size="28" font-weight="600" '
                   f'font-family="{MONO}" text-anchor="end">{esc(num)}</text>')
    n = len(subs)
    block = 12 + (15 + 12 * (n - 1) if n else 0)
    top_area = y + (20 if tag_text else 6)
    top = (top_area + y + h - 6) / 2 - block / 2
    cx = x + w / 2
    base = round(top + 10)
    out.append(f'<text x="{cx:g}" y="{base}" fill="{INK}" font-size="12" font-weight="600" '
               f'font-family="{SANS}" text-anchor="middle">{esc(name)}</text>')
    for i, s in enumerate(subs):
        out.append(f'<text x="{cx:g}" y="{base + 15 + 12 * i}" fill="{MUTED}" font-size="9" '
                   f'font-family="{MONO}" text-anchor="middle">{esc(s)}</text>')
    return "".join(out)


def zone(x, y, w, h, text) -> str:
    lw = ceil4(len(text) * 7 * 0.76 + 12)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{ink(0.02)}" '
            f'stroke="{ink(0.12)}" stroke-width="0.8"/>'
            f'<rect x="{x + 12}" y="{y + 4}" width="{lw}" height="12" rx="2" fill="{PAPER}"/>'
            f'<text x="{x + 12 + lw / 2:g}" y="{y + 13}" fill="{ink(0.50)}" font-size="7" font-family="{MONO}" '
            f'text-anchor="middle" letter-spacing="0.14em">{esc(text)}</text>')


def text(x, y, s, size=9, color=MUTED, family=MONO, anchor="start", weight=None, italic=False, track=None):
    wt = f' font-weight="{weight}"' if weight else ""
    it = ' font-style="italic"' if italic else ""
    tr = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-family="{family}" '
            f'text-anchor="{anchor}"{wt}{it}{tr}>{esc(s)}</text>')


def callout(x, y, lines, anchor="start") -> str:
    return "".join(text(x, y + 18 * i, s, size=14, color=MUTED, family=SERIF, anchor=anchor, italic=True)
                   for i, s in enumerate(lines))


def legend(y, width, items, x0=40) -> str:
    """items: ('box', kind, label) | ('line', arrow-kind, dashed, label) | ('dot', label) | ('ring', label)"""
    out = [line(x0, y - 8, width - x0, y - 8, ink(0.10), 0.8),
           text(x0, y + 8, "LEGEND", size=8, color=MUTED, track="0.18em")]
    x = x0
    yy = y + 24
    for it in items:
        if it[0] == "box":
            fill, stroke, _, _, dash = KINDS[it[1]]
            dd = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<rect x="{x}" y="{yy}" width="14" height="10" rx="2" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="1"{dd}/>')
            lab, sw = it[2], 20
        elif it[0] == "line":
            color, marker = ARROW[it[1]]
            dd = ' stroke-dasharray="4,3"' if it[2] else ""
            out.append(f'<line x1="{x}" y1="{yy + 5}" x2="{x + 28}" y2="{yy + 5}" stroke="{color}" '
                       f'stroke-width="1.2"{dd} marker-end="url(#{marker})"/>')
            lab, sw = it[3], 36
        elif it[0] == "dot":
            out.append(f'<circle cx="{x + 6}" cy="{yy + 5}" r="5" fill="{INK}"/>')
            lab, sw = it[1], 18
        elif it[0] == "ring":
            out.append(f'<circle cx="{x + 7}" cy="{yy + 5}" r="7" fill="none" stroke="{INK}" stroke-width="1"/>'
                       f'<circle cx="{x + 7}" cy="{yy + 5}" r="4" fill="{INK}"/>')
            lab, sw = it[1], 20
        elif it[0] == "frame":
            out.append(f'<rect x="{x}" y="{yy}" width="14" height="10" rx="2" fill="{ink(0.02)}" '
                       f'stroke="{ink(0.22)}" stroke-width="1"/>')
            lab, sw = it[1], 20
        out.append(text(x + sw, yy + 8, lab, size=9, color=MUTED, family=SANS))
        x += sw + ceil4(len(lab) * 4.9) + 28
    return "".join(out)


def start_dot(cx, cy):
    return f'<circle cx="{cx}" cy="{cy}" r="6" fill="{INK}"/>'


def end_dot(cx, cy):
    return (f'<circle cx="{cx}" cy="{cy}" r="8" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="{INK}"/>')


# ── Page shell ──────────────────────────────────────────────────────────────
CSS = f"""
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --color-paper: {PAPER}; --color-ink: {INK}; --color-muted: {MUTED}; --color-soft: {SOFT};
  --color-accent: {ACCENT}; --color-link: {LINK}; --color-rule: {ink(0.12)};
  --font-sans: {SANS}; --font-serif: {SERIF}; --font-mono: {MONO};
}}
body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink);
  min-height: 100vh; display: flex; justify-content: center; padding: 3rem 2rem; }}
.frame {{ max-width: 1280px; width: 100%; }}
.nav {{ font-family: var(--font-mono); font-size: 0.7rem; letter-spacing: 0.06em; margin-bottom: 1.75rem; }}
.nav a {{ color: var(--color-muted); text-decoration: none; border-bottom: 1px solid var(--color-rule); }}
.nav a:hover {{ color: var(--color-accent); border-color: var(--color-accent); }}
.eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }}
h1 {{ font-family: var(--font-serif); font-size: clamp(1.6rem, 2.4vw + 0.75rem, 2.25rem); font-weight: 400;
  letter-spacing: -0.02em; line-height: 1.15; margin-bottom: 0.6rem; }}
.lede {{ color: var(--color-muted); font-size: 0.95rem; line-height: 1.55; max-width: 62rem; margin-bottom: 1.75rem; }}
.lede code, .card code {{ font-family: var(--font-mono); font-size: 0.82em; color: var(--color-ink); }}
.figure {{ overflow-x: auto; }}
svg.diagram {{ width: 100%; min-width: 960px; display: block; }}
.cards {{ display: grid; gap: 1rem; margin-top: 2rem; }}
.card {{ background: #ffffff; border: 1px solid var(--color-rule); border-radius: 6px; padding: 1.25rem; }}
.card .eyebrow {{ margin-bottom: 0.6rem; }}
.card h3 {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }}
.card p, .card li {{ color: var(--color-muted); font-size: 0.85rem; line-height: 1.55; }}
.card ul {{ padding-left: 1.1rem; }}
.dot {{ width: 7px; height: 7px; border-radius: 50%; display: inline-block; background: var(--color-ink); }}
.dot.accent {{ background: var(--color-accent); }} .dot.link {{ background: var(--color-link); }}
.dot.muted {{ background: var(--color-muted); }}
footer {{ margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--color-rule);
  font-family: var(--font-mono); font-size: 0.68rem; color: var(--color-soft); line-height: 1.7; }}
"""


def svg(slug, title, desc, w, h, body, extra_defs="") -> str:
    return (f'<svg class="diagram" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-labelledby="{slug}-title {slug}-desc">'
            f'<title id="{slug}-title">{esc(title)}</title><desc id="{slug}-desc">{esc(desc)}</desc>'
            f'{defs(extra_defs)}<rect width="100%" height="100%" fill="{PAPER}"/>{body}</svg>')


def page(slug, eyebrow, title, lede, svg_markup, cards=(), card_cols="1.1fr 1fr 0.9fr", sources="") -> str:
    card_html = ""
    if cards:
        items = []
        for c in cards:
            dot = f'<span class="dot {c.get("dot", "")}"></span>'
            body = c["body"]
            if isinstance(body, (list, tuple)):
                body = "<ul>" + "".join(f"<li>{b}</li>" for b in body) + "</ul>"
            else:
                body = f"<p>{body}</p>"
            items.append(f'<div class="card"><p class="eyebrow">{esc(c["eyebrow"])}</p>'
                         f'<h3>{dot}{esc(c["title"])}</h3>{body}</div>')
        card_html = f'<div class="cards" style="grid-template-columns:{card_cols}">{"".join(items)}</div>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} · Cohesiq</title>
  <link href="{FONT_LINK}" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
  <div class="frame">
    <p class="nav"><a href="index.html">← Cohesiq diagrams</a></p>
    <p class="eyebrow">{esc(eyebrow)}</p>
    <h1>{esc(title)}</h1>
    <p class="lede">{lede}</p>
    <div class="figure">{svg_markup}</div>
    {card_html}
    <footer>{sources}<br>Generated by docs/diagrams/html/build.py · diagram-design skill · cohesiq profile</footer>
  </div>
</body>
</html>
"""
