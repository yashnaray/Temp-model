import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.api_manager import APIManager
from knowledge_base.web_scraper import FinalDump

class KnowledgeBaseScraper:
    def __init__(self, knowledge_base_path="knowledge_base"):
        self.knowledge_base_path = knowledge_base_path
        self.dump = FinalDump(knowledge_base_path)
        self.api_manager = APIManager()
        
    def scrape_real_estate_data(self, location):
        """Get real estate data for given location using APIs"""
        data = self.api_manager.get_property_data(location)
        
        # Save to real_estate_guidelines directory
        output_path = os.path.join(self.knowledge_base_path, "real_estate_guidelines")
        os.makedirs(output_path, exist_ok=True)
        filename = f"listings_{location.replace(' ', '_').replace(',', '')}"
        filepath = os.path.join(output_path, f"{filename}.json")
        self.dump.save_data({"location": location, "data": data}, filepath)
        return data
    
    def scrape_insurance_guidelines(self, address="123 Main St"):
        """Get insurance guidelines using APIs"""
        property_info = {'value': 300000, 'type': 'residential'}
        data = self.api_manager.get_insurance_analysis(property_info, address)
        
        # Save to insurance_guidelines directory
        output_path = os.path.join(self.knowledge_base_path, "insurance_guidelines")
        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, "insurance_guidelines.json")
        self.dump.save_data({"guidelines": data}, filepath)
        return data
    
    def scrape_building_codes(self, location, code_type="residential"):
        """Get building codes using APIs"""
        property_details = {'type': code_type, 'year_built': 2000}
        data = self.api_manager.get_building_compliance(property_details, location)
        
        # Save to building_codes directory
        output_path = os.path.join(self.knowledge_base_path, "building_codes")
        os.makedirs(output_path, exist_ok=True)
        filename = f"codes_{code_type}"
        filepath = os.path.join(output_path, f"{filename}.json")
        self.dump.save_data({"location": location, "codes": data}, filepath)
        return data
    
    def scrape_all_for_location(self, location, code_types=["residential", "commercial"]):
        """Scrape all data types for a specific location"""
        results = {}
        
        # Scrape real estate data
        results['real_estate'] = self.scrape_real_estate_data(location)
        
        # Scrape insurance guidelines
        results['insurance'] = self.scrape_insurance_guidelines()
        
        # Get building codes
        results['building_codes'] = {}
        for code_type in code_types:
            results['building_codes'][code_type] = self.scrape_building_codes(location, code_type)
        
        print(f"Scraped data for {location} saved to {self.knowledge_base_path}")
        return results

def main():
    """Example usage"""
    scraper = KnowledgeBaseScraper()
    
    # Get user input
    location = input("Enter location to scrape data for: ")
    
    # Get all data for the location
    results = scraper.scrape_all_for_location(location)
    
    # Test API connections
    api_status = scraper.api_manager.test_api_connections()
    print(f"API Status: {api_status}")
    
    print(f"Data collection completed. Data saved to knowledge_base directories.")

if __name__ == "__main__":
    main()