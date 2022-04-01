import sys
import dash
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from sqlite3 import connect
import datetime as dt


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
df = pd.DataFrame()
conn = connect(f'{sys.path[0]}/logdata.sqlite')
df = pd.read_sql('SELECT timestamp, distance, ir1, ir2, ir3, ir4, ir5, speed, direction, angle FROM drivedata', conn)
print(df)
#df = df.loc[df['timestamp'] != '0']
df = df[df['timestamp'] != '0']   # Zeilen mit 0 im Zeitstempel ausfiltern
print(df)
df['time'] = df.apply(
    lambda row: dt.datetime.fromtimestamp(float(row.timestamp)), axis=1)
print(df)
features = df.columns[1:len(df.columns)]


speed_max = df['speed'].max()
speed_min = df['speed'].min()
speed_mean = df['speed'].mean()
time_start = dt.datetime.fromtimestamp(float(df['timestamp'].min()))
time_stop = dt.datetime.fromtimestamp(float(df['timestamp'].max()))
duration = time_stop - time_start
drivetime_tot = duration.total_seconds()
drivetime_str = str(drivetime_tot) + " s"
distance_tot = drivetime_tot * speed_mean * (30/40) # ca. 30cm bei Geschwindigkeit 40 pro s
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
                children='Datenübersicht SensorCar',
                ),
        html.Div(children='Laberrhabarber',
                style={'marginTop': 10, 'marginLeft': 40}),
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
        dcc.Graph(id='dataplot'),
        html.Br(),
        html.Div(
                [
                dbc.Button('Prog. 2', id='startbutton-2', color='primary', className='p2-start', value='2'),
                #dbc.Button('Prog. 3', id='startbutton-3', color='primary', className='p3-start', value='3'),
                #dbc.Button('Prog. 4', id='startbutton-4', color='primary', className='p4-start', value='4'),
                html.Span(id='status-output', style={"verticalAlign": "middle"}),
                ], style={'marginTop': 10, 'marginLeft': 40}
                ), 
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


@app.callback(
    Output('status-output', 'children'), 
    #Output('status-output', 'children'), 
    #Output('status-output', 'children'), 
    [Input('startbutton-2', 'value')],
    #[Input('startbutton-3', 'value')],
    #[Input('startbutton-4', 'value')]
    )
def on_button_click(value):
    # Testdrive.py aufrufen mit entsprechendem Argument
    text = 'Fahrprogramm {} wird gestartet.'.format(value)
    return text


if __name__ == '__main__':
    app.run_server(debug=True)
