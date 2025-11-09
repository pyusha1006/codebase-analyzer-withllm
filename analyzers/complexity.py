"""Complexity analysis for codebases."""

from typing import List, Dict, Any, Optional
from models import FileInfo


class ComplexityAnalyzer:
    """Analyzes code complexity metrics with LLM-powered interpretation."""
    
    def __init__(self, llm_analyzer=None):
        """Initialize the complexity analyzer.
        
        Args:
            llm_analyzer: Optional LLM analyzer for intelligent interpretation
        """
        self.llm_analyzer = llm_analyzer
    
    def analyze(self, files: List[FileInfo], project_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze code complexity across files with intelligent interpretation.
        
        Args:
            files: List of parsed file information
            project_info: Optional project information for context
            
        Returns:
            Dictionary containing complexity metrics and interpretation
        """
        complexities = [f.complexity for f in files if f.complexity]
        
        if not complexities:
            return {"message": "No complexity data available"}
        
        # Calculate metrics
        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)
        min_complexity = min(complexities)
        high_complexity_files = [
            f.file_path for f in files 
            if f.complexity and f.complexity > 10
        ]
        
        metrics = {
            "average_complexity": avg_complexity,
            "max_complexity": max_complexity,
            "min_complexity": min_complexity,
            "high_complexity_files": high_complexity_files
        }
        
        # Add LLM-powered interpretation if available
        if self.llm_analyzer:
            interpretation = self._get_llm_interpretation(metrics, project_info)
            if interpretation:
                metrics["interpretation"] = interpretation
        
        return metrics
    
    def _get_llm_interpretation(self, metrics: Dict[str, Any], project_info: Optional[Dict[str, Any]]) -> Optional[str]:
        """Get LLM interpretation of complexity metrics.
        
        Args:
            metrics: Calculated complexity metrics
            project_info: Project information for context
            
        Returns:
            Intelligent interpretation or None if LLM call fails
        """
        try:
            context = f"""
Project Type: {project_info.get('frameworks', ['Unknown'])[0] if project_info else 'Unknown'}
Language: {project_info.get('language', 'Unknown') if project_info else 'Unknown'}

Complexity Metrics:
- Average Complexity: {metrics['average_complexity']:.2f}
- Maximum Complexity: {metrics['max_complexity']}
- Minimum Complexity: {metrics['min_complexity']}
- High Complexity Files (>10): {len(metrics['high_complexity_files'])}
"""
            
            prompt = f"""{context}

Analyze these complexity metrics and provide:
1. Overall assessment (is this good/bad/acceptable for this type of project?)
2. What the numbers indicate about code maintainability
3. Specific recommendations for improvement (if needed)

Keep response to 2-3 sentences, actionable and specific."""

            response = self.llm_analyzer._query_llm(
                system_prompt="You are a code quality expert analyzing complexity metrics.",
                user_prompt=prompt,
                max_tokens=200
            )
            
            return response.strip() if response else None
            
        except Exception as e:
            # Fail gracefully - return metrics without interpretation
            return None

