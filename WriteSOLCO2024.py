
from tools2024 import *
from COread2024 import *
from CO_route2024 import*
import numpy as np

machines_use = []
for ids in range(1, tools+1):
    machines_use.append(int(max_tools_used[ids].X))

def break_dictionaries(dictionaries):
    result = {}
    
    for key, dictionary in dictionaries.items():
        blocks = []
        current_block = []
        
        for item in dictionary:
            if item == ';':
                if current_block:
                    blocks.append(current_block)
                current_block = []
            elif item != ' ':
                current_block.append(str(item))
        
        if current_block:
            blocks.append(current_block)
        
        result[key] = [' '.join(block) for block in blocks]
    
    return result

formatted_visits_trucks = break_dictionaries(visits)
formatted_visits_technicians = break_dictionaries(visits_technicians)



file_path = '/Users/....../CO_Case2405sol.txt' # Specify the path and filename
file = open(file_path, 'w')

# Write data to the file
file.write(f"DATASET = {dataset}")
file.write(f"NAME = {name}\n")
file.write(f":TRUCK_DISTANCE {total distance trucks}\n")
file.write(f"NUMBER_OF_TRUCKS_DAYS = {truck_days}\n")
file.write(f"NUMBER_OF_TRUCKS_USED = {max_truck}\n")
file.write(f":TECHNICIAN_DISTANCE {total distance techs}\n")
file.write(f"NUMBER_OF_TECHNICIAN_DAYS = {tech_days}\n")
file.write(f"NUMBER_OF_TECHNICIAN_USED = {max_tech}\n")
file.write(f"IDLE_MACHINE_COSTS = {machines_costs}\n")
file.write(f"TOTAL_COST = {total_cost}\n")

for day in range(1,days+1):   #scheduling for trucks
    #print(day)
    file.write("\n")
    file.write("DAY = " + str(day)+"\n")
    file.write("NUMBER_OF_TRUCKS = " + str(number_of_trucks[day])+"\n")
    for j in range(1,number_of_trucks[day]+1):
        #print(j)
        file.write(str(j) + " " + formatted_visits_trucks[day][j-1]+"\n")
        

for day in range(1,days+1):  #scheduling for techs
    #print(day)
    file.write("NUMBER_OF_TECHNICIANS = " + str(number_of_technicians[day])+"\n")
    for j in range(1,number_of_technicians[day]+1):
        #print(j)
        file.write(str(j) + " " + formatted_visits_technicians[day][j-1]+"\n")

# Close the file
file.close()