# import readdata
# import optimization

def WriteResults():
    # Assume that the input variables are imported from the read file
    # Assume that the solution variables are imported from the optimization file
    filename = "output.txt"

    with open(filename, 'w') as results:
        results.writelines([
            f"DATASET =  {project_name}\n", # project_name is the name of the dataset VeRoLog 2019
            f"NAME = {instance_name}\n", # instance_name is the name of the instance
            f"\nTRUCK_DISTANCE = {total_truck_distance}",   # total_truck_distance is the total distance travelled by all trucks
            f"\nNUMBER_OF_TRUCK_DAYS = {sum_of_truck_days}", # sum_of_truck_days is the total number of times trucks have been used over all days
            f"\nNUMBER_OF_TRUCKS_USED = {total_trucks_used}", # total_trucks_used is the total number of trucks used
            f"\nTECHNICIAN_DISTANCE = {total_technician_distance}" # total_technician_distance is the total distance travelled by all technicians
            f"\nNUMBER_OF_TECHNICIAN_DAYS = {sum_of_technician_days}", # sum_of_technician_days is the total number of times technicians have been used over all days
            f"\nNUMBER_OF_TECHNICIANS_USED = {total_technicians_used}", # total_technicians_used is the total number of technicians used
            f"\nIDLE_MACHINE_COSTS = {total_idle_machine_costs}", # sum of the idles found in column 3 of input
            f"\nTOTAL_COST = {total_cost}\n" 
        ])
        
        for i in range(1, input_days + 1): # Totalroutes[routesperday[{truckdayusage}]]
            results.writelines([
            f"\nDAY = {i}",
            f"\nNUMBER_OF_TRUCKS = {len(trucks_per_day[i].keys())}"])
            
            for truck_id in sorted(trucks_per_day[i].keys()):
                results.writelines([
                    f"\n {truck_id} {trucks_per_day[i][truck_id]}"])
            
            results.writelines([f"\nNUMBER_OF_TECHNICIANS = {len(technicians_per_day[i].keys())}"])
            for technician_id in sorted(technicians_per_day[i].keys()):
                results.writelines([
                    f"\n {technician_id} {technicians_per_day[i][technician_id]}"]) 

        # Print number of technicians used for each day, same storing as trucks
        # Print technician id and route for each day
