import math

def calculate_atomic_distance(position1, position2):
    """
    Calculate the Euclidean distance between two 3D atomic positions.
    
    Parameters:
    position1 (tuple or list): Coordinates of the first atom (x1, y1, z1)
    position2 (tuple or list): Coordinates of the second atom (x2, y2, z2)
    
    Returns:
    float: Distance between the two atomic positions
    """
    # Unpack the coordinates
    x1, y1, z1 = position1
    x2, y2, z2 = position2
    
    # Calculate the squared differences
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    
    # Calculate Euclidean distance using square root of sum of squared differences
    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    
    return distance