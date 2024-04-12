#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 11:59:57 2024

@author: stijnsmoes
"""

from COread2024 import *
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
from collections import defaultdict


global d_schedule
d_schedule = {}

for day in range(1, days+1):
    d_schedule[day] = []
    
# Assign requests to delivery schedule
for day in range(1, days+1):
    for i in range(requests_size):
        if requests[i]["first_day"] == day:    
            d_schedule[day].append(i)
    
    
    