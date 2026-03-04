class SimpleVehicle:
    """
    Simple vehicle that moves along a straight road.
    - Have a position (x, y coordinates)
    - Move at a constant speed
    - Generate computing tasks
    """
    
    def __init__(self, id, position_x, speed, position_y=0):
        self.id = id
        self.x = position_x
        self.y = position_y
        self.speed = speed  # meters/second
        
    def move(self, time_delta=1.0):
        self.x += self.speed * time_delta
        
    def get_position(self): # gets current position of the vehicle as (x, y)
        return (self.x, self.y)
    
    def __repr__(self):
        return f"SimpleVehicle(id={self.id}, pos=({self.x:.1f}, {self.y:.1f}), speed={self.speed:.1f})"
