import loggingc2c as lg
lg.makedatabase('cardata.db')
print('fertig')
lg.add_usm('cardata.db',42)
print('geschrieben')
lg.read_usm('cardata.db')
print('lesen fertig')