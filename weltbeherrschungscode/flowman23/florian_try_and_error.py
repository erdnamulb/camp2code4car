import time
import os
import sys

import florian_auto as fa

# aktuellen Pfad herausfinden:
path_to_myproject = sys.path[0]
# mit dirname zweimal nach oben springen und dann mit join in die unterordner wechseln
# anschliessend mit sys.path.append den zu durchsuchenden Systempfad erweitern auf diesen ordner
# dieser wird dann auch nach dem basisklassen.py durchsucht
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(path_to_myproject)), "camp2code-project_phase_1", "Code"))



car = fa.SonicCar()
"""car.drive(20, 1)
time.sleep(1)
car.stop()
car.steering_angle = 135
time.sleep(1)
car.steering_angle = 45
time.sleep(1)
car.steering_angle = 90
car.stop()"""

print(car.distance)


