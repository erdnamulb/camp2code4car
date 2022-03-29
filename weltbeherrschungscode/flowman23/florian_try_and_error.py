from sqlite3 import connect
import time
import os
import sys
import florian_auto as fa
import loggingc2c as log

car = fa.SensorCar()


print(sys.path[0])
path_to_myproject = os.path.abspath(__file__)
print(path_to_myproject)
car.drive(80, -1)
time.sleep(3)

car.steering_angle = 90     # Räder gerade stellen
car.stop()                  # Auto anhalten
car.usm.stop()              # Ulraschall-Sensor ausschalten  
