import dash
from dash import dcc
from dash import html

# Inizialisierung der dash app
app = dash.Dash()

# Erstellen des Layouts
app.layout = html.Div(
    children=[
        html.H1(id='H1',
                children='HTML Component',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.H2(id='H2',
                children='2nd HTML Component'),
        html.Div(children='Ein ganz normaler Container (div) für Fließende Objekte'),
        html.H3(id='H3',
                children='Noch eines...'),
        html.H4(id='H4',
                children='Nummer vier',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.Div(children='Ein ganz normaler Container (div) für Fließende Objekte', 
                style={'textAlign': 'center', 'color':'blue', 'marginTop': 10, 'marginBottom': 20}),
    ]
)

# Starten der dash app
if __name__ == '__main__':
    app.run_server(debug=True)
