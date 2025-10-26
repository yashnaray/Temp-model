import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.home_inspector_agent import HomeInspectorAgent
from agents.insurance_agent import InsuranceAgent
from agents.real_estate_agent import RealEstateAgent
from agents.historical_analyzer import HistoricalAnalyzer
from rag.query_engine import PropertyQueryEngine
from typing import List, Dict

class PropertyOrchestrator:
    def __init__(self, query_engine: PropertyQueryEngine):
        self.query_engine = query_engine
        self.home_inspector = HomeInspectorAgent()
        self.insurance_agent = InsuranceAgent(query_engine)
        self.real_estate_agent = RealEstateAgent(query_engine)
        self.historical_analyzer = HistoricalAnalyzer()
        
    def comprehensive_property_analysis(self, images, property_info=None, analysis_type='full'):
        """Orchestrate comprehensive property analysis"""
        results = {
            'inspection_report': {},
            'insurance_assessment': {},
            'real_estate_analysis': {},
            'summary': {},
            'recommendations': []
        }
        
        # Step 1: Property Inspection
        inspection_report = self.home_inspector.inspect_property(images, property_info)
        results['inspection_report'] = inspection_report
        
        if analysis_type in ['full', 'insurance']:
            # Step 2: Insurance Risk Assessment
            insurance_assessment = self.insurance_agent.assess_insurance_risk(
                inspection_report, property_info
            )
            results['insurance_assessment'] = insurance_assessment
            
            # Get policy recommendations
            policy_recommendations = self.insurance_agent.get_policy_recommendations(
                insurance_assessment, property_info.get('value') if property_info else None
            )
            results['insurance_assessment']['policy_recommendations'] = policy_recommendations
        
        if analysis_type in ['full', 'real_estate']:
            # Step 3: Real Estate Analysis
            valuation = self.real_estate_agent.estimate_property_value(
                inspection_report, property_info
            )
            results['real_estate_analysis']['valuation'] = valuation
            
            # Generate listing description
            listing_description = self.real_estate_agent.generate_listing_description(
                inspection_report, property_info
            )
            results['real_estate_analysis']['listing'] = listing_description
            
            # Investment analysis
            investment_analysis = self.real_estate_agent.generate_investment_analysis(
                valuation, property_info
            )
            results['real_estate_analysis']['investment'] = investment_analysis
        
        # Step 4: Historical Analysis (if property info includes address)
        if property_info and 'address' in property_info:
            historical_data = self.historical_analyzer.get_historical_property_data(property_info['address'])
            results['historical_analysis'] = {
                'property_history': historical_data,
                'market_trends': self.historical_analyzer.get_market_trends(
                    property_info.get('location', property_info['address'])
                ),
                'maintenance_predictions': self.historical_analyzer.predict_future_maintenance(
                    inspection_report, historical_data
                )
            }
        
        # Step 5: Generate Summary and Recommendations
        results['summary'] = self._generate_summary(results)
        results['recommendations'] = self._consolidate_recommendations(results)
        
        # Enrich recommendations with RAG-driven cost and code checks
        enriched = []
        for rec in results['recommendations']:
            try:
                cost = self.query_engine.query_with_context(f"Estimate cost for: {rec}", query_type='cost_estimation')
            except Exception as e:
                cost = {'answer': f'Cost estimation unavailable: {e}'}
            try:
                codes = self.query_engine.query_with_context(f"Building code requirements for: {rec}", query_type='regulatory')
            except Exception as e:
                codes = {'answer': f'Regulatory lookup unavailable: {e}'}
            enriched.append({'recommendation': rec, 'cost_estimate': cost, 'code_check': codes})
        results['recommendation_details'] = enriched

        return results
    
    def _generate_summary(self, analysis_results):
        """Generate executive summary of analysis"""
        summary = {
            'overall_condition': 'unknown',
            'estimated_value': 0,
            'insurance_risk': 'unknown',
            'key_findings': []
        }
        
        # Extract key metrics
        inspection = analysis_results.get('inspection_report', {})
        summary['overall_condition'] = inspection.get('overall_condition', 'unknown')
        
        if 'real_estate_analysis' in analysis_results:
            valuation = analysis_results['real_estate_analysis'].get('valuation', {})
            summary['estimated_value'] = valuation.get('estimated_value', 0)
        
        if 'insurance_assessment' in analysis_results:
            insurance = analysis_results['insurance_assessment']
            summary['insurance_risk'] = insurance.get('overall_risk', 'unknown')
        
        # Key findings
        issues = inspection.get('issues', [])
        summary['key_findings'].extend(issues[:3])  # Top 3 issues
        
        return summary
    
    def _consolidate_recommendations(self, analysis_results):
        """Consolidate recommendations from all agents"""
        all_recommendations = []
        
        # Inspection recommendations
        inspection = analysis_results.get('inspection_report', {})
        all_recommendations.extend(inspection.get('recommendations', []))
        
        # Insurance recommendations
        if 'insurance_assessment' in analysis_results:
            insurance = analysis_results['insurance_assessment']
            all_recommendations.extend(insurance.get('coverage_recommendations', []))
        
        # Real estate recommendations
        if 'real_estate_analysis' in analysis_results:
            listing = analysis_results['real_estate_analysis'].get('listing', {})
            all_recommendations.extend(listing.get('recommendations', []))
        
        # Remove duplicates and prioritize
        unique_recommendations = list(set(all_recommendations))
        
        return unique_recommendations[:10]  # Top 10 recommendations
    
    def compare_with_historical_inspections(self, current_inspection: Dict, historical_inspections: List[Dict]) -> Dict:
        """Compare current inspection with historical data"""
        return self.historical_analyzer.compare_historical_conditions(
            current_inspection, historical_inspections
        )
    
    def get_property_history(self, address: str) -> Dict:
        """Get comprehensive property history"""
        return self.historical_analyzer.get_historical_property_data(address)
    
    def query_property_knowledge(self, question, context=None):
        """Query the property knowledge base"""
        return self.query_engine.query_with_context(
            question,
            query_type="general",
            user_context=context or {}
        )
    
    def get_cost_estimate(self, repair_description, property_info=None):
        """Get cost estimate for repairs/improvements"""
        context = {}
        if property_info:
            context.update(property_info)
        
        return self.query_engine.query_with_context(
            f"Cost estimate for {repair_description}",
            query_type="cost_estimation",
            user_context=context
        )
    
    def check_building_codes(self, work_description, location=None):
        """Check building code requirements"""
        context = {'location': location} if location else {}
        
        return self.query_engine.query_with_context(
            f"Building code requirements for {work_description}",
            query_type="regulatory",
            user_context=context
        )

# Backwards compatible alias
Orchestrator = PropertyOrchestrator
