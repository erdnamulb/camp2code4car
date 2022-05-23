from sqlite3 import connect
import time
import os
import sys
import florian_auto as fa
import loggingc2c as log

#print (os.path.dirname(sys.path[0]))


car = fa.CamCar()

car.testCam()
car.release()


#time.sleep(1)
#car.steering_angle = 90     # Räder gerade stellen
#car.stop()                  # Auto anhalten
#car.usm.stop()              # Ulraschall-Sensor ausschalten  
