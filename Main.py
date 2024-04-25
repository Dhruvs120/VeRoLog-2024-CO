#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


@author: stelianmunteanu
"""

import COread2024 as read
import Optimization as opt



for i in range (1, 10):
    to_read = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case240{i}.txt"  
    to_write = f"/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/instances 2024/CO_Case240{i}Sol.txt" 
    read.read_input(to_read) 
    opt.creates_firs_route()
    opt.creates_firs_install()          
    opt.finish() 
    opt.calculates_and_write(to_write)



