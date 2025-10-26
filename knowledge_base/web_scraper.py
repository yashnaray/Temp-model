import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict

class REGScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def scrape_listings(self, location: str) -> List[Dict]:
        response = self.session.get(f"{self.base_url}/search?location={location}")
        return REGParser().parse_listings(response.text)

class REGParser:
    def parse_listings(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []
        for item in soup.find_all('div', class_='listing'):
            listings.append({
                'price': item.find('span', class_='price').text if item.find('span', class_='price') else None,
                'address': item.find('div', class_='address').text if item.find('div', class_='address') else None,
                'details': item.find('div', class_='details').text if item.find('div', class_='details') else None
            })
        return listings

class IGLScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def scrape_guidelines(self) -> List[Dict]:
        response = self.session.get(f"{self.base_url}/guidelines")
        return IGLParser().parse_guidelines(response.text)

class IGLParser:
    def parse_guidelines(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        guidelines = []
        for section in soup.find_all('div', class_='guideline-section'):
            guidelines.append({
                'title': section.find('h3').text if section.find('h3') else None,
                'content': section.find('p').text if section.find('p') else None,
                'category': section.get('data-category', 'general')
            })
        return guidelines

class BCScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def scrape_codes(self, code_type: str) -> List[Dict]:
        response = self.session.get(f"{self.base_url}/codes/{code_type}")
        return BCParser().parse_codes(response.text)

class BCParser:
    def parse_codes(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        codes = []
        for code in soup.find_all('div', class_='code-section'):
            codes.append({
                'code_number': code.find('span', class_='code-num').text if code.find('span', class_='code-num') else None,
                'description': code.find('div', class_='description').text if code.find('div', class_='description') else None,
                'requirements': code.find('ul', class_='requirements').text if code.find('ul', class_='requirements') else None
            })
        return codes

class FinalDump:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_data(self, data: Dict, filepath: str):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def dump_all(self, reg_data: List[Dict], igl_data: List[Dict], bc_data: List[Dict]):
        self.save_data({'listings': reg_data}, os.path.join(self.output_dir, 'real_estate_data.json'))
        self.save_data({'guidelines': igl_data}, os.path.join(self.output_dir, 'insurance_guidelines.json'))
        self.save_data({'codes': bc_data}, os.path.join(self.output_dir, 'building_codes.json'))