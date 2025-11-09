"""LLM integration for code analysis using LangChain."""

from typing import List, Dict, Any, Optional
import json

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain.chat_models import ChatOpenAI
    except ImportError:
        ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    try:
        from langchain.chat_models import ChatAnthropic
    except ImportError:
        ChatAnthropic = None

try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    try:
        from langchain.schema import HumanMessage, SystemMessage
    except ImportError:
        from langchain.schema.messages import HumanMessage, SystemMessage

try:
    from langchain_community.callbacks import get_openai_callback
except ImportError:
    try:
        from langchain.callbacks import get_openai_callback
    except ImportError:
        get_openai_callback = None

try:
    import tiktoken
except ImportError:
    tiktoken = None

from config import config


class LLMAnalyzer:
    """LLM-based code analyzer using LangChain."""
    
    def __init__(self):
        """Initialize the LLM based on configuration."""
        self.llm = self._initialize_llm()
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.max_tokens = config.MAX_TOKENS_PER_CHUNK
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration."""
        if config.LLM_PROVIDER == "openai":
            if not ChatOpenAI:
                raise ValueError("OpenAI not available. Install: pip install langchain-openai")
            return ChatOpenAI(
                model=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY,
                temperature=0.1,
                max_tokens=4000
            )
        elif config.LLM_PROVIDER == "anthropic":
            if not ChatAnthropic:
                raise ValueError("Anthropic not available. Install: pip install langchain-anthropic")
            return ChatAnthropic(
                model=config.ANTHROPIC_MODEL,
                api_key=config.ANTHROPIC_API_KEY,
                temperature=0.1,
                max_tokens=4000
            )
        elif config.LLM_PROVIDER == "ollama":
            try:
                from langchain_ollama import OllamaLLM
                return OllamaLLM(
                    model=config.OLLAMA_MODEL,
                    base_url=config.OLLAMA_BASE_URL,
                    temperature=0.1
                )
            except ImportError:
                try:
                    # Fallback to old import for backwards compatibility
                    from langchain_community.llms import Ollama
                    return Ollama(
                        model=config.OLLAMA_MODEL,
                        base_url=config.OLLAMA_BASE_URL,
                        temperature=0.1
                    )
                except ImportError:
                    raise ValueError("Ollama not available. Install: pip install langchain-ollama")
        else:
            raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.encoding.encode(text))
    
    def analyze_project_overview(self, readme_content: str, 
                                  config_content: str,
                                  file_structure: List[str],
                                  language: str = "unknown",
                                  frameworks: List[str] = None) -> Dict[str, Any]:
        """Generate high-level project overview."""
        system_prompt = """You are an expert software architect analyzing a codebase.
Generate a comprehensive project overview including:
1. Project name and description
2. Main purpose and functionality
3. Key technologies used
4. Architecture pattern (e.g., MVC, microservices)
5. Main features

Return your analysis as a JSON object with these exact keys:
{
  "project_name": "string",
  "description": "string",
  "purpose": "string",
  "key_technologies": ["array", "of", "strings"],
  "architecture_pattern": "string",
  "main_features": ["array", "of", "strings"],
  "dependencies": ["array", "of", "key", "dependencies"]
}"""
        
        frameworks = frameworks or []
        frameworks_str = ', '.join(frameworks) if frameworks else 'Unknown'
        
        user_prompt = f"""Analyze this {language} project:

README Content:
{readme_content[:3000] if readme_content else 'No README found'}

Configuration File Content:
{config_content[:2000] if config_content else 'No config file found'}

Detected Language: {language}
Detected Frameworks: {frameworks_str}

File Structure Sample (first 50 files):
{chr(10).join(file_structure[:50])}

Provide the analysis as valid JSON."""
        
        response = self._query_llm(system_prompt, user_prompt)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return self._parse_response_to_dict(response)
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {}
    
    def generate_method_description(self, method_signature: str, class_name: str, annotations: list) -> str:
        """Generate description from method signature and annotations."""
        system_prompt = """You are an expert software developer. Generate a clear, concise 1-sentence description of what this method does based on its signature and annotations.
Focus on the business purpose, not implementation details."""
        
        annotations_str = ", ".join(annotations) if annotations else "none"
        
        user_prompt = f"""Class: {class_name}
Method Signature: {method_signature}
Annotations: {annotations_str}

Generate a 1-sentence description:"""
        
        response = self._query_llm(system_prompt, user_prompt)
        return response.strip().strip('"').strip("'")
    
    def generate_recommendations(self, analysis_summary: str) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        system_prompt = """You are a senior software architect conducting a code review.
Based on the codebase analysis, provide 5-7 actionable recommendations for improvement.
Focus on: code quality, maintainability, security, performance, and best practices.

Return as a JSON array of strings."""
        
        user_prompt = f"""Codebase Analysis Summary:
{analysis_summary}

Recommendations (as JSON array):"""
        
        response = self._query_llm(system_prompt, user_prompt)
        
        try:
            # Try to extract JSON array
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                # Fallback: split by newlines
                return [line.strip('- ').strip() 
                        for line in response.split('\n') 
                        if line.strip() and line.strip().startswith('-')]
        except Exception as e:
            print(f"Error parsing recommendations: {e}")
            return []
    
    def _query_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Query the LLM with given prompts."""
        try:
            # For Ollama, use simple string prompt
            if config.LLM_PROVIDER == "ollama":
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.llm.invoke(full_prompt)
                return response if isinstance(response, str) else str(response)
            
            # For OpenAI and Anthropic, use messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            if config.LLM_PROVIDER == "openai" and get_openai_callback:
                with get_openai_callback() as cb:
                    response = self.llm.invoke(messages)
                    print(f"Tokens used: {cb.total_tokens}, Cost: ${cb.total_cost:.4f}")
            else:
                response = self.llm.invoke(messages)
            
            return response.content if hasattr(response, 'content') else str(response)
        
        except Exception as e:
            print(f"Error querying LLM: {e}")
            import traceback
            print(traceback.format_exc())
            return "{}"
    
    def _parse_response_to_dict(self, response: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses."""
        result = {}
        lines = response.split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip('- ').strip().lower().replace(' ', '_')
                value = value.strip()
                result[key] = value
        
        return result
