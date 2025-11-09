"""Main entry point for the codebase analyzer CLI."""

import sys
import argparse
from pathlib import Path

from config import config
from analyzers import CodebaseAnalyzer


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze any codebase with AI-powered insights',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  python main.py
  
  # Analyze specific project
  python main.py --path ../SakilaProject
  
  # Analyze with specific language
  python main.py --path ../my-project --language python
  
  # Use specific LLM provider
  python main.py --path ../SakilaProject --provider ollama
  
  # Custom output location
  python main.py --path ../SakilaProject --output ./results/sakila_analysis.json
        """
    )
    
    parser.add_argument(
        '--path', '-p',
        type=str,
        default=None,
        help='Path to the codebase to analyze (default: from .env or current directory)'
    )
    
    parser.add_argument(
        '--language', '-l',
        type=str,
        choices=['auto', 'java', 'python', 'javascript', 'go', 'ruby', 'php', 'csharp'],
        default=None,
        help='Target language (default: auto-detect)'
    )
    
    parser.add_argument(
        '--provider',
        type=str,
        choices=['openai', 'anthropic', 'ollama'],
        default=None,
        help='LLM provider to use (default: from .env)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file path (default: ./output/analysis_results.json)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Specific model to use (e.g., gpt-4, codellama, claude-3-sonnet)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Override config with command-line arguments
        if args.path:
            config.CODEBASE_PATH = Path(args.path)
        
        if args.language:
            config.TARGET_LANGUAGE = args.language
        
        if args.provider:
            config.LLM_PROVIDER = args.provider
        
        if args.output:
            config.OUTPUT_PATH = Path(args.output)
        
        if args.model:
            if config.LLM_PROVIDER == "openai":
                config.OPENAI_MODEL = args.model
            elif config.LLM_PROVIDER == "anthropic":
                config.ANTHROPIC_MODEL = args.model
            elif config.LLM_PROVIDER == "ollama":
                config.OLLAMA_MODEL = args.model
        
        # Run the analyzer
        analyzer = CodebaseAnalyzer()
        analyzer.run()
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


