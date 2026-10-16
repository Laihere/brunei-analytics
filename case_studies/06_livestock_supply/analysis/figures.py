"""Charts for case study 06. Each builder returns (figure, table for the data-table view).

Local production is teal and imports grey throughout, so "how much was made in Brunei" always
reads the same way.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.charts import CONTEXT, INK, MUTED, TEAL_500

SHARE_PANELS = ["chicken", "eggs", "beef"]
CHAIN = ["hatching_eggs", "chicks", "chicken"]  # fertilized eggs → day-old chicks → meat
COLUMNS = {
    "year": "Year",
    "label": "Product",
    "unit": "Unit",
    "local": "Local production",
    "imports": "Imports",
    "imports_alive": "Imported live (t)",
    "imports_chilled_frozen": "Imported chilled & frozen (t)",
    "local_share_pct": "Local share of supply (%)",
}


def _pct(v: float) -> str:
    return f"{v:.0f}%" if v >= 10 else f"{v:.1f}%"


def shares(data: pd.DataFrame, cols: int = 3) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: local share of supply for chicken meat, eggs and beef, one panel each, 0–100%."""
    d = data[data["product"].isin(SHARE_PANELS)]
    titles = [d[d["product"] == p].label.iloc[0] for p in SHARE_PANELS]
    rows = 1 if cols == 3 else 3
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=titles,
        shared_yaxes=rows == 1,
        horizontal_spacing=0.05,
        vertical_spacing=0.12,
    )
    fig.update_annotations(font=dict(color=INK, size=13))
    for i, p in enumerate(SHARE_PANELS):
        s = d[d["product"] == p]
        where = dict(row=1, col=i + 1) if rows == 1 else dict(row=i + 1, col=1)
        fig.add_trace(
            go.Scatter(
                x=s.year,
                y=s.local_share_pct,
                mode="lines",
                line=dict(color=TEAL_500, width=2.5),
                fill="tozeroy",
                fillcolor="rgba(13, 148, 136, 0.12)",
                hovertemplate=f"{titles[i]}, %{{x}}: %{{y:.1f}}% local<extra></extra>",
                showlegend=False,
            ),
            **where,
        )
        last = s.iloc[-1]
        fig.add_annotation(
            x=last.year,
            y=last.local_share_pct,
            text=_pct(last.local_share_pct),
            showarrow=False,
            xanchor="right",
            yanchor="bottom",
            yshift=4,
            font=dict(color=INK, size=12),
            **where,
        )
        fig.update_yaxes(range=[0, 108], ticksuffix="%", dtick=25, **where)
    fig.update_xaxes(range=[1991, 2021], dtick=10)
    fig.update_layout(hovermode="closest", margin=dict(t=40))
    table = d[["year", "label", "local_share_pct"]].pivot(index="year", columns="label")
    table.columns = [f"{c} (%)" for _, c in table.columns]
    return fig, table.reset_index().rename(columns={"year": "Year"}).round(1)


def chicken_volumes(data: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: chicken meat supply, local (teal) and imported (grey), stacked, in tonnes."""
    d = data[data["product"] == "chicken"]
    fig = go.Figure()
    fig.add_bar(
        x=d.year,
        y=d.local / 1000,
        name="Produced locally",
        marker_color=TEAL_500,
        hovertemplate="%{x}: %{y:.1f} thousand t local<extra></extra>",
    )
    fig.add_bar(
        x=d.year,
        y=d.imports / 1000,
        name="Imported",
        marker_color=CONTEXT,
        hovertemplate="%{x}: %{y:.1f} thousand t imported<extra></extra>",
    )
    fig.update_layout(barmode="stack", hovermode="closest", bargap=0.2)
    fig.update_xaxes(dtick=4)
    fig.update_yaxes(ticksuffix="k t")
    table = d[["year", "local", "imports", "local_share_pct"]].round(1)
    table.columns = ["Year", "Produced locally (t)", "Imported (t)", "Local share (%)"]
    return fig, table


def chain(data: pd.DataFrame, a: int, b: int) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: local share at each step of the chicken chain, year a (grey) and year b (teal)."""
    d = data[data["product"].isin(CHAIN) & data.year.isin([a, b])]
    labels = {p: d[d["product"] == p].label.iloc[0] for p in CHAIN}
    order = [labels[p] for p in CHAIN]
    fig = go.Figure()
    for year, colour in ((a, CONTEXT), (b, TEAL_500)):
        y = d[d.year == year].set_index("label").reindex(order)
        fig.add_bar(
            name=str(year),
            orientation="h",
            y=order,
            x=y.local_share_pct,
            marker_color=colour,
            text=[_pct(v) for v in y.local_share_pct],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"%{{y}}, {year}: %{{x:.1f}}% local<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08, hovermode="closest")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, 115], showticklabels=False, showgrid=False)
    for i, text in enumerate(("hatch into", "grow into")):
        fig.add_annotation(
            x=0,
            y=i + 0.5,
            xref="paper",
            xanchor="right",
            xshift=-4,
            text=f"↓ {text}",
            showarrow=False,
            font=dict(size=10, color=MUTED),
        )
    table = d.pivot(index="label", columns="year", values="local_share_pct").reindex(order)
    table.columns = [f"Local share {c} (%)" for c in table.columns]
    return fig, table.reset_index().rename(columns={"label": "Step"}).round(1)


def beef_volumes(data: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 4: beef supply by source, stacked, from 2000. Local is teal; the two kinds of
    import are two greys, so teal always means "produced locally"."""
    d = data[data["product"] == "beef"]
    fig = go.Figure()
    parts = [
        ("local", "Produced locally", TEAL_500),
        ("imports_alive", "Imported live (slaughtered in Brunei)", MUTED),
        ("imports_chilled_frozen", "Imported chilled & frozen", CONTEXT),
    ]
    for col, name, colour in parts:
        fig.add_bar(
            x=d.year,
            y=d[col],
            name=name,
            marker_color=colour,
            hovertemplate=f"%{{x}}: %{{y:,.0f}} t<extra>{name}</extra>",
        )
    fig.update_layout(barmode="stack", hovermode="closest", bargap=0.2)
    fig.update_xaxes(dtick=4)
    fig.update_yaxes(tickformat=",", ticksuffix=" t")
    table = d[
        ["year", "local", "imports_alive", "imports_chilled_frozen", "local_share_pct"]
    ].round(1)
    return fig, table.rename(columns={**COLUMNS, "local": "Produced locally (t)"})
