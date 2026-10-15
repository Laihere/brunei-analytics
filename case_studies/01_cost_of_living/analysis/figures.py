"""Charts for case study 01. Each builder returns (figure, table for the data-table view)."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from shared.charts import CONTEXT, INK, MUTED, TEAL_500, highlight

BASE_YEAR = 2019
PERIODS = [  # labels describe when, not why (DESIGN.md §6; study scope)
    ("Before", 2015.5, 2019.5),
    ("Pandemic years<br>and after", 2019.5, 2022.5),
    ("Recent", 2022.5, 2025.5),
]
SHORT = {
    "Overall CPI": "All items",
    "Food and Non-Alcoholic Beverages": "Food & drink",
    "Clothing and Footwear": "Clothing",
    "Housing, Water, Electricity, Gas and Other Fuels": "Housing & utilities",
    "Furnishing, Household Equipment and Routine Household Maintenance": "Household goods",
    "Health": "Health",
    "Transport": "Transport",
    "Communication": "Communication",
    "Recreation and Culture": "Recreation",
    "Education": "Education",
    "Restaurants and Hotels": "Restaurants & hotels",
    "Miscellaneous Goods and Services": "Miscellaneous",
}
ITEM_SHORT = {  # chart labels; full names stay in the data table
    "Vegetable Oil (5 Kg Bottle)": "Vegetable oil (5 kg)",
    "Palm Oil (2 Kg Bottle)": "Palm oil (2 kg)",
    "Corn Oil (3 Kg Bottle)": "Corn oil (3 kg)",
    "Infant Formula Milk Powder (900g Per Tin)": "Infant formula (900 g)",
    "Maternal Formula Milk Powder (650g Per Box)": "Maternal formula (650 g)",
    "Ordinary Thai Rice (10 Kilogramme Bag)": "Thai rice, ordinary (10 kg)",
    "Fragrant Thai Rice (10 Kilogramme Bag)": "Thai rice, fragrant (10 kg)",
    "Glutinous Rice (10 Kilogramme Bag)": "Glutinous rice (10 kg)",
    "Sugar (Per Kilogramme)": "Sugar (1 kg)",
}
SHADE = "rgba(195, 194, 183, 0.18)"


def signed(v: float, digits: int = 1) -> str:
    """Signed percentage with a true minus sign."""
    return f"{v:+.{digits}f}%".replace("-", "−")


def _pad_range(values, share: float = 0.18) -> list[float]:
    """Axis range with room for bar labels, keeping zero in view."""
    lo, hi = min(0, min(values)), max(0, max(values))
    pad = (hi - lo) * share
    return [lo - pad / 3 if lo < 0 else lo - pad / 3, hi + pad]


def _label_bars(fig: go.Figure, values, names, digits: int) -> None:
    """Value labels for horizontal bars. Positive: at the bar tip. Negative: just right of
    zero, so the label never collides with the category names on narrow screens."""
    fig.data[0].update(
        text=[signed(v, digits) if v >= 0 else "" for v in values],
        textposition="outside",
        cliponaxis=False,
    )
    for v, name in zip(values, names, strict=True):
        if v < 0:
            fig.add_annotation(
                x=0,
                y=name,
                text=signed(v, digits),
                showarrow=False,
                xanchor="left",
                xshift=4,
                font=dict(color=INK, size=12),
            )


def _shade_pandemic(fig: go.Figure, labels: bool = True, **where) -> None:
    _, x0, x1 = PERIODS[1]
    fig.add_vrect(x0=x0, x1=x1, fillcolor=SHADE, line_width=0, layer="below", **where)
    if labels:
        for name, a, b in PERIODS:
            fig.add_annotation(
                x=(a + b) / 2,
                y=1.0,
                yref="paper",
                yanchor="bottom",
                text=name,
                showarrow=False,
                font=dict(size=11, color=MUTED),
            )


def annual_change(change: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: overall yearly % change, 2016–2025, with the three periods marked."""
    d = change[change.category == "Overall CPI"].sort_values("year")
    fig = go.Figure(
        go.Bar(
            x=d.year,
            y=d["pct_change"],
            marker_color=TEAL_500,
            hovertemplate="%{x}: %{y:+.1f}%<extra></extra>",
        )
    )
    for year in (2022, 2025):
        v = d.loc[d.year == year, "pct_change"].iloc[0]
        fig.add_annotation(
            x=year,
            y=v,
            text=signed(v),
            showarrow=False,
            yanchor="bottom" if v >= 0 else "top",
            yshift=4 if v >= 0 else -4,
            font=dict(color=INK, size=12),
        )
    _shade_pandemic(fig)
    fig.update_yaxes(ticksuffix="%", zeroline=True)
    fig.update_xaxes(dtick=1)
    fig.update_layout(hovermode="closest", margin=dict(t=32))
    table = d[["year", "pct_change"]].rename(columns={"year": "Year", "pct_change": "Change (%)"})
    return fig, table


def level_vs_base(index: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: overall and food prices relative to 2019 (= 100)."""
    keep = {"Overall CPI": "All items", "Food and Non-Alcoholic Beverages": "Food & drink"}
    d = index[index.category.isin(keep)].assign(series=lambda x: x.category.map(keep))
    fig = go.Figure()
    for name in ("All items", "Food & drink"):
        s = d[d.series == name].sort_values("year")
        fig.add_trace(
            go.Scatter(
                x=s.year,
                y=s.index_vs_base,
                name=name,
                hovertemplate=f"{name}, %{{x}}: %{{y:.1f}}<extra></extra>",
            )
        )
    food_end = d[(d.series == "Food & drink") & (d.year == 2025)].index_vs_base.iloc[0]
    all_end = d[(d.series == "All items") & (d.year == 2025)].index_vs_base.iloc[0]
    highlight(fig, "Food & drink", label=f"Food & drink {signed(food_end - 100)}")
    fig.add_annotation(
        x=2025,
        y=all_end,
        text=f"All items {signed(all_end - 100)}",
        showarrow=False,
        xanchor="right",
        yanchor="top",
        yshift=-6,
        font=dict(color=MUTED, size=12),
    )
    fig.add_hline(y=100, line=dict(color=MUTED, width=1))
    fig.add_annotation(
        x=2015,
        y=100,
        text="2019 level",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color=MUTED, size=11),
    )
    _shade_pandemic(fig)
    fig.update_xaxes(dtick=1)
    fig.update_layout(hovermode="x unified", margin=dict(t=32))
    table = d.pivot(index="year", columns="series", values="index_vs_base").round(1)
    return fig, table.reset_index().rename(columns={"year": "Year"})


def since_base_by_category(summary: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: change since 2019 by category, food highlighted, all items as reference."""
    col = f"change_since_{BASE_YEAR}_pct"
    overall = summary.loc[summary.category == "Overall CPI", col].iloc[0]
    d = summary[summary.category != "Overall CPI"].assign(name=lambda x: x.category.map(SHORT))
    d = d.sort_values(col)
    fig = go.Figure(
        go.Bar(
            x=d[col],
            y=d.name,
            orientation="h",
            hovertemplate="%{y}: %{x:+.1f}% since 2019<extra></extra>",
        )
    )
    highlight(fig, "Food & drink")
    _label_bars(fig, d[col], d.name, digits=1)
    fig.add_vline(x=overall, line=dict(color=MUTED, width=1))
    fig.add_annotation(
        x=overall,
        y=1.0,
        yref="paper",
        yanchor="bottom",
        text=f"All items {signed(overall)}",
        showarrow=False,
        font=dict(color=MUTED, size=11),
    )
    fig.update_xaxes(ticksuffix="%", zeroline=True, range=_pad_range(d[col]))
    fig.update_layout(hovermode="closest", margin=dict(t=32, r=48))
    table = d[["category", col]].rename(
        columns={"category": "Category", col: f"Change since {BASE_YEAR} (%)"}
    )
    return fig, table.iloc[::-1].round(1)


def category_timelines(index: pd.DataFrame, cols: int = 3) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 4: small multiples, one per category, against all items (grey)."""
    last = index[index.year == 2025].set_index("category").index_vs_base
    order = [c for c in last.drop("Overall CPI").sort_values(ascending=False).index]
    rows = -(-len(order) // cols)
    fig = make_subplots(
        rows=rows,
        cols=cols,
        shared_xaxes=True,
        shared_yaxes="all",
        subplot_titles=[f"{SHORT[c]} {signed(last[c] - 100, 0)}" for c in order],
        vertical_spacing=min(0.08, 0.36 / rows),
        horizontal_spacing=0.06,
    )
    overall = index[index.category == "Overall CPI"].sort_values("year")
    for i, cat in enumerate(order):
        r, c = divmod(i, cols)
        s = index[index.category == cat].sort_values("year")
        where = dict(row=r + 1, col=c + 1)
        fig.add_trace(
            go.Scatter(
                x=overall.year,
                y=overall.index_vs_base,
                mode="lines",
                line=dict(color=CONTEXT, width=1.5),
                hoverinfo="skip",
                showlegend=False,
            ),
            **where,
        )
        fig.add_trace(
            go.Scatter(
                x=s.year,
                y=s.index_vs_base,
                mode="lines",
                line=dict(color=TEAL_500, width=2),
                showlegend=False,
                hovertemplate=f"{SHORT[cat]}, %{{x}}: %{{y:.1f}}<extra></extra>",
            ),
            **where,
        )
        _shade_pandemic(fig, labels=False, **where)
        fig.add_hline(y=100, line=dict(color=CONTEXT, width=1), **where)
    fig.update_annotations(font=dict(size=12 if cols > 2 else 11, color=INK))
    # One y scale for every panel, so heights compare across rows (small-multiple rule).
    values = index.index_vs_base
    fig.update_xaxes(tickvals=[2019, 2025], showgrid=False)
    fig.update_yaxes(
        range=[values.min() - 2, values.max() + 2], tickvals=[90, 100, 110, 120], showgrid=True
    )
    fig.update_layout(hovermode="closest", margin=dict(t=40))
    table = index.pivot(index="year", columns="category", values="index_vs_base").round(1)
    table = table[["Overall CPI", *order]].rename(columns=SHORT)
    return fig, table.reset_index().rename(columns={"year": "Year"})


def subsidised_since_base(items: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 5: price change 2019 → 2025 for subsidised and price-controlled items."""
    w = items.pivot(index="item", columns="year", values="price_bnd")
    w = w.dropna(subset=[BASE_YEAR, 2025])  # drops Laila/Local rice (series break)
    d = pd.DataFrame(
        {
            "item": w.index,
            "price_2019": w[BASE_YEAR],
            "price_2025": w[2025],
            "change_pct": (w[2025] / w[BASE_YEAR] - 1) * 100,
        }
    ).sort_values("change_pct")
    fig = go.Figure(
        go.Bar(
            x=d.change_pct,
            y=d.item.map(ITEM_SHORT).fillna(d.item),
            orientation="h",
            customdata=d[["price_2019", "price_2025"]],
            hovertemplate=(
                "%{y}<br>BND %{customdata[0]:.2f} → %{customdata[1]:.2f} (%{x:+.1f}%)"
                "<extra></extra>"
            ),
        )
    )
    highlight(fig, ITEM_SHORT["Vegetable Oil (5 Kg Bottle)"])
    _label_bars(fig, d.change_pct, fig.data[0].y, digits=0)
    fig.update_xaxes(ticksuffix="%", zeroline=True, range=_pad_range(d.change_pct))
    fig.update_layout(hovermode="closest", margin=dict(r=48))
    table = d.iloc[::-1].rename(
        columns={
            "item": "Item",
            "price_2019": "2019 (BND)",
            "price_2025": "2025 (BND)",
            "change_pct": "Change (%)",
        }
    )
    return fig, table.round(2)
