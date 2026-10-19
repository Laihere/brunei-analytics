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


# District maps (choropleth). Shapes come from case_studies/_shared/outputs/brunei_districts.csv
# (geoBoundaries, approximate; DATA_USE_POLICY.md §6). Fills come from a stepped teal ramp, light
# to dark, and every district is labelled with its value, so colour is never the only signal.
STEPS = ["#ccefea", "#5ec4b8", "#0f766e", "#134e4a"]  # teal-100, -300, -700, -900
OUTLINE = "#8f8c85"  # district edges, visible against the lightest step and the surface


def step_colour(value: float, breaks: list[float]) -> str:
    """Fill for `value`: STEPS[i] for the i-th interval of `breaks` (len(STEPS) - 1 cut points)."""
    assert len(breaks) == len(STEPS) - 1
    return STEPS[sum(value >= b for b in breaks)]


@dataclass(frozen=True)
class Area:
    """One district on a map: `fill` colour, a short `value` label and a hover `tooltip`."""

    name: str
    fill: str
    value: str
    tooltip: str


def district_map(
    shapes, areas: list[Area], x: float, y: float, w: float, label_offsets: dict | None = None
) -> str:
    """Brunei's four districts scaled to width `w` at (x, y), each filled and labelled. `shapes`
    is the brunei_districts table; `label_offsets` nudges a label (district → (dx, dy), in px)
    when a district is too small to hold it, e.g. Brunei-Muara on small maps."""
    k = w / shapes.box_w.iloc[0]
    by_name = {a.name: a for a in areas}
    assert set(by_name) == set(shapes.district), "Every district needs a value."
    paths, labels = [], []
    for s in shapes.itertuples():
        a = by_name[s.district]
        paths.append(
            f'<g><title>{escape(a.tooltip)}</title><path d="{s.path}" fill="{a.fill}" '
            f'stroke="{OUTLINE}" stroke-width="{1 / k:.2f}" stroke-linejoin="round"/></g>'
        )
        dx, dy = (label_offsets or {}).get(s.district, (0, 0))
        lx, ly = x + s.label_x * k + dx, y + s.label_y * k + dy
        inside = (dx, dy) == (0, 0)
        ink = text_colour(a.fill) if inside else INK
        if not inside:  # leader line from the label's right edge to the district
            ex = lx + len(s.district) * 12 * CHAR_W / 2 + 4
            labels.append(
                f'<line x1="{ex:.1f}" y1="{ly - 4:.1f}" x2="{x + s.label_x * k:.1f}" '
                f'y2="{y + s.label_y * k:.1f}" stroke="{MUTED}" stroke-width="1"/>'
            )
        labels.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="12" fill="{ink}" '
            f'pointer-events="none"><tspan x="{lx:.1f}" font-weight="600">{escape(s.district)}'
            f'</tspan><tspan x="{lx:.1f}" dy="15">{escape(a.value)}</tspan></text>'
        )
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.4f})">{"".join(paths)}</g>'
        + "".join(labels)
    )


def map_height(shapes, w: float) -> float:
    return shapes.box_h.iloc[0] * w / shapes.box_w.iloc[0]


# Hierarchy tree (group → items), for changes in prices or indexes that don't add up: every
# item gets the same row, so nothing is sized by value. A chip beside each item is coloured
# by a diverging ramp (falls blue, rises red, little change grey); the signed change is
# always written next to it, so colour is never the only signal.
FALL_STRONG, FALL, NEUTRAL, RISE, RISE_STRONG = (
    "#2a78d6",
    "#a9c9f0",
    "#f0efec",
    "#f2a9a8",
    "#e34948",
)
DIVERGING = [FALL_STRONG, FALL, NEUTRAL, RISE, RISE_STRONG]


def change_colour(pct: float, flat: float = 0.5, strong: float = 10) -> str:
    """Diverging step for a % change: |change| < `flat` is grey, >= `strong` the darker step."""
    if pct <= -strong:
        return FALL_STRONG
    if pct <= -flat:
        return FALL
    if pct < flat:
        return NEUTRAL
    return RISE if pct < strong else RISE_STRONG


@dataclass(frozen=True)
class Leaf:
    """One item row: `change` is the signed text shown (e.g. "+28%"), `detail` the muted
    text after it (e.g. "B$2.67 → B$3.42 per kg", wide layout only)."""

    label: str
    colour: str
    change: str
    detail: str
    tooltip: str


ROW = 22
GROUP_GAP = 14


def tree(
    groups: list[tuple[str, list[Leaf]]], width: float, y0: float, compact: bool
) -> tuple[str, float]:
    """Groups and their items as a tree. Wide: group names on the left, linked by curves to
    their items. Compact (phones): an indented list with connector lines. Returns the markup
    and the y below the last row."""
    parts, y = [], y0
    longest_label = max(len(leaf.label) for _, leaves in groups for leaf in leaves)
    longest_change = max(len(leaf.change) for _, leaves in groups for leaf in leaves)
    # wide: group names' right edge; long names wrap onto two lines rather than widen the column
    gx = min(max(len(name) for name, _ in groups) * 13 * CHAR_W, 150) + 4
    ix = 18 if compact else gx + 46  # left edge of the item chips
    # right edge of the change text: after the longest label (wide), or the card edge (phones)
    change_x = (
        width - 4 if compact else ix + 18 + (longest_label + longest_change) * 13 * CHAR_W + 16
    )
    for name, leaves in groups:
        if compact:
            parts.append(
                f'<text x="0" y="{y + 14:.1f}" font-size="13" font-weight="600" '
                f'fill="{INK_2}">{escape(name)}</text>'
            )
            top = y + ROW
            rows_y = [top + i * ROW for i in range(len(leaves))]
            parts.append(
                f'<line x1="5" y1="{y + 19:.1f}" x2="5" y2="{rows_y[-1] + 11:.1f}" '
                f'stroke="{OUTLINE}" stroke-width="1"/>'
            )
        else:
            rows_y = [y + i * ROW for i in range(len(leaves))]
            mid = (rows_y[0] + rows_y[-1]) / 2 + 11
            lines = _wrap(name, 13, gx, max_lines=3) or [name]
            ty = mid + 4 - (len(lines) - 1) * 8
            for i, line in enumerate(lines):
                parts.append(
                    f'<text x="{gx:.1f}" y="{ty + i * 16:.1f}" text-anchor="end" font-size="13" '
                    f'font-weight="600" fill="{INK_2}">{escape(line)}</text>'
                )
            parts.append(f'<circle cx="{gx + 8:.1f}" cy="{mid:.1f}" r="3" fill="{OUTLINE}"/>')
        for leaf, ry in zip(leaves, rows_y, strict=True):
            cy = ry + 11
            if compact:
                parts.append(
                    f'<line x1="5" y1="{cy:.1f}" x2="{ix - 4:.1f}" y2="{cy:.1f}" '
                    f'stroke="{OUTLINE}" stroke-width="1"/>'
                )
            else:
                sx, ex = gx + 11, ix - 6
                parts.append(
                    f'<path d="M{sx:.1f},{mid:.1f} C{(sx + ex) / 2:.1f},{mid:.1f} '
                    f'{(sx + ex) / 2:.1f},{cy:.1f} {ex:.1f},{cy:.1f}" fill="none" '
                    f'stroke="{OUTLINE}" stroke-width="1"/>'
                )
            detail = (
                ""
                if compact
                else f'<text x="{change_x + 16:.1f}" y="{cy + 4:.1f}" font-size="12" '
                f'fill="{MUTED}">{escape(leaf.detail)}</text>'
            )
            parts.append(
                f"<g><title>{escape(leaf.tooltip)}</title>"
                f'<rect x="{ix - 6:.1f}" y="{ry:.1f}" width="{width - ix + 6:.1f}" height="{ROW}" '
                f'fill="{SURFACE}" fill-opacity="0"/>'
                f'<rect x="{ix:.1f}" y="{cy - 6:.1f}" width="12" height="12" rx="2" '
                f'fill="{leaf.colour}" stroke="{OUTLINE}" stroke-width="0.75"/>'
                f'<text x="{ix + 18:.1f}" y="{cy + 4:.1f}" font-size="13" fill="{INK}">'
                f"{escape(leaf.label)}</text>"
                f'<text x="{change_x:.1f}" y="{cy + 4:.1f}" text-anchor="end" font-size="13" '
                f'font-weight="600" fill="{INK}">{escape(leaf.change)}</text>{detail}</g>'
            )
        y = rows_y[-1] + ROW + GROUP_GAP
    return "".join(parts), y - GROUP_GAP
