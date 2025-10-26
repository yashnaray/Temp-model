import os
import json
from typing import List, Dict

class Document:
    """Simple document class"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class SimpleTextSplitter:
    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size
    def split_text(self, text):
        # naive splitter by sentences or fixed size
        if not text:
            return []
        parts = []
        for i in range(0, len(text), self.chunk_size):
            parts.append(text[i:i+self.chunk_size])
        return parts

class PropertyVectorStore:
    def __init__(self, embeddings_model=None):
        self.embeddings = None
        self.vector_store = None
        self.documents: List[Document] = []
        self.text_splitter = SimpleTextSplitter()

    def add_documents(self, documents: List[Document], categories: List[str] = None):
        """Add documents to the vector store"""
        if not documents:
            return
        for doc in documents:
            if categories:
                doc.metadata['category'] = categories[0] if len(categories)==1 else categories
            self.documents.append(doc)
        # Simple document storage without embeddings
        if self.vector_store is None:
            self.vector_store = {'docs': list(documents)}
        else:
            self.vector_store['docs'].extend(documents)

    def as_retriever(self, search_kwargs=None):
        """Return a retriever interface"""
        search_kwargs = search_kwargs or {"k": 5}
        
        def retriever_func(query, **kwargs):
            return self.query(query)[:search_kwargs.get("k", 5)]
        
        return retriever_func

    def query(self, query: str, categories: List[str] = None):
        """Simple keyword based query"""
        if not query:
            return []
        q = query.lower()
        matches = []
        for doc in self.documents:
            if q in (doc.page_content or "").lower():
                matches.append(doc)
        return matches

    def save(self, path: str):
        """Save the vector store to disk"""
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, 'docs.json'), 'w') as f:
            docs_data = [{'content': doc.page_content, 'metadata': doc.metadata} for doc in self.documents]
            json.dump(docs_data, f)

    def load(self, path: str):
        """Load the vector store from disk"""
        docs_file = os.path.join(path, 'docs.json')
        if os.path.exists(docs_file):
            with open(docs_file, 'r') as f:
                docs_data = json.load(f)
            self.documents = [Document(d['content'], d['metadata']) for d in docs_data]
            self.vector_store = {'docs': self.documents}

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'categories': list(set(doc.metadata.get('category', 'unknown') for doc in self.documents)),
            'storage_type': 'keyword_search'
        }
