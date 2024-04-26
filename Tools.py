import math
import numpy as np

def calculates_distance(coordinates1, coordinates2):
    return math.ceil(np.sqrt(pow(coordinates2[0] -  coordinates1[0],2) + pow(coordinates2[1] -  coordinates1[1],2)))