"""
SUMO integration utilities for vehicular edge computing simulation.

This module allows reading configuration from SUMO files so that:
1. POC/training simulations use the same parameters as SUMO
2. After training, you can visualize in SUMO with exact same setup
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Tuple, Optional


class SumoConfigReader:
    """
    Read configuration from SUMO XML files.
    
    Extracts:
    - RSU positions from .add.xml (POI elements)
    - Vehicle speeds from .rou.xml (vType elements)
    - Road geometry from .nod.xml (node elements)
    - Simulation duration from .sumocfg
    """
    
    def __init__(self, sumo_dir: str = "sumo"):
        """
        Initialize SUMO config reader.
        
        Args:
            sumo_dir: Directory containing SUMO XML files (default: "sumo")
        """
        self.sumo_dir = sumo_dir
        
    def _parse_xml(self, filename: str) -> Optional[ET.Element]:
        """Parse XML file and return root element."""
        filepath = os.path.join(self.sumo_dir, filename)
        if not os.path.exists(filepath):
            return None
        try:
            tree = ET.parse(filepath)
            return tree.getroot()
        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}")
            return None
    
    def read_rsu_positions(self, add_file: str = "poc.add.xml") -> Dict[str, Tuple[float, float]]:
        """
        Read RSU positions from SUMO additional file.
        
        Args:
            add_file: Name of .add.xml file
            
        Returns:
            Dictionary mapping RSU IDs to (x, y) positions
        """
        root = self._parse_xml(add_file)
        if root is None:
            return {}
        
        rsu_map = {}
        for poi in root.findall('poi'):
            poi_id = poi.get('id', '')
            if poi_id.startswith('RSU'):
                x = float(poi.get('x', 0))
                y = float(poi.get('y', 0))
                rsu_map[poi_id] = (x, y)
        
        return rsu_map
    
    def read_vehicle_speed(self, rou_file: str = "poc.rou.xml") -> Optional[float]:
        """
        Read vehicle max speed from SUMO route file.
        
        Args:
            rou_file: Name of .rou.xml file
            
        Returns:
            Maximum vehicle speed in m/s, or None if not found
        """
        root = self._parse_xml(rou_file)
        if root is None:
            return None
        
        for vtype in root.findall('vType'):
            max_speed = vtype.get('maxSpeed')
            if max_speed:
                return float(max_speed)
        
        return None
    
    def read_road_bounds(self, nod_file: str = "poc.nod.xml") -> Optional[Tuple[float, float]]:
        """
        Read road start and end positions from SUMO node file.
        
        Args:
            nod_file: Name of .nod.xml file
            
        Returns:
            Tuple of (min_x, max_x) or None if not found
        """
        root = self._parse_xml(nod_file)
        if root is None:
            return None
        
        x_values = []
        for node in root.findall('node'):
            x = node.get('x')
            if x:
                x_values.append(float(x))
        
        if x_values:
            return (min(x_values), max(x_values))
        
        return None
    
    def read_simulation_duration(self, cfg_file: str = "poc.sumocfg") -> Optional[float]:
        """
        Read simulation end time from SUMO config file.
        
        Args:
            cfg_file: Name of .sumocfg file
            
        Returns:
            Simulation duration in seconds, or None if not found
        """
        root = self._parse_xml(cfg_file)
        if root is None:
            return None
        
        time_elem = root.find('time')
        if time_elem is not None:
            end = time_elem.find('end')
            if end is not None:
                return float(end.get('value', 0))
        
        return None
    
    def read_all_config(self) -> Dict:
        """
        Read all configuration from SUMO files.
        
        Returns:
            Dictionary with all configuration parameters
        """
        config = {}
        
        # RSU positions
        rsu_map = self.read_rsu_positions()
        if rsu_map:
            config['rsu_map'] = rsu_map
            config['num_rsus'] = len(rsu_map)
        
        # Vehicle speed
        max_speed = self.read_vehicle_speed()
        if max_speed:
            config['vehicle_max_speed'] = max_speed
        
        # Road bounds
        road_bounds = self.read_road_bounds()
        if road_bounds:
            config['road_min_x'] = road_bounds[0]
            config['road_max_x'] = road_bounds[1]
            config['road_length'] = road_bounds[1] - road_bounds[0]
        
        # Simulation duration
        duration = self.read_simulation_duration()
        if duration:
            config['simulation_duration'] = duration
        
        return config
    
    def print_config(self):
        """Print configuration read from SUMO files."""
        config = self.read_all_config()
        
        print("\n" + "="*60)
        print("SUMO CONFIGURATION")
        print("="*60)
        
        if 'rsu_map' in config:
            print(f"RSUs: {config['num_rsus']}")
            for rsu_id, (x, y) in config['rsu_map'].items():
                print(f"  {rsu_id}: ({x:.1f}, {y:.1f})")
        
        if 'vehicle_max_speed' in config:
            print(f"Vehicle Max Speed: {config['vehicle_max_speed']:.1f} m/s")
        
        if 'road_length' in config:
            print(f"Road: {config['road_min_x']:.1f}m to {config['road_max_x']:.1f}m (length: {config['road_length']:.1f}m)")
        
        if 'simulation_duration' in config:
            print(f"Simulation Duration: {config['simulation_duration']:.0f} seconds")
        
        print("="*60 + "\n")
        
        return config


def write_sumo_config(rsu_map: Dict[str, Tuple[float, float]], 
                      vehicle_max_speed: float = 15.0,
                      road_length: float = 600.0,
                      num_vehicles: int = 3,
                      simulation_duration: float = 150.0,
                      sumo_dir: str = "sumo"):
    """
    Write SUMO configuration files from Python parameters.
    
    This is useful when you want to update SUMO files after changing
    parameters in your training code.
    
    Args:
        rsu_map: Dictionary of RSU positions
        vehicle_max_speed: Maximum vehicle speed in m/s
        road_length: Length of road in meters
        num_vehicles: Number of vehicles to spawn
        simulation_duration: Total simulation time in seconds
        sumo_dir: Directory to write SUMO files
    """
    os.makedirs(sumo_dir, exist_ok=True)
    
    # Generate POI (RSU) definitions
    poi_xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<additional>']
    for rsu_id, (x, y) in rsu_map.items():
        poi_xml_parts.append(
            f'<poi id="{rsu_id}" color="1,0.5,0" layer="1" x="{x:.2f}" '
            f'y="{y:.2f}" type="server_edge" width="20.0" height="10.0"/>'
        )
    poi_xml_parts.append('</additional>')
    
    add_xml = '\n'.join(poi_xml_parts)
    
    # Write additional file
    with open(os.path.join(sumo_dir, "poc.add.xml"), "w", encoding="utf-8") as f:
        f.write(add_xml)
    
    # Update route file with correct speed
    rou_xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<routes>']
    rou_xml_parts.append(
        f'<vType id="masina_conectata" accel="2.6" decel="4.5" '
        f'length="5.0" maxSpeed="{vehicle_max_speed:.2f}"/>'
    )
    rou_xml_parts.append('<route id="ruta_dreapta" edges="drum_principal"/>')
    rou_xml_parts.append('<route id="ruta_stanga" edges="drum_inapoi"/>')
    
    # Generate vehicle definitions
    for i in range(num_vehicles):
        depart_time = i * 4.0
        route = "ruta_dreapta" if i % 2 == 0 else "ruta_stanga"
        colors = ["1,0,0", "0,0,1", "0,1,0", "1,1,0", "1,0,1", "0,1,1"]
        color = colors[i % len(colors)]
        rou_xml_parts.append(
            f'<vehicle id="veh_{i+1}" type="masina_conectata" route="{route}" '
            f'depart="{depart_time:.2f}" color="{color}"/>'
        )
    
    rou_xml_parts.append('</routes>')
    rou_xml = '\n'.join(rou_xml_parts)
    
    with open(os.path.join(sumo_dir, "poc.rou.xml"), "w", encoding="utf-8") as f:
        f.write(rou_xml)
    
    print(f"✓ Updated SUMO configuration in {sumo_dir}/")
    print(f"  - {len(rsu_map)} RSUs")
    print(f"  - {num_vehicles} vehicles")
    print(f"  - Max speed: {vehicle_max_speed} m/s")
    print(f"  - Duration: {simulation_duration} seconds")


# Convenience function to sync configurations
def sync_sumo_config():
    """Read SUMO config and update infrastructure.config to match."""
    from infrastructure.config import SimulationConfig
    
    reader = SumoConfigReader()
    sumo_config = reader.read_all_config()
    
    if not sumo_config:
        print("Warning: Could not read SUMO configuration")
        return
    
    # Update SimulationConfig with SUMO values
    if 'rsu_map' in sumo_config:
        SimulationConfig.RSU_MAP = sumo_config['rsu_map']
    
    if 'vehicle_max_speed' in sumo_config:
        SimulationConfig.VEHICLE_SPEED_MAX = sumo_config['vehicle_max_speed']
        SimulationConfig.VEHICLE_SPEED_AVG = sumo_config['vehicle_max_speed'] * 0.8
    
    if 'road_length' in sumo_config:
        SimulationConfig.ROAD_LENGTH = sumo_config['road_length']
    
    print("✓ Synced infrastructure config with SUMO")
    reader.print_config()


if __name__ == "__main__":
    # Test reading SUMO config
    reader = SumoConfigReader()
    reader.print_config()
