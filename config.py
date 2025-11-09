"""Configuration management for the code analyzer."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the code analyzer."""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Updated to current model
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "codellama")
    
    # Analysis Configuration
    MAX_TOKENS_PER_CHUNK: int = int(os.getenv("MAX_TOKENS_PER_CHUNK", "8000"))
    CODEBASE_PATH: Path = Path(os.getenv("CODEBASE_PATH", "."))
    OUTPUT_PATH: Path = Path(os.getenv("OUTPUT_PATH", "./output/analysis_results.json"))
    
    # Auto-detect language or specify manually
    TARGET_LANGUAGE: str = os.getenv("TARGET_LANGUAGE", "auto")  # auto, java, python, javascript, go, etc.
    
    # File patterns to include (auto-populated based on detected language)
    INCLUDE_PATTERNS = os.getenv("INCLUDE_PATTERNS", "").split(",") if os.getenv("INCLUDE_PATTERNS") else []
    
    # File patterns to exclude (common across all languages)
    EXCLUDE_PATTERNS = [
        "**/target/**",
        "**/build/**",
        "**/dist/**",
        "**/.git/**",
        "**/.idea/**",
        "**/.vscode/**",
        "**/node_modules/**",
        "**/venv/**",
        "**/env/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.class",
        "**/*.jar",
        "**/*.war",
        "**/*.min.js",
        "**/*.min.css",
        "**/vendor/**",
        "**/coverage/**"
    ]
    
    # Language-specific patterns (auto-selected based on TARGET_LANGUAGE)
    LANGUAGE_PATTERNS = {
        "java": {
            "extensions": ["**/*.java"],
            "config_files": ["**/pom.xml", "**/build.gradle", "**/settings.gradle"],
            "parser": "java"
        },
        "python": {
            "extensions": ["**/*.py"],
            "config_files": ["**/requirements.txt", "**/setup.py", "**/pyproject.toml", "**/Pipfile"],
            "parser": "python"
        },
        "javascript": {
            "extensions": ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
            "config_files": ["**/package.json", "**/tsconfig.json", "**/.babelrc"],
            "parser": "javascript"
        },
        "go": {
            "extensions": ["**/*.go"],
            "config_files": ["**/go.mod", "**/go.sum"],
            "parser": "go"
        },
        "ruby": {
            "extensions": ["**/*.rb"],
            "config_files": ["**/Gemfile", "**/Rakefile"],
            "parser": "ruby"
        },
        "csharp": {
            "extensions": ["**/*.cs"],
            "config_files": ["**/*.csproj", "**/*.sln"],
            "parser": "csharp"
        },
        "php": {
            "extensions": ["**/*.php"],
            "config_files": ["**/composer.json"],
            "parser": "php"
        }
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI")
        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic")
        if not cls.CODEBASE_PATH.exists():
            raise ValueError(f"Codebase path does not exist: {cls.CODEBASE_PATH}")


config = Config()


