import os
import yaml
from dotenv import load_dotenv

load_dotenv()

def load_yaml(filepath):
    """Loads a YAML file given a relative path from the project root."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Project Root
    path = os.path.join(base_path, filepath)
    if not os.path.exists(path):
        # Fallback for old core-relative paths if needed, or error logging
        print(f"Warning: Config file not found at {path}")
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_prompts():
    """Aggregates split prompt files into a single dictionary."""
    prompts = {}
    stages = ["safety", "planner", "interviewer", "analyst"]
    for stage in stages:
        prompts[stage] = load_yaml(f"src/config/prompts/{stage}.yaml")
    return prompts

# Load resources once at module level
PROMPTS = load_prompts()
MODELS_CONFIG = load_yaml("src/config/models.yaml")

def get_models_config():
    global MODELS_CONFIG
    if not MODELS_CONFIG:
        MODELS_CONFIG = load_yaml("src/config/models.yaml")
    return MODELS_CONFIG

# Model Accessors
def get_model_id(model_type="reasoning"):
    return get_models_config().get("models", {}).get(model_type, "llama3")

REASONING_MODEL_ID = get_model_id("reasoning")
FAST_MODEL_ID = get_model_id("fast")

def get_provider():
    return get_models_config().get("provider", "ollama")

def get_base_url():
    return get_models_config().get("base_url", "http://localhost:11434")
