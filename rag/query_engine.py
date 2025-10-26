import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PromptTemplate:
    """Simple prompt template to replace LangChain dependency"""
    def __init__(self, input_variables: list, template: str):
        self.input_variables = input_variables
        self.template = template
    
    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)
from vector_store import PropertyVectorStore
from utils.openrouter_llm import OpenRouterLLM
from typing import List, Dict

class PropertyQueryEngine:
    def __init__(self, vector_store: PropertyVectorStore):
        self.vector_store = vector_store
        # Use OpenRouter with free Deepseek model
        self.llm = OpenRouterLLM(model="deepseek/deepseek-chat")
        print(f"Initialized with OpenRouter LLM: {self.llm.model}")
        self.prompts = {
            'cost_estimation': PromptTemplate(
                input_variables=["context", "question"],
                template="You are a construction cost estimator. Use the following context to provide accurate cost estimates.\n\nContext: {context}\n\nQuestion: {question}\n\nProvide an itemized estimate where possible."
            ),
            'regulatory': PromptTemplate(
                input_variables=["context", "question"],
                template="You are a regulatory assistant. Given the context below, summarize applicable building codes and regulatory requirements.\n\nContext: {context}\n\nQuestion: {question}"
            ),
            'general': PromptTemplate(
                input_variables=["context", "question"],
                template="Use the context to answer the question concisely.\n\nContext: {context}\n\nQuestion: {question}"
            )
        }

    def query_with_context(self, question: str, query_type: str = 'general', user_context: dict = None, cv_context: dict = None, top_k: int = 5) -> dict:
        """Run a retrieval-augmented query and return an LLM answer plus sources."""
        user_context = user_context or {}
        cv_context = cv_context or {}
        # enhance query
        enhanced = self._enhance_query(question, cv_context, user_context)
        # select categories and retrieve
        categories = self._select_categories(query_type, cv_context)
        retriever = None
        try:
            retriever = self.vector_store.as_retriever()
        except Exception:
            retriever = None
        retrieved_docs = []
        if retriever:
            try:
                retrieved_docs = retriever(enhanced, top_k=top_k)
            except Exception:
                # fallback to direct query
                retrieved_docs = self.vector_store.query(enhanced, categories=categories) if hasattr(self.vector_store, 'query') else []
        else:
            if hasattr(self.vector_store, 'query'):
                retrieved_docs = self.vector_store.query(enhanced, categories=categories)

        # Build context text
        context_text = ''
        for d in retrieved_docs:
            text = getattr(d, 'page_content', str(d))
            meta = getattr(d, 'metadata', {})
            context_text += f"Source: {meta.get('source', meta.get('category','unknown'))}\n{text}\n\n"

        # Select prompt template
        prompt = self.prompts.get(query_type, self.prompts.get('general'))
        try:
            prompt_text = prompt.format(context=context_text, question=question)
        except Exception:
            prompt_text = f"Context:\n{context_text}\nQuestion: {question}"

        # Call OpenRouter LLM
        try:
            llm_result = self.llm.invoke(prompt_text)
        except Exception as e:
            llm_result = f"LLM invocation failed: {e}"

        return {
            'question': question,
            'enhanced_query': enhanced,
            'answer': llm_result,
            'source_documents': retrieved_docs,
            'retrieved': [{'content': getattr(d,'page_content',None),'metadata': getattr(d,'metadata',{})} for d in retrieved_docs]
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
