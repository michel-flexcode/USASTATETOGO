from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# <-- ici le df
data = {
    "state": ["CA", "CA", "TX", "TX", "NY", "FL"],
    "category": ["A", "B", "A", "C", "B", "A"],
    "value": [100, 50, 80, 40, 70, 60]
}

df = pd.DataFrame(data)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        options=[{"label": s, "value": s} for s in sorted(df["state"].unique())],
        multi=True,
        id="state_filter",
        placeholder="Select states"
    ),

    dcc.Dropdown(
        options=[{"label": c, "value": c} for c in sorted(df["category"].unique())],
        multi=True,
        id="category_filter",
        placeholder="Select categories"
    ),

    dcc.Graph(id="usa_map")
])

@app.callback(
    Output("usa_map", "figure"),
    Input("state_filter", "value"),
    Input("category_filter", "value")
)
def update_map(states, categories):
    filtered = df.copy()

    if states:
        filtered = filtered[filtered["state"].isin(states)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]

    grouped = filtered.groupby("state", as_index=False)["value"].sum()

    fig = px.choropleth(
        grouped,
        locations="state",
        locationmode="USA-states",
        color="value",
        scope="usa",
        color_continuous_scale="Blues"
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True)

