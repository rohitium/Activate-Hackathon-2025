import numpy as np
import os

# Standard atomic masses for common biological elements
ATOMIC_MASSES = {
    'H': 1.008,   # Hydrogen
    'C': 12.011,  # Carbon
    'N': 14.007,  # Nitrogen
    'O': 15.999,  # Oxygen
    'P': 30.974,  # Phosphorus
    'S': 32.065,  # Sulfur
}

def calculate_chain_center_of_mass(pdb_file, chain_id):
    """
    Calculate the center of mass for a specific chain in a PDB file.
    
    Parameters:
    pdb_file (str): Path to the PDB file
    chain_id (str): Identifier of the chain to calculate center of mass
    
    Returns:
    tuple: (x, y, z) coordinates of the chain's center of mass
    """
    # Lists to store atom coordinates and masses
    chain_coords = []
    chain_masses = []
    
    # Ensure the file exists before trying to open
    if not os.path.exists(pdb_file):
        raise FileNotFoundError(f"PDB file not found: {pdb_file}")
    
    # Read the PDB file
    with open(pdb_file, 'r') as f:
        for line in f:
            # Parse ATOM records
            if line.startswith('ATOM'):
                # Extract chain identifier (column 21, 0-based index would be 20)
                current_chain = line[21].strip()
                
                # Check if this atom belongs to the desired chain
                if current_chain == chain_id:
                    # Extract element (column 76-78, 0-based index would be 76-78)
                    element = line[76:78].strip()
                    if not element:
                        # If no element specified, try to infer from atom name
                        element = line[12:16].strip()[0]
                    
                    # Get atomic mass
                    mass = ATOMIC_MASSES.get(element.upper(), 12.011)  # Default to carbon mass if unknown
                    
                    # Extract coordinates
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    
                    # Store coordinates and mass
                    chain_coords.append([x, y, z])
                    chain_masses.append(mass)
    
    # Check if any atoms were found for the chain
    if not chain_coords:
        raise ValueError(f"No atoms found for chain {chain_id}")
    
    # Convert to numpy arrays for efficient calculation
    coords_array = np.array(chain_coords)
    masses_array = np.array(chain_masses)
    
    # Calculate center of mass
    total_mass = np.sum(masses_array)
    weighted_coords = coords_array * masses_array[:, np.newaxis]
    center_of_mass = np.sum(weighted_coords, axis=0) / total_mass
    
    return tuple(center_of_mass)