import requests
import json
from typing import Dict, List, Optional

class RealEstateAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_urls = {
            'zillow': 'https://api.bridgedataoutput.com/api/v2',
            'rentals': 'https://api.rentals.com/v1',
            'realtor': 'https://api.realtor.com/v2'
        }
    
    def search_properties(self, location: str, property_type: str = 'residential') -> List[Dict]:
        """Search for properties in a location"""
        if not self.api_key:
            return self._mock_property_data(location)
        
        try:
            url = f"{self.base_urls['zillow']}/listings"
            params = {
                'location': location,
                'property_type': property_type,
                'status': 'active',
                'limit': 50
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return self._parse_property_listings(data)
        except Exception as e:
            print(f"API Error: {e}")
        
        return self._mock_property_data(location)
    
    def get_comparable_sales(self, address: str, radius_miles: float = 1.0) -> List[Dict]:
        """Get comparable sales data"""
        if not self.api_key:
            return self._mock_comparable_sales()
        
        try:
            url = f"{self.base_urls['zillow']}/comps"
            params = {
                'address': address,
                'radius': radius_miles,
                'sold_within_days': 180
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json().get('comparables', [])
        except Exception as e:
            print(f"API Error: {e}")
        
        return self._mock_comparable_sales()
    
    def _parse_property_listings(self, data: Dict) -> List[Dict]:
        """Parse API response into standardized format"""
        listings = []
        for item in data.get('listings', []):
            listings.append({
                'id': item.get('id'),
                'address': item.get('address'),
                'price': item.get('price'),
                'bedrooms': item.get('bedrooms'),
                'bathrooms': item.get('bathrooms'),
                'sqft': item.get('square_feet'),
                'property_type': item.get('property_type'),
                'listing_date': item.get('list_date')
            })
        return listings
    
    def _mock_property_data(self, location: str) -> List[Dict]:
        """Mock property data when API is unavailable"""
        return [
            {
                'id': 'mock_1',
                'address': f'123 Main St, {location}',
                'price': 350000,
                'bedrooms': 3,
                'bathrooms': 2,
                'sqft': 2200,
                'property_type': 'single_family',
                'listing_date': '2024-01-15'
            },
            {
                'id': 'mock_2',
                'address': f'456 Oak Ave, {location}',
                'price': 425000,
                'bedrooms': 4,
                'bathrooms': 2.5,
                'sqft': 2800,
                'property_type': 'single_family',
                'listing_date': '2024-01-20'
            }
        ]
    
    def _mock_comparable_sales(self) -> List[Dict]:
        """Mock comparable sales data"""
        return [
            {
                'address': '789 Similar St',
                'sale_price': 340000,
                'sale_date': '2024-01-10',
                'sqft': 2100,
                'bedrooms': 3,
                'bathrooms': 2
            }
        ]