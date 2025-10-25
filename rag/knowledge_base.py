import os
import json
import pandas as pd
from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    CSVLoader
)

class KnowledgeBase:
    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = knowledge_base_path
        self.documents = {}
        
    def load_knowledge_base(self):
        loaders = {
            'building_codes': DirectoryLoader(
                f"{self.knowledge_base_path}/building_codes",
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            ),
            'insurance_guidelines': DirectoryLoader(
                f"{self.knowledge_base_path}/insurance_guidelines", 
                glob="**/*.json",
                loader_cls=TextLoader
            ),
            'real_estate_data': CSVLoader(
                f"{self.knowledge_base_path}/real_estate_data/neighborhood_comps.csv"
            ),
            'construction_standards': DirectoryLoader(
                f"{self.knowledge_base_path}/construction_standards",
                glob="**/*.txt",
                loader_cls=TextLoader
            )
        }
        
        for category, loader in loaders.items():
            try:
                self.documents[category] = loader.load()
                print(f"Loaded {len(self.documents[category])} documents from {category}")
            except Exception as e:
                print(f"Error loading {category}: {e}")
                self.documents[category] = []
    
    def get_documents_by_category(self, category: str) -> List[Document]:
        return self.documents.get(category, [])
    