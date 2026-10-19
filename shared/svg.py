"""Static SVG charts for the chart types the Plotly basic bundle doesn't have (treemaps for
now; Sankeys and maps later). Drawn at build time, so pages load no extra JavaScript and
nothing from third parties (DATA_USE_POLICY.md §8). Chart rules: DESIGN.md §8, which types
fit which data: docs/CHART_TYPES.md.

Each block carries a <title>, which browsers show as a tooltip on hover; the chart card's
table view holds every value, so nothing depends on hovering.
"""

from dataclasses import dataclass
from html import escape

from shared.charts import FONT, INK, INK_2, MUTED, SURFACE

WHITE = "#ffffff"
CHAR_W = 0.56  # average glyph width of the system UI font, in em (for fitting labels)
GAP = 2  # surface gap between blocks, px (dataviz mark spec)
RADIUS = 4


@dataclass(frozen=True)
class Block:
    """One treemap block: `value` sets its area; `label` and `note` are drawn inside it when
    they fit, and `tooltip` is shown on hover."""

    label: str
    value: float
    colour: str
    note: str = ""
    tooltip: str = ""


def _luminance(hex_colour: str) -> float:
    rgb = [int(hex_colour.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    """WCAG contrast ratio of two colours."""
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def text_colour(fill: str) -> str:
    """Ink or white, whichever reads better on `fill` (WCAG ratio, never the series colour)."""
    return INK if contrast(INK, fill) >= contrast(WHITE, fill) else WHITE


def _worst(row: list[float], side: float) -> float:
    s = sum(row)
    return max(max(row) * side**2 / s**2, s**2 / (side**2 * min(row)))


def squarify(values: list[float], x: float, y: float, w: float, h: float) -> list[tuple]:
    """Squarified treemap layout (Bruls, Huizing & van Wijk, 2000). `values` must be sorted
    largest first; returns one (x, y, w, h) per value, in the same order, filling the box."""
    total = sum(values)
    areas = [v * w * h / total for v in values]
    rects = []
    while areas:
        side = min(w, h)
        row = [areas[0]]
        while len(row) < len(areas) and _worst(row + [areas[len(row)]], side) <= _worst(row, side):
            row.append(areas[len(row)])
        s = sum(row)
        if w >= h:  # lay the row as a column on the left
            cw, yy = s / h, y
            for a in row:
                rects.append((x, yy, cw, a / cw))
                yy += a / cw
            x, w = x + cw, w - cw
        else:  # lay the row along the top
            rh, xx = s / w, x
            for a in row:
                rects.append((xx, y, a / rh, rh))
                xx += a / rh
            y, h = y + rh, h - rh
        areas = areas[len(row) :]
    return rects


def _fits(text: str, size: float, width: float) -> bool:
    return len(text) * size * CHAR_W <= width


def _wrap(text: str, size: float, width: float, max_lines: int = 3) -> list[str]:
    """Split `text` into at most `max_lines` lines that fit `width`; [] if it can't fit."""
    lines: list[str] = []
    for word in text.split():
        if lines and _fits(f"{lines[-1]} {word}", size, width):
            lines[-1] += f" {word}"
        elif _fits(word, size, width):
            lines.append(word)
        else:
            return []
    return lines if len(lines) <= max_lines else []


def _note_lines(note: str, size: float, width: float) -> list[str]:
    """A note such as "28% · B$1.6 bn" on one line, or one part per line when it doesn't fit."""
    if not note:
        return []
    if _fits(note, size, width):
        return [note]
    parts = note.split(" · ")
    return parts if all(_fits(p, size, width) for p in parts) else []


def treemap_panel(blocks: list[Block], x: float, y: float, w: float, h: float) -> str:
    """Blocks of one treemap, largest first, inside the box (x, y, w, h)."""
    blocks = sorted(blocks, key=lambda b: b.value, reverse=True)
    parts = []
    rects = squarify([b.value for b in blocks], x, y, w, h)
    for b, (bx, by, bw, bh) in zip(blocks, rects, strict=True):
        ix, iy = bx + GAP / 2, by + GAP / 2
        iw, ih = max(bw - GAP, 0.5), max(bh - GAP, 0.5)
        r = min(RADIUS, iw / 2, ih / 2)
        ink = text_colour(b.colour)
        text = ""
        pad, line_h = 8, 16
        size = 13
        lines = _wrap(b.label, size, iw - 2 * pad)
        if not lines:  # narrow block: one step smaller before giving up
            size, pad = 12, 6
            lines = _wrap(b.label, size, iw - 2 * pad)
        notes = _note_lines(b.note, 12, iw - 2 * pad)
        if lines and line_h * (len(lines) + len(notes)) + 12 > ih:
            notes = []  # label only
        if lines and line_h * len(lines) + 12 <= ih:
            ty = iy + 4
            for i, line in enumerate(lines + notes):
                ty += line_h
                note = i >= len(lines)
                weight = "" if note else ' font-weight="600"'
                text += (
                    f'<text x="{ix + pad:.1f}" y="{ty:.1f}" font-size="{12 if note else size}"'
                    f'{weight} fill="{ink}">{escape(line)}</text>'
                )
        tip = f"<title>{escape(b.tooltip or b.label)}</title>"
        parts.append(
            f'<g>{tip}<rect x="{ix:.1f}" y="{iy:.1f}" width="{iw:.1f}" height="{ih:.1f}" '
            f'rx="{r:.1f}" fill="{b.colour}"/>{text}</g>'
        )
    return "".join(parts)


def svg(width: float, height: float, body: str) -> str:
    """Wrap chart parts in a responsive SVG (scales to the card width, keeps its shape).
    aria-hidden: the chart card's wrapper carries the text summary for screen readers."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" class="svg-chart" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" width="100%" '
        f'preserveAspectRatio="xMidYMid meet" aria-hidden="true" '
        f'style="font-family:{escape(FONT, quote=True)};background:{SURFACE}">{body}</svg>'
    )


def heading(x: float, y: float, text: str, note: str = "") -> str:
    """Panel heading, e.g. "2018" with "B$5.6 bn imports" after it."""
    extra = f'<tspan fill="{MUTED}" font-weight="400"> {escape(note)}</tspan>' if note else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="13" font-weight="600" fill="{INK_2}">'
        f"{escape(text)}{extra}</text>"
    )


def legend(
    x: float, y: float, items: list[tuple[str, str]], width: float = 10_000
) -> tuple[str, float]:
    """Legend of colour swatches and labels (always shown for 2+ colours), wrapping into rows
    within `width`. Returns the markup and the y of its last row."""
    parts, cx = [], x
    for label, colour in items:
        item_w = 18 + len(label) * 12 * CHAR_W
        if cx > x and cx + item_w > x + width:
            cx, y = x, y + 20
        parts.append(
            f'<rect x="{cx:.1f}" y="{y - 10:.1f}" width="12" height="12" rx="2" fill="{colour}"/>'
            f'<text x="{cx + 18:.1f}" y="{y:.1f}" font-size="12" fill="{INK_2}">'
            f"{escape(label)}</text>"
        )
        cx += item_w + 20
    return "".join(parts), y
