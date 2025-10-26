"""LLM Configuration for OpenRouter integration"""

# OpenRouter free models
FREE_MODELS = {
    "deepseek-chat": "deepseek/deepseek-chat",
    "gemma-2-9b": "google/gemma-2-9b-it:free", 
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instruct:free",
    "phi-3-mini": "microsoft/phi-3-mini-128k-instruct:free",
    "zephyr-7b": "huggingface/zephyr-7b-beta:free"
}

# Default model
DEFAULT_MODEL = "deepseek/deepseek-chat"

# Model parameters
MODEL_PARAMS = {
    "temperature": 0.7,
    "max_tokens": 1000,
    "timeout": 30
}

def get_model_name(model_key: str = "deepseek-chat") -> str:
    """Get full model name from key"""
    return FREE_MODELS.get(model_key, DEFAULT_MODEL)