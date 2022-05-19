import os.path
import json
import uuid
import dash
from dash import html, dcc
from dash.dependencies import Output, Input, State
from dash import callback_context
from dash_extensions import Keyboard
from flask import Flask, Response, request
from basisklassen_cam import Camera
from basecar import BaseCar


car = BaseCar()
take_image = False


def generate_camera_image(camera_class):
    """Generator for the images from the camera for the live view in dash

    Args:
        camera_class (object): Object of the class Camera

    Yields:
        bytes: Bytes string with the image information
    """
    image_id = 0
    run_id = str(uuid.uuid4())[:8]
    if not os.path.exists(os.path.join(os.getcwd(), "images")):
        os.makedirs(os.path.join(os.getcwd(), "images"))
    while True:
        frame = camera_class.get_frame()
        jepg = camera_class.get_jpeg(frame)

        if car.speed > 0 and take_image:
            take_an_image(camera_class, image_id, run_id, frame)
            image_id = image_id + 1

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jepg + b'\r\n\r\n')


def take_an_image(camera_class, image_id, run_id, frame):
    """Save an image from the camera

    Args:
        camera_class: Object of the class Camera
        image_id: Integer with the image id
        run_id: String with the run id
        frame: Frame from the camera
    """
    camera_class.save_frame(
        "images/", f"{run_id}_{image_id}_{int(car.steering_angle):03d}.jpeg", frame)


server = Flask(__name__)
app = dash.Dash(__name__, server=server)


def shutdown_server():
    """Will shut down the server when the function is called

    Raises:
        RuntimeError: If the server runtime is not corret
    """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@server.route('/video_feed')
def video_feed():
    """Will return the video feed from the camera

    Returns:
        Response: Response object with the video feed
    """
    return Response(generate_camera_image(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.layout = html.Div(children=[
    html.H1("Remotesteuerung des Auto mit WSAD"),
    html.H2("Einstellungen"),
    html.Div(
        [Keyboard(id="keyboard_down"), html.Div(id="output_down")],
    ),
    html.Div(
        [Keyboard(id="keyboard_up"), html.Div(id="output_up")]
    ),
    html.Div([
        html.Button('Speed = 20', id='btn-nclicks-1', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
        html.Button('Speed = 30', id='btn-nclicks-2', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
        html.Button('Speed = 40', id='btn-nclicks-3', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
        html.Div(id='container-button-timestamp')
    ]),
    html.Div([
        html.Button('Take Images', id='take-images-button', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
        html.Button('Rücklenken deaktivieren', id='angle-button-press', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
        html.Button('STOP SERVER', id='stop-button-press', n_clicks=0, style={
                    'font-size': '12px', 'width': '140px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
    ]),
    html.H2('Sensitivität des Lenkwinkels'),
    html.Div([
        dcc.Slider(1, 45, 1,
                   value=10,
                   marks=None,
                   tooltip={"placement": "bottom", "always_visible": False},
                   id='my-slider'
                   ),
        html.Div(id='slider-output-container')
    ], style={
        'font-size': '12px', 'width': '700px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height': '37px', 'verticalAlign': 'top'}),
    dcc.Store(id='intermediate-value-speed'),
    dcc.Store(id='intermediate-value-return-angle'),
    html.Div([
        html.H2("Kamera Feed"),
        html.Img(src="/video_feed")
    ])
]
)


@app.callback(
    Output("output_down", "children"),
    [Input("keyboard_down", "n_keydowns"),
     Input('intermediate-value-speed', 'data'),
     Input('my-slider', 'value')],
    [State("keyboard_down", "keydown"),
     ])
def keydown(n_keydowns, chosen_speed, slider_value, event_keydown):
    """Will return the keydown event from the keyboard

    Args:
        n_keydowns (int): Number of keydowns
        chosen_speed (int): Chosen speed
        event_keydown (str): Keydown event

    Returns:
        str: String with the keydown event
    """
    print(event_keydown, n_keydowns)
    if event_keydown is None:
        return "No event_keydown"
    elif event_keydown["key"] == "w":
        car.drive(speed=chosen_speed)
        return "w-down"
    elif event_keydown["key"] == "a":
        car.steering_angle = car.steering_angle - slider_value
        return "a-down"
    elif event_keydown["key"] == "s":
        car.drive(speed=chosen_speed, direction=-1)
        return "s-down"
    elif event_keydown["key"] == "d":
        car.steering_angle = car.steering_angle + slider_value
        return "d-down"
    return json.dumps(event_keydown)


@app.callback(
    Output("output_up", "children"),
    [Input("keyboard_down", "n_keyups"),
     Input('intermediate-value-return-angle', 'data')],
    [State("keyboard_down", "keyup")])
def keyup(n_keydowns, intermediate_value_return_angle, event_release_key):
    """Will return the keyup event from the keyboard

    Args:
        n_keydowns (int): Number of keydowns
        event_release_key (str): Keyup event

    Returns:
        str: String with the keyup event
    """
    print(event_release_key)
    if event_release_key is None:
        return "No event_release_key"
    elif event_release_key["key"] == "w":
        car.drive(speed=0)
        return "w-up"
    elif event_release_key["key"] == "s":
        car.drive(speed=0, direction=-1)
        return "s-up"
    if intermediate_value_return_angle:
        if event_release_key["key"] == "a":
            car.steering_angle = intermediate_value_return_angle
            return "a-up"
        elif event_release_key["key"] == "d":
            car.steering_angle = intermediate_value_return_angle
            return "d-up"
    return json.dumps(event_release_key)


@app.callback(
    [Output('container-button-timestamp', 'children'),
     Output('intermediate-value-speed', 'data')],
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks'),
)
def displayClick(btn1, btn2, btn3):
    """Will return the speed of the car that is chosen by pressing the buttons

    Args:
        btn1 (int): Number of clicks on the first button
        btn2 (int): Number of clicks on the second button
        btn3 (int): Number of clicks on the third button

    Returns:
        html.Div: Div with the speed of the car as a string
        int: Speed of the car
    """
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        chosen_speed = 20
        msg = 'Gewählte Geschwindigkeit ist 20'
    elif 'btn-nclicks-2' in changed_id:
        chosen_speed = 30
        msg = 'Gewählte Geschwindigkeit ist 30'
    elif 'btn-nclicks-3' in changed_id:
        chosen_speed = 40
        msg = 'Gewählte Geschwindigkeit ist 40'
    else:
        chosen_speed = 30
        msg = 'Gewählte Geschwindigkeit ist 30'
    return [html.Div(msg), chosen_speed]


@app.callback(Output('stop-button-press', 'children'), Input("stop-button-press", "n_clicks"))
def shutdown(n_clicks):
    """Will shutdown the server

    Args:
        n_clicks (int): Number of clicks on the button stop-button-press

    Returns:
        str: String with the shutdown message
    """
    click_amount = 3
    if n_clicks >= click_amount:
        shutdown_server()
        print("shutting down")
        return html.Div("Server shutting down")
    msg = f"Press {click_amount-n_clicks} times for server shutdown"
    return html.Div(msg)


@app.callback(Output('take-images-button', 'children'), Input("take-images-button", "n_clicks"))
def trigger_image_button(n_clicks):
    """Will change take_image to True or False depending on the click of the button

    Args:
        n_clicks (int): Number of clicks on the button take-images-button

    Returns:
        str: String with the message that tells if image taking is active or not
    """
    global take_image
    if n_clicks % 2 == 0:
        take_image = False
        return html.Div("Press to take images")
    else:
        take_image = True
        return html.Div("Taking images")


@app.callback([Output('angle-button-press', 'children'),
               Output('intermediate-value-return-angle', 'data')],
              Input("angle-button-press", "n_clicks"))
def trigger_image_button(n_clicks):
    """Will change intermediate-value-return-angle to True or False depending on the click of the button

    Args:
        n_clicks (int): Number of clicks on the button angle-button-press

    Returns:
        str: String with the message that tells if image taking is active or not
    """
    if n_clicks % 2 == 0:
        intermediate_value_return_angle = 90
        return html.Div("Rücklenken deaktivieren"), intermediate_value_return_angle
    else:
        intermediate_value_return_angle = False
        return html.Div("Rücklenken aktivieren"), intermediate_value_return_angle


@app.callback(
    Output('slider-output-container', 'children'),
    Input('my-slider', 'value'))
def update_output(value):
    return 'Die gewählte Sensitivität für das Lenken ist: "{}"'.format(value)


if __name__ == '__main__':
    print("RUNNING")
    try:
        car.shake_front_wheels(3)
    except:
        print('Auto nicht bereit! Womöglich eine fehlende Konfig-Parameter')

    app.run_server(host="0.0.0.0", port=8050, debug=True)
