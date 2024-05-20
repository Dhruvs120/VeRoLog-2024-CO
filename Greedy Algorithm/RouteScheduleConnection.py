#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 09:50:19 2024

@author: stelianmunteanu
"""


import ReadInput as read
import GreedyRouting as rt
import GreedySchedule as sch
import WriteOutput as write

global brut_route_schedule
global route_schedule

def creates_firs_route():
    global brut_route_schedule
    global route_schedule
    brut_route_schedule = rt.init_route_schedules()
    brut_route_schedule = rt.assign()
    brut_route_schedule = rt.assign_as_late(brut_route_schedule)
    route_schedule = rt.creates_route_schedule(brut_route_schedule)
    route_schedule = rt.formats_route_schedule(route_schedule)


global install_schedule
global tech_schedule
global schedule_combinations
global check_list

def creates_firs_install():
    
    global install_schedule
    global tech_schedule
    global schedule_combinations
    global check_list
    global route_schedule
       
    install_schedule = sch.creates_install_schedule(route_schedule)
    tech_schedule = sch.init_tech_schedule()
    schedule_combinations = sch.creates_combinations(install_schedule)
    check_list, tech_schedule = sch.creates_schedule(schedule_combinations, tech_schedule)

#checks if all the requests have been fullfilled
def checks_all_requests(check_list):
    return all(elem in check_list for elem in list(read.requests.keys())) 

#gets a list of requests that have not been fullfilled yet
def get_unfull_req(check_list):
    unfull_req = [elem for elem in list(read.requests.keys()) if elem not in check_list]
    return unfull_req

#returns the day a certain request is assigned in a schedule
def get_day(req_id, brut_route_schedule):
    day_result = None
    for day, route in brut_route_schedule.items():
        if req_id in route:
            day_result = day
    return day_result

#returns the cheapest day, a request can be re-assigned to
def get_cheapest_day(req_id, brut_route_schedule):
    min_costs = float('inf')
    day = None
    current_day = get_day(req_id, brut_route_schedule)
    for i in range(read.requests[req_id]["first_day"], read.requests[req_id]["last_day"]):
        brut_route_schedule[i].append(req_id)
        route_schedule = rt.creates_route_schedule(brut_route_schedule)
        costs = rt.calculates_routing_costs(route_schedule, False)
        if costs < min_costs:
            day = i
            min_costs = costs
            brut_route_schedule[i].remove(req_id)
    return day

#re-assigns the missing requests if they are present
def finish():    
    global brut_route_schedule
    global route_schedule
    global install_schedule
    global tech_schedule
    global schedule_combinations
    global check_list
    
    unfull_req = get_unfull_req(check_list)
    while not checks_all_requests(check_list):
        for i in unfull_req:

            day = get_day(i, brut_route_schedule)
            cheapest_day = get_cheapest_day(i, brut_route_schedule)
            #brut_route_schedule[day].remove(i)
            brut_route_schedule[cheapest_day].append(i)
            route_schedule = rt.creates_route_schedule(brut_route_schedule)
            route_schedule = rt.formats_route_schedule(route_schedule)
            install_schedule = sch.creates_install_schedule(route_schedule)
            tech_schedule = sch.init_tech_schedule()
            schedule_combinations = sch.creates_combinations(install_schedule)
            check_list, tech_schedule = sch.creates_schedule(schedule_combinations, tech_schedule)
        
            
def calculates_and_write(file_path):
    truck_distance, number_truck_days, number_trucks_used, total_routing_costs = rt.calculates_routing_costs(route_schedule, True)
    technician_distance, number_technician_days, number_technicians, idle_machine_costs, total_installation_costs = sch.calculates_installation_costs(tech_schedule, route_schedule, True)
    total_costs = total_routing_costs + total_installation_costs 
    write.WriteResults(file_path, read.dataset, read.name, truck_distance, number_truck_days, number_trucks_used, technician_distance, number_technician_days, number_technicians, idle_machine_costs,
                     total_costs, read.days, route_schedule, tech_schedule)







    