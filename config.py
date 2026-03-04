"""
Configuration and constants for vehicular edge computing simulations

This module provides centralized configuration that can:
1. Use default hardcoded values
2. Load from SUMO configuration files (if available)
3. Be customized programmatically

SUMO Integration:
  If sumo/poc.add.xml exists, RSU positions are loaded from SUMO
  This ensures training and visualization use the same parameters
"""

import os


class SimulationConfig:
    """
    Centralized configuration for POC simulations.
    
    Contains default values for:
    - Computing resources (CPU power)
    - Network parameters (bandwidth, range)
    - RSU infrastructure (locations, coverage)
    - Simulation parameters (time steps, probabilities)
    """
    
    # ========================================================================
    # COMPUTING RESOURCES
    # ========================================================================
    
    # CPU power in Million Instructions per second (MI/s)
    CPU_VEHICLE = 1000      # Vehicle onboard computer (smartphone-level)
    CPU_RSU = 15000         # Roadside unit (15x more powerful than vehicle)
    
    # Computation scaling
    CPU_VEHICLE_LOW = 500   # Low-end vehicle
    CPU_VEHICLE_HIGH = 2000 # High-end vehicle
    CPU_RSU_LOW = 10000     # Budget RSU
    CPU_RSU_HIGH = 30000    # High-performance RSU
    
    # ========================================================================
    # NETWORK PARAMETERS
    # ========================================================================
    
    # Network bandwidth in MB/s
    NETWORK_SPEED_5G = 100      # 5G network (800 Mbps)
    NETWORK_SPEED_4G = 12.5     # 4G LTE (100 Mbps)
    NETWORK_SPEED_WIFI = 50     # WiFi 6 (400 Mbps)
    
    # Default network speed
    NETWORK_SPEED = NETWORK_SPEED_5G
    
    # RSU communication range in meters
    RSU_RANGE = 45.0        # Typical 5G mmWave range
    RSU_RANGE_EXTENDED = 100.0  # Extended range (sub-6 GHz)
    
    # ========================================================================
    # RSU INFRASTRUCTURE
    # ========================================================================
    
    # Default RSU placement (x, y coordinates in meters)
    # Simulates RSUs along a highway/road
    RSU_MAP_DEFAULT = {
        "RSU_1": (150.0, 15.0),
        "RSU_2": (350.0, -15.0)
    }
    
    # Dense urban deployment
    RSU_MAP_DENSE = {
        "RSU_1": (100.0, 10.0),
        "RSU_2": (200.0, -10.0),
        "RSU_3": (300.0, 10.0),
        "RSU_4": (400.0, -10.0)
    }
    
    # Sparse suburban deployment
    RSU_MAP_SPARSE = {
        "RSU_1": (200.0, 0.0),
        "RSU_2": (600.0, 0.0)
    }
    
    # Default RSU map
    RSU_MAP = RSU_MAP_DEFAULT
    
    # ========================================================================
    # SIMULATION PARAMETERS
    # ========================================================================
    
    # Number of vehicles in simulation
    NUM_VEHICLES = 3
    
    # Simulation duration
    NUM_STEPS = 10          # Time steps
    TIME_STEP_DURATION = 1.0  # Seconds per step
    
    # Task generation
    TASK_PROBABILITY = 0.5  # 50% chance per vehicle per step
    TASK_PROBABILITY_HIGH = 0.7  # High traffic scenario
    TASK_PROBABILITY_LOW = 0.3   # Low traffic scenario
    
    # Vehicle movement
    VEHICLE_SPEED_MIN = 10.0    # m/s (36 km/h)
    VEHICLE_SPEED_MAX = 15.0    # m/s (54 km/h)
    VEHICLE_SPEED_AVG = 12.5    # m/s (45 km/h)
    
    # Road parameters
    ROAD_LENGTH = 500.0     # meters
    ROAD_WIDTH = 20.0       # meters
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @classmethod
    def get_standard_config(cls):
        """Get standard configuration as a dictionary."""
        return {
            'cpu_vehicle': cls.CPU_VEHICLE,
            'cpu_rsu': cls.CPU_RSU,
            'network_speed': cls.NETWORK_SPEED,
            'rsu_map': cls.RSU_MAP,
            'rsu_range': cls.RSU_RANGE,
            'num_vehicles': cls.NUM_VEHICLES,
            'num_steps': cls.NUM_STEPS,
            'task_probability': cls.TASK_PROBABILITY
        }
    
    @classmethod
    def get_high_performance_config(cls):
        """Get high-performance configuration."""
        return {
            'cpu_vehicle': cls.CPU_VEHICLE_HIGH,
            'cpu_rsu': cls.CPU_RSU_HIGH,
            'network_speed': cls.NETWORK_SPEED_5G,
            'rsu_map': cls.RSU_MAP_DENSE,
            'rsu_range': cls.RSU_RANGE_EXTENDED,
            'num_vehicles': cls.NUM_VEHICLES,
            'num_steps': cls.NUM_STEPS,
            'task_probability': cls.TASK_PROBABILITY_HIGH
        }
    
    @classmethod
    def get_low_resource_config(cls):
        """Get low-resource configuration for stress testing."""
        return {
            'cpu_vehicle': cls.CPU_VEHICLE_LOW,
            'cpu_rsu': cls.CPU_RSU_LOW,
            'network_speed': cls.NETWORK_SPEED_4G,
            'rsu_map': cls.RSU_MAP_SPARSE,
            'rsu_range': cls.RSU_RANGE,
            'num_vehicles': cls.NUM_VEHICLES * 2,
            'num_steps': cls.NUM_STEPS,
            'task_probability': cls.TASK_PROBABILITY_HIGH
        }
    
    @classmethod
    def print_config(cls, config_dict=None):
        """Print current configuration in readable format."""
        if config_dict is None:
            config_dict = cls.get_standard_config()
        
        print("\n" + "="*60)
        print("SIMULATION CONFIGURATION")
        print("="*60)
        print(f"Vehicle CPU:     {config_dict['cpu_vehicle']} MI/s")
        print(f"RSU CPU:         {config_dict['cpu_rsu']} MI/s")
        print(f"Network Speed:   {config_dict['network_speed']} MB/s")
        print(f"RSU Range:       {config_dict['rsu_range']} meters")
        print(f"Number of RSUs:  {len(config_dict['rsu_map'])}")
        print(f"Number of Vehicles: {config_dict['num_vehicles']}")
        print(f"Time Steps:      {config_dict['num_steps']}")
        print(f"Task Probability: {config_dict['task_probability']*100:.0f}%")
        print("="*60 + "\n")
    
    @classmethod
    def create_rsu_manager(cls, rsu_map=None, cpu_power=None, comm_range=None):
        """
        Create an RSUManager with RSU objects from configuration.
        
        Args:
            rsu_map: Dictionary of RSU positions (default: cls.RSU_MAP)
            cpu_power: CPU power for RSUs (default: cls.CPU_RSU)
            comm_range: Communication range (default: cls.RSU_RANGE)
            
        Returns:
            RSUManager object with configured RSUs
        """
        from .rsu import RSU, RSUManager
        
        if rsu_map is None:
            rsu_map = cls.RSU_MAP
        if cpu_power is None:
            cpu_power = cls.CPU_RSU
        if comm_range is None:
            comm_range = cls.RSU_RANGE
        
        rsus = [
            RSU(rsu_id, pos[0], pos[1], cpu_power=cpu_power, 
                communication_range=comm_range)
            for rsu_id, pos in rsu_map.items()
        ]
        
        return RSUManager(rsus)
    
    @classmethod
    def create_rsu_from_dict(cls, rsu_dict, cpu_power=None, comm_range=None):
        """
        Create a single RSU object from dictionary entry.
        
        Args:
            rsu_dict: Dictionary with 'id' and 'position' keys
            cpu_power: CPU power (default: cls.CPU_RSU)
            comm_range: Communication range (default: cls.RSU_RANGE)
            
        Returns:
            RSU object
        """
        from .rsu import RSU
        
        if cpu_power is None:
            cpu_power = cls.CPU_RSU
        if comm_range is None:
            comm_range = cls.RSU_RANGE
        
        return RSU(
            rsu_dict['id'], 
            rsu_dict['position'][0], 
            rsu_dict['position'][1],
            cpu_power=cpu_power,
            communication_range=comm_range
        )
    
    @classmethod
    def load_from_sumo(cls, sumo_dir: str = "sumo", verbose: bool = True):
        """
        Load configuration from SUMO files.
        
        Updates class attributes with values from SUMO XML files.
        This ensures your training uses the same parameters as SUMO visualization.
        
        Args:
            sumo_dir: Directory containing SUMO files (default: "sumo")
            verbose: Print what was loaded (default: True)
        
        Returns:
            True if successfully loaded, False otherwise
        """
        # Avoid circular import
        from .sumo_integration import SumoConfigReader
        
        reader = SumoConfigReader(sumo_dir)
        sumo_config = reader.read_all_config()
        
        if not sumo_config:
            if verbose:
                print(f"Warning: Could not load SUMO config from {sumo_dir}/")
            return False
        
        # Update class attributes
        if 'rsu_map' in sumo_config:
            cls.RSU_MAP = sumo_config['rsu_map']
            if verbose:
                print(f"✓ Loaded {len(sumo_config['rsu_map'])} RSUs from SUMO")
        
        if 'vehicle_max_speed' in sumo_config:
            cls.VEHICLE_SPEED_MAX = sumo_config['vehicle_max_speed']
            cls.VEHICLE_SPEED_AVG = sumo_config['vehicle_max_speed'] * 0.8
            if verbose:
                print(f"✓ Loaded vehicle max speed: {sumo_config['vehicle_max_speed']} m/s")
        
        if 'road_length' in sumo_config:
            cls.ROAD_LENGTH = sumo_config['road_length']
            if verbose:
                print(f"✓ Loaded road length: {sumo_config['road_length']} m")
        
        if verbose:
            print("✓ Configuration synced with SUMO\n")
        
        return True


# Try to load from SUMO on import (if files exist)
if os.path.exists(os.path.join("sumo", "poc.add.xml")):
    SimulationConfig.load_from_sumo(verbose=False)


# Convenience shortcuts for backward compatibility
CPU_VEHICLE = SimulationConfig.CPU_VEHICLE
CPU_RSU = SimulationConfig.CPU_RSU
NETWORK_SPEED = SimulationConfig.NETWORK_SPEED
RSU_MAP = SimulationConfig.RSU_MAP
RSU_RANGE = SimulationConfig.RSU_RANGE
NUM_VEHICLES = SimulationConfig.NUM_VEHICLES
NUM_STEPS = SimulationConfig.NUM_STEPS
TASK_PROBABILITY = SimulationConfig.TASK_PROBABILITY
