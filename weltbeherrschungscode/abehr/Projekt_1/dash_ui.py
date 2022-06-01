import sys, os
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import SensorCar 
from andreas_car_0_2 import main

from dash import Dash, html, Input, Output, callback_context

app = Dash(__name__)

app.layout = html.Div([
    html.Button('Prog 0', id='btn-nclicks-0', n_clicks=0),
    html.Button('Prog 1', id='btn-nclicks-1', n_clicks=0),
    html.Button('Prog 2', id='btn-nclicks-2', n_clicks=0),    
    html.Button('Prog 3', id='btn-nclicks-3', n_clicks=0),
    html.Button('Prog 4', id='btn-nclicks-4', n_clicks=0),
    html.Button('Prog 5', id='btn-nclicks-5', n_clicks=0),
    html.Button('Prog 6', id='btn-nclicks-6', n_clicks=0),
    html.Button('Prog 7', id='btn-nclicks-7', n_clicks=0),
    html.Div(id='container-button-timestamp')
])

@app.callback(
    Output('container-button-timestamp', 'children'),
    Input('btn-nclicks-0', 'n_clicks'),
    Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('btn-nclicks-3', 'n_clicks'),
    Input('btn-nclicks-4', 'n_clicks'),
    Input('btn-nclicks-5', 'n_clicks'),
    Input('btn-nclicks-6', 'n_clicks'),
    Input('btn-nclicks-7', 'n_clicks')
)
def displayClick(btn0,btn1,btn2,btn3, btn4, btn5, btn6, btn7):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    car = SensorCar()
    if 'btn-nclicks-3' in changed_id:
        msg = 'Prog 3 wurde ausgeführt'
        main(3, car)
        #print(car.df)
    elif 'btn-nclicks-4' in changed_id:
        msg = 'Prog 4 wurde ausgeführt'
        main(4, car)
    elif 'btn-nclicks-5' in changed_id:
        msg = 'Prog 5 wurde ausgeführt'
        main(5, car)
    elif 'btn-nclicks-6' in changed_id:
        msg = 'Prog 6 wurde ausgeführt'
        main(6, car)
    elif 'btn-nclicks-0' in changed_id:
        msg = 'Prog 0 wurde ausgeführt'
        main(0, car)
    elif 'btn-nclicks-1' in changed_id:
        msg = 'Prog 1 wurde ausgeführt'
        main(1, car)
    elif 'btn-nclicks-2' in changed_id:
        msg = 'Prog 2 wurde ausgeführt'
        main(2, car)
    elif 'btn-nclicks-7' in changed_id:
        msg = 'Prog 7 wurde ausgeführt'
        main(7, car)
    else:
        msg = 'None of the buttons have been clicked yet'
    return html.Div(msg)

if __name__ == '__main__':
    app.run_server(debug=True)