import os
import yaml
from dotenv import load_dotenv
from config.settings import Settings

load_dotenv()
settings = Settings()

def load_yaml(filepath):
    """Loads a YAML file given a relative path from the project root."""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_path, filepath)
    if not os.path.exists(path):
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

def load_responses():
    """Load response templates from responses.yaml."""
    return load_yaml("src/config/responses.yaml")

# Load resources once at module level
PROMPTS = load_prompts()
RESPONSES = load_responses()

# Model configuration from settings
REASONING_MODEL_ID = settings.reasoning_model
REASONING_MODEL_TEMP = settings.reasoning_temperature
FAST_MODEL_ID = settings.fast_model
FAST_MODEL_TEMP = settings.fast_temperature

def get_provider():
    return settings.llm_provider

def get_base_url():
    return settings.llm_base_url
