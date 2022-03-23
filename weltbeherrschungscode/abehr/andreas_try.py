import os
import sys
import time
# from ../../camp2code-project_phase_1/Code/basisklassen import *
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(sys.path[0])), 'camp2code-project_phase_1', 'Code'))
from basisklassen import *
import traceback




# ----------------- init --------------------
bw = Back_Wheels()
fw = Front_Wheels()
usm = Ultrasonic()
irm = Infrared()

fw.turn(90)