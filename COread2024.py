dataset = ""
name = ""

days = 0
truck_capacity = 0
truck_max_distance = 0

truck_distance_cost = 0
truck_day_cost = 0
truck_cost = 0
technician_distance_cost = 0
technician_day_cost = 0
technician_cost = 0

machines = 0
coordinates_size = 0
requests_size = 0
technician_size = 0

coordinates_list = {}
requests = {}
technicians = {}
machines_set = {}
machines_size = {}

def read_input(filename):
    file = open(filename, 'r')
    read_header(file)
    file.readline()
    read_parameters(file)
    file.readline()
    read_costs(file)
    file.readline()
    read_machines(file)
    file.readline()
    read_coordinates_list(file)
    file.readline()
    read_requests(file)
    file.readline()
    read_technicians(file)

def read_header(file):
    global dataset 
    dataset = file.readline().replace("DATASET = ", '')
    global name
    name = file.readline().replace("NAME = ", '')

def read_parameters(file):
    global days 
    days = int(file.readline().replace("DAYS = ", ''))
    global truck_capacity
    truck_capacity = int(file.readline().replace("TRUCK_CAPACITY = ", ''))
    global truck_max_distance
    truck_max_distance = int(file.readline().replace("TRUCK_MAX_DISTANCE = ", ''))

def read_costs(file):
    global truck_distance_cost 
    truck_distance_cost = int(file.readline().replace("TRUCK_DISTANCE_COST = ", ''))
    global truck_day_cost 
    truck_day_cost = int(file.readline().replace("TRUCK_DAY_COST = ", ''))
    global truck_cost 
    truck_cost = int(file.readline().replace("TRUCK_COST = ", ''))
   
    global technician_distance_cost
    technician_distance_cost = int(file.readline().replace("TECHNICIAN_DISTANCE_COST = ", ''))
    global technician_day_cost
    technician_day_cost = int(file.readline().replace("TECHNICIAN_DAY_COST = ", ''))
    global technician_cost
    technician_cost = int(file.readline().replace("TECHNICIAN_COST = ", ''))
    
def read_machines(file):
    global machines 
    machines = int(file.readline().replace("MACHINES = ", ''))
    read_tool_details(file)

def read_tool_details(file):
    global machines_set
    global machines_size
    
    i = 0
    while i < machines:
        line = file.readline()
        entries = line.split()
        machines_set[i] = {'machine_id':int(entries[0]), "size":int(entries[1]), 'idle_fee':int(entries[2])}       
        machines_size[i] = int(entries[1])
        i+=1
        
def read_coordinates_list(file):
    global coordinates_size
    global coordinates_list 
 
    coordinates_size = int(file.readline().replace("LOCATIONS = ", ''))
    for i in range(int(coordinates_size)):
        coordinates = file.readline().split()
        cust_id = int(coordinates[0])
        x_coord = int(coordinates[1])
        y_coord = int(coordinates[2])

        coordinates_list[cust_id-1] = [x_coord, y_coord]
    
def read_requests(file):
    global requests_size
    global requests
    
    requests_size = int(file.readline().replace("REQUESTS = ", ''))
    
    for i in range(requests_size):
        request = file.readline().split()
        request_id = int(request[0])
        location_id = int(request[1])
        first_day = int(request[2])
        last_day = int(request[3])
        machine_id = int(request[4])
        nr_machines = int(request[5])
    
        requests[i] = {'location_id':location_id, "first_day":first_day, 'last_day':last_day, 
                                'machine_id':machine_id, 'nr_machines':nr_machines}       



def read_technicians(file):
    global technician_size
    global technicians
    
    technician_size = int(file.readline().replace("TECHNICIANS = ", ''))
    
    for i in range(technician_size):
        technician = file.readline().split()
        technician_id = int(technician[0])
        location_id = int(technician[1])
        tech_max_distance = int(technician[2])
        tech_max_install = int(technician[3])
        
        # Extract machine capabilities if available
        if len(technician) >= 5:
            machine_capabilities = [int(val) for val in technician[4:]]
        else:
            machine_capabilities = []
        
        technicians[i] = {'location_id': location_id,'tech_max_distance': tech_max_distance,
            'tech_max_install': tech_max_install,'machine_capabilities': machine_capabilities}
        
read_input("/Users/stijnsmoes/Desktop/UNI ass453/CO 2024/instances 2024/CO_Case2406.txt")






