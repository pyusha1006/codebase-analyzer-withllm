"""Method extraction for key business logic."""

from typing import List, Dict
from rich.console import Console

from models import FileInfo, KeyMethodSummary


class MethodExtractor:
    """Extracts key business logic methods from files."""
    
    def __init__(self, llm_analyzer, console: Console = None):
        """Initialize the method extractor.
        
        Args:
            llm_analyzer: LLM analyzer for generating descriptions
            console: Rich console for display output
        """
        self.llm_analyzer = llm_analyzer
        self.console = console or Console()
    
    def extract(self, 
                files: List[FileInfo],
                key_components: Dict[str, List[str]]) -> List[KeyMethodSummary]:
        """Extract key business logic methods for summary.
        
        Args:
            files: List of parsed file information
            key_components: Dictionary of identified key components
            
        Returns:
            List of key method summaries with descriptions
        """
        key_methods = []
        
        # Create a component type mapping
        component_type_map = {}
        for comp_type, class_names in key_components.items():
            for class_name in class_names:
                component_type_map[class_name] = comp_type
        
        self.console.print("  Generating method descriptions using LLM...")
        
        for file in files:
            for cls in file.classes:
                component_type = component_type_map.get(cls.name)
                
                # Only include methods from key components (controllers, services)
                if component_type not in ['controllers', 'services']:
                    continue
                
                for method in cls.methods:
                    # Only include business logic methods
                    if not method.is_business_logic:
                        continue
                    
                    # Generate description using LLM
                    try:
                        description = self.llm_analyzer.generate_method_description(
                            method.signature,
                            cls.name,
                            method.annotations
                        )
                    except Exception as e:
                        self.console.print(
                            f"  [yellow]Warning: Could not generate description for "
                            f"{cls.name}.{method.name}[/yellow]"
                        )
                        description = None
                    
                    key_methods.append(KeyMethodSummary(
                        class_name=cls.name,
                        method_name=method.name,
                        signature=method.signature,
                        description=description,
                        annotations=method.annotations,
                        component_type=component_type
                    ))
        
        return key_methods

