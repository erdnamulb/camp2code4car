import sys
from cv2 import VideoCapture, cuda_GpuMat_Allocator
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
from flask import Flask, Response

from requests import Response
from frame_editing import *

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY])
server = Flask(__name__)

#app = dash.Dash(__name__)
df = pd.DataFrame()
conn = connect(f'{sys.path[0]}/logdata.sqlite')
#conn = connect(f'{sys.path[0]}/P5_45speed_5ms_300_q.sqlite')
df = pd.read_sql('SELECT timestamp, distance, ir1, ir2, ir3, ir4, ir5, speed, direction, angle FROM drivedata', conn)
df = df[df['timestamp'] != '0']   # Zeilen mit 0 im Zeitstempel ausfiltern
# print(df)
df['time'] = df.apply(
    lambda row: dt.datetime.fromtimestamp(float(row.timestamp)), axis=1)
#print(df)
features = df.columns[1:len(df.columns)-1]

#cam = CamCar()
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

def gen():
    cam = CamCar
    while True:
        frame = cam.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@server.route('/video_feed')
def video_feed():
    return Response(gen(CamCar()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

card_speed_max = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("v_max", className="card-title"),
                html.P(
                    speed_max,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "10rem"}, color="primary", inverse=True,
)

card_speed_min = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("v_min", className="card-title"),
                html.P(
                    speed_min,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "10rem"}, color="primary", inverse=True,
)

card_speed_mean = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("v_avg", className="card-title"),
                html.P(
                    speed_mean,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "10rem"}, color="primary", inverse=True,
)

card_drivetime_tot = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Gesamtzeit", className="card-title"),
                html.P(
                    drivetime_str,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "12rem"}, color="secondary", inverse=True,
)

card_distance_tot = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Gesamtstrecke", className="card-title"),
                html.P(
                    distance_str,
                    className="card-text",
                ),
            ]
        ),
    ],
    style={"width": "12rem"}, color="secondary", inverse=True,
)


COL_Headline = [  # Col Headline
    dbc.Col(
        [  # Col 1
            html.H1(
                id="title_main",
                children="PiCar Dashboard Gruppe 3",
                style={
                    "textAlign": "center",
                    "marginTop": 40,
                    "marginBottom": 30,
                    #"text-decoration": "underline",
                },
            )
        ],
        width=12,
    ),
]

COL_Manual = [
    dbc.Col(
        [html.H5("manuell an/aus"), 
        dbc.Switch(id="sw_manual")], 
        #width=4
        ),
    ]

COL_Joystick = [
    dbc.Col([
        html.H5("Car-Stick"),
        daq.Joystick(id="joystick", size=100, className="mb-3")],
        #width=4,
    ),
    dbc.Col(
        [
            html.P(id="value_joystick"),
        ],
        width=3,
    ),
    ]

COL_Slider = [
    dbc.Col([html.H5("vMax:")], width=5),
    dbc.Col(
        [
            dcc.Slider(
                min=0,
                max=100,
                step=10,
                id="slider_speed",
                value=30,
                updatemode="drag",
                vertical=True
            )
        ],
        width=8,
    ),
    ]

CARD_SteeringControl = dbc.Card(
    [
        dbc.Row(
            dbc.Col([
                dbc.Row(COL_Manual),
                dbc.Row(COL_Joystick)
            ], width=12
            ),
        ),
    ],
)

COL_Graph = [  # Diagramm
    dbc.Row([
            dcc.Graph(id='dataplot'),
            html.Div(id="dummy"),
            html.Div(id="dummy2"),
            dcc.Interval(id="intervall_10s", interval=10000),
            dcc.Interval(
                id="interval_startup",
                max_intervals=1,
                    ),
            ])
    ]

COL_Dropdown = [  # Auswahlfeld
    dbc.Row([
            html.H5(id="titel_LogDetails", children="Graph Auswahl"),
            dcc.Dropdown( # Dropdown Auswahl
                id='choose_data',
                options=[{'label': i, 'value': i} for i in features],
                value='distance',
                #multi=True,
                style={"color": "black",
                    "paddingBottom": 10},
                ),
            ],
            style={"paddingBottom": 10},
        ),
    ]

COL_LiveView = [ 
    dbc.Row(
            [  
                html.H1(
                    id="titel_Kamera",
                    children="LiveView",
                    style={
                        "textAlign": "center",
                        "paddingBottom": 10,
                    },
                )
            ]
        ),
    dbc.Row(
            [  # Kamerabild
                html.Img(src="/video_feed")
            ]
        ),
]

app.layout = \
dbc.Container\
([
    dbc.Row(
        [  # erste Zeile - Überschrift
            dbc.Col(
                COL_Headline,
            ),
        ],
        justify="center",
    ),
    dbc.Row(
        [  # zweite Zeile - Werteanzeigen
            dbc.Col(
                card_speed_max,
                #width=2
            ),
            #dbc.Col([], width=1),  # Col Space
            dbc.Col(
                card_speed_min,
                #width=3
            ),
            dbc.Col(
                card_speed_mean,
            ),
            dbc.Col(
                card_drivetime_tot,
            ),
            dbc.Col(
                card_distance_tot,
            ),
        ],
        justify="center",
        style={"paddingTop": 20, "paddingBottom": 20},
    ),
    dbc.Row(
        [  # dritte Zeile
            dbc.Col(
                COL_Dropdown,
                width=2,
                align='center'
            ),
            #dbc.Col([], width=1),  # Col Space
            dbc.Col(
                COL_Graph,
                #width=3
            ),
            #dbc.Col(
            #    COL_Graph,
            #),
        ],
        justify="center",
        style={"paddingTop": 20, "paddingBottom": 20},
    ),
    dbc.Row(
        [  # vierte Zeile
            dbc.Col([
                dbc.Row(COL_Manual),
                dbc.Row(html.Div(id="empty", children=' ')),
                dbc.Row(COL_Joystick)
            ],
                #CARD_SteeringControl,
                width=2,
                align='center'
            ),
            #dbc.Col([], width=1),  # Col Space
            dbc.Col(
                COL_Slider,
                width=2
            ),
            dbc.Col(
                COL_LiveView,
                width=8
            ),

        ],
        justify="center",
        style={"paddingTop": 20, "paddingBottom": 20},
    ),

])


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
