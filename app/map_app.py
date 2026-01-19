from dash import Dash, dcc, html, Input, Output, ALL
import plotly.express as px
import pandas as pd
import sqlite3

DB_PATH = "data/usa.db"


def load_global_filters():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, name, label FROM filters WHERE parent_id IS NULL", conn
    )
    conn.close()
    return df


def load_subfilters(parent_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, name, label FROM filters WHERE parent_id = ?", conn, params=(parent_id,)
    )
    conn.close()
    return df


df_globals = load_global_filters()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("USA Map – Multi Filters"),

    # 1) Global filters (checkbox)
    dcc.Checklist(
        id="global-filters",
        options=[{"label": r["label"], "value": r["id"]} for _, r in df_globals.iterrows()],
        value=[]
    ),

    # 2) Subfilters container (one dropdown per selected global filter)
    html.Div(id="subfilters-container"),

    # 3) Map
    dcc.Graph(id="usa-map")
])


# -----------------------
# Create one dropdown per global filter (optional)
# -----------------------
@app.callback(
    Output("subfilters-container", "children"),
    Input("global-filters", "value")
)
def create_subfilters(global_ids):
    children = []

    for gid in global_ids:
        df_sub = load_subfilters(gid)

        # if no subfilters exist, don't show dropdown
        if df_sub.empty:
            continue

        children.append(
            html.Div([
                html.H4(f"Subfilters for {df_globals[df_globals.id == gid].iloc[0]['label']}"),
                dcc.Dropdown(
                    id={"type": "subfilter-dropdown", "index": gid},
                    options=[{"label": r["label"], "value": r["id"]} for _, r in df_sub.iterrows()],
                    multi=True,
                    placeholder="Select subfilters..."
                )
            ])
        )

    return children


# -----------------------
# Map update with global + optional subfilters
# -----------------------
@app.callback(
    Output("usa-map", "figure"),
    Input("global-filters", "value"),
    Input({"type": "subfilter-dropdown", "index": ALL}, "value")
)
def update_map(global_ids, sub_values):
    sub_ids = [item for sub in sub_values if sub for item in sub]

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT s.code, s.name
        FROM states s
        JOIN state_filters sf ON sf.state_code = s.code
    """

    params = []
    conditions = []

    # Global filter condition
    if global_ids:
        conditions.append(f"sf.filter_id IN ({','.join('?'*len(global_ids))})")
        params.extend(global_ids)

    # Subfilter condition
    if sub_ids:
        conditions.append(f"sf.filter_id IN ({','.join('?'*len(sub_ids))})")
        params.extend(sub_ids)

    if conditions:
        query += " WHERE " + " OR ".join(conditions)

    query += " GROUP BY s.code"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    fig = px.choropleth(
        df,
        locations="code",
        locationmode="USA-states",
        scope="usa",
        hover_name="name"
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
