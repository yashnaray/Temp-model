import requests
from typing import Dict, List, Optional

class BuildingCodesAPI:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_urls = {
            'icc': 'https://api.iccsafe.org/v1',
            'municipal': 'https://api.municode.com/v1',
            'permits': 'https://api.buildingpermits.com/v1'
        }
    
    def get_building_codes(self, location: str, code_type: str = 'residential') -> List[Dict]:
        """Get building codes for location and type"""
        if not self.api_key:
            return self._mock_building_codes(code_type)
        
        try:
            url = f"{self.base_urls['icc']}/codes"
            params = {
                'location': location,
                'code_type': code_type,
                'current': True
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json().get('codes', [])
        except Exception as e:
            print(f"Building Codes API Error: {e}")
        
        return self._mock_building_codes(code_type)
    
    def get_permit_requirements(self, work_type: str, location: str) -> Dict:
        """Get permit requirements for specific work type"""
        if not self.api_key:
            return self._mock_permit_requirements(work_type)
        
        try:
            url = f"{self.base_urls['permits']}/requirements"
            params = {
                'work_type': work_type,
                'location': location
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Permits API Error: {e}")
        
        return self._mock_permit_requirements(work_type)
    
    def check_compliance(self, property_details: Dict, location: str) -> Dict:
        """Check property compliance with current codes"""
        if not self.api_key:
            return self._mock_compliance_check()
        
        try:
            url = f"{self.base_urls['icc']}/compliance"
            payload = {
                'property': property_details,
                'location': location
            }
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Compliance API Error: {e}")
        
        return self._mock_compliance_check()
    
    def get_inspection_requirements(self, permit_type: str) -> List[Dict]:
        """Get required inspections for permit type"""
        inspection_map = {
            'electrical': [
                {'stage': 'rough_in', 'description': 'Rough electrical inspection'},
                {'stage': 'final', 'description': 'Final electrical inspection'}
            ],
            'plumbing': [
                {'stage': 'rough_in', 'description': 'Rough plumbing inspection'},
                {'stage': 'final', 'description': 'Final plumbing inspection'}
            ],
            'structural': [
                {'stage': 'foundation', 'description': 'Foundation inspection'},
                {'stage': 'framing', 'description': 'Framing inspection'},
                {'stage': 'final', 'description': 'Final structural inspection'}
            ]
        }
        
        return inspection_map.get(permit_type, [])
    
    def _mock_building_codes(self, code_type: str) -> List[Dict]:
        """Mock building codes data"""
        return [
            {
                'code_id': 'IRC_2021_R302',
                'title': 'Fire-Resistance-Rated Construction',
                'description': 'Requirements for fire-resistant construction between dwelling units',
                'category': 'fire_safety',
                'effective_date': '2021-01-01'
            },
            {
                'code_id': 'IRC_2021_R311',
                'title': 'Means of Egress',
                'description': 'Requirements for exits and emergency egress',
                'category': 'safety',
                'effective_date': '2021-01-01'
            }
        ]
    
    def _mock_permit_requirements(self, work_type: str) -> Dict:
        """Mock permit requirements"""
        requirements = {
            'electrical': {
                'permit_required': True,
                'estimated_cost': 150,
                'processing_time': '5-10 business days',
                'required_documents': ['electrical_plan', 'contractor_license']
            },
            'plumbing': {
                'permit_required': True,
                'estimated_cost': 125,
                'processing_time': '3-7 business days',
                'required_documents': ['plumbing_plan', 'contractor_license']
            },
            'roofing': {
                'permit_required': True,
                'estimated_cost': 200,
                'processing_time': '7-14 business days',
                'required_documents': ['structural_plan', 'contractor_license']
            }
        }
        
        return requirements.get(work_type, {
            'permit_required': False,
            'estimated_cost': 0,
            'processing_time': 'N/A',
            'required_documents': []
        })
    
    def _mock_compliance_check(self) -> Dict:
        """Mock compliance check results"""
        return {
            'overall_compliance': 'compliant',
            'issues': [],
            'recommendations': [
                'Consider upgrading smoke detectors to current standards',
                'Verify GFCI outlets in bathrooms and kitchen'
            ],
            'last_updated': '2024-01-01'
        }