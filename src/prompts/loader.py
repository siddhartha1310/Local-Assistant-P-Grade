import os
import yaml
from loguru import logger
from typing import Dict, List, Optional
from src.prompts.models import PromptTemplate

class PromptLoader:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self.prompts: Dict[str, PromptTemplate] = {}

    def load_all(self) -> Dict[str, PromptTemplate]:
        """Loads all YAML prompt templates from the directory."""
        if not os.path.exists(self.prompts_dir):
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            return {}

        new_prompts = {}
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                file_path = os.path.join(self.prompts_dir, filename)
                try:
                    prompt = self.load_file(file_path)
                    if prompt:
                        new_prompts[prompt.id] = prompt
                except Exception as e:
                    logger.error(f"Failed to load prompt from {filename}: {e}")
        
        self.prompts = new_prompts
        logger.info(f"Loaded {len(self.prompts)} prompt templates.")
        return self.prompts

    def load_file(self, file_path: str) -> Optional[PromptTemplate]:
        """Loads a single prompt template from a YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        if not data or 'id' not in data or 'template' not in data:
            logger.warning(f"Invalid prompt format in {file_path}")
            return None
            
        return PromptTemplate(
            id=data['id'],
            version=str(data.get('version', '1.0.0')),
            description=data.get('description', ''),
            template=data['template'],
            filename=os.path.basename(file_path),
            metadata=data.get('metadata', {})
        )

    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        return self.prompts.get(prompt_id)

    def list_prompts(self) -> List[dict]:
        return [
            {"id": p.id, "version": p.version, "description": p.description}
            for p in self.prompts.values()
        ]

# Global loader instance
prompt_loader = PromptLoader()
