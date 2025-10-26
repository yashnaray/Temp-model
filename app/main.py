import os
import sys

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if not os.getenv("OPENROUTER_API_KEY"):
    print("\nTo use free LLM models, get a free API key from https://openrouter.ai")
    print("Then set: export OPENROUTER_API_KEY=your_key_here\n")

# Suppress warnings during imports
import warnings
warnings.filterwarnings('ignore')

from knowledge_base.scraper_integration import KnowledgeBaseScraper
from rag.knowledge_base import KnowledgeBase
from rag.vector_store import PropertyVectorStore
from rag.query_engine import PropertyQueryEngine
from agents.orchestrator import PropertyOrchestrator
try:
    import cv2
except ImportError:
    print("OpenCV not available - image analysis will use mock data")
    cv2 = None

class PropertyAnalysisApp:
    def __init__(self):
        self.scraper = KnowledgeBaseScraper()
        self.knowledge_base = KnowledgeBase("knowledge_base")
        self.vector_store = PropertyVectorStore()
        self.query_engine = PropertyQueryEngine(self.vector_store)
        self.orchestrator = PropertyOrchestrator(self.query_engine)
        
    def setup_knowledge_base(self, location=None):
        """Setup knowledge base with scraped data"""
        if location:
            print(f"Scraping data for {location}...")
            self.scraper.scrape_all_for_location(location)
        
        print("Loading knowledge base...")
        self.knowledge_base.load_knowledge_base()
        
        # Add documents to vector store
        for category, docs in self.knowledge_base.documents.items():
            if docs:
                self.vector_store.add_documents(docs, [category] * len(docs))
        
        print("Knowledge base setup complete.")
    
    def query_property(self, question: str, query_type: str = "general"):
        """Query the property analysis system"""
        return self.query_engine.query_with_context(question, query_type)
    
    def analyze_property_images(self, image_paths, property_info=None, analysis_type='full'):
        """Analyze property using uploaded images"""
        images = []
        for path in image_paths:
            img = cv2.imread(path)
            if img is not None:
                images.append(img)
        
        if not images:
            return {'error': 'No valid images provided'}
        
        return self.orchestrator.comprehensive_property_analysis(
            images, property_info, analysis_type
        )
    
    def run_interactive(self):
        """Run interactive mode"""
        print("Property Analysis System")
        print("=" * 30)
        
        # Setup
        location = input("Enter location for data scraping (or press Enter to skip): ")
        if location.strip():
            self.setup_knowledge_base(location)
        else:
            self.setup_knowledge_base()
        
        # Interactive querying
        while True:
            print("\nOptions:")
            print("1. Ask a question")
            print("2. Analyze property images")
            print("3. Get property history")
            print("4. Help - Show input examples")
            print("5. Quit")
            
            choice = input("\nSelect option (1-5): ")
            
            if choice == '5':
                break
            elif choice == '4':
                self.show_help()
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
                image_paths = input("Enter image paths (comma-separated): ").split(',')
                image_paths = [path.strip() for path in image_paths if path.strip()]
                
                analysis_type = input("Analysis type (full/insurance/real_estate): ") or "full"
                address = input("Enter property address (optional): ").strip()
                property_info = {'address': address} if address else None
                
                try:
                    result = self.analyze_property_images(image_paths, property_info, analysis_type)
                    print(f"\nAnalysis Results:")
                    print(f"Overall Condition: {result['summary']['overall_condition']}")
                    print(f"Estimated Value: ${result['summary']['estimated_value']:,.2f}")
                    print(f"Insurance Risk: {result['summary']['insurance_risk']}")
                    
                    if 'historical_analysis' in result:
                        hist = result['historical_analysis']
                        print(f"\nHistorical Analysis:")
                        if 'property_history' in hist:
                            price_trends = hist['property_history'].get('price_trends', {})
                            print(f"5-year appreciation: {price_trends.get('5_year', 0)}%")
                    
                    print(f"\nTop Recommendations:")
                    for i, rec in enumerate(result['recommendations'][:5], 1):
                        print(f"{i}. {rec}")
                except Exception as e:
                    print(f"Error: {e}")
            elif choice == '3':
                address = input("Enter property address: ").strip()
                if address:
                    try:
                        history = self.orchestrator.get_property_history(address)
                        print(f"\nProperty History for {address}:")
                        
                        if 'sales_history' in history:
                            print("\nSales History:")
                            for sale in history['sales_history']:
                                print(f"  {sale['date']}: ${sale['price']:,}")
                        
                        if 'price_trends' in history:
                            trends = history['price_trends']
                            print(f"\nPrice Trends:")
                            print(f"  1 year: {trends.get('1_year', 0)}%")
                            print(f"  5 year: {trends.get('5_year', 0)}%")
                    except Exception as e:
                        print(f"Error: {e}")
            else:
                print("Invalid option")
    
    def show_help(self):
        """Show input examples and explanations"""
        print("\n" + "=" * 50)
        print("INPUT EXAMPLES & EXPLANATIONS")
        print("=" * 50)
        
        print("\n1. ASK A QUESTION:")
        print("   Question examples:")
        print("   - 'What are common roof repair costs?'")
        print("   - 'Building codes for electrical work'")
        print("   - 'Insurance requirements for flood zones'")
        
        print("\n   Query Types:")
        print("   - general: General property questions")
        print("   - cost_estimation: Cost and pricing queries")
        print("   - regulatory: Building codes and regulations")
        
        print("\n2. ANALYZE PROPERTY IMAGES:")
        print("   Image paths (comma-separated):")
        print("   - C:\\Users\\photos\\house1.jpg, C:\\Users\\photos\\roof.jpg")
        print("   - /home/user/property.png")
        print("   - Multiple images: img1.jpg, img2.png, img3.jpeg")
        print("   Note: Requires OpenCV and TensorFlow for full functionality")
        
        print("\n   Analysis types:")
        print("   - full: Complete analysis (inspection + insurance + real estate)")
        print("   - insurance: Focus on insurance risk assessment")
        print("   - real_estate: Focus on property valuation")
        
        print("\n   Property address (optional):")
        print("   - '123 Main St, City, State'")
        print("   - 'Press Enter to skip'")
        
        print("\n3. GET PROPERTY HISTORY:")
        print("   Address examples:")
        print("   - '456 Oak Avenue, Springfield, IL'")
        print("   - '789 Pine Street, Austin, TX 78701'")
        print("   - Any valid street address")
        
        print("\nNOTE: System uses mock data when models unavailable")
        print("Install TensorFlow and OpenCV for full image analysis")
        print("=" * 50)

def main():
    app = PropertyAnalysisApp()
    app.run_interactive()

if __name__ == "__main__":
    main()