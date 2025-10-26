import os
import json
import pandas as pd
from typing import List, Dict

class Document:
    """Simple document class to replace LangChain dependency"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class SimpleLoader:
    """Simple file loader to replace LangChain loaders"""
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def load(self) -> List[Document]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [Document(page_content=content, metadata={'source': self.file_path})]
        except Exception as e:
            print(f"Error loading {self.file_path}: {e}")
            return []
class KnowledgeBase:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.documents = {}
        
    def load_knowledge_base(self):
        self.documents['building_codes'] = self._load_directory(f"{self.knowledge_base_path}/building_codes", ['.pdf', '.txt'])
        self.documents['insurance_guidelines'] = self._load_directory(f"{self.knowledge_base_path}/insurance_guidelines", ['.json', '.txt'])
        self.documents['construction_standards'] = self._load_directory(f"{self.knowledge_base_path}/construction_standards", ['.txt'])
        self.documents['real_estate_data'] = self._load_directory(f"{self.knowledge_base_path}/real_estate_data", ['.csv', '.txt'])
        
        # Create mock documents if directories don't exist
        for category in ['building_codes', 'insurance_guidelines', 'construction_standards', 'real_estate_data']:
            if not self.documents[category]:
                self.documents[category] = [Document(
                    page_content=f"Mock {category} data for testing",
                    metadata={'source': f'mock_{category}', 'category': category}
                )]
            print(f"Loaded {len(self.documents[category])} documents from {category}")
    
    def _load_directory(self, directory: str, extensions: List[str]) -> List[Document]:
        documents = []
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if any(filename.endswith(ext) for ext in extensions):
                    file_path = os.path.join(directory, filename)
                    loader = SimpleLoader(file_path)
                    documents.extend(loader.load())
        return documents
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        return self.documents.get(category, [])
    