import math
from typing import Tuple, List, Dict

class CoordinateUtils:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def find_nearby_properties(target_coords: Tuple[float, float], 
                             property_list: List[Dict], 
                             radius_km: float = 5.0) -> List[Dict]:
        """Find properties within specified radius"""
        target_lat, target_lon = target_coords
        nearby = []
        
        for prop in property_list:
            if 'coordinates' in prop:
                prop_lat, prop_lon = prop['coordinates']
                distance = CoordinateUtils.haversine_distance(
                    target_lat, target_lon, prop_lat, prop_lon
                )
                
                if distance <= radius_km:
                    prop_copy = prop.copy()
                    prop_copy['distance_km'] = distance
                    nearby.append(prop_copy)
        
        # Sort by distance
        return sorted(nearby, key=lambda x: x['distance_km'])
    
    @staticmethod
    def get_bounding_box(center_coords: Tuple[float, float], 
                        radius_km: float) -> Dict[str, float]:
        """Get bounding box coordinates for a given center and radius"""
        lat, lon = center_coords
        
        # Approximate conversion (1 degree ≈ 111 km)
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
        
        return {
            'north': lat + lat_delta,
            'south': lat - lat_delta,
            'east': lon + lon_delta,
            'west': lon - lon_delta
        }
    
    @staticmethod
    def is_within_bounds(coords: Tuple[float, float], 
                        bounds: Dict[str, float]) -> bool:
        """Check if coordinates are within bounding box"""
        lat, lon = coords
        
        return (bounds['south'] <= lat <= bounds['north'] and 
                bounds['west'] <= lon <= bounds['east'])
    
    @staticmethod
    def geocode_address(address: str) -> Tuple[float, float]:
        """Convert address to coordinates (mock implementation)"""
        # This would integrate with a real geocoding service
        # For now, return mock coordinates
        return (40.7128, -74.0060)  # NYC coordinates as default