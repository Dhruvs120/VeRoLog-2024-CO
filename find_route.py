#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 11:59:57 2024

@author: stijnsmoes
"""

import itertools
from machines2024 import *
from COread2024 import *
import numpy as np
import math

global loc_schedule
loc_schedule = {}

for day in range(1, days+1):
    loc_schedule[day] = []
    
# Assign requests to delivery schedule
for day in range(1, days+1):
    for i in range(len(d_schedule[day])):
        loc_schedule[day].append(requests[d_schedule[day][i]]["location_id"])     
        
global cord_schedule
cord_schedule = {}

for day in range(1, days+1):
    cord_schedule[day] = []
    
# Assign requests to delivery schedule
for day in range(1, days+1):
        for i in range(len(d_schedule[day])):
            cord_schedule[day].append(coordinates_list[loc_schedule[day][i]])       