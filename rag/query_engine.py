from langchain.chat_models import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from vector_store import PropertyVectorStore

class PropertyQueryEngine:
    def __init__(self, vector_store: PropertyVectorStore):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(temperature=0, model="deepseek-R1")
        self.prompts = {
            'cost_estimation': PromptTemplate(
                input_variables=["context", "question"],
                template="""
                You are a construction cost estimator. Use the following context to provide accurate cost estimates.
                
                Context: {context}
                
                Question: {question}
                
                Provide:
                1. Estimated cost range
                2. Factors affecting cost
                3. Regional variations if available
                4. Timeframe for completion
                
                Answer:
                """
            ),
            'regulatory': PromptTemplate(
                input_variables=["context", "question"],
                template="""
                You are a building code expert. Provide precise regulatory information.
                
                Context: {context}
                
                Question: {question}
                
                Focus on:
                - Code requirements
                - Permit needs
                - Compliance issues
                - Potential violations
                
                Answer:
                """
            )
        }
    
    def query_with_context(self, question: str, query_type: str = "general", 
                          cv_context: dict = {}, user_context: dict = {}):
        enhanced_question = self._enhance_query(question, cv_context, user_context)
        categories = self._select_categories(query_type, cv_context)
        docs = self.vector_store.query(enhanced_question, categories)
        prompt_template = self.prompts.get(query_type, self.prompts['general'])
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": prompt_template}
        )
        
        result = qa_chain.run(enhanced_question)
        return {
            'answer': result,
            'source_documents': docs,
            'enhanced_question': enhanced_question
        }
    
    def _enhance_query(self, question: str, cv_context: dict, user_context: dict) -> str:
        enhanced = question
        
        if cv_context:
            enhanced += f" Property features: {cv_context.get('components', [])}. "
            enhanced += f" Condition scores: {cv_context.get('condition_scores', {})}. "
        
        if user_context:
            enhanced += f" User type: {user_context.get('user_type', 'general')}. "
            enhanced += f" Location: {user_context.get('location', 'unknown')}. "
        
        return enhanced
    
    def _select_categories(self, query_type: str, cv_context: dict) -> list:
        categories = ['general']
        if query_type == 'cost_estimation': categories.append('cost')
        elif query_type == 'regulatory': categories.append('regulatory')
        if cv_context: categories.extend(cv_context.get('components', []))
        return list(set(categories))