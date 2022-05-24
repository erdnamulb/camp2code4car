import sys
import dash
import pandas as pd
from dash import dcc
from dash import html
import dash_daq as daq
#import dash_html_components as html
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from sqlite3 import connect
import datetime as dt


app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
#app = dash.Dash(__name__)
df = pd.DataFrame()
#conn = connect(f'{sys.path[0]}/logdata.sqlite')
conn = connect(f'{sys.path[0]}/P5_45speed_5ms_300_q.sqlite')
df = pd.read_sql('SELECT timestamp, distance, ir1, ir2, ir3, ir4, ir5, speed, direction, angle FROM drivedata', conn)
df = df[df['timestamp'] != '0']   # Zeilen mit 0 im Zeitstempel ausfiltern
# print(df)
df['time'] = df.apply(
    lambda row: dt.datetime.fromtimestamp(float(row.timestamp)), axis=1)
#print(df)
features = df.columns[1:len(df.columns)-1]


speed_max = df['speed'].max()
speed_min = df['speed'].min()
speed_mean = round(df['speed'].mean(),2)
time_start = dt.datetime.fromtimestamp(float(df['timestamp'].min()))
time_stop = dt.datetime.fromtimestamp(float(df['timestamp'].max()))
duration = time_stop - time_start
drivetime_tot = round(duration.total_seconds(),1)
drivetime_str = str(drivetime_tot) + " s"
distance_tot = round(drivetime_tot * speed_mean * (30/40), 1) # ca. 30cm bei Geschwindigkeit 40 pro s
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
        html.Br(),
        html.Div(
            children=[
                dbc.Row([
                dbc.Col([card_speed_max], width=3),
                dbc.Col([card_speed_min], width=3),
                dbc.Col([card_speed_mean], width=3),
                ], align='center'),
                html.Br(),
                dbc.Row([
                dbc.Col([card_drivetime_tot], width=3),
                dbc.Col([card_distance_tot], width=3),
                ], align='center')
            ], style={'marginTop': 10, 'marginLeft': 40}
        ),
        html.Br(),
        dcc.Dropdown(
            id='choose_data',
            options=[{'label': i, 'value': i} for i in features],
            value='distance',
        ),
        html.Br(),
        dcc.Graph(id='dataplot')
    ]
)


@app.callback(
    Output(component_id='dataplot', component_property='figure'),
    [Input(component_id='choose_data', component_property='value')])
def graph_update(value_of_input_component):
    fig = px.line(df, x=pd.to_datetime(df['time']), y=df[value_of_input_component],
    title="Gruppe 3 Fahrdaten", 
    labels={'x': 'Zeit', 'y':value_of_input_component})
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
