#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 16:32:00 2024

@author: stelianmunteanu
"""
import COread2024 as read




def WriteResults(file_path, dataset, name, truck_distance, number_truck_days, number_trucks_used, technician_distance, number_technician_days, number_technicians, idle_machine_costs,
                 total_costs, days, route_schedule, tech_schedule):


    with open(file_path, 'w') as results:
        results.writelines([
            f"\nDATASET =  {dataset}", 
            f"NAME = {name}", 
            f"\nTRUCK_DISTANCE = {round(truck_distance)}",   
            f"\nNUMBER_OF_TRUCK_DAYS = {number_truck_days}", 
            f"\nNUMBER_OF_TRUCKS_USED = {number_trucks_used}", 
            f"\nTECHNICIAN_DISTANCE = {technician_distance}", 
            f"\nNUMBER_OF_TECHNICIAN_DAYS = {number_technician_days}", 
            f"\nNUMBER_OF_TECHNICIANS_USED = {number_technicians}", 
            f"\nIDLE_MACHINE_COSTS = {idle_machine_costs}", 
            f"\nTOTAL_COST = {total_costs}\n" 
        ])
        
        for i in range(1, read.days + 1): 
            number_of_trucks = 0
            if route_schedule[i][0]:
                number_of_trucks = len(route_schedule[i])
                
            results.writelines([
            f"\nDAY = {i}",     
            f"\nNUMBER_OF_TRUCKS = {number_of_trucks}"])
            
            for truck_id in range(number_of_trucks):
                results.writelines([
                    f"\n {truck_id + 1} {' '.join(map(str, route_schedule[i][truck_id]))}"])
            
            results.writelines([f"\nNUMBER_OF_TECHNICIANS = {len(tech_schedule[i])}"])
            for route, technician_id in tech_schedule[i].items():
                results.writelines([
                    f"\n {technician_id} {' '.join(map(str, route))}"])
                
            results.writelines(["\n"])  # Empty line
    

