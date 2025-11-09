"""Language detection for codebases."""

from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter
from config import config


class LanguageDetector:
    """Detects the primary programming language of a codebase."""
    
    LANGUAGE_EXTENSIONS = {
        ".java": "java",
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "javascript",
        ".tsx": "javascript",
        ".go": "go",
        ".rb": "ruby",
        ".cs": "csharp",
        ".php": "php",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".rs": "rust",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala"
    }
    
    CONFIG_FILE_INDICATORS = {
        "pom.xml": "java",
        "build.gradle": "java",
        "package.json": "javascript",
        "requirements.txt": "python",
        "setup.py": "python",
        "pyproject.toml": "python",
        "go.mod": "go",
        "Gemfile": "ruby",
        "composer.json": "php",
        "Cargo.toml": "rust"
    }
    
    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path
    
    def detect_language(self) -> str:
        """Detect the primary language of the codebase."""
        # Check for config file indicators first
        config_language = self._check_config_files()
        if config_language:
            return config_language
        
        # Count files by extension
        language_counts = self._count_files_by_language()
        
        if not language_counts:
            return "unknown"
        
        # Return the most common language
        return language_counts.most_common(1)[0][0]
    
    def _check_config_files(self) -> Optional[str]:
        """Check for language-specific configuration files."""
        for config_file, language in self.CONFIG_FILE_INDICATORS.items():
            matches = list(self.codebase_path.rglob(config_file))
            if matches:
                return language
        return None
    
    def _count_files_by_language(self) -> Counter:
        """Count source files by detected language."""
        language_counts = Counter()
        
        # Search for source files
        for ext, language in self.LANGUAGE_EXTENSIONS.items():
            pattern = f"**/*{ext}"
            files = list(self.codebase_path.rglob(pattern))
            
            # Filter out excluded directories
            filtered_files = [
                f for f in files
                if not any(excluded in str(f) for excluded in [
                    'node_modules', 'venv', 'env', 'target', 'build',
                    'dist', '.git', '__pycache__', 'vendor'
                ])
            ]
            
            if filtered_files:
                language_counts[language] += len(filtered_files)
        
        return language_counts
    
    def get_file_patterns(self, language: str) -> List[str]:
        """Get file patterns for a specific language."""
        if language in config.LANGUAGE_PATTERNS:
            patterns = config.LANGUAGE_PATTERNS[language]["extensions"]
            patterns.extend(config.LANGUAGE_PATTERNS[language]["config_files"])
            patterns.append("**/README.md")
            patterns.append("**/readme.md")
            patterns.append("**/README.rst")
            patterns.append("**/LICENSE")
            return patterns
        return ["**/*"]
    
    def detect_project_info(self) -> Dict[str, any]:
        """Detect project type and framework information."""
        info = {
            "language": self.detect_language(),
            "frameworks": [],
            "build_tools": [],
            "package_manager": None
        }
        
        # Detect frameworks and tools
        if (self.codebase_path / "pom.xml").exists():
            info["build_tools"].append("Maven")
            # Check for Spring Boot
            pom_content = (self.codebase_path / "pom.xml").read_text()
            if "spring-boot" in pom_content.lower():
                info["frameworks"].append("Spring Boot")
        
        if (self.codebase_path / "build.gradle").exists():
            info["build_tools"].append("Gradle")
        
        if (self.codebase_path / "package.json").exists():
            info["package_manager"] = "npm/yarn"
            package_json = (self.codebase_path / "package.json").read_text()
            if "react" in package_json.lower():
                info["frameworks"].append("React")
            if "vue" in package_json.lower():
                info["frameworks"].append("Vue")
            if "angular" in package_json.lower():
                info["frameworks"].append("Angular")
            if "express" in package_json.lower():
                info["frameworks"].append("Express")
            if "next" in package_json.lower():
                info["frameworks"].append("Next.js")
        
        if (self.codebase_path / "requirements.txt").exists():
            info["package_manager"] = "pip"
            reqs = (self.codebase_path / "requirements.txt").read_text()
            if "django" in reqs.lower():
                info["frameworks"].append("Django")
            if "flask" in reqs.lower():
                info["frameworks"].append("Flask")
            if "fastapi" in reqs.lower():
                info["frameworks"].append("FastAPI")
        
        if (self.codebase_path / "go.mod").exists():
            info["package_manager"] = "go modules"
        
        if (self.codebase_path / "Gemfile").exists():
            info["package_manager"] = "Bundler"
            gemfile = (self.codebase_path / "Gemfile").read_text()
            if "rails" in gemfile.lower():
                info["frameworks"].append("Ruby on Rails")
        
        return info
    
    def get_project_name(self) -> str:
        """Extract project name from codebase."""
        import json
        import re
        
        # Try package.json
        package_json = self.codebase_path / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if "name" in data:
                    return data["name"]
            except Exception:
                pass
        
        # Try pom.xml
        pom_xml = self.codebase_path / "pom.xml"
        if pom_xml.exists():
            try:
                content = pom_xml.read_text()
                match = re.search(r'<artifactId>(.*?)</artifactId>', content)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Try setup.py
        setup_py = self.codebase_path / "setup.py"
        if setup_py.exists():
            try:
                content = setup_py.read_text()
                match = re.search(r'name=["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
            except Exception:
                pass
        
        # Fallback to directory name
        return self.codebase_path.name

