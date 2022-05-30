import os, json, time
import socket
import pandas as pd
import datetime
import plotly.express as px
from dash import dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
from flask import Flask, Response, request
from auto_code_Allan import CamCar


"""Initialisiere DataFrame und Car."""
df = None
car = CamCar()

car_scale = 1/1
car_blur = 1
car_dilation = 2
car_canny_lower = 50
car_canny_upper = 125
car_houghes_threshold = 40
car_houghes_minLineLength = 70
car_houghes_maxLineGap = 30


"""Initialisiere Flask-Server und Dash-APP."""
server = Flask(__name__)
app = dash.Dash(
    __name__,
    server = server,
    external_stylesheets=[dbc.themes.SUPERHERO],
    meta_tags=[
        {"name": "viewport"},
        {"content": "width = device,width, initial-scale=1.0"},
    ],
)


@server.route('/video_feed')
def video_feed():
    """Will return the video feed from the camera
    Returns:
        Response: Response object with the video feed
    """
    return Response(car.get_image_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def get_ip_address():
    """Ermittlung der IP-Adresse im Netzwerk
    Returns:
        str: lokale IP-Adresse
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    socket_ip = s.getsockname()[0]
    s.close()
    return socket_ip


def getLoggerFiles():
    """Files im Ordner "Logger" auflisten
    Returns:
        list: Log-Dateien
    """
    fileList = []
    outputList = []
    if os.path.isdir("Logger"):
        fileList = os.listdir("Logger")
        for file in fileList:
            if file.partition(".")[2] == "log":
                outputList.append(file)
            outputList.sort()
            outputList.reverse()
    return outputList


def getLogItemsList():
    """Definition der Spaltennamen für die Daten im Logfile
    Returns:
        list: Spaltennamen
    """
    return [
        "time",
        "v",
        "dir",
        "st_angle",
    ]


def load_data_to_df(pfad):
    """aktualisiert die Daten im Dataframe
    Args:
        pfad (str): Dateipfad zum File das geladen werden soll
    """
    global df
    df = pd.read_json(os.path.join("Logger", pfad))
    df.columns = getLogItemsList()

"""Liste der Fahrparcours fuer das Dropdown."""
FP_LISTE = [  # Liste der auswählbaren Fahrprogramme
    {"label": "FP 1 --- Parameter-Tuning", "value": 1},
    {"label": "FP 2 --- OpenCV", "value": 2},
    {"label": "FP 3 --- DeepNN", "value": 3},
]

"""CARDS der KPI."""
kpi_1 = dbc.Card([dbc.CardBody([html.H6("vMax"), html.P(id="kpi1")])])
kpi_2 = dbc.Card([dbc.CardBody([html.H6("vMin"), html.P(id="kpi2")])])
kpi_3 = dbc.Card([dbc.CardBody([html.H6("vMean"), html.P(id="kpi3")])])
kpi_4 = dbc.Card([dbc.CardBody([html.H6("time"), html.P(id="kpi4")])])
kpi_5 = dbc.Card([dbc.CardBody([html.H6("vm"), html.P(id="kpi5")])])

"""ROW der Joystick Ansicht."""
row_joystick = dbc.Row(
    [
        dbc.Col(
            [
                html.P("Manuell on/off"),
                dbc.Switch(id="sw_manual"),
            ], 
            width=4),
        dbc.Col(
            daq.Joystick(id="joystick", size=100, className="mb-3"),
            width=4,
        ),
        dbc.Col(
            [
                html.P(id="value_joystick"),
            ],
            width=4,
        ),
    ]
)

"""CARD der Manuellen Steuerung."""
CARD_ManuelleSteuerung = dbc.Card(
    [
        dbc.Row(
            [  # Titel Manuelle Steuerung
                html.H3(
                    id="label_test",
                    children="Manuelle Steuerung",
                    style={
                        "textAlign": "left",
                        "paddingTop": 20,
                        "paddingBottom": 20,
                    },
                )
            ]
        ),
        dbc.Row(
            [  # Slider Speed
                dbc.Col([html.H6("max. speed:")], width=4),
                dbc.Col(
                    [
                        dcc.Slider(
                            min=0,
                            max=100,
                            step=10,
                            id="slider_speed",
                            value=50,
                            updatemode="drag",
                        ),
                    ],
                    width=8,
                ),
            ]
        ),
        row_joystick,
    ],
)

"""Spalte der Headline."""
COL_Headline = [  # Col Headline
    dbc.Col(
        [  # Col 1
            html.H1(
                id="title_main",
                children="Camp2Code - Gruppe 4",
                style={
                    "textAlign": "center",
                    "marginTop": 20,
                    "marginBottom": 10,
                    "text-decoration": "underline",
                },
            )
        ],
        width=12,
    ),
]

"""Spalte des Parameter-Tunings."""
COL_Tuning = [  # Col Tuning
    dbc.Col(
        [   
            dbc.Row([
                dbc.Col([
                    html.H2(
                    id="titel_Parameter_Tuning",
                    children="Parameter Tuning",
                    style={"textAlign": "left"},
                    ),
                ],width=4),
                dbc.Col([
                    dbc.Button(
                            children="save params",
                            id="btn_save_params",
                            color="dark",
                            n_clicks=0,
                        ),
                ],width=2),
            ]),
            dbc.Switch(id="switch_canny",
                        label=""
                        ),
            dbc.Switch(id="switch_houghes",
                        label=""
                        ),
            html.Div(
                [
                    dbc.Button(
                        "Pre-Processing",
                        id="collapse-button-pre",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        [
                            html.Div(id='output-container-scale-slider'),
                            dcc.Slider(
                            min=1,
                            max=5,
                            step=1,
                            id="slider_scale",
                            value=1,
                            updatemode="drag",
                            ),
                            html.Div(id='output-container-blur-slider'),
                            dcc.Slider(
                            min=1,
                            max=5,
                            step=1,
                            id="slider_blur",
                            value=car_blur,
                            updatemode="drag",
                            ),
                            html.Div(id='output-container-dilation-slider'),
                            dcc.Slider(
                            min=1,
                            max=5,
                            step=1,
                            id="slider_dilation",
                            value=car_dilation,
                            updatemode="drag",
                            ),
                        ],
                        id="collapse-pre",
                        is_open=False,
                        style={"paddingBottom": 10,
                                "paddingTop": 10,
                        },  
                    ),
                ],
                style={"paddingBottom": 10},
            ),
            html.Div(
                [
                    dbc.Button(
                        "Canny Edge Detection",
                        id="collapse-button-canny",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        [
                            html.Div(id='output-container-canny-lower-slider'),
                            dcc.Slider(
                                min=0,
                                max=255,
                                step=5,
                                id="slider_canny_lower",
                                value=car_canny_lower,
                                updatemode="drag",
                            ),
                            html.Div(id='output-container-canny-upper-slider'),
                            dcc.Slider(
                                min=0,
                                max=255,
                                step=5,
                                id="slider_canny_upper",
                                value=car_canny_upper,
                                updatemode="drag",
                            ),
                        ],
                        id="collapse-canny",
                        is_open=False,
                        style={"paddingBottom": 10,
                                "paddingTop": 10,
                        },
                    ),
                ],
                style={"paddingBottom": 10},
            ),
            html.Div(
                [
                    dbc.Button(
                        "Houghes Lines P",
                        id="collapse-button-houghes",
                        color="primary",
                        n_clicks=0,
                    ),
                    dbc.Collapse(
                        [
                            html.Div(id='output-container-houghes_threshold'),
                            dcc.Slider(
                                min=0,
                                max=100,
                                step=2,
                                id="slider_houghes_threshold",
                                value=car_houghes_threshold,
                                updatemode="drag",
                            ),
                            html.Div(id='output-container-houghes_minLineLength'),
                            dcc.Slider(
                                min=0,
                                max=140,
                                step=2,
                                id="slider_houghes_minLineLength",
                                value=car_houghes_minLineLength,
                                updatemode="drag",
                            ),
                            html.Div(id='output-container-houghes_maxLineGap'),
                            dcc.Slider(
                                min=0,
                                max=100,
                                step=2,
                                id="slider_houghes_maxLineGap",
                                value=car_houghes_maxLineGap,
                                updatemode="drag",
                            ),
                        ],
                        id="collapse-houghes",
                        is_open=False,
                        style={"paddingBottom": 10,
                                "paddingTop": 10,
                        },
                    ),
                ],
                style={"paddingBottom": 10},
            ),   
        ],
    )
]

"""Spalte der Log-Files."""
COL_Logfiles = [  # Col Logfiles
    dbc.Row(
        [
            html.H2(  # Überschrift
                id="title_Logfiles",
                children="Logfiles",
            ),
            dcc.Dropdown(  # Dropdown Logfiles
                id="dd_Logfiles",
                placeholder="Bitte Logging-File wählen!",
                options=getLoggerFiles(),
                value="0",
                multi=False,
                style={"color": "black"},
            ),
        ]
    ),
    dbc.Row(
        [
            dbc.Col([kpi_1]),
            dbc.Col([kpi_2]),
            dbc.Col([kpi_3]),
            dbc.Col([kpi_4]),
            dbc.Col([kpi_5]),
        ],
        style={"paddingTop": 10, "paddingBottom": 10},
    ),
]

"""Spalte der Plots."""
COL_Plot = [  # Col Plot
    dbc.Row(
            [
                html.H3(id="titel_LogDetails", children="Plot-Line Auswahl"),
                dcc.Dropdown(  # Dropdown Log-Details
                    id="dd_LogDetails",
                    options=getLogItemsList()[1:],
                    value=getLogItemsList()[1:4],
                    multi=True,
                    style={"color": "black"},
                ),
            ],
            style={"paddingBottom": 10},
        ),
    dbc.Row(
            [
                dcc.Graph(id="plot_Logfile"),
                        html.P(
                            id="Fussnote",
                            children="...hier das Copyright ;)",
                            style={"textAlign": "right"},
                        ),
                        html.Div(id="dummy"),
                        html.Div(id="dummy2"),
                        dcc.Interval(id="interval_10s", interval=10000),
                        dcc.Interval(
                            id="interval_startup",
                            max_intervals=1,
                        ),
            ]
    )
]

"""Spalte der Fahrzeugsteuerung."""
COL_Fahrzeugsteuerung = [  # Col Fahrzeugsteuerung
    dbc.Row(
        [  # Titel
            html.H2(
                id="titel_Fahrzeugsteuerung",
                children="Fahrzeugsteuerung",
                style={
                    "textAlign": "center",
                    "paddingBottom": 10,
                },
            )
        ]
    ),
    dbc.Row(
        [  # Dropdown Fahrprogramm
            dcc.Dropdown(
                id="dd_Fahrprogramm",
                placeholder="Bitte Fahrprogramm wählen:",
                options=FP_LISTE,
                value=0,
                style={"color": "black"},
            )
        ]
    ),
    dbc.Row(
        [  # Buttons
            dbc.Col(
                [
                    dbc.Button(
                        children="START",
                        id="btn_start",
                        color="dark",
                        n_clicks=0,
                    )
                ],
                width=4,
            ),
            dbc.Col(
                [   
                    html.Div(
                        dbc.Button(
                            [dbc.Spinner(size="sm"), " Driving..."],
                            color="dark",
                            disabled=True,
                        ),
                        id="spinner",
                        style={'display':'none'},
                    )
                ],
                width=4,
            ),
            dbc.Col(
                [
                    dbc.Button(
                        children="STOP",
                        id="btn_stop",
                        color="dark",
                        n_clicks=0,
                    )
                ],
                width=4,
            ),
        ],
        style={"paddingTop": 10, "paddingBottom": 10},
        justify="between",
    ),
    dbc.Row(
        [  # Manuelle Steuerung
            CARD_ManuelleSteuerung,
        ]
    ),
]

"""Spalte der Kamera-View."""
COL_Kamera = [  # Col Kamera
    dbc.Row(
            [  # Titel
                html.H2(
                    id="titel_Kamera",
                    children="Kamera",
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

"""App-Layout fuer die Dash-Anwendung."""
app.layout = dbc.Container(
    [
        dbc.Row(
            [  # Row 1
                dbc.Col(
                    COL_Headline,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [  # Row 2
                dbc.Col(
                    COL_Fahrzeugsteuerung,
                ),
                dbc.Col([], width=1),  # Col Space
                dbc.Col(
                    COL_Kamera,
                ),
            ],
            justify="center",
            style={"paddingTop": 20, "paddingBottom": 20},
        ),
        dbc.Row(
            [   # Row 3
                dbc.Col(  # Tuning
                    COL_Tuning,
                ),
            ],
            style={"paddingTop": 20, "paddingBottom": 20},
        ),
        dbc.Row(
            [   # Row 4
                dbc.Col(  # Logfile-Handling
                    COL_Logfiles,
                ),
            ],
            style={"paddingTop": 20, "paddingBottom": 20},
        ),
        dbc.Row(
            [   # Row 5
                dbc.Col(  # Plot
                    COL_Plot,
                ),
            ],
            style={"paddingTop": 20, "paddingBottom": 20},
        ),
    ]
)


@app.callback(
    Output("collapse-pre", "is_open"),
    [Input("collapse-button-pre", "n_clicks")],
    [State("collapse-pre", "is_open")],
)
def toggle_collapse_pre(n, is_open):
    """Steuert die Collapse-Widgets. 
    
    Collapse-Widgets:
        Pre-Processing
        Canny
        Houghes
    """
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-canny", "is_open"),
    [Input("collapse-button-canny", "n_clicks")],
    [State("collapse-canny", "is_open")],
)
def toggle_collapse_canny(n, is_open):
    """Steuert die Collapse-Widgets. 
    
    Collapse-Widgets:
        Pre-Processing
        Canny
        Houghes
    """
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-houghes", "is_open"),
    [Input("collapse-button-houghes", "n_clicks")],
    [State("collapse-houghes", "is_open")],
)
def toggle_collapse_houghes(n, is_open):
    """Steuert die Collapse-Widgets. 
    
    Collapse-Widgets:
        Pre-Processing
        Canny
        Houghes
    """
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("value_joystick", "children"),
    Input("joystick", "angle"),
    Input("joystick", "force"),
    State("sw_manual", "value"),
    State("slider_speed", "value"),
)
def joystick_values(angle, force, switch, max_Speed):
    """Steuerung über Joystick
        berechnet anhand der Joystick-Werte den Lenkeinschlag
        und mit der eingestellten Maximalgeschwindigkeit
        die Fahrgeschwindigkeit.
    Args:
        angle (float): Winkelwert des Joysticks
        force (float): Kraftweg des Joysticks
        switch (bool): Schalter "manuelle Fahrt"
        max_Speed (int): Wert Slider "slider_speed"
    Returns:
        str: gibt die ermittelten Sollwerte zurück
    """
    debug = ""
    if angle != None and force != None:
        if switch:
            power = round(force, 1)
            winkel = 0
            dir = 0
            if force == 0:
                winkel = 0
                dir = 0
                car.drive(0, 0)
                car.steering_angle = 90
            else:
                power = power * max_Speed
                if power > max_Speed:
                    power = max_Speed
                if angle <= 180:
                    dir = 1
                    winkel = round(45 - (angle / 2), 0)
                else:
                    dir = -1
                    winkel = round(((angle - 180) / 2) - 45, 0)
                car.drive(int(power), dir)
                car.steering_angle = winkel+90
                debug = f"Angle: {winkel} speed: {power} dir: {dir}"
        else:
            debug = "Man. mode off"
            car.drive(0, 0)
            car.steering_angle = 90
    else:
        debug = "None-Value"
    return debug


def computeKPI(data):
    """Berechnung der Kenndaten des Log-Files.
    Args:
        data (pandas.DataFrame): Log-Daten als DataFrame
    Returns:
        tuple of str: berechnete Werte
    """
    vmax = data["v"].max()
    vmin = data["v"][1:].min()
    vmean = round(data["v"].mean(), 2)
    duration = round(data["time"].max(), 2)
    route = round(vmean * duration, 2)
    return vmax, vmin, vmean, duration, route


@app.callback(
    Output(component_id="kpi1", component_property="children"),
    Output(component_id="kpi2", component_property="children"),
    Output(component_id="kpi3", component_property="children"),
    Output(component_id="kpi4", component_property="children"),
    Output(component_id="kpi5", component_property="children"),
    Input("dd_Logfiles", "value"),
)
def update_KPI_DD(logFile):
    """Aktualisieren der Kennwerte nach auswahl eines neuen Files.
    Args:
        logFile (str): nur wegen input nötig
    Returns:
        str: setzt die "children" der kpi's
    """
    global df
    time.sleep(0.2)  # damit das File erst geladen werden kann
    try:
        vmax, vmin, vmean, duration, route = computeKPI(df)
        return vmax, vmin, vmean, duration, route
    except:
        return 0, 0, 0, 0, 0


@app.callback(
    Output("plot_Logfile", "figure"),
    Input("dd_Logfiles", "value"),
    Input("dd_LogDetails", "value"),
)
def selectedLog(logFile, logDetails):
    """Auswahl des Logfiles.
    Args:
        logFile (str): Log-File
        logDetails (list): Liste mit Elementen die angezeigt werden sollen
    Returns:
        plotly figure: Graph mit ausgewählten Daten
    """
    global df
    if logFile != "0":
        load_data_to_df(logFile)
        # df = pd.read_json(os.path.join("Logger", logFile))
        # time.sleep(0.1)
        # df.columns = getLogItemsList()
        if logDetails != []:
            fig = px.line(df, x="time", y=logDetails, title=logFile)
        else:
            fig = px.line(df, x="time", y="st_angle", title=logFile)
        return fig
    else:
        return px.line()


@app.callback(
    Output("dd_Logfiles", "options"),
    Input("interval_10s", "n_intervals"),
)
def updateFileList(value):
    """Alle 10 Sekunden den Logger-Ordner auf neue Files prüfen."""
    return getLoggerFiles()


@app.callback(
    Output("spinner", "style"),
    Input("btn_start", "n_clicks"),
    Input("btn_stop", "n_clicks"),
)
def spinner_action(btn_start, btn_stop):
    """Steuert den Spinner anhand der Start und Stop Buttons."""
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    spinner_style = {'display':'none'}
    if "btn_start" in changed_id:
        spinner_style = {'display':'block'}
    if "btn_stop" in changed_id:
        spinner_style = {'display':'none'}

    return spinner_style


@app.callback(
    Output("sw_manual", "value"),
    Input("btn_start", "n_clicks"),
    Input("btn_stop", "n_clicks"),
    Input("btn_save_params", "n_clicks"),
    State("dd_Fahrprogramm", "value"),
    State("slider_speed", "value"),
)
def button_action(btn_start, btn_stop, btn_save_params, fp, speed):
    """Buttons "Start" und "Stop" verarbeiten.
    Returns:
        int: Schalter für manuellen Betrieb auf 0 setzen
    """
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    if "btn_start" in changed_id:
        if fp == 1:
            car.parameter_tuning()
        elif fp == 2:
            car.fp_opencv(speed)
        elif fp == 3:
            car.fp_deepnn(speed)

    if "btn_stop" in changed_id:
        car._active = False
        
    if "btn_save_params" in changed_id:
        car.save_params()

    return 0


@app.callback(
    Output('output-container-scale-slider', 'children'),
    Output('output-container-blur-slider', 'children'),
    Output('output-container-dilation-slider', 'children'),
    Output('output-container-canny-lower-slider', 'children'),
    Output('output-container-canny-upper-slider', 'children'),
    Output('output-container-houghes_threshold', 'children'),
    Output('output-container-houghes_minLineLength', 'children'),
    Output('output-container-houghes_maxLineGap', 'children'),
    Input("slider_scale", "value"),
    Input("slider_blur", "value"),
    Input("slider_dilation", "value"),
    Input("slider_canny_lower", "value"),
    Input("slider_canny_upper", "value"),
    Input("slider_houghes_threshold", "value"),
    Input("slider_houghes_minLineLength", "value"),
    Input("slider_houghes_maxLineGap", "value"),
    Input("interval_startup", "n_intervals"),
)
def slider_action(scale, blur, dilation, canny_lower, canny_upper, houghes_threshold, houghes_minLineLength, houghes_maxLineGap, interval_startup):
    """Anpassung der Werte aus dem Parameter Tuning im Car-Objekt."""
    car._frame_scale = 1/scale
    car._frame_blur = blur
    car._frame_dilation = dilation
    car._canny_lower = canny_lower
    car._canny_upper = canny_upper
    car._houghes_threshold = houghes_threshold
    car._houghes_minLineLength = houghes_minLineLength
    car._houghes_maxLineGap = houghes_maxLineGap

    return 'Frame-Scale: "{}"'.format(scale),\
            'Gaussian-Blur Repitions: "{}"'.format(blur),\
            'Dilation-Kernel-Size: "{}"'.format(dilation),\
            'Canny-Lower: "{}"'.format(canny_lower),\
            'Canny-Upper: "{}"'.format(canny_upper),\
            'Houghes-Threshold: "{}"'.format(houghes_threshold),\
            'Houghes-minLineLength: "{}"'.format(houghes_minLineLength),\
            'Houghes-maxLineGap: "{}"'.format(houghes_maxLineGap)


@app.callback(
    Output('switch_canny', 'label'),
    Output('switch_houghes', 'label'),
    Input('switch_canny', 'value'),
    Input('switch_houghes', 'value'),
)
def switch_action(sw_canny, sw_houghes):
    """Anzeige des Canny und oder Houges Frames zum Original Kamerabild."""

    car._canny_frame = True if sw_canny else False
    car._houghLP_frame = True if sw_houghes else False

    return f'Canny Edge Detection: {sw_canny}',\
            f'Houghes Lines: {sw_houghes}'


if __name__ == "__main__":
    """Main-Programm der Dashboard App"""
    app.run_server(debug=False, host=get_ip_address())