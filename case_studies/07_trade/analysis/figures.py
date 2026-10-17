"""Charts for case study 07. Each builder returns (figure, table for the data-table view).

Exports are teal and imports violet throughout (CATEGORICAL order, validated as a pair against
the chart surface). In the section charts, the section the text is about is teal, a second
one violet, and the rest context grey, each with a legend and an end label.
"""

import pandas as pd
import plotly.graph_objects as go

from shared.charts import CATEGORICAL, CONTEXT, INK, SURFACE, TEAL_500

VIOLET = CATEGORICAL[1]
FLOW_COLOUR = {"exports": TEAL_500, "imports": VIOLET}
FLOW_LABEL = {"exports": "Exports", "imports": "Imports"}


def _bn(v: float) -> str:
    """BND million → "B$9.7 bn"."""
    return f"B${v / 1000:.1f} bn"


def _ticks(years: pd.Series) -> list[int]:
    """Every 5 years within the data, so the space kept for end labels shows no later years."""
    return [y for y in range(2000, int(years.max()) + 1, 5) if y >= years.min() - 1]


def _end_label(fig: go.Figure, x, y, text: str, colour: str, position: str = "middle right"):
    fig.add_trace(
        go.Scatter(
            x=[x],
            y=[y],
            mode="markers+text",
            text=[text],
            textposition=position,
            textfont=dict(color=INK, size=12),
            marker=dict(color=colour, size=8, line=dict(width=2, color=SURFACE)),
            hoverinfo="skip",
            showlegend=False,
        )
    )


def flows(trade: pd.DataFrame, compact: bool = False) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: exports and imports by year, BND billion, one axis. `compact` (phones) labels
    the line ends with the value only, so the labels fit; the legend names the lines."""
    fig = go.Figure()
    last = trade.iloc[-1]
    for flow in ("exports", "imports"):
        fig.add_trace(
            go.Scatter(
                x=trade.year,
                y=trade[flow] / 1000,
                name=FLOW_LABEL[flow],
                mode="lines",
                line=dict(color=FLOW_COLOUR[flow], width=2.5),
                hovertemplate=f"{FLOW_LABEL[flow]}: B$%{{y:.1f}} bn<extra></extra>",
            )
        )
        text = f"{last[flow] / 1000:.1f}" if compact else _bn(last[flow])
        _end_label(fig, last.year, last[flow] / 1000, text, FLOW_COLOUR[flow])
    fig.update_yaxes(rangemode="tozero", tickprefix="B$", ticksuffix=" bn")
    fig.update_xaxes(
        range=[trade.year.min() - 0.5, trade.year.max() + 3], tickvals=_ticks(trade.year)
    )
    fig.update_layout(showlegend=True, hovermode="x unified")
    table = trade[["year", "exports", "imports", "balance"]].copy()
    table[["exports", "imports", "balance"]] = table[["exports", "imports", "balance"]].round(1)
    table.columns = ["Year", "Exports (B$ million)", "Imports (B$ million)", "Balance (B$ million)"]
    return fig, table


def balance(trade: pd.DataFrame, compact: bool = False) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: balance of trade (exports − imports) by year; the smallest year in teal.
    `compact` (phones) leaves out the label, which the narrow bars can't fit; the chart title
    names the year and the data table has the value."""
    low = trade.loc[trade.balance.idxmin(), "year"]
    colours = [TEAL_500 if y == low else CONTEXT for y in trade.year]
    fig = go.Figure(
        go.Bar(
            x=trade.year,
            y=trade.balance / 1000,
            marker=dict(color=colours, line=dict(width=0)),
            hovertemplate="%{x}: surplus of B$%{y:.1f} bn<extra></extra>",
            showlegend=False,
        )
    )
    row = trade[trade.year == low].iloc[0]
    if not compact:
        _label_low(fig, low, row.balance)
    fig.update_yaxes(rangemode="tozero", tickprefix="B$", ticksuffix=" bn")
    fig.update_xaxes(dtick=5)
    fig.update_layout(hovermode="closest")
    table = trade[["year", "balance"]].round(1)
    table.columns = ["Year", "Balance of trade (B$ million)"]
    return fig, table


def _label_low(fig: go.Figure, low: int, value: float):
    fig.add_annotation(  # up and to the left, clear of the neighbouring bars
        x=low,
        y=value / 1000,
        text=f"{low}: {_bn(value)}",
        showarrow=True,
        arrowcolor=INK,
        arrowwidth=1,
        arrowhead=0,
        ax=-70,
        ay=-60,
        xanchor="right",
        font=dict(color=INK, size=12),
        bgcolor=SURFACE,
    )


def _section_lines(
    sections: pd.DataFrame,
    flow: str,
    shown: list[int],
    focus: int,
    second: int,
    compact: bool = False,
) -> tuple[go.Figure, pd.DataFrame]:
    """Share of exports or imports by section, for the `shown` sections; the rest are summed
    into "All other sections" so the shares on the chart always add up to 100%."""
    d = sections[sections.flow == flow].copy()
    d["group"] = d.sitc.where(d.sitc.isin(shown), -1)
    names = dict(zip(d.sitc, d.section, strict=False)) | {-1: "All other sections"}
    g = d.groupby(["year", "group"], as_index=False).share_pct.sum()
    colour = {focus: TEAL_500, second: VIOLET}
    greys = [c for c in [*shown, -1] if c not in colour]
    dash = {c: ("solid" if i == 0 else "dot") for i, c in enumerate(greys)}  # not colour alone
    fig = go.Figure()
    last_year = g.year.max()
    order = [c for c in [*shown, -1] if c not in (focus, second)] + [second, focus]  # focus on top
    for code in order:
        s = g[g.group == code]
        c = colour.get(code, CONTEXT)
        fig.add_trace(
            go.Scatter(
                x=s.year,
                y=s.share_pct,
                name=names[code],
                mode="lines",
                line=dict(
                    color=c, width=2.5 if code in colour else 2, dash=dash.get(code, "solid")
                ),
                hovertemplate=f"{names[code]}: %{{y:.1f}}%<extra></extra>",
            )
        )
        end = s[s.year == last_year].share_pct.iloc[0]
        if not compact:
            _end_label(fig, last_year, end, f"{names[code]} {end:.0f}%", c)
        elif code in colour:  # phones: value only, highlighted lines only; legend names all
            _end_label(fig, last_year, end, f"{end:.0f}%", c)
    fig.update_yaxes(range=[0, 100], ticksuffix="%", dtick=25)
    fig.update_xaxes(
        range=[g.year.min() - 0.5, last_year + (3 if compact else 8)], tickvals=_ticks(g.year)
    )
    fig.update_layout(showlegend=True, hovermode="x unified")
    table = g.assign(name=g.group.map(names))
    table = table.pivot(index="year", columns="name", values="share_pct")
    table = table[[names[c] for c in [*shown, -1]]].round(1)
    table.columns = [f"{c} (% of {flow})" for c in table.columns]
    return fig, table.reset_index().rename(columns={"year": "Year"})


def export_mix(sections: pd.DataFrame, compact: bool = False) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: share of exports, mineral fuels (teal) and chemicals (violet), 2009 onwards."""
    return _section_lines(sections, "exports", [3, 5], focus=3, second=5, compact=compact)


def import_mix(sections: pd.DataFrame, compact: bool = False) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 4: share of imports by the largest sections, mineral fuels (teal) and machinery
    and transport (violet), 2000 onwards."""
    return _section_lines(sections, "imports", [3, 7, 6], focus=3, second=7, compact=compact)
