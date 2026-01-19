from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd
import sqlite3

DB_PATH = "data/usa.db"

def load_states():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT code, name FROM states", conn)
    conn.close()
    return df

df_states = load_states()

app = Dash(__name__)

app.layout = html.Div([
    html.H1("USA Map"),

    dcc.Graph(
        figure=px.choropleth(
            df_states,
            locations="code",
            locationmode="USA-states",
            scope="usa",
            hover_name="name"
        )
    )
])

if __name__ == "__main__":
    app.run(debug=True)
