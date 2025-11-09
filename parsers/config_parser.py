"""Parser for configuration files (XML, properties, etc.)."""

from pathlib import Path
from typing import Dict, Any


class ConfigFileParser:
    """Parser for configuration files (XML, properties, etc.)."""
    
    @staticmethod
    def parse_pom(file_path: Path) -> Dict[str, Any]:
        """Extract information from pom.xml."""
        import re
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            dependencies = re.findall(r'<artifactId>(.*?)</artifactId>', content)
            version = re.search(r'<version>(.*?)</version>', content)
            
            return {
                "dependencies": list(set(dependencies)),
                "version": version.group(1) if version else None
            }
        except Exception:
            return {}
    
    @staticmethod
    def parse_properties(file_path: Path) -> Dict[str, str]:
        """Parse application.properties file."""
        try:
            properties = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        properties[key.strip()] = value.strip()
            return properties
        except Exception:
            return {}

