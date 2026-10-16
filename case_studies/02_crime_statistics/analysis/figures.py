"""Charts for case study 02. Each builder returns (figure, table for the data-table view).

Every chart compares the years side by side: earlier years in context grey, the latest in teal.
"""

import pandas as pd
import plotly.graph_objects as go

from shared.charts import CONTEXT, TEAL_500

SHORT = {  # chart labels; full published names stay in the data table
    "Against Human Body": "Against the human body",
    "Against Property": "Against property",
    "Other Offences Against Penal Code": "Other Penal Code offences",
    "Against Various Acts": "Various Acts",
    "Against Immigration Act": "Immigration Act",
    "Against Misuses of Drug Act": "Misuse of Drugs Act",
    "Against Customs & Excise Act": "Customs & Excise Act",
    "Against Labour Act": "Labour Act",
    "Other Acts": "Other Acts (merged)",
}
COLUMNS = {
    "year": "Year",
    "offence": "Type of offence (as published)",
    "cases": "Cases",
    "solved": "Solved",
    "solved_pct": "Solved (%)",
    "arrests": "Persons arrested",
}


def _grouped_bars(d: pd.DataFrame, value: str, fmt: str, suffix: str = "") -> go.Figure:
    """Horizontal bars, one group per offence (largest latest-year value on top), one bar
    per year. Missing values get no bar and a "not published" label."""
    years = sorted(d.year.unique())
    latest = d[d.year == years[-1]].sort_values(value, ascending=False, na_position="last")
    order = [SHORT[o] for o in latest.offence]
    fig = go.Figure()
    for year in years:
        y = d[d.year == year].assign(label=lambda x: x.offence.map(SHORT))
        y = y.set_index("label").reindex(order)
        fig.add_bar(
            name=str(year),
            orientation="h",
            y=order,
            x=y[value],
            marker_color=TEAL_500 if year == years[-1] else CONTEXT,
            text=[format(v, fmt) + suffix if pd.notna(v) else "not published" for v in y[value]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"%{{y}}, {year}: %{{x:{fmt}}}{suffix}<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.08, hovermode="closest")
    fig.update_yaxes(autorange="reversed")  # first category and first year on top
    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=True)
    return fig


def _table(d: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return d[cols].rename(columns=COLUMNS).reset_index(drop=True)


def police_cases(rows: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 1: cases handled by police, by type of offence."""
    d = rows[rows.handled_by == "police"]
    fig = _grouped_bars(d, "cases", ",.0f")
    fig.update_xaxes(range=[0, d.cases.max() * 1.22])
    return fig, _table(d, ["year", "offence", "cases"])


def police_solved(rows: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 2: share of police cases solved, by type of offence."""
    d = rows[rows.handled_by == "police"]
    fig = _grouped_bars(d, "solved_pct", ".0f", "%")
    fig.update_xaxes(range=[0, 118])
    return fig, _table(d, ["year", "offence", "cases", "solved", "solved_pct"])


def other_agency_cases(rows: pd.DataFrame) -> tuple[go.Figure, pd.DataFrame]:
    """Chart 3: cases handled by other agencies, by Act."""
    d = rows[rows.handled_by == "other agencies"]
    fig = _grouped_bars(d, "cases", ",.0f")
    fig.update_xaxes(range=[0, d.cases.max() * 1.22])
    return fig, _table(d, ["year", "offence", "cases", "solved", "arrests"])
