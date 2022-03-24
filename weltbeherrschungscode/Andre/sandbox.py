import sys, os
import loggingc2c as log
'''
db_path = f"{sys.path[0]}/cardata.db"
print(db_path)


lg.makedatabase_singletable(db_path)
print('fertig')
lg.add_data(db_path, 1, 2, 3, 4, 5)
print('geschrieben')
lg.read_data(db_path)
print('lesen fertig')
'''

the_frame = log.init_dataframe()
print(the_frame)

log.add_row_df(the_frame, 3, [5,6,7,8,9], 3, 4, 5)
log.add_row_df(the_frame, 5, [6,6,6,6,6], 15, 5, 5)
log.add_row_df(the_frame, 7, [8,8,8,8,8], 25, 6, 5)
log.add_row_df(the_frame, 11, [10,10,10,10,10], 35, 7, 5)
print(the_frame)

