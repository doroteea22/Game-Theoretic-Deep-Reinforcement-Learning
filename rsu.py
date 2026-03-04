"""
Roadside Unit (RSU) classes for edge computing infrastructure
"""

import math


class RSU:
    """
    Roadside Unit - Edge computing server along the road.
    
    Represents a stationary edge computing node that:
    - Has a fixed position (x, y coordinates)
    - Has computing resources (CPU power)
    - Has a communication range
    - Can track load and queued tasks (for future DRL)
    """
    
    def __init__(self, id, position_x, position_y, cpu_power=15000, 
                 communication_range=45.0, max_queue_size=None):
        """
        Initialize an RSU.
        
        Args:
            id: RSU identifier (e.g., "RSU_1")
            position_x: X coordinate (meters)
            position_y: Y coordinate (meters)
            cpu_power: Computing power in MI/s (default: 15000)
            communication_range: Maximum communication distance in meters (default: 45.0)
            max_queue_size: Maximum number of queued tasks (default: None = unlimited)
        """
        self.id = id
        self.x = position_x
        self.y = position_y
        self.cpu_power = cpu_power
        self.range = communication_range
        self.max_queue_size = max_queue_size
        
        # Resource tracking (for future DRL/scheduling)
        self.current_load = 0.0  # Current CPU utilization (0.0 to 1.0)
        self.task_queue = []     # Queued tasks waiting for execution
        self.tasks_processed = 0 # Total tasks processed
        self.total_processing_time = 0.0  # Total time spent processing
        
    def get_position(self):
        """
        Get RSU position.
        
        Returns:
            Tuple of (x, y) coordinates in meters
        """
        return (self.x, self.y)
    
    def distance_to(self, position):
        """
        Calculate distance to a position (typically a vehicle).
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            Distance in meters
        """
        return math.sqrt((self.x - position[0])**2 + (self.y - position[1])**2)
    
    def is_in_range(self, position):
        """
        Check if a position is within communication range.
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            True if within range, False otherwise
        """
        return self.distance_to(position) <= self.range
    
    def can_accept_task(self):
        """
        Check if RSU can accept a new task.
        
        For simple POC: always True
        For future: check queue size, load, etc.
        
        Returns:
            True if can accept task, False otherwise
        """
        if self.max_queue_size is None:
            return True
        return len(self.task_queue) < self.max_queue_size
    
    def add_task(self, task):
        """
        Add a task to the queue.
        
        Args:
            task: Task dictionary
            
        Returns:
            True if added, False if queue full
        """
        if not self.can_accept_task():
            return False
        
        self.task_queue.append(task)
        return True
    
    def process_task(self, task, execution_time):
        """
        Record task processing (for statistics).
        
        Args:
            task: Task that was processed
            execution_time: Time taken to process (seconds)
        """
        self.tasks_processed += 1
        self.total_processing_time += execution_time
    
    def get_load(self):
        """
        Get current CPU load (0.0 to 1.0).
        
        For future implementation with queuing simulation.
        
        Returns:
            Current load as fraction (0.0 = idle, 1.0 = fully loaded)
        """
        return self.current_load
    
    def set_load(self, load):
        """
        Set current CPU load.
        
        Args:
            load: Load fraction (0.0 to 1.0)
        """
        self.current_load = max(0.0, min(1.0, load))
    
    def get_statistics(self):
        """
        Get RSU statistics.
        
        Returns:
            Dictionary with RSU stats
        """
        return {
            'id': self.id,
            'position': (self.x, self.y),
            'cpu_power': self.cpu_power,
            'range': self.range,
            'tasks_processed': self.tasks_processed,
            'total_processing_time': self.total_processing_time,
            'avg_processing_time': (
                self.total_processing_time / self.tasks_processed 
                if self.tasks_processed > 0 else 0.0
            ),
            'current_load': self.current_load,
            'queue_length': len(self.task_queue)
        }
    
    def __repr__(self):
        return (f"RSU(id={self.id}, pos=({self.x:.1f}, {self.y:.1f}), "
                f"cpu={self.cpu_power} MI/s, range={self.range:.1f}m, "
                f"tasks={self.tasks_processed})")


class RSUManager:
    """
    Manages a collection of RSUs.
    
    Provides convenient methods for:
    - Finding nearest RSU
    - Finding RSUs in range
    - Load balancing across RSUs
    """
    
    def __init__(self, rsus=None):
        """
        Initialize RSU manager.
        
        Args:
            rsus: List of RSU objects or dict mapping RSU_ID -> (x, y)
        """
        if rsus is None:
            self.rsus = []
        elif isinstance(rsus, dict):
            # Convert from dict format (backward compatibility)
            self.rsus = [
                RSU(rsu_id, pos[0], pos[1]) 
                for rsu_id, pos in rsus.items()
            ]
        else:
            self.rsus = rsus
    
    def add_rsu(self, rsu):
        """Add an RSU to the manager."""
        self.rsus.append(rsu)
    
    def get_rsu_by_id(self, rsu_id):
        """
        Get RSU by ID.
        
        Args:
            rsu_id: RSU identifier
            
        Returns:
            RSU object or None if not found
        """
        for rsu in self.rsus:
            if rsu.id == rsu_id:
                return rsu
        return None
    
    def find_nearest_rsu(self, position):
        """
        Find nearest RSU to a position.
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            RSU object or None if no RSUs
        """
        if not self.rsus:
            return None
        
        return min(self.rsus, key=lambda rsu: rsu.distance_to(position))
    
    def find_rsus_in_range(self, position):
        """
        Find all RSUs within communication range of a position.
        
        Args:
            position: Tuple of (x, y) coordinates
            
        Returns:
            List of RSU objects in range
        """
        return [rsu for rsu in self.rsus if rsu.is_in_range(position)]
    
    def find_best_rsu(self, position, criteria='nearest'):
        """
        Find best RSU for offloading based on criteria.
        
        Args:
            position: Tuple of (x, y) coordinates
            criteria: Selection criteria:
                - 'nearest': Closest RSU in range
                - 'least_loaded': RSU with lowest load
                - 'most_powerful': RSU with highest CPU power
                - 'shortest_queue': RSU with shortest queue
                
        Returns:
            RSU object or None if none in range
        """
        in_range = self.find_rsus_in_range(position)
        if not in_range:
            return None
        
        if criteria == 'nearest':
            return min(in_range, key=lambda rsu: rsu.distance_to(position))
        elif criteria == 'least_loaded':
            return min(in_range, key=lambda rsu: rsu.get_load())
        elif criteria == 'most_powerful':
            return max(in_range, key=lambda rsu: rsu.cpu_power)
        elif criteria == 'shortest_queue':
            return min(in_range, key=lambda rsu: len(rsu.task_queue))
        else:
            return in_range[0]
    
    def get_all_statistics(self):
        """
        Get statistics for all RSUs.
        
        Returns:
            List of statistics dictionaries
        """
        return [rsu.get_statistics() for rsu in self.rsus]
    
    def print_statistics(self):
        """Print statistics for all RSUs."""
        print("\n" + "="*70)
        print("RSU STATISTICS")
        print("="*70)
        
        for rsu in self.rsus:
            stats = rsu.get_statistics()
            print(f"\n{stats['id']}:")
            print(f"  Position: ({stats['position'][0]:.1f}, {stats['position'][1]:.1f})")
            print(f"  CPU Power: {stats['cpu_power']} MI/s")
            print(f"  Range: {stats['range']:.1f} meters")
            print(f"  Tasks Processed: {stats['tasks_processed']}")
            if stats['tasks_processed'] > 0:
                print(f"  Avg Processing Time: {stats['avg_processing_time']:.3f} seconds")
            print(f"  Current Load: {stats['current_load']*100:.1f}%")
            print(f"  Queue Length: {stats['queue_length']}")
        
        print("="*70 + "\n")
    
    def to_dict(self):
        """
        Convert RSU manager to dictionary format.
        
        Returns:
            Dictionary mapping RSU_ID -> (x, y) for backward compatibility
        """
        return {rsu.id: (rsu.x, rsu.y) for rsu in self.rsus}
    
    def __len__(self):
        return len(self.rsus)
    
    def __iter__(self):
        return iter(self.rsus)
    
    def __repr__(self):
        return f"RSUManager({len(self.rsus)} RSUs)"
