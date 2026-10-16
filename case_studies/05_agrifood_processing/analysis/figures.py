"""Charts for case study 05. Each builder returns (figure, table for the data-table view).

Values are shown in B$ million. The category first counted in 2013 is always grey, so it never
reads as growth of the categories that were already counted.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.charts import CONTEXT, INK, TEAL_500

NEW = "Fast or instant food"
COLUMNS = {
    "year": "Year",
    "category": "Product category",
    "category_ms": "Kategori (Malay, as published)",
    "district": "District",
    "comparable_bnd": "Categories counted every year (B$)",
    "new_category_bnd": "Fast or instant food, first counted 2013 (B$)",
    "total_bnd": "Total (B$)",
    "livestock_bnd": "Livestock-based (B$)",
    "crop_bnd": "Crop-based (B$)",
    "value_bnd": "Market value (B$)",
    "businesses": "Businesses",
    "employees": "Employees",
    "share_pct": "Share of market value (%)",
    "businesses_share_pct": "Share of businesses (%)",
    "employees_share_pct": "Share of employees (%)",
    "value_bnd_share_pct": "Share of market value (%)",
}


def millions(v: float, d: int = 1) -> str:
    return f"B${v / 1e6:,.{d}f}m"


def series_chart(series: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: market value per year, with the 2013 newcomer stacked on top in grey."""
    fig = go.Figure()
    fig.add_bar(
        x=series.year,
        y=series.comparable_bnd / 1e6,
        name="Categories counted every year",
        marker_color=TEAL_500,
        hovertemplate="%{x}: B$%{y:.1f}m<extra>Categories counted every year</extra>",
    )
    fig.add_bar(
        x=series.year,
        y=series.new_category_bnd / 1e6,
        name=f"{NEW} (first counted in 2013)",
        marker_color=CONTEXT,
        hovertemplate="%{x}: B$%{y:.1f}m<extra>" + NEW + "</extra>",
    )
    last = series.iloc[-1]
    fig.add_annotation(
        x=last.year, y=last.total_bnd / 1e6, text=millions(last.total_bnd), showarrow=False,
        yanchor="bottom", yshift=4, font=dict(color=INK, size=12),
    )  # fmt: skip
    for _, r in series[series.year.isin([series.year.min(), series.year.max() - 1])].iterrows():
        fig.add_annotation(
            x=r.year, y=r.comparable_bnd / 1e6, text=millions(r.comparable_bnd), showarrow=False,
            yanchor="bottom", yshift=4, font=dict(color=INK, size=12),
        )  # fmt: skip
    fig.update_layout(barmode="stack", hovermode="closest")
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(
        tickprefix="B$", ticksuffix="m", range=[0, series.total_bnd.max() / 1e6 * 1.15]
    )
    cols = ["year", "livestock_bnd", "crop_bnd", "total_bnd", "new_category_bnd", "comparable_bnd"]
    return fig, series[cols].round(0).rename(columns=COLUMNS)


def categories_chart(trend: pd.DataFrame, a: int, b: int) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: market value by category in year a (grey) and year b (teal)."""
    d = trend[trend.year.isin([a, b])]
    order = d[d.year == b].sort_values("value_bnd", ascending=False).category.tolist()
    fig = go.Figure()
    for year, colour in ((a, CONTEXT), (b, TEAL_500)):
        y = d[d.year == year].set_index("category").reindex(order)
        fig.add_bar(
            name=str(year),
            orientation="h",
            y=order,
            x=y.value_bnd / 1e6,
            marker_color=colour,
            text=[f"{v / 1e6:.1f}" for v in y.value_bnd],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"%{{y}}, {year}: B$%{{x:.2f}}m<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05, hovermode="closest")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(
        showticklabels=False, showgrid=False, range=[0, d.value_bnd.max() / 1e6 * 1.15]
    )
    table = d.pivot(index=["category", "category_ms"], columns="year", values="value_bnd")
    table = table.reindex(order, level=0).reset_index()
    table.columns = ["Product category", "Kategori (Malay)", f"{a} (B$)", f"{b} (B$)"]
    return fig, table.round(0)


def _share_panels(d: pd.DataFrame, label: str, panels, cols: int, highlight: str = ""):
    rows = 1 if cols == len(panels) else len(panels)
    fig = make_subplots(
        rows=rows, cols=cols, subplot_titles=[t for _, t in panels], shared_yaxes=True,
        horizontal_spacing=0.04, vertical_spacing=0.1,
    )  # fmt: skip
    fig.update_annotations(font=dict(color=INK, size=13))
    for i, (col, _) in enumerate(panels):
        where = dict(row=1, col=i + 1) if rows == 1 else dict(row=i + 1, col=1)
        fig.add_bar(
            orientation="h",
            y=d[label],
            x=d[col],
            marker_color=[TEAL_500 if v == highlight else CONTEXT for v in d[label]],
            text=[f"{v:.0f}%" if v >= 1 else f"{v:.1f}%" for v in d[col]],  # no misleading 0%
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
            showlegend=False,
            **where,
        )
        fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, 118], **where)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(hovermode="closest", margin=dict(t=40))
    return fig


def producers_chart(cats: pd.DataFrame, cols: int = 2) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: each category's share of businesses and of market value, 2013."""
    d = cats.assign(businesses_share_pct=cats.businesses / cats.businesses.sum() * 100)
    d = d.sort_values("businesses", ascending=False)
    panels = [
        ("businesses_share_pct", "Share of businesses*"),
        ("share_pct", "Share of market value"),
    ]
    fig = _share_panels(d, "category", panels, cols, highlight="Traditional foods")
    cols_out = [
        "category",
        "category_ms",
        "businesses",
        "businesses_share_pct",
        "value_bnd",
        "share_pct",
    ]
    return fig, d[cols_out].round(1).rename(columns=COLUMNS)


def districts_chart(districts: pd.DataFrame, cols: int = 3) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 4: each district's share of businesses, employees and market value, 2013."""
    panels = [
        ("businesses_share_pct", "Businesses"),
        ("employees_share_pct", "Employees"),
        ("value_bnd_share_pct", "Market value"),
    ]
    fig = _share_panels(districts, "district", panels, cols, highlight="Brunei-Muara")
    out = ["district", "businesses", "employees", "value_bnd"] + [c for c, _ in panels]
    return fig, districts[out].round(1).rename(columns=COLUMNS)
