"""Charts for case study 03. Each builder returns (figure, table for the data-table view).

Period averages are drawn as flat segments over the years they cover, so readers see the
level of each period without reading single noisy years as a trend.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.charts import CONTEXT, INK, MUTED, SURFACE, TEAL_500

PANELS = [("accidents", "Accidents"), ("injuries", "People injured"), ("deaths", "People killed")]
COLUMNS = {
    "year": "Year",
    "accidents": "Accidents",
    "injuries": "People injured",
    "deaths": "People killed",
    "injuries_per_100_accidents": "Injured per 100 accidents",
    "deaths_per_1000_accidents": "Killed per 1,000 accidents",
}


def _span(period: str) -> tuple[int, int]:
    a, b = period.split("–")
    return int(a), int(b)


def _period_lines(
    fig, avg: pd.DataFrame, measure: str, color: str, fmt: str, label: bool = False, **where
) -> None:
    """One flat segment per period at its average. Labels are only for bar charts: on line
    charts they collide with the points, and the values are in the text, tiles and hover."""
    for _, p in avg.iterrows():
        a, b = _span(p.period)
        fig.add_trace(
            go.Scatter(
                x=[a - 0.4, b + 0.4],
                y=[p[measure]] * 2,
                mode="lines",
                line=dict(color=color, width=2, dash="dot"),
                hovertemplate=f"{p.period} average: {format(p[measure], fmt)}<extra></extra>",
                showlegend=False,
            ),
            **where,
        )
        if not label:
            continue
        fig.add_annotation(
            x=(a + b) / 2,
            y=p[measure],
            text=format(p[measure], fmt),
            showarrow=False,
            yanchor="bottom",
            yshift=2,
            font=dict(size=11, color=color),
            bgcolor=SURFACE,
            **where,
        )


def overview(
    roads: pd.DataFrame, avg: pd.DataFrame, cols: int = 3
) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: accidents, injuries and deaths per year, each in its own panel from zero,
    with 3-year averages."""
    rows = 1 if cols == 3 else 3
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=[t for _, t in PANELS],
        horizontal_spacing=0.08,
        vertical_spacing=0.12,
    )
    fig.update_annotations(font=dict(color=INK, size=13))  # panel titles only, added first
    for i, (col, _) in enumerate(PANELS):
        where = dict(row=1, col=i + 1) if cols == 3 else dict(row=i + 1, col=1)
        fig.add_trace(
            go.Scatter(
                x=roads.year,
                y=roads[col],
                mode="lines+markers",
                line=dict(color=TEAL_500),
                marker=dict(color=TEAL_500),
                hovertemplate="%{x}: %{y:,}<extra></extra>",
                showlegend=False,
            ),
            **where,
        )
        _period_lines(fig, avg, col, MUTED, ",.0f", **where)
        fig.update_yaxes(range=[0, roads[col].max() * 1.18], tickformat=",", **where)
    fig.update_xaxes(dtick=2)
    fig.update_layout(hovermode="closest", margin=dict(t=40))
    table = roads[["year", "accidents", "injuries", "deaths"]].rename(columns=COLUMNS)
    return fig, table


def deaths(roads: pd.DataFrame, avg: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: people killed each year (grey) against 3-year averages (teal)."""
    fig = go.Figure(
        go.Bar(
            x=roads.year,
            y=roads.deaths,
            marker_color=CONTEXT,
            text=roads.deaths,
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}: %{y} killed<extra></extra>",
            showlegend=False,
        )
    )
    _period_lines(fig, avg, "deaths", TEAL_500, ".0f", label=True)
    for trace in fig.data[1:]:
        trace.line.update(dash="solid", width=3)
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, roads.deaths.max() * 1.2])
    fig.update_layout(hovermode="closest")
    table = roads[["year", "deaths"]].rename(columns=COLUMNS)
    return fig, table


def per_accident(roads: pd.DataFrame, avg: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: people injured per 100 accidents, with 3-year averages."""
    fig = go.Figure(
        go.Scatter(
            x=roads.year,
            y=roads.injuries_per_100_accidents,
            mode="lines+markers",
            line=dict(color=TEAL_500),
            marker=dict(color=TEAL_500),
            hovertemplate="%{x}: %{y:.1f} per 100 accidents<extra></extra>",
            showlegend=False,
        )
    )
    _period_lines(fig, avg, "injuries_per_100_accidents", MUTED, ".1f")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, roads.injuries_per_100_accidents.max() * 1.2])
    fig.update_layout(hovermode="closest")
    cols = ["year", "accidents", "injuries", "deaths"]
    cols += ["injuries_per_100_accidents", "deaths_per_1000_accidents"]
    table = roads[cols].round(1).rename(columns=COLUMNS)
    return fig, table
