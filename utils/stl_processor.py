import numpy as np
from stl import mesh
import logging

logger = logging.getLogger(__name__)

def process_stl_file(file_path):
    """
    Process an STL file and generate basic G-code parameters
    
    Args:
        file_path (str): Path to the STL file
        
    Returns:
        dict: G-code parameters including volume, dimensions, and layer info
    """
    try:
        # Load the STL file
        stl_mesh = mesh.Mesh.from_file(file_path)
        
        # Calculate volume
        volume = stl_mesh.get_mass_properties()[0]  # in mm³
        
        # Get dimensions
        minx = maxx = miny = maxy = minz = maxz = None
        for p in stl_mesh.points:
            # p contains (x1, y1, z1, x2, y2, z2, x3, y3, z3) for each triangle
            for i in range(0, 9, 3):
                x = p[i]
                y = p[i+1]
                z = p[i+2]
                
                if minx is None:
                    minx = maxx = x
                    miny = maxy = y
                    minz = maxz = z
                else:
                    minx = min(minx, x)
                    maxx = max(maxx, x)
                    miny = min(miny, y)
                    maxy = max(maxy, y)
                    minz = min(minz, z)
                    maxz = max(maxz, z)
        
        # Calculate dimensions
        dimensions = {
            'x': maxx - minx,
            'y': maxy - miny,
            'z': maxz - minz
        }
        
        # Estimate number of layers (assuming 0.2mm layer height)
        layer_height = 0.2  # mm
        num_layers = int(dimensions['z'] / layer_height)
        
        # Generate basic G-code parameters
        gcode_params = {
            'volume': volume,  # mm³
            'dimensions': dimensions,  # mm
            'num_layers': num_layers,
            'layer_height': layer_height,
            'infill': 0.2  # 20% infill
        }
        
        return gcode_params
        
    except Exception as e:
        logger.error(f"Error processing STL file: {str(e)}")
        raise
