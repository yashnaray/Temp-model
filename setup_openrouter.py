#!/usr/bin/env python3
"""Setup script for OpenRouter API integration"""

import os
import sys

def setup_openrouter():
    """Interactive setup for OpenRouter API"""
    print("OpenRouter Setup")
    print("=" * 20)
    print("\n1. Go to https://openrouter.ai")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print("4. Enter it below (or press Enter to skip)")
    
    api_key = input("\nEnter your OpenRouter API key: ").strip()
    
    if api_key:
        # Set environment variable for current session
        os.environ["OPENROUTER_API_KEY"] = api_key
        
        # Create .env file
        env_file = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_file, "w") as f:
            f.write(f"OPENROUTER_API_KEY={api_key}\n")
        
        print(f"\n✓ API key saved to {env_file}")
        print("✓ Environment variable set for current session")
        
        # Test the API
        try:
            from utils.openrouter_llm import OpenRouterLLM
            llm = OpenRouterLLM(api_key=api_key)
            response = llm.invoke("Hello, this is a test.")
            print("✓ API test successful!")
            print(f"Response: {response[:100]}...")
        except Exception as e:
            print(f"⚠ API test failed: {e}")
    else:
        print("\nSkipping API key setup. The system will use mock responses.")
    
    print("\nAvailable free models:")
    from config.llm_config import FREE_MODELS
    for key, model in FREE_MODELS.items():
        print(f"  - {key}: {model}")
    
    print("\nSetup complete! Run 'python app/main.py' to start the application.")

if __name__ == "__main__":
    setup_openrouter()