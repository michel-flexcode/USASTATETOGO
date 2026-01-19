from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import sqlite3

def load_data():
    conn = sqlite3.connect("usa.db")
    df = pd.read_sql_query("SELECT * FROM states", conn)
    conn.close()
    return df

df = load_data()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("USA Map - Multi Filters (DB)"),

    dcc.Checklist(
        options=[
            {"label": "Gun Rights", "value": "gun_rights"},
            {"label": "Tax Free", "value": "tax_free"},
            {"label": "Anti-Squat Law", "value": "anti_squat"},
            {"label": "Left-Wing Law", "value": "left_law"},
            {"label": "Abortion Allowed", "value": "abortion"},
        ],
        value=[],
        id="filters"
    ),

    dcc.Graph(id="usa_map")
])

@app.callback(
    Output("usa_map", "figure"),
    Input("filters", "value")
)
def update_map(active_filters):
    filtered = df.copy()
    for f in active_filters:
        filtered = filtered[filtered[f] == 1]

    fig = px.choropleth(
        filtered,
        locations="state",
        locationmode="USA-states",
        color="state",
        scope="usa"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
