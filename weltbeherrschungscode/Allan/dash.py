import sqlite3
import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import loggingc2c as db
import sys
import plotly.graph_objects as go


sys.path.append('/home/pi/Projektphase1/camp2code4car/camp2code-project_phase_1/weltbeherrschungscode/Allan')

df = db.init_dataframe()

app = dash.Dash()   #initialising dash app


def stock_prices():
    # Function for creating line chart showing Google stock prices over time 
    fig = go.Figure([go.Scatter(x = df['timestamp'], y = df['speed'],\
                     line = dict(color = 'firebrick', width = 4), name = 'Google')
                     ])
    fig.update_layout(title = 'Speed over time',
                      xaxis_title = 'time',
                      yaxis_title = 'Speed'
                      )
    return fig  

 
app.layout = html.Div(id = 'parent', children = [
    html.H1(id = 'H1', children = 'Styling using html components', style = {'textAlign':'center',\
                                            'marginTop':40,'marginBottom':40}),

        
        dcc.Graph(id = 'line_plot', figure = stock_prices())    
    ]
)

if __name__ == '__main__': 
    app.run_server()