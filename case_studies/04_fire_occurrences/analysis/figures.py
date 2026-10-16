"""Charts for case study 04. Each builder returns (figure, table for the data-table view).

The three years with the most fires are teal in every chart, so readers can follow them from
the totals to the area burned and the districts; other years are context grey.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.charts import CONTEXT, INK, MUTED, SURFACE, TEAL_500

ORDER = ["Brunei-Muara", "Belait", "Tutong", "Temburong"]  # largest share first
COLUMNS = {
    "year": "Year",
    "district": "District",
    "fires": "Fires",
    "share_pct": "Share of the year's fires (%)",
    "forest_ha": "Forest burned (ha)",
    "grass_peat_ha": "Grass/peat burned (ha)",
    "total_ha": "Total burned (ha)",
}


def peak_years(totals: pd.DataFrame, n: int = 3) -> list[int]:
    return totals.nlargest(n, "fires").year.tolist()


def _colours(years, peaks) -> list[str]:
    return [TEAL_500 if y in peaks else CONTEXT for y in years]


def _quiet_stretch(totals: pd.DataFrame, level: float) -> float:
    """Middle of the longest run of years below `level`, where a label won't touch a bar."""
    best, run = [], []
    for year, v in zip(totals.year, totals.fires, strict=True):
        run = run + [year] if v < level else []
        best = run if len(run) > len(best) else best
    return (best[0] + best[-1]) / 2 if best else totals.year.iloc[0]


def yearly(totals: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: fires per year, peak years teal, with the median year as a reference line."""
    peaks = peak_years(totals)
    median = totals.fires.median()
    fig = go.Figure(
        go.Bar(
            x=totals.year,
            y=totals.fires,
            marker_color=_colours(totals.year, peaks),
            text=[
                f"{v:,}" if y in peaks else ""
                for y, v in zip(totals.year, totals.fires, strict=True)
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{x}: %{y:,} fires<extra></extra>",
        )
    )
    fig.add_hline(y=median, line=dict(color=MUTED, width=1.5, dash="dot"))
    fig.add_annotation(
        x=_quiet_stretch(totals, median),
        xanchor="center",
        bgcolor=SURFACE,
        y=median,
        yanchor="bottom",
        text=f"Median year: {int(median + 0.5):,}",  # halves round up, as on the page
        showarrow=False,
        font=dict(size=11, color=MUTED),
    )
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(tickformat=",", range=[0, totals.fires.max() * 1.12])
    fig.update_layout(hovermode="closest")
    return fig, totals[["year", "fires"]].rename(columns=COLUMNS)


def fires_and_area(totals: pd.DataFrame, cols: int = 2) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: fires and hectares burned side by side for the years both exist."""
    peaks = peak_years(totals)
    d = totals.dropna(subset=["total_ha"])
    titles = ["Fires", "Forest and grass/peat burned (hectares)"]
    rows = 1 if cols == 2 else 2
    fig = make_subplots(
        rows=rows, cols=cols, subplot_titles=titles, horizontal_spacing=0.1, vertical_spacing=0.18
    )
    fig.update_annotations(font=dict(color=INK, size=13))
    for i, (col, fmt) in enumerate((("fires", ",.0f"), ("total_ha", ",.0f"))):
        where = dict(row=1, col=i + 1) if cols == 2 else dict(row=i + 1, col=1)
        fig.add_trace(
            go.Bar(
                x=d.year,
                y=d[col],
                marker_color=_colours(d.year, peaks),
                hovertemplate=f"%{{x}}: %{{y:{fmt}}}<extra></extra>",
                showlegend=False,
            ),
            **where,
        )
        fig.update_yaxes(tickformat=",", **where)
    fig.update_xaxes(dtick=2)
    fig.update_layout(hovermode="closest", margin=dict(t=40))
    table = d[["year", "fires", "forest_ha", "grass_peat_ha", "total_ha"]].rename(columns=COLUMNS)
    return fig, table


def districts(
    fires: pd.DataFrame, totals: pd.DataFrame, cols: int = 4
) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: fires per year in each district, each panel on its own scale."""
    peaks = peak_years(totals)
    rows = -(-len(ORDER) // cols)
    fig = make_subplots(
        rows=rows, cols=cols, subplot_titles=ORDER, horizontal_spacing=0.07, vertical_spacing=0.16
    )
    fig.update_annotations(font=dict(color=INK, size=13))
    for i, name in enumerate(ORDER):
        d = fires[fires.district == name]
        fig.add_trace(
            go.Bar(
                x=d.year,
                y=d.fires,
                marker_color=_colours(d.year, peaks),
                hovertemplate=f"{name}, %{{x}}: %{{y:,}} fires<extra></extra>",
                showlegend=False,
            ),
            row=i // cols + 1,
            col=i % cols + 1,
        )
    fig.update_xaxes(dtick=4, tickangle=0)
    fig.update_yaxes(tickformat=",")
    fig.update_layout(hovermode="closest", margin=dict(t=40), bargap=0.2)
    table = fires[["year", "district", "fires", "share_pct"]].round(1).rename(columns=COLUMNS)
    return fig, table
