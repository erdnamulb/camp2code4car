import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from auto_code import CamCar 

from datetime import datetime
import numpy as np


car = CamCar()

car.get_frame()