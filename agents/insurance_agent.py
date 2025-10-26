import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.query_engine import PropertyQueryEngine

class InsuranceAgent:
    def __init__(self, query_engine: PropertyQueryEngine):
        self.query_engine = query_engine
        self.risk_factors = {
            'foundation_cracks': 0.3,
            'roof_damage': 0.4,
            'water_damage': 0.5,
            'structural_issues': 0.6,
            'fire_hazards': 0.8
        }
        
    def assess_insurance_risk(self, inspection_report, property_info=None):
        """Assess insurance risk based on inspection report"""
        risk_assessment = {
            'overall_risk': 'low',
            'risk_score': 0.0,
            'risk_factors': [],
            'coverage_recommendations': [],
            'premium_impact': 'neutral'
        }
        
        risk_score = 0.0
        
        # Analyze foundation issues
        foundation = inspection_report['components'].get('foundation', {})
        if 'analysis' in foundation:
            severity = foundation['analysis'].get('severity_score', 0)
            if severity > 2:
                risk_score += self.risk_factors['foundation_cracks']
                risk_assessment['risk_factors'].append('Foundation structural concerns')
        
        # Analyze roof condition
        roof = inspection_report['components'].get('roof', {})
        if 'condition' in roof:
            if isinstance(roof['condition'], tuple):
                condition_score, features = roof['condition']
                if condition_score < 0:
                    risk_score += self.risk_factors['roof_damage']
                    risk_assessment['risk_factors'].append('Roof deterioration')
        
        # Check for water damage indicators
        for component, data in inspection_report['components'].items():
            if 'material' in data:
                moisture_damage = data['material'].get('moisture_damage', 0)
                if moisture_damage > 0.3:
                    risk_score += self.risk_factors['water_damage']
                    risk_assessment['risk_factors'].append(f'Water damage in {component}')
        
        # Check for changes indicating deterioration
        if 'changes' in inspection_report:
            change_pct = inspection_report['changes'].get('change_percentage', 0)
            if change_pct > 10:
                risk_score += 0.2
                risk_assessment['risk_factors'].append('Rapid property deterioration')
        
        # Calculate overall risk
        risk_assessment['risk_score'] = min(risk_score, 1.0)
        
        if risk_score > 0.6:
            risk_assessment['overall_risk'] = 'high'
            risk_assessment['premium_impact'] = 'increase'
        elif risk_score > 0.3:
            risk_assessment['overall_risk'] = 'medium'
            risk_assessment['premium_impact'] = 'slight_increase'
        else:
            risk_assessment['overall_risk'] = 'low'
            risk_assessment['premium_impact'] = 'neutral'
        
        # Generate coverage recommendations
        risk_assessment['coverage_recommendations'] = self._generate_coverage_recommendations(risk_assessment)
        
        return risk_assessment
    
    def get_policy_recommendations(self, risk_assessment, property_value=None):
        """Get insurance policy recommendations"""
        recommendations = {
            'coverage_types': [],
            'deductible_suggestions': {},
            'additional_riders': []
        }
        
        # Basic coverage
        recommendations['coverage_types'].extend(['dwelling', 'personal_property', 'liability'])
        
        # Risk-based recommendations
        if 'Water damage' in str(risk_assessment['risk_factors']):
            recommendations['coverage_types'].append('flood_insurance')
            recommendations['additional_riders'].append('water_backup_coverage')
        
        if 'Foundation' in str(risk_assessment['risk_factors']):
            recommendations['additional_riders'].append('foundation_coverage')
        
        if 'Roof' in str(risk_assessment['risk_factors']):
            recommendations['deductible_suggestions']['roof'] = 'consider_higher_deductible'
        
        # Deductible recommendations based on risk
        if risk_assessment['overall_risk'] == 'high':
            recommendations['deductible_suggestions']['general'] = 'lower_deductible_recommended'
        elif risk_assessment['overall_risk'] == 'low':
            recommendations['deductible_suggestions']['general'] = 'higher_deductible_for_savings'
        
        return recommendations
    
    def _generate_coverage_recommendations(self, risk_assessment):
        """Generate specific coverage recommendations"""
        recommendations = []
        
        if risk_assessment['overall_risk'] == 'high':
            recommendations.append("Consider comprehensive coverage with lower deductibles")
            recommendations.append("Regular property inspections recommended")
        
        if 'Foundation' in str(risk_assessment['risk_factors']):
            recommendations.append("Add foundation coverage rider")
        
        if 'Water damage' in str(risk_assessment['risk_factors']):
            recommendations.append("Consider flood insurance and water backup coverage")
        
        if 'Roof' in str(risk_assessment['risk_factors']):
            recommendations.append("Roof replacement coverage recommended")
        
        return recommendations
    
    def query_insurance_guidelines(self, question, context=None):
        """Query insurance guidelines from knowledge base"""
        return self.query_engine.query_with_context(
            question, 
            query_type="regulatory",
            user_context=context or {}
        )