"""Noteworthy aspects identification for codebases."""

from typing import List, Dict, Any, Optional


class AspectAnalyzer:
    """Identifies noteworthy aspects of a codebase using LLM intelligence."""
    
    def __init__(self, llm_analyzer=None):
        """Initialize the aspect analyzer.
        
        Args:
            llm_analyzer: Optional LLM analyzer for intelligent insights
        """
        self.llm_analyzer = llm_analyzer
    
    def identify(self, 
                 statistics: Dict[str, Any],
                 complexity_summary: Dict[str, Any],
                 key_components: Dict[str, List[str]],
                 project_info: Optional[Dict[str, Any]] = None) -> List[str]:
        """Identify noteworthy aspects of the codebase using LLM.
        
        Args:
            statistics: Codebase statistics dictionary
            complexity_summary: Complexity analysis results
            key_components: Identified key components
            project_info: Optional project information for context
            
        Returns:
            List of noteworthy aspect descriptions
        """
        # Use LLM for intelligent insights if available
        if self.llm_analyzer:
            llm_aspects = self._get_llm_insights(statistics, complexity_summary, key_components, project_info)
            if llm_aspects:
                return llm_aspects
        
        # Fallback to rule-based analysis
        return self._rule_based_analysis(statistics, complexity_summary, key_components)
    
    def _get_llm_insights(self,
                          statistics: Dict[str, Any],
                          complexity_summary: Dict[str, Any],
                          key_components: Dict[str, List[str]],
                          project_info: Optional[Dict[str, Any]]) -> Optional[List[str]]:
        """Get LLM-powered insights about the codebase.
        
        Args:
            statistics: Codebase statistics
            complexity_summary: Complexity metrics
            key_components: Component categorization
            project_info: Project context
            
        Returns:
            List of intelligent insights or None if LLM call fails
        """
        try:
            context = f"""
Project Information:
- Type: {project_info.get('frameworks', ['Unknown'])[0] if project_info else 'Unknown'}
- Language: {project_info.get('language', 'Unknown') if project_info else 'Unknown'}

Statistics:
- Total Files: {statistics.get('total_files', 0)}
- Total Lines: {statistics.get('total_lines', 0)}
- Classes: {statistics.get('total_classes', 0)}
- Business Logic Methods: {statistics.get('total_methods', 0)}

Architecture:
- Controllers: {len(key_components.get('controllers', []))}
- Services: {len(key_components.get('services', []))}
- Repositories: {len(key_components.get('repositories', []))}
- Entities: {len(key_components.get('entities', []))}
- Configurations: {len(key_components.get('configurations', []))}

Complexity:
- Average: {complexity_summary.get('average_complexity', 0):.2f}
- Max: {complexity_summary.get('max_complexity', 0)}
- High Complexity Files: {len(complexity_summary.get('high_complexity_files', []))}

Key Classes:
{self._format_components(key_components)}
"""
            
            prompt = f"""{context}

Analyze this codebase and identify 5-7 noteworthy aspects. Focus on:
1. Architecture quality and patterns
2. Code organization and structure
3. Complexity and maintainability
4. Potential issues or smells
5. Best practices being followed
6. Areas for improvement

Provide each aspect as a concise, insightful observation (one sentence each).
Be specific and actionable, not generic."""

            response = self.llm_analyzer._query_llm(
                system_prompt="You are a software architect analyzing codebase quality and architecture.",
                user_prompt=prompt,
                max_tokens=400
            )
            
            if response:
                # Parse response into list of aspects
                aspects = [line.strip('- ').strip() for line in response.strip().split('\n') 
                          if line.strip() and not line.strip().startswith('#')]
                return [a for a in aspects if len(a) > 20]  # Filter out very short lines
            
            return None
            
        except Exception as e:
            # Fail gracefully - use rule-based fallback
            return None
    
    def _format_components(self, key_components: Dict[str, List[str]]) -> str:
        """Format components for LLM context.
        
        Args:
            key_components: Dictionary of component types and names
            
        Returns:
            Formatted string
        """
        lines = []
        for comp_type, names in key_components.items():
            if names and comp_type in ['controllers', 'services', 'configurations']:
                lines.append(f"- {comp_type.title()}: {', '.join(names[:5])}")
        return '\n'.join(lines) if lines else "No key components identified"
    
    def _rule_based_analysis(self,
                            statistics: Dict[str, Any],
                            complexity_summary: Dict[str, Any],
                            key_components: Dict[str, List[str]]) -> List[str]:
        """Fallback rule-based analysis when LLM is unavailable.
        
        Args:
            statistics: Codebase statistics
            complexity_summary: Complexity metrics
            key_components: Component categorization
            
        Returns:
            List of basic observations
        """
        aspects = []
        
        # Architecture observations
        if key_components.get('controllers') and key_components.get('services'):
            aspects.append(
                f"Well-structured MVC architecture with {len(key_components['controllers'])} "
                f"controllers and {len(key_components['services'])} services"
            )
        
        # Entity count
        if key_components.get('entities'):
            aspects.append(f"Data model contains {len(key_components['entities'])} entity classes")
        
        # Complexity analysis
        if 'average_complexity' in complexity_summary:
            avg_complexity = complexity_summary['average_complexity']
            if avg_complexity < 2:
                aspects.append(
                    f"Low code complexity (avg: {avg_complexity:.1f}) indicates maintainable code"
                )
            elif avg_complexity > 5:
                aspects.append(
                    f"High code complexity (avg: {avg_complexity:.1f}) may require refactoring"
                )
        
        # High complexity files
        if complexity_summary.get('high_complexity_files'):
            aspects.append(
                f"{len(complexity_summary['high_complexity_files'])} files with "
                f"high complexity (>10) need attention"
            )
        
        # Codebase size
        lines = statistics.get('total_lines', 0)
        if lines < 3000:
            aspects.append(f"Compact codebase ({lines} lines) - easy to navigate and understand")
        elif lines > 10000:
            aspects.append(f"Large codebase ({lines} lines) - consider modularization")
        
        # Method count vs class count
        methods = statistics.get('total_methods', 0)
        classes = statistics.get('total_classes', 1)
        avg_methods = methods / classes if classes > 0 else 0
        if avg_methods < 3:
            aspects.append(
                f"Classes have few business methods (avg: {avg_methods:.1f}) - "
                f"likely following single responsibility principle"
            )
        
        # Security configuration
        if 'WebSecurityConfig' in key_components.get('configurations', []):
            aspects.append("Spring Security configured for authentication and authorization")
        
        return aspects

