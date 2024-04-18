#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 16:32:00 2024

@author: stelianmunteanu
"""

from Optimization import *

#truck variables
total_truck_distance = sum(get_distance(j) for sublist in route_schedule.values() for j in sublist if j)
number_trucks_used = max(len(sublist) for sublist in route_schedule.values())
sum_of_truck_days = sum(1 for sublist in route_schedule.values() for item in sublist if item) 

#technician variables
tech_list = []
tech_list = [tech for value in tech_schedule.values() for tech in value.values()]
total_technicians_used = len(set(tech_list))
total_technician_distance = sum(is_in_max_dist(key, value) for sublist in tech_schedule.values() for key, value in sublist.items())   
sum_of_technician_days = sum(len(sublist) for sublist in tech_schedule.values()) 
total_idle_machine_costs = 0
delays = {}
delays = {key: {"delivery_day": day} for key in requests for day in range(1, days + 1) for route in route_schedule[day] if key in route} 
for key in requests:
    for day in range(1, days + 1):
        for installation in tech_schedule[day]:
            if key in installation:
                delays[key]["installation_day"] = day
for key in delays:
    if key != 9:
        delay_days = delays[key]["installation_day"] - delays[key]["delivery_day"] - 1
        delays_cost = machines_set[requests[key]["machine_id"]]["idle_fee"]
        total_idle_machine_costs = total_idle_machine_costs + delays_cost * delay_days



def WriteResults():
    
    file_path = '/Users/stelianmunteanu/Desktop/univer/Combinatorial Optimization/Case/validator/CO_Case2420sol.txt' # Specify the path and filename

    with open(file_path, 'w') as results:
        results.writelines([
            f"\nDATASET =  {dataset}", 
            f"NAME = {name}", 
            f"\nTRUCK_DISTANCE = {round(total_truck_distance)}",   
            f"\nNUMBER_OF_TRUCK_DAYS = {sum_of_truck_days}", 
            f"\nNUMBER_OF_TRUCKS_USED = {number_trucks_used}", 
            f"\nTECHNICIAN_DISTANCE = {round(total_technician_distance)}", 
            f"\nNUMBER_OF_TECHNICIAN_DAYS = {sum_of_technician_days}", 
            f"\nNUMBER_OF_TECHNICIANS_USED = {total_technicians_used}", 
            f"\nIDLE_MACHINE_COSTS = {total_idle_machine_costs}", 
            f"\nTOTAL_COST = {round(total_costs)}\n" 
        ])
        
        for i in range(1, days + 1): 
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
        
WriteResults()    
 

        
       
        # Print number of technicians used for each day, same storing as trucks
        # Print technician id and route for each day

