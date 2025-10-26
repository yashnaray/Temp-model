import os
from typing import Dict, Optional
from .real_estate_api import RealEstateAPI
from .insurance_api import InsuranceAPI
from .building_codes_api import BuildingCodesAPI
from .weather_api import WeatherAPI

class APIManager:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.real_estate_api = RealEstateAPI(self.api_keys.get('real_estate'))
        self.insurance_api = InsuranceAPI(self.api_keys.get('insurance'))
        self.building_codes_api = BuildingCodesAPI(self.api_keys.get('building_codes'))
        self.weather_api = WeatherAPI(self.api_keys.get('weather'))
    
    def _load_api_keys(self) -> Dict[str, Optional[str]]:
        """Load API keys from environment variables"""
        return {
            'real_estate': os.getenv('REAL_ESTATE_API_KEY'),
            'insurance': os.getenv('INSURANCE_API_KEY'),
            'building_codes': os.getenv('BUILDING_CODES_API_KEY'),
            'weather': os.getenv('OPENWEATHERMAP_API_KEY'),
            'google_maps': os.getenv('GOOGLE_MAPS_API_KEY')
        }
    
    def get_property_data(self, location: str) -> Dict:
        """Get comprehensive property data for location"""
        return {
            'listings': self.real_estate_api.search_properties(location),
            'market_data': self._get_market_summary(location)
        }
    
    def get_insurance_analysis(self, property_info: Dict, address: str) -> Dict:
        """Get comprehensive insurance analysis"""
        risk_factors = self.insurance_api.get_risk_factors(address)
        quote = self.insurance_api.get_quote(property_info, ['dwelling', 'personal_property', 'liability'])
        recommendations = self.insurance_api.get_coverage_recommendations(
            property_info.get('value', 300000),
            risk_factors.get('overall_risk_score', 0.3)
        )
        
        return {
            'risk_factors': risk_factors,
            'quote': quote,
            'recommendations': recommendations
        }
    
    def get_building_compliance(self, property_details: Dict, location: str) -> Dict:
        """Get building code compliance information"""
        codes = self.building_codes_api.get_building_codes(location)
        compliance = self.building_codes_api.check_compliance(property_details, location)
        
        return {
            'applicable_codes': codes,
            'compliance_status': compliance
        }
    
    def get_weather_assessment(self, coordinates: tuple) -> Dict:
        """Get weather-related risk assessment"""
        return self.weather_api.get_weather_risks(coordinates)
    
    def get_permit_info(self, work_type: str, location: str) -> Dict:
        """Get permit requirements for specific work"""
        requirements = self.building_codes_api.get_permit_requirements(work_type, location)
        inspections = self.building_codes_api.get_inspection_requirements(work_type)
        
        return {
            'requirements': requirements,
            'inspections': inspections
        }
    
    def _get_market_summary(self, location: str) -> Dict:
        """Get market summary for location"""
        # This would aggregate data from multiple sources
        return {
            'median_price': 365000,
            'price_trend': 'increasing',
            'inventory': 'low',
            'days_on_market': 35
        }
    
    def test_api_connections(self) -> Dict:
        """Test all API connections"""
        results = {}
        
        # Test each API
        try:
            self.real_estate_api.search_properties('Test City')
            results['real_estate'] = 'connected' if self.api_keys.get('real_estate') else 'mock_data'
        except Exception as e:
            results['real_estate'] = f'error: {e}'
        
        try:
            self.insurance_api.get_risk_factors('123 Test St')
            results['insurance'] = 'connected' if self.api_keys.get('insurance') else 'mock_data'
        except Exception as e:
            results['insurance'] = f'error: {e}'
        
        try:
            self.building_codes_api.get_building_codes('Test City')
            results['building_codes'] = 'connected' if self.api_keys.get('building_codes') else 'mock_data'
        except Exception as e:
            results['building_codes'] = f'error: {e}'
        
        try:
            self.weather_api.get_current_weather((40.7128, -74.0060))
            results['weather'] = 'connected' if self.api_keys.get('weather') else 'mock_data'
        except Exception as e:
            results['weather'] = f'error: {e}'
        
        return results