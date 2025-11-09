"""Component identification for codebases."""

from typing import List, Dict
from models import FileInfo


class ComponentAnalyzer:
    """Identifies key components in a codebase (controllers, services, etc.)."""
    
    def identify(self, files: List[FileInfo]) -> Dict[str, List[str]]:
        """Identify key components in the codebase.
        
        Args:
            files: List of parsed file information
            
        Returns:
            Dictionary mapping component types to class names
        """
        components = {
            "controllers": [],
            "services": [],
            "repositories": [],
            "entities": [],
            "configurations": []
        }
        
        for file in files:
            for cls in file.classes:
                class_name = cls.name
                
                # Identify by naming conventions and annotations
                if "Controller" in class_name or "Controller" in cls.annotations:
                    components["controllers"].append(class_name)
                elif "Service" in class_name or "Service" in cls.annotations:
                    components["services"].append(class_name)
                elif "Repository" in class_name or "Repository" in cls.annotations:
                    components["repositories"].append(class_name)
                elif "Entity" in cls.annotations or (file.package and "entities" in file.package):
                    components["entities"].append(class_name)
                elif "Configuration" in cls.annotations or "Config" in class_name:
                    components["configurations"].append(class_name)
        
        return components

