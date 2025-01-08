import os
import requests
import json
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache duration in seconds (1 hour)
CACHE_DURATION = 3600

class PriceService:
    def __init__(self):
        self.api_key = os.getenv('PLASTIC_EXCHANGE_API_KEY')
        self.base_url = "https://api.plasticexchange.com/v1"
        self.last_update = None
        self.cached_prices = None

    @lru_cache(maxsize=1)
    def get_material_price(self, material_type='PLA'):
        """
        Get the current price for the specified material type.
        Uses caching to prevent excessive API calls.
        
        Args:
            material_type (str): Type of material (PLA, ABS, PETG, etc.)
            
        Returns:
            float: Price per kilogram in USD
        """
        try:
            # Check if we need to refresh cache
            current_time = datetime.now()
            if (self.last_update is None or 
                current_time - self.last_update > timedelta(seconds=CACHE_DURATION)):
                
                # If no API key, return default prices
                if not self.api_key:
                    logger.warning("No API key set, using default prices")
                    return self._get_default_price(material_type)
                
                # Make API request
                response = requests.get(
                    f"{self.base_url}/materials/{material_type}/price",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.cached_prices = data
                    self.last_update = current_time
                    return data['price_per_kg']
                else:
                    logger.error(f"API request failed: {response.status_code}")
                    return self._get_default_price(material_type)
                    
            return self.cached_prices['price_per_kg']
            
        except Exception as e:
            logger.error(f"Error fetching material price: {str(e)}")
            return self._get_default_price(material_type)
    
    def _get_default_price(self, material_type):
        """Default prices when API is unavailable"""
        default_prices = {
            'PLA': 25.00,  # USD per kg
            'ABS': 22.00,
            'PETG': 27.00,
            'TPU': 35.00
        }
        return default_prices.get(material_type, 25.00)  # Default to PLA price if type unknown
