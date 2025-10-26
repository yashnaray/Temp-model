import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from rag.vector_store import PropertyVectorStore
from rag.query_engine import PropertyQueryEngine
from rag.knowledge_base import KnowledgeBase

class TestKnowledgeBase:
    def setup_method(self):
        self.kb_path = "test_knowledge_base"
        self.kb = KnowledgeBase(self.kb_path)
    
    def test_init(self):
        assert self.kb.knowledge_base_path == self.kb_path
        assert isinstance(self.kb.documents, dict)
    
    def test_get_documents_by_category(self):
        result = self.kb.get_documents_by_category("nonexistent")
        assert result == []

class TestPropertyVectorStore:
    def setup_method(self):
        self.vector_store = PropertyVectorStore()
    
    def test_init(self):
        assert self.vector_store.embeddings is not None
        assert self.vector_store.text_splitter is not None
        assert self.vector_store.vector_store is not None
    
    def test_query_empty_categories(self):
        result = self.vector_store.query("test query", categories=[])
        assert isinstance(result, list)
    
    def test_as_retriever(self):
        retriever = self.vector_store.as_retriever()
        assert retriever is not None

class TestPropertyQueryEngine:
    def setup_method(self):
        mock_vector_store = Mock()
        self.query_engine = PropertyQueryEngine(mock_vector_store)
    
    def test_init(self):
        assert self.query_engine.vector_store is not None
        assert self.query_engine.llm is not None
        assert 'cost_estimation' in self.query_engine.prompts
        assert 'regulatory' in self.query_engine.prompts
    
    def test_enhance_query(self):
        cv_context = {'components': ['roof', 'walls'], 'condition_scores': {'roof': 8}}
        user_context = {'user_type': 'inspector', 'location': 'NYC'}
        
        enhanced = self.query_engine._enhance_query("test query", cv_context, user_context)
        assert "test query" in enhanced
        assert "roof" in enhanced
        assert "NYC" in enhanced
    
    def test_select_categories(self):
        cv_context = {'components': ['roof', 'walls']}
        categories = self.query_engine._select_categories('cost_estimation', cv_context)
        
        assert 'general' in categories
        assert 'cost' in categories
        assert 'roof' in categories

if __name__ == "__main__":
    pytest.main([__file__])