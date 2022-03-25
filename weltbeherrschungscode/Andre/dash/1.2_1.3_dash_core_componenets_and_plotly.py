import dash
from dash import dcc
from dash import html
import plotly.express as px


app = dash.Dash()
df = px.data.stocks()


def stock_prices(df_name):
    """Function to create a line chart representing Google stock prices over time."""
    fig = px.box(df, y=df[df_name])
    #fig = px.box(df, x=df['date'], y=df[df_name])
    return fig


app.layout = html.Div(
    children=[
        html.H1(id='H1',
                children='HTML Component',
                style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
        html.H1(id='H2',
                children='2nd HTML Component'),
        html.Div(children='Ein ganz normaler Container (div) für Fließende Objekte'),
        dcc.Graph(id='line_plot1', figure=stock_prices('GOOG')),
        dcc.Graph(id='line_plot2', figure=stock_prices('AMZN')),
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)
