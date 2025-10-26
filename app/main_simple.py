import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.scraper_integration import KnowledgeBaseScraper
from rag.knowledge_base import KnowledgeBase
from rag.vector_store import PropertyVectorStore
from rag.query_engine import PropertyQueryEngine

class SimplePropertyApp:
    def __init__(self):
        self.scraper = KnowledgeBaseScraper()
        self.knowledge_base = KnowledgeBase("knowledge_base")
        self.vector_store = PropertyVectorStore()
        self.query_engine = PropertyQueryEngine(self.vector_store)
        
    def setup_knowledge_base(self, location=None):
        """Setup knowledge base with scraped data"""
        if location:
            print(f"Collecting data for {location}...")
            try:
                self.scraper.scrape_all_for_location(location)
            except Exception as e:
                print(f"Data collection error: {e}")
        
        print("Loading knowledge base...")
        try:
            self.knowledge_base.load_knowledge_base()
            
            # Add documents to vector store
            for category, docs in self.knowledge_base.documents.items():
                if docs:
                    self.vector_store.add_documents(docs, [category] * len(docs))
            
            print("Knowledge base setup complete.")
        except Exception as e:
            print(f"Knowledge base setup error: {e}")
    
    def query_property(self, question: str, query_type: str = "general"):
        """Query the property analysis system"""
        return self.query_engine.query_with_context(question, query_type)
    
    def run_interactive(self):
        """Run interactive mode"""
        print("Simple Property Analysis System")
        print("=" * 35)
        
        # Setup
        location = input("Enter location for data collection (or press Enter to skip): ")
        if location.strip():
            self.setup_knowledge_base(location)
        else:
            self.setup_knowledge_base()
        
        # Interactive querying
        while True:
            print("\nOptions:")
            print("1. Ask a question")
            print("2. Test API connections")
            print("3. Quit")
            
            choice = input("\nSelect option (1-3): ")
            
            if choice == '3':
                break
            elif choice == '1':
                print("\nQuery Types: general, cost_estimation, regulatory")
                question = input("\nEnter your question: ")
                query_type = input("Query type (default: general): ") or "general"
                
                try:
                    result = self.query_property(question, query_type)
                    print(f"\nAnswer: {result['answer']}")
                    print(f"Sources: {len(result['source_documents'])} documents")
                except Exception as e:
                    print(f"Error: {e}")
            elif choice == '2':
                try:
                    api_status = self.scraper.api_manager.test_api_connections()
                    print(f"\nAPI Connection Status:")
                    for api, status in api_status.items():
                        print(f"  {api}: {status}")
                except Exception as e:
                    print(f"API test error: {e}")
            else:
                print("Invalid option")

def main():
    app = SimplePropertyApp()
    app.run_interactive()

if __name__ == "__main__":
    main()