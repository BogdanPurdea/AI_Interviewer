import os
import json
from datetime import datetime
from config.settings import Settings

settings = Settings()

class StorageService:
    @staticmethod
    def save_interview(topic: str, transcript: list, analysis: dict) -> str:
        """Saves the interview transcript and analysis to a JSON file."""
        os.makedirs(settings.interviews_dir, exist_ok=True)
        filename = f"{settings.interviews_dir}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{topic.replace(' ', '_')}.json"
        
        data = {
            "topic": topic,
            "transcript": transcript,
            "analysis": analysis
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
            
        return filename
