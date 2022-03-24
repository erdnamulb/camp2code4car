from sqlite3 import connect
import time
import os
import sys

import florian_auto as fa
import loggingc2c as log

car = fa.SonicCar()

db_w_path = f"{sys.path[0]}/flodb.sqlite"

#log.makedatabase(db_w_path)
#log.add_usm(db_w_path, 39)
"""log.read_all(db_w_path)
log.read_driving(db_w_path)
log.read_steering(db_w_path)
log.read_infrared(db_w_path)"""
car.usm.timeout = 0.06
print(car.usm.timeout)
car.usm.stop()
