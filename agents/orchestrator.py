from typing import Dict, List, Any
from langchain.agents import AgentExecutor, Tool
from langchain.memory import ConversationBufferMemory
from crewai import Agent, Task, Crew, Process
from home_inspector_agent import HomeInspectorAgent
class PropertyOrchestrator:
    def __init__(self, query_engine, vision_system):
        self.query_engine = query_engine
        self.vision_system = vision_system
        self.agents = self._initialize_agents()
        self.memory = ConversationBufferMemory()
    
    def _initialize_agents(self):
        """Initialize specialized agents"""
        return {
            'home_inspector': HomeInspectorAgent(self.query_engine),
            'insurance_analyst': InsuranceAnalystAgent(self.query_engine),
            'real_estate_consultant': RealEstateConsultantAgent(self.query_engine),
            'cost_estimator': CostEstimatorAgent(self.query_engine)
        }
    
    def analyze_property(self, image, user_context: Dict) -> Dict:
        """Orchestrate multi-agent property analysis"""
        
        # Step 1: Computer Vision Analysis
        cv_results = self.vision_system.analyze_property(image)
        
        # Step 2: Determine which agents to activate
        activated_agents = self._select_agents(user_context, cv_results)
        
        # Step 3: Execute agent tasks in parallel
        agent_results = {}
        for agent_name in activated_agents:
            agent = self.agents[agent_name]
            agent_results[agent_name] = agent.analyze(
                cv_results=cv_results,
                user_context=user_context
            )
        
        # Step 4: Synthesize final report
        final_report = self._synthesize_report(agent_results, cv_results, user_context)
        
        return final_report
    
    def _select_agents(self, user_context: Dict, cv_results: Dict) -> List[str]:
        """Intelligently select which agents to activate based on context"""
        agents_to_activate = []
        
        user_type = user_context.get('user_type', 'homeowner')
        
        # Base agents for all users
        agents_to_activate.extend(['home_inspector', 'cost_estimator'])
        
        # Context-specific agents
        if user_type == 'home_buyer':
            agents_to_activate.append('real_estate_consultant')
        elif user_type == 'insurance_claim':
            agents_to_activate.append('insurance_analyst')
        elif user_type == 'real_estate_investor':
            agents_to_activate.extend(['real_estate_consultant', 'insurance_analyst'])
        
        # CV-based agent activation
        condition_scores = cv_results.get('condition_scores', {})
        if any(score < 5 for score in condition_scores.values()):
            agents_to_activate.append('insurance_analyst')  # For risk assessment
        
        return list(set(agents_to_activate))
