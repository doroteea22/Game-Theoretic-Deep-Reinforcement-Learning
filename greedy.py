import math
#Greedy decision: pick minimum time option.
class GreedyOffloading:
    def __init__(self, rsus, cpu_rsu, cpu_veh, bandwidth_5g):
        self.rsus = rsus
        self.cpu_rsu = cpu_rsu
        self.cpu_veh = cpu_veh
        self.bandwidth_5g = bandwidth_5g
        self.rsu_range = 45.0
    
    def distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def transmission_time(self, data_mb, distance):
        return data_mb / self.bandwidth_5g
    
    def make_decision(self, task, vehicle_pos, prev_location=None): # Returns: (location=local/rsu_id, time, details={exec_time, transmission_time, total_time})
        mi = task['mi']
        input_mb = task['input_size_mb']
        is_final = task.get('is_final', False)
        
        best_location = None
        best_time = float('inf')
        best_details = {}
        
        #Local
        local_time = mi / self.cpu_veh
        
        if local_time < best_time:
            best_time = local_time
            best_location = 'local'
            best_details = {
                'exec_time': local_time,
                'transmission_time': 0,
                'total_time': local_time
            }
        
        #RSU
        for rsu_id, rsu_pos in self.rsus.items():
            dist = self.distance(vehicle_pos, rsu_pos)
            
            if dist > self.rsu_range:
                continue
            
            exec_time = mi / self.cpu_rsu
            transmission_time = 0
            
            # Upload input if data not already at this RSU
            if prev_location != rsu_id:
                transmission_time += self.transmission_time(input_mb, dist)
            
            #Download output if final task
            if is_final:
                output_mb = calculate_output_size(input_mb, mi)
                transmission_time += self.transmission_time(output_mb, dist)
            
            total_time = exec_time + transmission_time
            
            #Choose best offloading option
            if total_time < best_time:
                best_time = total_time
                best_location = rsu_id
                best_details = {
                    'exec_time': exec_time,
                    'transmission_time': transmission_time,
                    'total_time': total_time,
                    'distance': dist
                }
        
        return best_location, best_details


def calculate_output_size(input_mb, mi):
    if mi >= 1500:
        ratio = 0.3
    elif mi >= 800:
        ratio = 0.2
    else:
        ratio = 0.1
    return max(0.5, round(input_mb * ratio, 2))