
class HomeInspectorAgent:
    def __init__(self, query_engine):
        self.query_engine = query_engine
        self.role = "Professional Home Inspector"
        self.goal = "Identify property issues and provide maintenance recommendations"
    
    def analyze(self, cv_results: Dict, user_context: Dict) -> Dict:
        inspection_questions = self._generate_inspection_questions(cv_results)
        
        inspection_results = {}
        for component, condition in cv_results.get('condition_scores', {}).items():
            if condition < 7:
                question = f"What are common issues with {component} showing condition score {condition}?"
                result = self.query_engine.query_with_context(
                    question=question,
                    query_type="regulatory",
                    cv_context=cv_results,
                    user_context=user_context
                )
                inspection_results[component] = result
        
        # Generate maintenance timeline
        maintenance_schedule = self._generate_maintenance_schedule(cv_results)
        
        return {
            'inspection_findings': inspection_results,
            'maintenance_schedule': maintenance_schedule,
            'priority_repairs': self._identify_priority_repairs(cv_results),
            'safety_concerns': self._identify_safety_issues(cv_results)
        }
    
    def _generate_maintenance_schedule(self, cv_results: Dict) -> List[Dict]:
        schedule = []
        
        for component, condition in cv_results.get('condition_scores', {}).items():
            if condition < 8:
                urgency = "Immediate" if condition < 5 else "Soon" if condition < 7 else "Monitor"
                schedule.append({
                    'component': component,
                    'action': f"Inspect and repair {component}",
                    'urgency': urgency,
                    'estimated_cost': f"${condition * 100}-${condition * 500}",
                    'timeline': "1-2 weeks" if urgency == "Immediate" else "1-3 months"
                })
        
        return schedule