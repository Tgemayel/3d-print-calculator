import logging
from .price_service import PriceService

logger = logging.getLogger(__name__)

# Constants for calculations
FILAMENT_DIAMETER = 1.75  # mm
FILAMENT_DENSITY = {
    'PLA': 1.24,  # g/cm³
    'ABS': 1.04,
    'PETG': 1.27,
    'TPU': 1.21
}
PRINT_SPEED = 60  # mm/s
TRAVEL_SPEED = 120  # mm/s

class GCodeAnalyzer:
    def __init__(self):
        self.price_service = PriceService()

    def analyze_gcode(self, gcode_params, material_type='PLA'):
        """
        Analyze G-code parameters to estimate print time and material usage

        Args:
            gcode_params (dict): Parameters from STL processing
            material_type (str): Type of material (PLA, ABS, PETG, etc.)

        Returns:
            dict: Estimates including print time and material usage
        """
        try:
            # Calculate material volume (accounting for infill)
            volume_mm3 = gcode_params['volume'] * gcode_params['infill']

            # Get material density based on type
            density = FILAMENT_DENSITY.get(material_type, FILAMENT_DENSITY['PLA'])

            # Convert volume to weight
            # Convert mm³ to cm³ and multiply by density
            material_weight = (volume_mm3 / 1000) * density

            # Get current price per kg
            price_per_kg = self.price_service.get_material_price(material_type)

            # Convert price per kg to price per gram
            price_per_gram = price_per_kg / 1000

            # Estimate print time
            total_distance = (
                gcode_params['dimensions']['x'] * 
                gcode_params['dimensions']['y'] * 
                gcode_params['num_layers']
            )

            # Calculate time in minutes
            print_time = (total_distance / PRINT_SPEED) / 60

            # Add time for travel moves (estimated as 20% of print time)
            print_time *= 1.2

            # Add time for first layer and other operations
            print_time += 5

            # Calculate material cost
            material_cost = material_weight * price_per_gram

            return {
                'print_time': round(print_time, 2),  # minutes
                'material_usage': round(material_weight, 2),  # grams
                'cost': round(material_cost, 2),  # USD
                'material_type': material_type,
                'price_per_kg': round(price_per_kg, 2)  # USD/kg
            }

        except Exception as e:
            logger.error(f"Error analyzing G-code parameters: {str(e)}")
            raise

# Create instance
analyzer = GCodeAnalyzer()

def analyze_gcode(gcode_params, material_type='PLA'):
    """
    Wrapper function for backward compatibility
    """
    return analyzer.analyze_gcode(gcode_params, material_type)