import requests
from typing import Dict, Optional, Tuple

class WeatherAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, coordinates: Tuple[float, float]) -> Dict:
        """Get current weather for coordinates"""
        lat, lon = coordinates
        
        if not self.api_key:
            return self._mock_current_weather()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_current_weather(data)
        except Exception as e:
            print(f"Weather API Error: {e}")
        
        return self._mock_current_weather()
    
    def get_weather_history(self, coordinates: Tuple[float, float], days: int = 30) -> Dict:
        """Get historical weather data"""
        if not self.api_key:
            return self._mock_weather_history()
        
        # Note: Historical weather requires different API endpoint
        return self._mock_weather_history()
    
    def get_weather_risks(self, coordinates: Tuple[float, float]) -> Dict:
        """Assess weather-related risks for property"""
        current = self.get_current_weather(coordinates)
        
        risks = {
            'flood_risk': 'low',
            'wind_risk': 'low',
            'hail_risk': 'low',
            'freeze_risk': 'low'
        }
        
        # Assess risks based on current conditions
        if current.get('humidity', 0) > 80:
            risks['flood_risk'] = 'moderate'
        
        if current.get('wind_speed', 0) > 25:
            risks['wind_risk'] = 'high'
        
        if current.get('temperature', 70) < 32:
            risks['freeze_risk'] = 'high'
        
        return {
            'current_conditions': current,
            'risk_assessment': risks,
            'recommendations': self._generate_weather_recommendations(risks)
        }
    
    def _parse_current_weather(self, data: Dict) -> Dict:
        """Parse OpenWeatherMap response"""
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': data['wind'].get('deg', 0),
            'conditions': data['weather'][0]['description'],
            'visibility': data.get('visibility', 10000) / 1000  # Convert to km
        }
    
    def _mock_current_weather(self) -> Dict:
        """Mock current weather data"""
        return {
            'temperature': 72,
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 8,
            'wind_direction': 180,
            'conditions': 'partly cloudy',
            'visibility': 10
        }
    
    def _mock_weather_history(self) -> Dict:
        """Mock historical weather data"""
        return {
            'avg_temperature': 68,
            'avg_humidity': 62,
            'total_precipitation': 2.5,
            'max_wind_speed': 35,
            'extreme_events': [
                {'date': '2024-01-15', 'event': 'heavy_rain', 'intensity': 'moderate'}
            ]
        }
    
    def _generate_weather_recommendations(self, risks: Dict) -> list:
        """Generate recommendations based on weather risks"""
        recommendations = []
        
        if risks['flood_risk'] == 'high':
            recommendations.append('Consider flood insurance and drainage improvements')
        
        if risks['wind_risk'] == 'high':
            recommendations.append('Inspect roof and secure outdoor items')
        
        if risks['freeze_risk'] == 'high':
            recommendations.append('Protect pipes from freezing and check heating system')
        
        if risks['hail_risk'] == 'high':
            recommendations.append('Consider impact-resistant roofing materials')
        
        return recommendations