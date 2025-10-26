import requests
import json
import time
import math
from typing import Dict, List, Optional, Tuple

class MapsAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key 
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def geocode(self, address: str) -> Optional[Dict]:
        """Geocode an address using OpenStreetMap Nominatim (FREE)"""
        try:
            url = f"{self.nominatim_url}/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {'User-Agent': 'PropertyAnalysisApp/1.0'}
            
            response = requests.get(url, params=params, headers=headers)
            time.sleep(1)  # Rate limit: 1 request per second
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = data[0]
                    return {
                        'lat': float(result['lat']),
                        'lng': float(result['lon']),
                        'formatted_address': result['display_name'],
                        'place_id': result['place_id']
                    }
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """Reverse geocode coordinates using OpenStreetMap Nominatim (FREE)"""
        try:
            url = f"{self.nominatim_url}/reverse"
            params = {
                'lat': lat,
                'lon': lng,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {'User-Agent': 'PropertyAnalysisApp/1.0'}
            
            response = requests.get(url, params=params, headers=headers)
            time.sleep(1)  # Rate limit
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'formatted_address': data['display_name'],
                    'components': self._parse_osm_address(data.get('address', {}))
                }
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
        
        return None
    
    def get_nearby_places(self, lat: float, lng: float, 
                         place_type: str = 'amenity',
                         radius: int = 1000) -> List[Dict]:
        """Find nearby places using OpenStreetMap Overpass API (FREE)"""
        try:
            radius_deg = radius / 111000  # Convert meters to degrees
            
            query = f"""
            [out:json][timeout:25];
            (
              node["{place_type}"]({lat-radius_deg},{lng-radius_deg},{lat+radius_deg},{lng+radius_deg});
              way["{place_type}"]({lat-radius_deg},{lng-radius_deg},{lat+radius_deg},{lng+radius_deg});
            );
            out center meta;
            """
            
            response = requests.post(self.overpass_url, data=query)
            time.sleep(1)  # Rate limit
            
            if response.status_code == 200:
                data = response.json()
                places = []
                
                for element in data.get('elements', [])[:10]:  # Limit results
                    if 'tags' in element:
                        name = element['tags'].get('name', 'Unknown')
                        element_lat = element.get('lat') or element.get('center', {}).get('lat')
                        element_lng = element.get('lon') or element.get('center', {}).get('lon')
                        
                        if element_lat and element_lng:
                            distance = self._calculate_distance(
                                lat, lng, element_lat, element_lng
                            )
                            places.append({
                                'name': name,
                                'address': '',
                                'rating': 0,
                                'distance': distance,
                                'place_id': str(element.get('id', ''))
                            })
                
                return sorted(places, key=lambda x: x['distance'])
        except Exception as e:
            print(f"Places search error: {e}")
        
        return []
    
    def get_property_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a property/place"""
        if not self.api_key:
            return {
                'name': 'Mock Property',
                'address': '123 Mock St',
                'phone': '555-0123',
                'website': 'www.mockproperty.com'
            }
        
        try:
            url = f"{self.base_url}/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,reviews',
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                result = data['result']
                return {
                    'name': result.get('name', ''),
                    'address': result.get('formatted_address', ''),
                    'phone': result.get('formatted_phone_number', ''),
                    'website': result.get('website', ''),
                    'rating': result.get('rating', 0),
                    'reviews': result.get('reviews', [])
                }
        except Exception as e:
            print(f"Place details error: {e}")
        
        return None
    
    def calculate_route(self, origin: str, destination: str) -> Optional[Dict]:
        """Calculate route between two locations"""
        if not self.api_key:
            return {
                'distance': '5.2 km',
                'duration': '12 mins',
                'steps': []
            }
        
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]['legs'][0]
                
                return {
                    'distance': route['distance']['text'],
                    'duration': route['duration']['text'],
                    'steps': [step['html_instructions'] for step in route['steps']]
                }
        except Exception as e:
            print(f"Directions error: {e}")
        
        return None
    
    def _parse_osm_address(self, address: Dict) -> Dict:
        """Parse OpenStreetMap address components"""
        return {
            'street_number': address.get('house_number'),
            'street_name': address.get('road'),
            'city': address.get('city') or address.get('town') or address.get('village'),
            'state': address.get('state'),
            'zip_code': address.get('postcode'),
            'country': address.get('country')
        }
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth's radius in km
        lat1_rad = math.radians(lat1)
        lng1_rad = math.radians(lng1)
        lat2_rad = math.radians(lat2)
        lng2_rad = math.radians(lng2)
        
        dlat = lat2_rad - lat1_rad
        dlng = lng2_rad - lng1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c

# Test the API
if __name__ == "__main__":
    api = MapsAPI()
    
    # Test geocoding
    print("Testing OpenStreetMap geocoding...")
    result = api.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    if result:
        print(f"Coordinates: {result['lat']}, {result['lng']}")
        print(f"Address: {result['formatted_address']}")
        
        # Test nearby places
        print("\nFinding nearby restaurants...")
        places = api.get_nearby_places(result['lat'], result['lng'], 'restaurant')
        print(f"Found {len(places)} nearby restaurants")
        for place in places[:3]:
            print(f"  - {place['name']} ({place['distance']:.2f} km away)")
    else:
        print("Geocoding failed")