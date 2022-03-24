import os
import sys
import time

import andreas_car_0_1 as ab
import weltbeherrschungscode.abehr.Archiv.loggingc2c as log

car = ab.SonicCar()


db_path = f"{sys.path[0]}/andreasdb.sqlite"

log.makedatabase(db_path)
log.add_usm(db_path,car.distance)
log.read_usm(db_path)