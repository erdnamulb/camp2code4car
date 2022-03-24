import sqlite3
from dash import *
import plotly.express as px
import pandas as pd

database = "/home/pi/Projektphase1/camp2code4car/weltbeherrschungscode/Allan/AllanDB.sqlite"

conn = sqlite3.connect(database)

df = pd.read_sql("select * from sqlite_master", con=conn)
print(df)