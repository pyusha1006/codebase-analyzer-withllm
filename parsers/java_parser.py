"""Code parsing utilities for Java source files."""

from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import javalang
except ImportError:
    javalang = None

try:
    import lizard
except ImportError:
    lizard = None

from models import FileInfo, ClassInfo, MethodInfo


class JavaCodeParser:
    """Parser for Java source code files."""
    
    def __init__(self):
        if not javalang:
            print("Warning: javalang not installed. Java parsing will be limited.")
        if not lizard:
            print("Warning: lizard not installed. Complexity analysis unavailable.")
    
    def parse_file(self, file_path: Path) -> Optional[FileInfo]:
        """Parse a Java file and extract structured information."""
        if not javalang:
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use javalang for AST parsing
            try:
                tree = javalang.parse.parse(content)
            except Exception as e:
                return self._create_basic_file_info(file_path, content)
            
            # Extract package and imports
            package_name = tree.package.name if tree.package else None
            imports = [imp.path for imp in tree.imports] if tree.imports else []
            
            # Extract classes
            classes = []
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_info = self._parse_class(node, package_name, content)
                classes.append(class_info)
            
            # Calculate complexity using lizard
            complexity_info = self._calculate_complexity(file_path)
            
            # Count lines
            lines = content.split('\n')
            total_lines = len(lines)
            code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('//'))
            comment_lines = total_lines - code_lines
            
            return FileInfo(
                file_path=str(file_path),
                file_type="java",
                package=package_name,
                imports=imports,
                classes=classes,
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                complexity=complexity_info.get('average_complexity', 0)
            )
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_class(self, node: javalang.tree.ClassDeclaration, 
                     package: Optional[str], content: str) -> ClassInfo:
        """Parse a class declaration."""
        # Extract annotations
        annotations = []
        if node.annotations:
            annotations = [ann.name for ann in node.annotations]
        
        # Extract methods
        methods = []
        if node.body:
            for member in node.body:
                if isinstance(member, javalang.tree.MethodDeclaration):
                    method_info = self._parse_method(member)
                    methods.append(method_info)
        
        return ClassInfo(
            name=node.name,
            package=package,
            annotations=annotations,
            methods=methods
        )
    
    def _parse_method(self, node: javalang.tree.MethodDeclaration) -> MethodInfo:
        """Parse a method declaration."""
        # Extract annotations
        annotations = []
        if node.annotations:
            annotations = [ann.name for ann in node.annotations]
        
        # Extract parameters
        parameters = []
        if node.parameters:
            for param in node.parameters:
                param_type = param.type.name if hasattr(param.type, 'name') else str(param.type)
                parameters.append({
                    "name": param.name,
                    "type": param_type
                })
        
        # Build signature
        params_str = ", ".join([f"{p['type']} {p['name']}" for p in parameters])
        return_type = node.return_type.name if node.return_type and hasattr(node.return_type, 'name') else "void"
        signature = f"{return_type} {node.name}({params_str})"
        
        # Determine if this is a business logic method
        is_business_logic = self._is_business_logic_method(node.name, annotations, len(parameters))
        
        return MethodInfo(
            name=node.name,
            signature=signature,
            return_type=return_type if node.return_type else "void",
            annotations=annotations,
            is_business_logic=is_business_logic
        )
    
    def _is_business_logic_method(self, name: str, annotations: List[str], param_count: int) -> bool:
        """Determine if a method contains business logic."""
        # Skip getters and setters
        if name.startswith('get') and param_count == 0:
            return False
        if name.startswith('set') and param_count == 1:
            return False
        if name.startswith('is') and param_count == 0:
            return False
        
        # Skip common utility methods
        utility_methods = ['equals', 'hashCode', 'toString', 'clone', 'finalize']
        if name in utility_methods:
            return False
        
        # Keep methods with annotations (likely endpoints, services, etc.)
        business_annotations = ['PostMapping', 'GetMapping', 'PutMapping', 'DeleteMapping', 
                               'RequestMapping', 'Service', 'Transactional', 'Async']
        if any(ann in business_annotations for ann in annotations):
            return True
        
        # Keep methods that look like business operations
        business_keywords = ['create', 'update', 'delete', 'save', 'find', 'search', 
                            'process', 'calculate', 'validate', 'authenticate', 
                            'authorize', 'send', 'receive', 'fetch', 'load', 'rent']
        if any(keyword in name.lower() for keyword in business_keywords):
            return True
        
        return False
    
    def _calculate_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Calculate code complexity metrics using lizard."""
        if not lizard:
            return {"average_complexity": 0}
            
        try:
            analysis = lizard.analyze_file(str(file_path))
            complexities = [func.cyclomatic_complexity for func in analysis.function_list]
            
            return {
                "total_functions": len(analysis.function_list),
                "average_complexity": sum(complexities) / len(complexities) if complexities else 0,
                "max_complexity": max(complexities) if complexities else 0,
                "nloc": analysis.nloc
            }
        except Exception:
            return {"average_complexity": 0}
    
    def _create_basic_file_info(self, file_path: Path, content: str) -> FileInfo:
        """Create basic file info when full parsing fails."""
        lines = content.split('\n')
        return FileInfo(
            file_path=str(file_path),
            file_type="java",
            total_lines=len(lines),
            code_lines=sum(1 for line in lines if line.strip()),
            comment_lines=0
        )


