import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class HistoricalAnalyzer:
    def __init__(self):
        self.historical_data_path = "data/historical"
        
    def get_historical_property_data(self, address: str) -> Dict:
        """Get historical property data including sales, assessments, and changes"""
        return {
            'sales_history': [
                {'date': '2020-03-15', 'price': 285000, 'type': 'sale'},
                {'date': '2015-08-22', 'price': 245000, 'type': 'sale'},
                {'date': '2010-11-10', 'price': 195000, 'type': 'sale'}
            ],
            'assessment_history': [
                {'year': 2024, 'assessed_value': 320000, 'tax_amount': 4800},
                {'year': 2023, 'assessed_value': 310000, 'tax_amount': 4650},
                {'year': 2022, 'assessed_value': 295000, 'tax_amount': 4425}
            ],
            'price_trends': {
                '1_year': 3.2,
                '5_year': 15.8,
                '10_year': 64.1
            }
        }
    
    def compare_historical_conditions(self, current_inspection: Dict, historical_inspections: List[Dict]) -> Dict:
        """Compare current property condition with historical inspections"""
        comparison = {
            'condition_trend': 'stable',
            'deterioration_rate': 0.0,
            'improvement_areas': [],
            'declining_areas': [],
            'timeline': []
        }
        
        if not historical_inspections:
            return comparison
        
        current_score = self._get_condition_score(current_inspection)
        historical_scores = [self._get_condition_score(insp) for insp in historical_inspections]
        
        if historical_scores:
            avg_historical = sum(historical_scores) / len(historical_scores)
            change = current_score - avg_historical
            
            if change > 0.5:
                comparison['condition_trend'] = 'improving'
            elif change < -0.5:
                comparison['condition_trend'] = 'declining'
                comparison['deterioration_rate'] = abs(change)
        
        # Compare specific components
        current_components = current_inspection.get('components', {})
        
        for component, current_data in current_components.items():
            historical_component_data = []
            for hist_insp in historical_inspections:
                if component in hist_insp.get('components', {}):
                    historical_component_data.append(hist_insp['components'][component])
            
            if historical_component_data:
                component_trend = self._analyze_component_trend(current_data, historical_component_data)
                if component_trend == 'improving':
                    comparison['improvement_areas'].append(component)
                elif component_trend == 'declining':
                    comparison['declining_areas'].append(component)
        
        return comparison
    
    def get_market_trends(self, location: str, timeframe: str = '5_years') -> Dict:
        """Get historical market trends for location"""
        return {
            'price_history': {
                '2024': 365000,
                '2023': 350000,
                '2022': 335000,
                '2021': 315000,
                '2020': 295000
            },
            'inventory_trends': {
                '2024': 'low',
                '2023': 'normal',
                '2022': 'high'
            },
            'appreciation_rate': 5.2
        }
    
    def analyze_maintenance_timeline(self, inspection_history: List[Dict]) -> Dict:
        """Analyze maintenance patterns over time"""
        timeline = {
            'major_repairs': [],
            'routine_maintenance': [],
            'neglected_areas': [],
            'maintenance_score': 0
        }
        
        if len(inspection_history) < 2:
            return timeline
        
        # Sort by date
        sorted_inspections = sorted(inspection_history, 
                                  key=lambda x: x.get('date', '2024-01-01'))
        
        for i in range(1, len(sorted_inspections)):
            prev_inspection = sorted_inspections[i-1]
            curr_inspection = sorted_inspections[i]
            
            # Check for improvements (indicating maintenance)
            prev_score = self._get_condition_score(prev_inspection)
            curr_score = self._get_condition_score(curr_inspection)
            
            if curr_score > prev_score + 0.5:
                timeline['major_repairs'].append({
                    'date': curr_inspection.get('date'),
                    'improvement': curr_score - prev_score
                })
        
        return timeline
    
    def predict_future_maintenance(self, current_inspection: Dict, historical_data: Dict) -> Dict:
        """Predict future maintenance needs based on historical patterns"""
        predictions = {
            'next_12_months': [],
            'next_5_years': [],
            'estimated_costs': {}
        }
        
        # Analyze current condition and historical trends
        current_condition = current_inspection.get('overall_condition', 'fair')
        
        # Predict based on component age and condition
        components = current_inspection.get('components', {})
        
        for component, data in components.items():
            if component == 'roof':
                if 'condition' in data and isinstance(data['condition'], tuple):
                    condition_score = data['condition'][0]
                    if condition_score < 0:
                        predictions['next_12_months'].append(f'{component} repair needed')
                        predictions['estimated_costs'][component] = 15000
            
            elif component == 'foundation':
                if 'analysis' in data:
                    severity = data['analysis'].get('severity_score', 0)
                    if severity > 2:
                        predictions['next_5_years'].append(f'{component} major work needed')
                        predictions['estimated_costs'][component] = 25000
        
        return predictions
    
    def _get_condition_score(self, inspection: Dict) -> float:
        """Extract numerical condition score from inspection"""
        condition = inspection.get('overall_condition', 'unknown')
        score_map = {
            'excellent': 5.0,
            'good': 4.0,
            'fair': 3.0,
            'poor': 2.0,
            'unknown': 3.0
        }
        return score_map.get(condition, 3.0)
    
    def _analyze_component_trend(self, current_data: Dict, historical_data: List[Dict]) -> str:
        """Analyze trend for specific component"""
        if 'condition' in current_data:
            current_score = self._get_condition_score({'overall_condition': current_data.get('condition', 'fair')})
            historical_scores = [self._get_condition_score({'overall_condition': data.get('condition', 'fair')}) 
                               for data in historical_data]
            
            if historical_scores:
                avg_historical = sum(historical_scores) / len(historical_scores)
                if current_score > avg_historical + 0.3:
                    return 'improving'
                elif current_score < avg_historical - 0.3:
                    return 'declining'
        
        return 'stable'