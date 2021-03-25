import math
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "Images/test_2.jpg"
abs_file_path = os.path.join(script_dir, rel_path)

nr = int(input('Nr = '))
print(nr -7)

print(str)