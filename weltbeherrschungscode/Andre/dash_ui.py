import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
df = px.data.stocks()

speed_max = 55
speed_min = 15
speed_mean = 35
drivetime_tot = 1234
drivetime_str = str(drivetime_tot) + " s"
distance_tot = drivetime_tot * speed_mean
distance_str = str(distance_tot) + " cm"

card_speed_max = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("v_max", className="card-title"),
                html.P(
                    speed_max,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"}, color="primary", inverse=True,
)

card_speed_min = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("v_min", className="card-title"),
                html.P(
                    speed_min,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"}, color="primary", inverse=True,
)

card_speed_mean = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("v_avg", className="card-title"),
                html.P(
                    speed_mean,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"}, color="primary", inverse=True,
)

card_drivetime_tot = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("Gesamtzeit", className="card-title"),
                html.P(
                    drivetime_str,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"}, color="secondary", inverse=True,
)

card_distance_tot = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H3("Gesamtstrecke", className="card-title"),
                html.P(
                    distance_str,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "18rem"}, color="secondary", inverse=True,
)

app.layout = html.Div(
    children=[
        html.H1(id='H1',
                children='Sensordaten Cockpit',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.H4(id='H2',
                children='Datenübersicht SensorCar'),
        html.Div(children='Laberrhabarber'),
        html.Br(),
        dbc.Row([
            dbc.Col([card_speed_max], width=3),
            dbc.Col([card_speed_min], width=3),
            dbc.Col([card_speed_mean], width=3),
        ], align='center'),
        html.Br(),
        dbc.Row([
            dbc.Col([card_drivetime_tot], width=3),
            dbc.Col([card_distance_tot], width=3),
        ], align='center'),
    ]
)



if __name__ == '__main__':
    app.run_server(debug=True)
