import requests
import json
import os
from typing import Optional

class OpenRouterLLM:
    """OpenRouter API client for free LLM models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek/deepseek-chat"):
        # Try to load from .env file
        self._load_env()
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Free models available on OpenRouter
        self.free_models = [
            "deepseek/deepseek-chat",
            "google/gemma-2-9b-it:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "huggingface/zephyr-7b-beta:free"
        ]
        
        if not self.api_key:
            print("Warning: No OpenRouter API key found. Using mock responses.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """Invoke the LLM with a prompt"""
        if self.use_mock:
            return self._mock_response(prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000)
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            return self._mock_response(prompt)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Alternative method name for compatibility"""
        return self.invoke(prompt, **kwargs)
    
    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.invoke(prompt, **kwargs)
    
    def _mock_response(self, prompt: str) -> str:
        """Generate mock response when API is unavailable"""
        if "cost estimate" in prompt.lower():
            return """Based on typical construction costs:
- Material costs: $2,000-5,000
- Labor costs: $1,500-3,500
- Total estimated range: $3,500-8,500
Note: Actual costs vary by location and specific requirements."""
        
        elif "building code" in prompt.lower():
            return """Common building code requirements:
- Permits required for structural work
- Electrical work must meet NEC standards
- Plumbing must comply with local codes
- Inspections required at key milestones
Consult local building department for specific requirements."""
        
        elif "property" in prompt.lower() and "condition" in prompt.lower():
            return """Property condition assessment indicates:
- Overall condition appears fair to good
- Regular maintenance recommended
- Address any identified issues promptly
- Consider professional inspection for detailed evaluation"""
        
        else:
            return f"""Based on the available information, here's a comprehensive response to your query about property analysis. 

Key considerations include:
- Property condition and maintenance needs
- Market factors and location benefits
- Regulatory compliance requirements
- Cost-effective improvement strategies

For specific details, please consult with relevant professionals in your area."""

    def _load_env(self):
        """Load environment variables from .env file"""
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    def set_model(self, model: str):
        """Change the model being used"""
        if model in self.free_models:
            self.model = model
            print(f"Switched to model: {model}")
        else:
            print(f"Warning: {model} may not be free. Available free models: {self.free_models}")
            self.model = model