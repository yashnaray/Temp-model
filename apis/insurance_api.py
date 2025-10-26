import requests
from typing import Dict, List, Optional

class InsuranceAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_urls = {
            'progressive': 'https://api.progressive.com/v1',
            'geico': 'https://api.geico.com/v1',
            'state_farm': 'https://api.statefarm.com/v1'
        }
    
    def get_quote(self, property_info: Dict, coverage_types: List[str]) -> Dict:
        """Get insurance quote for property"""
        if not self.api_key:
            return self._mock_quote(property_info)
        
        try:
            url = f"{self.base_urls['progressive']}/quotes"
            payload = {
                'property': property_info,
                'coverage_types': coverage_types,
                'effective_date': '2024-01-01'
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Insurance API Error: {e}")
        
        return self._mock_quote(property_info)
    
    def get_risk_factors(self, address: str) -> Dict:
        """Get risk factors for property location"""
        if not self.api_key:
            return self._mock_risk_factors()
        
        try:
            url = f"{self.base_urls['progressive']}/risk-assessment"
            params = {'address': address}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Risk API Error: {e}")
        
        return self._mock_risk_factors()
    
    def get_coverage_recommendations(self, property_value: int, risk_score: float) -> Dict:
        """Get coverage recommendations based on property and risk"""
        base_coverage = property_value * 0.8  # 80% coverage typical
        
        if risk_score > 0.7:
            recommended_deductible = min(2500, property_value * 0.01)
            additional_coverage = ['flood', 'earthquake', 'umbrella']
        elif risk_score > 0.4:
            recommended_deductible = min(5000, property_value * 0.015)
            additional_coverage = ['flood']
        else:
            recommended_deductible = min(10000, property_value * 0.02)
            additional_coverage = []
        
        return {
            'dwelling_coverage': base_coverage,
            'recommended_deductible': recommended_deductible,
            'additional_coverage': additional_coverage,
            'estimated_premium': self._calculate_premium(base_coverage, risk_score)
        }
    
    def _calculate_premium(self, coverage_amount: float, risk_score: float) -> float:
        """Calculate estimated premium"""
        base_rate = coverage_amount * 0.003  # 0.3% base rate
        risk_multiplier = 1 + risk_score
        return base_rate * risk_multiplier
    
    def _mock_quote(self, property_info: Dict) -> Dict:
        """Mock insurance quote"""
        property_value = property_info.get('value', 300000)
        return {
            'quote_id': 'mock_quote_123',
            'annual_premium': property_value * 0.004,
            'dwelling_coverage': property_value * 0.8,
            'personal_property': property_value * 0.5,
            'liability': 300000,
            'deductible': 2500,
            'effective_date': '2024-01-01'
        }
    
    def _mock_risk_factors(self) -> Dict:
        """Mock risk factors"""
        return {
            'flood_risk': 'moderate',
            'fire_risk': 'low',
            'crime_rate': 'low',
            'weather_risk': 'moderate',
            'overall_risk_score': 0.35
        }