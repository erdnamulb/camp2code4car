import time
import os
import sys

import florian_auto as fa

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

"""messungen = 50
for i in range(messungen):
    print(car.distance)
    time.sleep(1)"""


distance = car.distance
car.drive(20,1)
while distance > 7 or distance < 0:
    distance = car.distance
    print("Abstand zum Hindernis", distance)
    time.sleep(.1)
car.stop()
print("Auto angehalten")


