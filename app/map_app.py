from dash import Dash, dcc, html, Input, Output, ALL
import plotly.express as px
import pandas as pd
import sqlite3

DB_PATH = "data/usa.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM states", conn)
    conn.close()
    return df

def load_filters():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM filters", conn)
    conn.close()
    return df

def load_state_filters():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT sf.state_code, f.category, f.name
        FROM state_filters sf
        JOIN filters f ON sf.filter_id = f.id
    """, conn)
    conn.close()
    return df

df_states = load_data()
df_filters = load_filters()
df_state_filters = load_state_filters()

app = Dash(__name__)

# global filters (parent_id IS NULL)
global_filters = df_filters[df_filters["parent_id"].isnull()]

app.layout = html.Div([
    html.H1("USA Map - Multi Filters (DB)"),

    dcc.Checklist(
        id="global-filters",
        options=[{"label": r["label"], "value": r["name"]} for _, r in global_filters.iterrows()],
        value=[]
    ),

    html.Div(id="subfilter-container"),
    dcc.Graph(id="usa-map"),
])


@app.callback(
    Output("subfilter-container", "children"),
    Input("global-filters", "value")
)
def render_subfilters(active_globals):
    children = []
    for g in active_globals:
        parent = global_filters[global_filters["name"] == g].iloc[0]
        children_rows = df_filters[df_filters["parent_id"] == parent["id"]]

        if not children_rows.empty:
            children.append(html.Div([
                html.Label(f"Subfilters for {parent['label']}"),
                dcc.Checklist(
                    id={"type": "subfilters", "index": g},
                    options=[{"label": r["label"], "value": r["name"]} for _, r in children_rows.iterrows()],
                    value=[]
                )
            ]))
    return children


@app.callback(
    Output("usa-map", "figure"),
    Input("global-filters", "value"),
    Input({"type": "subfilters", "index": ALL}, "value")
)
def update_map(active_globals, subfilter_values):
    filtered = df_states.copy()

    # 1) global filters only (no subfilters)
    if active_globals and not any(subfilter_values):
        # keep states that match at least one subfilter of each global
        for g in active_globals:
            parent = global_filters[global_filters["name"] == g].iloc[0]
            child_names = df_filters[df_filters["parent_id"] == parent["id"]]["name"].tolist()
            state_codes = df_state_filters[df_state_filters["name"].isin(child_names)]["state_code"].unique()
            filtered = filtered[filtered["code"].isin(state_codes)]

    # 2) subfilters selected (AND logic)
    if any(subfilter_values):
        # subfilter_values is a list of lists
        for sublist in subfilter_values:
            for sf in sublist:
                state_codes = df_state_filters[df_state_filters["name"] == sf]["state_code"].unique()
                filtered = filtered[filtered["code"].isin(state_codes)]

    # If empty, keep all and show message
    if filtered.empty:
        filtered = df_states.copy()

    fig = px.choropleth(
        filtered,
        locations="code",
        locationmode="USA-states",
        color="name",
        scope="usa"
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
