"""Main orchestrator for codebase analysis."""

import sys
from pathlib import Path
from typing import List, Dict, Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import config
from models import FileInfo, ProjectOverview, CodebaseAnalysis
from parsers import JavaCodeParser, ConfigFileParser
from llm import LLMAnalyzer
from detectors import LanguageDetector
from .statistics import StatisticsAnalyzer
from .components import ComponentAnalyzer
from .complexity import ComplexityAnalyzer
from .aspects import AspectAnalyzer
from utils import MethodExtractor, OutputFormatter


class CodebaseAnalyzer:
    """Main codebase analyzer orchestrator."""
    
    def __init__(self):
        """Initialize the analyzer with all required components."""
        self.console = Console()
        self.java_parser = JavaCodeParser()
        self.config_parser = ConfigFileParser()
        self.llm_analyzer = LLMAnalyzer()
        self.language_detector = LanguageDetector(config.CODEBASE_PATH)
        
        # Initialize analyzers (pass LLM analyzer for intelligent analysis)
        self.stats_analyzer = StatisticsAnalyzer(self.console)
        self.component_analyzer = ComponentAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer(self.llm_analyzer)
        self.aspect_analyzer = AspectAnalyzer(self.llm_analyzer)
        self.method_extractor = MethodExtractor(self.llm_analyzer, self.console)
        
        self.detected_language = None
        self.project_info = None
    
    def run(self) -> CodebaseAnalysis:
        """Run the complete analysis pipeline.
        
        Returns:
            Complete codebase analysis
        """
        try:
            config.validate()
            self.console.print("[bold green]Starting Codebase Analysis...[/bold green]")
            
            # Step 0: Detect language and project info
            self.console.print("\n[bold]Step 0: Detecting project language and type...[/bold]")
            self._detect_language()
            
            # Step 1: Discover and parse files
            self.console.print("\n[bold]Step 1: Discovering and parsing files...[/bold]")
            files = self._discover_and_parse_files()
            self.console.print(f"✓ Parsed {len(files)} files")
            
            # Step 2: Extract project overview
            self.console.print("\n[bold]Step 2: Analyzing project overview with LLM...[/bold]")
            overview = self._analyze_overview()
            self.console.print(f"✓ Project: {overview.project_name}")
            
            # Step 3: Calculate statistics
            self.console.print("\n[bold]Step 3: Calculating statistics...[/bold]")
            statistics = self.stats_analyzer.calculate(files)
            self.stats_analyzer.display(statistics)
            
            # Step 4: Identify key components
            self.console.print("\n[bold]Step 4: Identifying key components...[/bold]")
            key_components = self.component_analyzer.identify(files)
            
            # Step 5: Extract key methods
            self.console.print("\n[bold]Step 5: Extracting key business logic methods...[/bold]")
            key_methods = self.method_extractor.extract(files, key_components)
            
            # Step 6: Analyze complexity (with LLM interpretation)
            self.console.print("\n[bold]Step 6: Analyzing code complexity...[/bold]")
            complexity_summary = self.complexity_analyzer.analyze(files, self.project_info)
            
            # Step 7: Identify noteworthy aspects (with LLM insights)
            self.console.print("\n[bold]Step 7: Identifying noteworthy aspects...[/bold]")
            noteworthy_aspects = self.aspect_analyzer.identify(
                statistics, complexity_summary, key_components, self.project_info
            )
            
            # Step 8: Generate recommendations
            self.console.print("\n[bold]Step 8: Generating recommendations...[/bold]")
            recommendations = self._generate_recommendations(files, statistics)
            
            # Step 9: Build final analysis
            analysis = CodebaseAnalysis(
                overview=overview,
                statistics=statistics,
                key_methods=key_methods,
                key_components=key_components,
                complexity_summary=complexity_summary,
                recommendations=recommendations,
                noteworthy_aspects=noteworthy_aspects
            )
            
            # Step 10: Save results
            OutputFormatter.save(analysis)
            
            self.console.print("\n[bold green]✓ Analysis complete![/bold green]")
            self.console.print(f"Results saved to: {config.OUTPUT_PATH}")
            
            return analysis
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Analysis interrupted by user[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[bold red]Error: {e}[/bold red]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
            sys.exit(1)
    
    def _detect_language(self):
        """Detect project language and frameworks."""
        if config.TARGET_LANGUAGE == "auto":
            self.detected_language = self.language_detector.detect_language()
        else:
            self.detected_language = config.TARGET_LANGUAGE
        
        self.project_info = self.language_detector.detect_project_info()
        self.console.print(f"✓ Detected language: {self.detected_language}")
        if self.project_info.get("frameworks"):
            self.console.print(f"✓ Frameworks: {', '.join(self.project_info['frameworks'])}")
    
    def _discover_and_parse_files(self) -> List[FileInfo]:
        """Discover and parse all relevant files in the codebase.
        
        Returns:
            List of parsed files
        """
        files = []
        codebase_path = config.CODEBASE_PATH
        
        # Get file patterns for detected language
        file_patterns = self.language_detector.get_file_patterns(self.detected_language)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Parsing files...", total=None)
            
            # Find all source files based on detected language
            all_files = []
            for pattern in file_patterns:
                if pattern.endswith(('.java', '.py', '.js', '.ts', '.go', '.rb', '.cs', '.php')):
                    all_files.extend(list(codebase_path.glob(pattern)))
            
            for source_file in all_files:
                # Skip excluded patterns
                if any(excluded.strip('*') in str(source_file) for excluded in config.EXCLUDE_PATTERNS):
                    continue
                
                # Parse based on file type
                file_info = None
                if source_file.suffix == '.java' and self.detected_language == 'java':
                    file_info = self.java_parser.parse_file(source_file)
                elif source_file.suffix == '.py' and self.detected_language == 'python':
                    file_info = self._create_generic_file_info(source_file, 'python')
                elif source_file.suffix in ['.js', '.ts', '.jsx', '.tsx'] and self.detected_language == 'javascript':
                    file_info = self._create_generic_file_info(source_file, 'javascript')
                else:
                    file_info = self._create_generic_file_info(source_file, self.detected_language)
                
                if file_info:
                    files.append(file_info)
                    progress.update(task, description=f"Parsing {source_file.name}...")
        
        return files
    
    def _create_generic_file_info(self, file_path: Path, language: str) -> FileInfo:
        """Create basic file info for non-Java files.
        
        Args:
            file_path: Path to the file
            language: Programming language
            
        Returns:
            Basic file information or None if read fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            return FileInfo(
                file_path=str(file_path),
                file_type=language,
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=total_lines - code_lines
            )
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
            return None
    
    def _analyze_overview(self) -> ProjectOverview:
        """Analyze project overview using LLM.
        
        Returns:
            Project overview with metadata
        """
        codebase_path = config.CODEBASE_PATH
        
        # Get project name from detector
        project_name = self.language_detector.get_project_name()
        
        # Read README (try multiple variations)
        readme_content = ""
        for readme_name in ["README.md", "readme.md", "README.rst", "README.txt", "README"]:
            readme_path = codebase_path / readme_name
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                break
        
        # Read config files based on detected language
        config_content = ""
        config_data = {}
        
        if self.detected_language == "java":
            pom_path = codebase_path / "pom.xml"
            if pom_path.exists():
                with open(pom_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
                config_data = self.config_parser.parse_pom(pom_path)
        elif self.detected_language == "python":
            req_path = codebase_path / "requirements.txt"
            if req_path.exists():
                with open(req_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
        elif self.detected_language == "javascript":
            pkg_path = codebase_path / "package.json"
            if pkg_path.exists():
                with open(pkg_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()
        
        # Get file structure
        file_structure = []
        patterns = self.language_detector.get_file_patterns(self.detected_language)
        for pattern in patterns[:3]:  # First 3 patterns (main extensions)
            if pattern.endswith(('.java', '.py', '.js', '.ts', '.go', '.rb', '.cs', '.php')):
                for path in codebase_path.glob(pattern):
                    if not any(excl.strip('*') in str(path) for excl in config.EXCLUDE_PATTERNS):
                        try:
                            rel_path = path.relative_to(codebase_path)
                            file_structure.append(str(rel_path))
                        except ValueError:
                            pass
        
        # Analyze with LLM
        overview_data = self.llm_analyzer.analyze_project_overview(
            readme_content, config_content, file_structure,
            language=self.detected_language,
            frameworks=self.project_info.get('frameworks', [])
        )
        
        # Prepare dependencies list
        dependencies = []
        if 'dependencies' in config_data:
            dependencies = config_data['dependencies'][:20]
        elif self.project_info.get('frameworks'):
            dependencies = self.project_info['frameworks']
        
        # Create ProjectOverview with fallback values
        return ProjectOverview(
            project_name=overview_data.get('project_name', project_name),
            description=overview_data.get('description', f'{self.detected_language.title()} project'),
            purpose=overview_data.get('purpose', f'Software project written in {self.detected_language}'),
            key_technologies=overview_data.get('key_technologies', 
                                              [self.detected_language.title()] + self.project_info.get('frameworks', [])),
            architecture_pattern=overview_data.get('architecture_pattern', 'Unknown'),
            main_features=overview_data.get('main_features', []),
            dependencies=dependencies
        )
    
    def _generate_recommendations(self, files: List[FileInfo], statistics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations using LLM.
        
        Args:
            files: List of parsed files
            statistics: Codebase statistics
            
        Returns:
            List of recommendation strings
        """
        summary = f"""
Project Statistics:
- Files: {statistics['total_files']}
- Classes: {statistics['total_classes']}
- Business Logic Methods: {statistics['total_methods']}
- Total Lines: {statistics['total_lines']}
- Average File Size: {statistics['average_file_size']} lines

Technology Stack: {', '.join(self.project_info.get('key_technologies', ['Spring Boot', 'Java']))}
"""
        
        return self.llm_analyzer.generate_recommendations(summary)

