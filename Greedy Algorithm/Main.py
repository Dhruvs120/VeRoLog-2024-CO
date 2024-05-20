#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 17:26:42 2024

@author: stelianmunteanu
"""

import COread2024 as read
import RouteScheduleConnection as rsc


for i in range (1, 10):
    to_read = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case240{i}.txt"  
    to_write = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case240{i}Sol.txt" 
    read.read_input(to_read) 
    rsc.creates_firs_route()
    rsc.creates_firs_install()          
    rsc.finish() 
    rsc.calculates_and_write(to_write)


for i in range (10, 21):
    to_read = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case24{i}.txt"  
    to_write = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case24{i}Sol.txt" 
    read.read_input(to_read) 
    rsc.creates_firs_route()
    rsc.creates_firs_install()          
    rsc.finish() 
    rsc.calculates_and_write(to_write)
