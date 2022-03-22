import os
import sys

# working directory ermitteln und durchhangeln
absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)
parent_dir = os.path.dirname(file_dir)
parent_dir = os.path.dirname(parent_dir)
new_path = os.path.join(parent_dir, 'camp2code-project_phase_1')   
new_path = os.path.join(new_path, 'Code')   
sys.path.append(new_path)
print(new_path)

from basisklassen import *


