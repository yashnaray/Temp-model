import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PropertyVectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.vector_store= Chroma(client=chromadb.Client(), embedding_function=self.embeddings)
        self.persist_directory = persist_directory
    
    def initialize_vector_store(self, knowledge_base: KnowledgeBase):
        all_documents = []
        
        for category, docs in knowledge_base.documents.items():
            for doc in docs:
                doc.metadata['category'] = category
                doc.metadata['source'] = 'knowledge_base'
            
            split_docs = self.text_splitter.split_documents(docs)
            all_documents.extend(split_docs)
        
        self.vector_store = Chroma.from_documents(
            documents=all_documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vector_store.persist()
    
    def query(self, query: str, categories: List[str] = None, n_results: int = 5):
        """Query the vector store with optional category filtering"""
        if categories:
            where_clause = {"category": {"$in": categories}}
            results = self.vector_store.similarity_search(
                query, 
                k=n_results,
                filter=where_clause
            )
        else: results = self.vector_store.similarity_search(query, k=n_results)
        
        return results
    def as_retriever(self):
        return self.vector_store.as_retriever()