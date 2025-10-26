import requests
import time
from typing import Dict, List, Optional, Tuple

class FreeMapsAPI:
    def __init__(self):
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
        """Find nearby places using Overpass API (FREE)"""
        try:
            # Convert radius to degrees (approximate)
            radius_deg = radius / 111000  # 1 degree ≈ 111km
            
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
                
                for element in data.get('elements', [])[:10]:  # Limit to 10 results
                    if 'tags' in element:
                        name = element['tags'].get('name', 'Unknown')
                        element_lat = element.get('lat') or element.get('center', {}).get('lat')
                        element_lng = element.get('lon') or element.get('center', {}).get('lon')
                        
                        if element_lat and element_lng:
                            distance = self._calculate_distance(lat, lng, element_lat, element_lng)
                            places.append({
                                'name': name,
                                'lat': element_lat,
                                'lng': element_lng,
                                'distance': distance,
                                'type': place_type
                            })
                
                return sorted(places, key=lambda x: x['distance'])
        except Exception as e:
            print(f"Places search error: {e}")
        
        return []
    
    def get_property_info(self, lat: float, lng: float) -> Dict:
        """Get property information from OpenStreetMap"""
        try:
            radius_deg = 0.001  # Small radius for property-specific search
            
            query = f"""
            [out:json][timeout:25];
            (
              way["building"]({lat-radius_deg},{lng-radius_deg},{lat+radius_deg},{lng+radius_deg});
              relation["building"]({lat-radius_deg},{lng-radius_deg},{lat+radius_deg},{lng+radius_deg});
            );
            out geom meta;
            """
            
            response = requests.post(self.overpass_url, data=query)
            time.sleep(1)
            
            if response.status_code == 200:
                data = response.json()
                buildings = []
                
                for element in data.get('elements', []):
                    if 'tags' in element:
                        tags = element['tags']
                        buildings.append({
                            'building_type': tags.get('building', 'yes'),
                            'name': tags.get('name'),
                            'address': self._extract_address_from_tags(tags),
                            'levels': tags.get('building:levels'),
                            'year': tags.get('start_date') or tags.get('construction_date')
                        })
                
                return {'buildings': buildings}
        except Exception as e:
            print(f"Property info error: {e}")
        
        return {'buildings': []}
    
    def _parse_osm_address(self, address: Dict) -> Dict:
        """Parse OpenStreetMap address components"""
        return {
            'house_number': address.get('house_number'),
            'street': address.get('road'),
            'city': address.get('city') or address.get('town') or address.get('village'),
            'state': address.get('state'),
            'postcode': address.get('postcode'),
            'country': address.get('country')
        }
    
    def _extract_address_from_tags(self, tags: Dict) -> str:
        """Extract address from OSM tags"""
        parts = []
        if tags.get('addr:housenumber'):
            parts.append(tags['addr:housenumber'])
        if tags.get('addr:street'):
            parts.append(tags['addr:street'])
        if tags.get('addr:city'):
            parts.append(tags['addr:city'])
        return ' '.join(parts) if parts else None
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in kilometers"""
        import math
        
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

# Example usage
if __name__ == "__main__":
    api = FreeMapsAPI()
    
    # Test geocoding
    result = api.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    if result:
        print(f"Coordinates: {result['lat']}, {result['lng']}")
        
        # Test nearby places
        places = api.get_nearby_places(result['lat'], result['lng'], 'restaurant')
        print(f"Found {len(places)} nearby restaurants")