import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.query_engine import PropertyQueryEngine

class RealEstateAgent:
    def __init__(self, query_engine: PropertyQueryEngine):
        self.query_engine = query_engine
        
    def estimate_property_value(self, inspection_report, property_info=None):
        """Estimate property value based on inspection and market data"""
        valuation = {
            'estimated_value': 0,
            'condition_adjustment': 0,
            'market_factors': {},
            'comparable_properties': [],
            'value_range': {'low': 0, 'high': 0}
        }
        
        # Base value from property info
        base_value = property_info.get('base_value', 200000) if property_info else 200000
        
        # Condition-based adjustments
        condition_multiplier = self._get_condition_multiplier(inspection_report)
        adjusted_value = base_value * condition_multiplier
        
        valuation['estimated_value'] = adjusted_value
        valuation['condition_adjustment'] = (condition_multiplier - 1.0) * 100
        
        # Value range (±10%)
        valuation['value_range'] = {
            'low': adjusted_value * 0.9,
            'high': adjusted_value * 1.1
        }
        
        return valuation
    
    def _get_condition_multiplier(self, inspection_report):
        """Calculate value multiplier based on property condition"""
        overall_condition = inspection_report.get('overall_condition', 'unknown')
        
        condition_multipliers = {
            'excellent': 1.15,
            'good': 1.05,
            'fair': 1.0,
            'poor': 0.85,
            'unknown': 1.0
        }
        
        base_multiplier = condition_multipliers.get(overall_condition, 1.0)
        
        # Additional adjustments for specific issues
        issues = inspection_report.get('issues', [])
        for issue in issues:
            if 'foundation' in issue.lower():
                base_multiplier -= 0.1
            elif 'roof' in issue.lower():
                base_multiplier -= 0.05
            elif 'water damage' in issue.lower():
                base_multiplier -= 0.08
        
        return max(base_multiplier, 0.5)  # Minimum 50% of base value
    
    def generate_listing_description(self, inspection_report, property_info=None):
        """Generate property listing description"""
        description = {
            'highlights': [],
            'condition_notes': [],
            'recommendations': []
        }
        
        # Positive highlights
        overall_condition = inspection_report.get('overall_condition', 'unknown')
        if overall_condition in ['excellent', 'good']:
            description['highlights'].append(f"Property in {overall_condition} condition")
        
        # Component highlights
        components = inspection_report.get('components', {})
        for component, data in components.items():
            if 'material' in data:
                material_type = data['material'].get('material_type', 'unknown')
                if material_type in ['Metal', 'Glass']:
                    description['highlights'].append(f"Durable {material_type.lower()} {component}")
        
        # Condition notes
        issues = inspection_report.get('issues', [])
        for issue in issues:
            description['condition_notes'].append(issue)
        
        # Recommendations for buyers
        recommendations = inspection_report.get('recommendations', [])
        description['recommendations'] = recommendations
        
        return description
    
    def assess_market_timing(self, property_info=None, location=None):
        """Assess market timing for buying/selling"""
        timing_assessment = {
            'recommendation': 'neutral',
            'market_conditions': 'stable',
            'factors': []
        }
        
        # This would typically integrate with real market data
        # For now, providing basic assessment structure
        
        if location:
            # Query market data from knowledge base
            market_query = f"Current real estate market conditions in {location}"
            market_data = self.query_engine.query_with_context(
                market_query,
                query_type="general",
                user_context={'location': location}
            )
            
            timing_assessment['market_data'] = market_data
        
        return timing_assessment
    
    def get_comparable_properties(self, property_info, location=None):
        """Get comparable property data"""
        comparables = {
            'similar_properties': [],
            'price_range': {'low': 0, 'high': 0},
            'market_trends': {}
        }
        
        if location:
            # Query comparable properties from knowledge base
            comp_query = f"Similar properties for sale in {location}"
            comp_data = self.query_engine.query_with_context(
                comp_query,
                query_type="general",
                user_context={'location': location, 'property_type': property_info.get('type', 'residential')}
            )
            
            comparables['query_results'] = comp_data
        
        return comparables
    
    def generate_investment_analysis(self, valuation, property_info=None):
        """Generate investment analysis for property"""
        analysis = {
            'roi_potential': 'unknown',
            'rental_yield': 0,
            'appreciation_forecast': 'stable',
            'investment_grade': 'C'
        }
        
        estimated_value = valuation.get('estimated_value', 0)
        condition_adjustment = valuation.get('condition_adjustment', 0)
        
        # Basic investment grading
        if condition_adjustment > 5:
            analysis['investment_grade'] = 'A'
            analysis['roi_potential'] = 'high'
        elif condition_adjustment > 0:
            analysis['investment_grade'] = 'B'
            analysis['roi_potential'] = 'medium'
        elif condition_adjustment > -10:
            analysis['investment_grade'] = 'C'
            analysis['roi_potential'] = 'low'
        else:
            analysis['investment_grade'] = 'D'
            analysis['roi_potential'] = 'poor'
        
        return analysis