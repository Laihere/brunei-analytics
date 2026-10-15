"""House chart style for Plotly (turquoise theme, DESIGN.md §7–8).

Default chart: one series in teal, the rest in context grey (`highlight`). Use the
categorical palette only when every series matters, at most 4. Palettes were checked
with the dataviz validator; yellow sits below 3:1, so every chart ships with the
table view (see shared.components.chart_card).
"""

import textwrap

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from shared.provenance import Provenance, short_credit

TEAL_500 = "#0d9488"  # brand mark: highlighted series
TEAL_700 = "#0f766e"
CONTEXT = "#c3c2b7"  # non-highlighted series
CATEGORICAL = [TEAL_500, "#6250d6", "#eda100", "#e34948"]  # teal, violet, yellow, red
SEQUENTIAL = ["#5ec4b8", "#2aa898", TEAL_500, TEAL_700, "#134e4a"]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#6b6863"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'

CONFIG = {"displayModeBar": False, "responsive": True}

_axis = dict(
    automargin=True,
    gridcolor=GRID,
    gridwidth=1,
    linecolor=BASELINE,
    zerolinecolor=BASELINE,
    tickfont=dict(color=MUTED),
    title=dict(font=dict(color=INK_2)),
)

pio.templates["brunei"] = go.layout.Template(
    layout=dict(
        font=dict(family=FONT, color=INK, size=13),
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        colorway=CATEGORICAL,
        xaxis={**_axis, "showgrid": False},
        yaxis={**_axis, "showgrid": True},
        legend=dict(font=dict(color=INK_2), orientation="h", y=1.02, yanchor="bottom", x=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=GRID, font=dict(color=INK, family=FONT)),
        bargap=0.35,
        margin=dict(l=8, r=8, t=24, b=8),
    ),
    data=dict(
        scatter=[
            go.Scatter(
                line=dict(width=2),
                marker=dict(size=8, line=dict(width=2, color=SURFACE)),
            )
        ],
        bar=[go.Bar(marker=dict(cornerradius=4, line=dict(width=0)))],
    ),
)
pio.templates.default = "brunei"


def highlight(fig: go.Figure, focus: str, label: str | None = None) -> go.Figure:
    """Colour one series (line charts: trace name) or one category (bar charts) in teal
    and send everything else to context grey (DESIGN.md §8, Von Restorff)."""
    focus_line = None
    for trace in fig.data:
        if trace.type == "scatter":
            on = trace.name == focus
            colour = TEAL_500 if on else CONTEXT
            trace.update(mode="lines", line=dict(color=colour, width=2))
            if on:
                focus_line = trace
        elif trace.type == "bar":
            cats = trace.y if trace.orientation == "h" else trace.x
            trace.marker.color = [TEAL_500 if c == focus else CONTEXT for c in cats]

    if focus_line is not None:
        # Highlighted line on top of the grey ones, with a labelled end dot.
        fig.data = tuple(t for t in fig.data if t is not focus_line) + (focus_line,)
        fig.add_trace(
            go.Scatter(
                x=[focus_line.x[-1]],
                y=[focus_line.y[-1]],
                mode="markers+text",
                text=[label or focus],
                textposition="top left",
                textfont=dict(color=INK, size=12),
                marker=dict(color=TEAL_500, size=9, line=dict(width=2, color=SURFACE)),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.update_layout(showlegend=False)
    return fig


def add_credit(fig: go.Figure, provenance: list[Provenance], width: int = 120) -> go.Figure:
    """Credit line inside the image, for static exports only. On the site the chart card
    prints the credit as real text instead (shared.components.chart_card)."""
    fig.add_annotation(
        text="<br>".join(textwrap.wrap(short_credit(provenance), width)),
        xref="paper",
        yref="paper",
        x=0,
        y=-0.22,
        xanchor="left",
        yanchor="top",
        showarrow=False,
        align="left",
        font=dict(size=11, color=MUTED),
    )
    fig.update_layout(margin=dict(b=96))
    return fig


def data_table(df: pd.DataFrame) -> str:
    """Accessible table view of a chart's data, as HTML."""
    return df.to_html(index=False, classes="table table-sm", border=0)
