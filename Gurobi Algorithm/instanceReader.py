from objectClasses import Dataset, Machine, Location, Request, Technician

def ReadInstance(instance_file):
    dataset = None
    machines = {}
    locations = {}
    requests = {}
    technicians = {}

    with open(instance_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                key, *values = line.split()
                if key == 'DATASET':
                    dataset_name = line.split('=')[-1].strip()
                    dataset = Dataset(dataset_name)
                elif key == 'NAME':
                    dataset.name = ' '.join(values[1:])
                elif key == 'DAYS':
                    dataset.days = int(values[-1])
                elif key == 'TRUCK_CAPACITY':
                    dataset.truck_capacity = int(values[-1])
                elif key == 'TRUCK_MAX_DISTANCE':
                    dataset.truck_max_distance = int(values[-1])
                elif key == 'TRUCK_DISTANCE_COST':
                    dataset.truck_distance_cost = int(values[-1])
                elif key == 'TRUCK_DAY_COST':
                    dataset.truck_day_cost = int(values[-1])
                elif key == 'TRUCK_COST':
                    dataset.truck_cost = int(values[-1])
                elif key == 'TECHNICIAN_DISTANCE_COST':
                    dataset.technician_distance_cost = int(values[-1])
                elif key == 'TECHNICIAN_DAY_COST':
                    dataset.technician_day_cost = int(values[-1])
                elif key == 'TECHNICIAN_COST':
                    dataset.technician_cost = int(values[-1])

                elif key == 'MACHINES':
                    num_machines_line = line.strip()
                    num_machines = int(num_machines_line.split('=')[-1].strip().split()[0])
                    for _ in range(num_machines):
                        machine_line = file.readline().strip()
                        if machine_line:
                            machine_values = machine_line.split()
                            if len(machine_values) == 3:
                                machine_id = machine_values[0]
                                size = int(machine_values[1])
                                idle_penalty = int(machine_values[2])
                                machines[machine_id] = Machine(machine_id, size, idle_penalty)
                            else:
                                print("Error: Invalid format in MACHINES section.")
                        else:
                            print("Error: Expected number of machines not found in MACHINES section.")
                elif key == 'LOCATIONS':
                    num_locations_line = line.strip()
                    num_locations = int(num_locations_line.split('=')[-1].strip().split()[0])
                    for _ in range(num_locations):
                        location_line = file.readline().strip()
                        if location_line:
                            location_values = location_line.split()
                            if len(location_values) == 3:
                                location_id = location_values[0]
                                x = int(location_values[1])
                                y = int(location_values[2])
                                locations[location_id] = Location(location_id, x, y)
                            else:
                                print("Error: Invalid format in LOCATIONS section.")
                        else:
                            print("Error: Expected number of locations not found in LOCATIONS section.")
                elif key == 'REQUESTS':
                    num_requests_line = line.strip()
                    num_requests = int(num_requests_line.split('=')[-1].strip())
                    for _ in range(num_requests):
                        request_line = file.readline().strip()
                        if request_line:
                            request_values = request_line.split()
                            if len(request_values) == 6:
                                request_id = int(request_values[0])
                                location_id = request_values[1]
                                start_day = int(request_values[2])
                                end_day = int(request_values[3])
                                machine_id = request_values[4]
                                quantity = int(request_values[5])
                                requests[request_id] = Request(request_id, location_id, start_day, end_day, machine_id, quantity)
                            else:
                                print("Error: Invalid format in REQUESTS section.")
                        else:
                            print("Error: Expected number of requests not found in REQUESTS section.")
                elif key == 'TECHNICIANS':
                    num_technicians_line = line.strip()
                    num_technicians = int(num_technicians_line.split('=')[-1].strip())
                    for _ in range(num_technicians):
                        technician_line = file.readline().strip()
                        if technician_line:
                            technician_values = technician_line.split()
                            if len(technician_values) >= 5:
                                technician_id = int(technician_values[0])
                                location_id = technician_values[1]
                                max_distance_per_day = int(technician_values[2])
                                max_installations_per_day = int(technician_values[3])
                                machine_capabilities = [int(val) for val in technician_values[4:]]
                                technicians[technician_id] = Technician(technician_id, location_id, max_distance_per_day, max_installations_per_day, machine_capabilities)
                            else:
                                print("Error: Invalid format in TECHNICIANS section.")
                        else:
                            print("Error: Expected number of technicians not found in TECHNICIANS section.")

    return dataset, machines, locations, requests, technicians
