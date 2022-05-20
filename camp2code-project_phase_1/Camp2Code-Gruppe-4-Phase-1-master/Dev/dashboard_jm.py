import os
import json
import pandas as pd
import time
import datetime
from dash import dash, dcc, html, callback_context
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_bootstrap_components as dbc
import PiCar_work as PiCar
import socket


df = None
car = PiCar.SensorCar(filter_deepth=2)


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
        "US",
        "IR1",
        "IR2",
        "IR3",
        "IR4",
        "IR5",
    ]


def load_data_to_df(pfad):
    """aktualisiert die Daten im Dataframe

    Args:
        pfad (str): Dateipfad zum File das geladen werden soll
    """
    global df
    df = pd.read_json(os.path.join("Logger", pfad))
    df.columns = getLogItemsList()


FP_LISTE = [  # Liste der auswählbaren Fahrprogramme
    {"label": "FP 1, vor-zurück", "value": 1},
    {"label": "FP 2, im Kreis", "value": 2},
    {"label": "FP 3, US-Testfahrt", "value": 3},
    {"label": "FP 4, Erkundungsfahrt", "value": 4},
    {
        "label": "FP 5, LineFollower",
        "value": 5,
    },
    {
        "label": "FP 6, LineFollower enge Kurve",
        "value": 6,
    },
    {
        "label": "FP 7, LineFollower mit US",
        "value": 7,
    },
    {
        "label": "FP 8, Sensor-Test",
        "value": 8,
    },
    {
        "label": "FP 9, gerade zurücksetzen",
        "value": 9,
    },
]


kpi_1 = dbc.Card([dbc.CardBody([html.H6("vMax"), html.P(id="kpi1")])])
kpi_2 = dbc.Card([dbc.CardBody([html.H6("vMin"), html.P(id="kpi2")])])
kpi_3 = dbc.Card([dbc.CardBody([html.H6("vMean"), html.P(id="kpi3")])])
kpi_4 = dbc.Card([dbc.CardBody([html.H6("time"), html.P(id="kpi4")])])
kpi_5 = dbc.Card([dbc.CardBody([html.H6("vm"), html.P(id="kpi5")])])


row_joystick = dbc.Row(
    [
        dbc.Col(
            [html.P("Manuell on/off"), dbc.Switch(id="sw_manual")],
            width=4,
        ),
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
CARD_ManuelleSteuerung = dbc.Card(
    [
        # dbc.Row(
        #     [  # Titel Manuelle Steuerung
        #         html.H3(
        #             id="label_test",
        #             children="Manuelle Steuerung",
        #             style={
        #                 "textAlign": "left",
        #                 "paddingTop": 20,
        #                 "paddingBottom": 20,
        #             },
        #         )
        #     ]
        # ),
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
                            value=40,
                            updatemode="drag",
                        )
                    ],
                    width=8,
                ),
            ],
            style={"paddingTop": 20, "paddingBottom": 10, "paddinglLeft": 20},
        ),
        row_joystick,
    ]
)

CARD_CALIBRATION = dbc.Card(id="card_calibration", children="comming soon ...")

TAB_FZG = dcc.Tabs(
    id="tab_fzg",
    value="Manuelle Steuerung",
    children=[
        dcc.Tab(
            id="tab_control",
            value="Manuelle Steuerung",
            label="Manuelle Steuerung",
            children=[
                CARD_ManuelleSteuerung,
            ],
            style={"color": "grey"},
        ),
        dcc.Tab(
            id="tab_calibration",
            value="Kalibrierung PiCar",
            label="Kalibrierung PiCar",
            children=[
                CARD_CALIBRATION,
            ],
            style={"color": "grey"},
        ),
    ],
)
COL_Logfiles = [
    dbc.Row(
        [
            html.H2(  # Überschrift
                id="title_Logfiles",
                children="Logfiles",
                style={"textAlign": "center", "paddingBottom": 20},
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
            dbc.Col([kpi_1], width=4),
            dbc.Col([kpi_2], width=4),
            dbc.Col([kpi_3], width=4),
        ],
        style={"paddingTop": 20, "paddingBottom": 20},
    ),
    dbc.Row(
        [
            dbc.Col([kpi_4], width=4),
            dbc.Col([kpi_5], width=4),
        ],
        style={"paddingBottom": 20},
    ),
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
            # dcc.Checklist(
            #     id="cl_Graph_Lines", options=getLogGraphList(),
            # ),
        ],
        style={"paddingBottom": 10},
    ),
]
COL_Fahrzeugsteuerung = [  # Col Fahrzeugsteuerung
    dbc.Row(
        [  # Titel
            html.H2(
                id="titel_Fahrzeugsteuerung",
                children="Fahrzeugsteuerung",
                style={
                    "textAlign": "center",
                    "paddingBottom": 20,
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
                        children="Start Prog",
                        id="btn_start",
                        color="dark",
                        className="me-1",
                        n_clicks=0,
                    )
                ],
                width=4,
            ),
            dbc.Col(
                [],
                width=4,
            ),
            dbc.Col(
                [
                    dbc.Button(
                        children="STOP",
                        id="btn_stop",
                        color="dark",
                        className="me-1",
                        n_clicks=0,
                    )
                ],
                width=4,
            ),
        ],
        style={"paddingTop": 20, "paddingBottom": 20},
        justify="center",
    ),
    dbc.Row(
        [
            TAB_FZG,
        ]
    ),
]


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.SUPERHERO],
    meta_tags=[
        {"name": "viewport"},
        {"content": "width = device,width, initial-scale=1.0"},
    ],
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [  # Row 1
                dbc.Col(
                    [  # Col 1
                        html.H1(
                            id="title_main",
                            children="Camp2Code - Gruppe 4",
                            style={
                                "textAlign": "center",
                                "marginTop": 40,
                                "marginBottom": 40,
                            },
                        )
                    ],
                    width=12,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [  # Row 2
                dbc.Col(  # Logfile-Handling
                    COL_Logfiles,
                    width=5,
                    # style={"backgroundColor": "darkgrey"},
                ),
                dbc.Col([], width=2),  # Col Space
                dbc.Col(
                    COL_Fahrzeugsteuerung,
                    width=5,
                    # style={"backgroundColor": "darkgrey"},
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dcc.Graph(id="plot_Logfile"),
                html.P(
                    id="Fussnote",
                    children="hier das Copyright ;)",
                    style={"textAlign": "right"},
                ),
                html.Div(id="dummy"),
                html.Div(id="dummy2"),
                dcc.Interval(id="intervall_10s", interval=10000),
                dcc.Interval(
                    id="interval_startup",
                    max_intervals=1,
                ),
            ],
            style={"paddingTop": 10, "paddingBottom": 10},
        ),  # Row 3
    ]
)


@app.callback(Output("dummy", "children"), Input("interval_startup", "n_intervals"))
def welcome_scene(value):
    car.welcome()
    return ""


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
        und zusätzlich mit der eingestellten Maximalgeschwindigkeit die Fahrgeschwindigkeit

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
                car.steering_angle = 0
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
                car.steering_angle = winkel
                debug = f"Angle: {winkel} speed: {power} dir: {dir}"
        else:
            debug = "Man. mode off"
            car.drive(0, 0)
            car.steering_angle = 0
    else:
        debug = "None-Value"
    return debug


def computeKPI(data):
    """Berechnung der Kenndaten des Log-Files

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
    """Aktualisieren der Kennwerte nach auswahl eines neuen Files

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


# @app.callback(
#     Output(component_id="label_test", component_property="children"),
#     Input(component_id="slider_speed", component_property="value"),
#     Input(component_id="dd_Fahrprogramm", component_property="value"),
# )
# def write_label(speed, Fahrprogramm):
#     # fp.updateSpeed(speed)

#     return "Fahrprogramm: " + str(Fahrprogramm) + " Speed: " + str(speed)


@app.callback(
    Output("plot_Logfile", "figure"),
    Input("dd_Logfiles", "value"),
    Input("dd_LogDetails", "value"),
)
def selectedLog(logFile, logDetails):
    """Auswahl des Logfiles

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
    Input("intervall_10s", "n_intervals"),
)
def updateFileList(value):
    """alle 10 Sekunden den Logger-Ordner auf neue Files prüfen"""
    return getLoggerFiles()


@app.callback(
    Output("sw_manual", "value"),
    Input("btn_start", "n_clicks"),
    Input("btn_stop", "n_clicks"),
    State("dd_Fahrprogramm", "value"),
    State("slider_speed", "value"),
)
def button_action(btn_start, btn_stop, FP, speed):
    """Buttons "Start" und "Stop" verarbeiten

    Args:
        btn_start (_type_): _description_
        btn_stop (_type_): _description_
        FP (_type_): _description_
        speed (_type_): _description_

    Returns:
        int: Schalter für manuellen Betrieb auf 0 setzen
    """
    changed_id = [p["prop_id"] for p in callback_context.triggered][0]
    if "btn_start" in changed_id:
        car.start_parcours(FP)
    if "btn_stop" in changed_id:
        car.stop_parcours()
        pass
    return 0


if __name__ == "__main__":
    app.run_server(debug=True, host=get_ip_address())
