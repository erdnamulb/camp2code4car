import sys, os
import loggingc2c as lg

db_path = f"{sys.path[0]}/cardata.db"
print(db_path)


lg.makedatabase_singletable(db_path)
print('fertig')
lg.add_data(db_path, 1, 2, 3, 4, 5)
print('geschrieben')
lg.read_data(db_path)
print('lesen fertig')

