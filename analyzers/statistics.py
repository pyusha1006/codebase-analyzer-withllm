"""Statistics analysis for codebases."""

from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table

from models import FileInfo


class StatisticsAnalyzer:
    """Analyzes and displays codebase statistics."""
    
    def __init__(self, console: Console = None):
        """Initialize the statistics analyzer.
        
        Args:
            console: Rich console for display output. If None, creates a new one.
        """
        self.console = console or Console()
    
    def calculate(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Calculate codebase statistics.
        
        Args:
            files: List of parsed file information
            
        Returns:
            Dictionary containing statistics metrics
        """
        total_files = len(files)
        total_lines = sum(f.total_lines for f in files)
        total_code_lines = sum(f.code_lines for f in files)
        total_classes = sum(len(f.classes) for f in files)
        
        # Count only business logic methods
        total_methods = sum(
            sum(1 for m in c.methods if m.is_business_logic)
            for f in files for c in f.classes
        )
        
        # File type distribution
        file_types = {}
        for file in files:
            file_types[file.file_type] = file_types.get(file.file_type, 0) + 1
        
        return {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_code_lines": total_code_lines,
            "total_classes": total_classes,
            "total_methods": total_methods,
            "file_types": file_types,
            "average_file_size": total_lines // total_files if total_files > 0 else 0,
            "average_methods_per_class": total_methods // total_classes if total_classes > 0 else 0
        }
    
    def display(self, stats: Dict[str, Any]):
        """Display statistics in a nice table.
        
        Args:
            stats: Statistics dictionary from calculate()
        """
        table = Table(title="Codebase Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Files", str(stats['total_files']))
        table.add_row("Total Lines", str(stats['total_lines']))
        table.add_row("Code Lines", str(stats['total_code_lines']))
        table.add_row("Total Classes", str(stats['total_classes']))
        table.add_row("Business Logic Methods", str(stats['total_methods']))
        table.add_row("Avg File Size", str(stats['average_file_size']))
        table.add_row("Avg Methods/Class", str(stats['average_methods_per_class']))
        
        self.console.print(table)

