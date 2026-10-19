"""Charts for case study 09. Each builder returns (figure, table for the data-table view).

Charts 1 and 3 are hierarchy trees (static SVG, shared.svg.tree): group → item, every item the
same size, because prices in different units don't add up. A chip beside each item shows its
change on a diverging ramp (falls blue, rises red, under 0.5% grey); the signed change is
written beside it. Chart 2 is a range chart (Plotly bars from the lowest to the highest index
value, a dot for the last year).
"""

import pandas as pd
import plotly.graph_objects as go

from shared import svg
from shared.charts import CONTEXT, INK, SURFACE, TEAL_500

FOOD_ORDER = [
    "Rice and cereals",
    "Fresh meat and poultry",
    "Milk, eggs and fats",
    "Fish and prawns",
    "Vegetables and fruits",
]
NONFOOD_ORDER = ["Housing, water, electricity and gas", "Passports"]
LEGEND = [
    ("Fell 10% or more", svg.FALL_STRONG),
    ("Fell", svg.FALL),
    ("Little change (under 0.5%)", svg.NEUTRAL),
    ("Rose", svg.RISE),
    ("Rose 10% or more", svg.RISE_STRONG),
]


def signed(pct: float) -> str:
    """One decimal, so the text always agrees with the colour step (e.g. −9.9%, not −10%)."""
    return "no change" if abs(pct) < 0.05 else f"{pct:+.1f}%".replace("-", "−")


def money(v: float) -> str:
    return f"B${v:,.2f}"


def _unit(unit: str) -> str:
    return "" if unit in ("", "each") else f" {unit}" if unit.startswith("per") else f" ({unit})"


def _tree(change: pd.DataFrame, order: list[str], first: int, last: int, compact: bool):
    groups = []
    for g in order:
        # largest rise first; ties keep the published order
        rows = change[change.group == g].sort_values("change_pct", ascending=False, kind="stable")
        leaves = []
        for r in rows.to_dict("records"):
            a, b, unit = money(r[f"price_{first}"]), money(r[f"price_{last}"]), _unit(r["unit"])
            leaves.append(
                svg.Leaf(
                    label=r["label"],
                    colour=svg.change_colour(r["change_pct"]),
                    change=signed(r["change_pct"]),
                    # "unit not stated" stays in the tooltip and table; it doesn't fit the row
                    detail=f"{a} → {b}" + ("" if r["unit"] == "unit not stated" else unit),
                    tooltip=(
                        f"{r['label']}{unit}: {a} in {first}, {b} in {last} "
                        f"({signed(r['change_pct'])})"
                    ),
                )
            )
        groups.append((g, leaves))
    width = 340 if compact else 720
    body, legend_y = svg.legend(0, 14, LEGEND, width)
    rows_svg, bottom = svg.tree(groups, width, legend_y + 18, compact)
    table = change.assign(group=pd.Categorical(change.group, order, ordered=True))
    table = table.sort_values(["group", "change_pct"], ascending=[True, False])
    table = table[["group", "label", "unit", f"price_{first}", f"price_{last}", "change_pct"]]
    table.columns = [
        "Group",
        "Item",
        "Unit",
        f"{first} (B$)",
        f"{last} (B$)",
        f"Change {first}–{last} (%)",
    ]
    return svg.svg(width, bottom + 4, body + rows_svg), table.round(2).reset_index(drop=True)


def food_tree(change: pd.DataFrame, first: int, last: int, compact: bool = False):
    """Chart 1: food items by group, change in average retail price."""
    return _tree(change, FOOD_ORDER, first, last, compact)


def nonfood_tree(change: pd.DataFrame, first: int, last: int, compact: bool = False):
    """Chart 3: non-food items by group, change in price."""
    return _tree(change, NONFOOD_ORDER, first, last, compact)


def food_ranges(
    prices: pd.DataFrame, first: int, last: int, highlight: list[str], compact: bool = False
) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: for each food item, the lowest-to-highest index (first year = 100) over
    first–last as a bar, and the last year as a dot. Items sorted by the width of the range;
    `highlight` items in teal, the rest grey."""
    d = prices[prices.year.between(first, last)]
    g = d.groupby("label").index_2013.agg(low="min", high="max")
    g["end"] = d[d.year == last].set_index("label").index_2013
    g["width"] = g.high - g.low
    g = g.sort_values("width")
    colours = [TEAL_500 if lab in highlight else CONTEXT for lab in g.index]
    fig = go.Figure()
    fig.add_bar(
        orientation="h",
        y=g.index,
        x=g.width,
        base=g.low,
        marker=dict(color=colours, line=dict(width=0)),
        customdata=g[["low", "high"]].round(0).values,
        hovertemplate=(
            "%{y}: lowest %{customdata[0]:.0f}, highest %{customdata[1]:.0f}<extra></extra>"
        ),
        showlegend=False,
    )
    fig.add_scatter(
        x=g.end,
        y=g.index,
        mode="markers",
        marker=dict(color=INK, size=8, line=dict(width=2, color=SURFACE)),
        name=str(last),
        hovertemplate=f"%{{y}}, {last}: %{{x:.0f}}<extra></extra>",
        showlegend=False,
    )
    fig.add_vline(x=100, line=dict(color=INK, width=1, dash="dot"))
    fig.update_layout(hovermode="closest", bargap=0.35)
    fig.update_xaxes(showgrid=True, dtick=10 if not compact else 20)
    fig.update_yaxes(tickfont=dict(size=11 if compact else 12))
    table = g.reset_index()[["label", "low", "high", "end"]].iloc[::-1].round(1)
    table.columns = ["Item", f"Lowest, {first}–{last}", f"Highest, {first}–{last}", f"{last}"]
    return fig, table
