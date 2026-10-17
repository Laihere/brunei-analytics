"""Charts for case study 08. Each builder returns (figure, table for the data-table view).

Local containers are teal and transhipment violet (the pair validated for case study 07).
Uncontainerised cargo is one series, so it is teal with no legend.
"""

import pandas as pd
import plotly.graph_objects as go

from shared.charts import CATEGORICAL, SURFACE, TEAL_500

VIOLET = CATEGORICAL[1]


def containers(df: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: containers handled per year, thousand TEU, local and transhipment stacked."""
    fig = go.Figure()
    for col, name, colour in [
        ("local_teu", "Local (to or from Brunei)", TEAL_500),
        ("transhipment_teu", "Transhipment (passing through)", VIOLET),
    ]:
        fig.add_trace(
            go.Bar(
                x=df.year,
                y=df[col] / 1000,
                name=name,
                marker=dict(color=colour, line=dict(width=1, color=SURFACE)),  # gap between
                hovertemplate=f"{name}: %{{y:.1f}}k TEU<extra></extra>",
            )
        )
    fig.update_layout(
        barmode="stack", showlegend=True, hovermode="x unified", legend_traceorder="normal"
    )  # legend in reading order: local first
    fig.update_yaxes(ticksuffix="k TEU", rangemode="tozero")
    fig.update_xaxes(dtick=2)
    table = df[
        ["year", "local_teu", "transhipment_teu", "total_teu", "total_published_teu", "gap_teu"]
    ].copy()
    table.columns = [
        "Year",
        "Local (TEU)",
        "Transhipment (TEU)",
        "Local + transhipment (TEU)",
        "Total as published (TEU)",
        "Difference (TEU)",
    ]
    return fig, table


def cargo(df: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: uncontainerised cargo per year, million tonnes."""
    fig = go.Figure(
        go.Bar(
            x=df.year,
            y=df.cargo_tonnes / 1e6,
            marker=dict(color=TEAL_500),
            hovertemplate="%{x}: %{y:.2f} million tonnes<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_yaxes(ticksuffix="m t", rangemode="tozero")
    fig.update_xaxes(dtick=2)
    fig.update_layout(hovermode="closest")
    table = df[["year", "cargo_tonnes", "change_pct"]].copy()
    table.columns = ["Year", "Uncontainerised cargo (tonnes)", "Change on previous year (%)"]
    return fig, table
