import os
import sys
# from ../../camp2code-project_phase_1/Code/basisklassen import *

project = os.path.abspath(__file__)
origin_path = sys.path[-2]
# print(project)
print(os.path.join(os.path.dirname(origin_path)),"camp2code-project_phase_1/","Code" )