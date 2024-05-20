#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 08:48:11 2024

@author: stelianmunteanu
"""

import math
import numpy as np

def calculates_distance(coordinates1, coordinates2):
    distance = math.ceil(np.sqrt((coordinates2[0]-coordinates1[0])**2 + (coordinates2[1]-coordinates1[1])**2))
    return distance