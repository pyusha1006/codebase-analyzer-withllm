"""Output formatting and saving for analysis results."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any

from models import CodebaseAnalysis
from config import config


class OutputFormatter:
    """Handles formatting and saving of analysis results."""
    
    @staticmethod
    def save(analysis: CodebaseAnalysis, output_path: Path = None):
        """Save analysis results to JSON file.
        
        Args:
            analysis: The complete codebase analysis
            output_path: Path to save the output (defaults to config.OUTPUT_PATH)
        """
        if output_path is None:
            output_path = config.OUTPUT_PATH
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and add metadata
        result = analysis.model_dump()
        result['metadata'] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "llm_provider": config.LLM_PROVIDER,
            "llm_model": (
                config.OPENAI_MODEL if config.LLM_PROVIDER == "openai" 
                else config.ANTHROPIC_MODEL if config.LLM_PROVIDER == "anthropic"
                else config.OLLAMA_MODEL
            )
        }
        
        # Convert any sets to lists for JSON serialization
        result = OutputFormatter._convert_sets_to_lists(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def _convert_sets_to_lists(obj: Any) -> Any:
        """Recursively convert sets to lists for JSON serialization.
        
        Args:
            obj: Object to convert
            
        Returns:
            Object with sets converted to lists
        """
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: OutputFormatter._convert_sets_to_lists(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [OutputFormatter._convert_sets_to_lists(item) for item in obj]
        else:
            return obj

