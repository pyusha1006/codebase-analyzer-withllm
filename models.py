"""Data models for structured code analysis output.

These Pydantic models define the schema for the JSON output,
providing type safety, validation, and documentation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MethodInfo(BaseModel):
    """Information about a method or function."""
    
    name: str = Field(description="Method name")
    signature: str = Field(description="Full method signature")
    description: Optional[str] = Field(None, description="AI-generated description")
    return_type: Optional[str] = Field(None, description="Return type if available")
    complexity: Optional[float] = Field(None, description="Cyclomatic complexity")
    annotations: List[str] = Field(default_factory=list, description="Method annotations/decorators")
    is_business_logic: bool = Field(True, description="Whether this is business logic (not getter/setter)")


class ClassInfo(BaseModel):
    """Information about a class (used internally during parsing)."""
    
    name: str
    package: Optional[str] = None
    description: Optional[str] = None
    annotations: List[str] = Field(default_factory=list)
    methods: List[MethodInfo] = Field(default_factory=list)


class FileInfo(BaseModel):
    """Information about a source file (used internally during parsing)."""
    
    file_path: str
    file_type: str
    package: Optional[str] = None
    imports: List[str] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    complexity: Optional[float] = None


class ProjectOverview(BaseModel):
    """High-level project overview."""
    
    project_name: str
    description: str
    purpose: str
    key_technologies: List[str] = Field(default_factory=list)
    architecture_pattern: Optional[str] = None
    main_features: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class KeyMethodSummary(BaseModel):
    """Summary of a key business logic method (appears in final output)."""
    
    class_name: str = Field(description="Name of the containing class")
    method_name: str = Field(description="Name of the method")
    signature: str = Field(description="Full method signature")
    description: Optional[str] = Field(None, description="AI-generated method description")
    annotations: List[str] = Field(default_factory=list, description="Method annotations")
    component_type: Optional[str] = Field(None, description="Component type (controller, service, entity, etc.)")


class CodebaseAnalysis(BaseModel):
    """Complete codebase analysis result (final JSON output)."""
    
    overview: ProjectOverview = Field(description="High-level project overview")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="Code statistics")
    key_methods: List[KeyMethodSummary] = Field(default_factory=list, description="Key business logic methods")
    key_components: Dict[str, List[str]] = Field(default_factory=dict, description="Component breakdown")
    complexity_summary: Dict[str, Any] = Field(default_factory=dict, description="Complexity metrics")
    recommendations: List[str] = Field(default_factory=list, description="Analysis recommendations")
    noteworthy_aspects: List[str] = Field(default_factory=list, description="Notable aspects")


