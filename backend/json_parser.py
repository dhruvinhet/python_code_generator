import json
import re
import logging
from typing import Dict, Any, Optional, Union
from parsing_debugger import debug_logger

class RobustJSONParser:
    """
    A robust JSON parser that handles common issues with AI-generated JSON responses.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_json_response(self, response: Union[str, dict], expected_keys: Optional[list] = None, 
                          agent_type: str = "unknown", project_id: str = None) -> Optional[Dict[Any, Any]]:
        """
        Parse JSON response with multiple fallback strategies.
        
        Args:
            response: The response from AI agent (string or dict)
            expected_keys: List of expected keys in the JSON (for validation)
            agent_type: Type of agent generating the response (for debugging)
            project_id: ID of the project being generated (for debugging)
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        if isinstance(response, dict):
            return response
            
        if not isinstance(response, str):
            self.logger.error(f"Invalid response type: {type(response)}")
            return None
            
        # Strategy 1: Direct JSON parsing
        try:
            result = json.loads(response)
            if self._validate_json(result, expected_keys):
                return result
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from text wrapper
        try:
            result = self._extract_json_from_text(response)
            if result and self._validate_json(result, expected_keys):
                return result
        except:
            pass
        
        # Strategy 3: Fix common JSON issues and retry
        try:
            fixed_response = self._fix_common_json_issues(response)
            result = json.loads(fixed_response)
            if self._validate_json(result, expected_keys):
                return result
        except:
            pass
        
        # Strategy 4: Extract using regex patterns
        try:
            result = self._extract_json_with_regex(response)
            if result and self._validate_json(result, expected_keys):
                return result
        except:
            pass
        
        # Strategy 5: Clean and normalize the JSON string
        try:
            cleaned_response = self._clean_json_string(response)
            result = json.loads(cleaned_response)
            if self._validate_json(result, expected_keys):
                return result
        except:
            pass
        
        self.logger.error(f"Failed to parse JSON response after all strategies. Response preview: {response[:200]}...")
        
        # Log the failure for debugging
        if agent_type != "unknown":
            try:
                debug_logger.log_parsing_failure(
                    response=str(response) if response else "",
                    agent_type=agent_type,
                    project_id=project_id,
                    error_msg="All parsing strategies failed"
                )
            except Exception as debug_error:
                self.logger.warning(f"Failed to log parsing failure: {debug_error}")
        
        return None
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[Any, Any]]:
        """Extract JSON from text that may contain additional content."""
        # Find the first { and last }
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return None
            
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues."""
        # Remove markdown code blocks
        json_str = re.sub(r'```(?:json)?\n?', '', json_str, flags=re.IGNORECASE)
        json_str = re.sub(r'\n?```', '', json_str)
        
        # Fix unescaped backslashes in strings
        # This is tricky - we need to escape backslashes that aren't already escaped
        # But not break legitimate escape sequences
        
        # First, let's find the JSON boundaries
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = json_str[start_idx:end_idx]
        
        # Fix common escape issues
        json_str = self._fix_escape_sequences(json_str)
        
        # Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        return json_str
    
    def _fix_escape_sequences(self, text: str) -> str:
        """Fix escape sequence issues in JSON strings."""
        result = []
        i = 0
        in_string = False
        
        while i < len(text):
            char = text[i]
            
            if char == '"' and (i == 0 or text[i-1] != '\\'):
                in_string = not in_string
                result.append(char)
            elif in_string and char == '\\':
                # Handle escape sequences
                if i + 1 < len(text):
                    next_char = text[i + 1]
                    if next_char in '"\\nrtbf/':
                        # Valid escape sequence
                        result.append(char)
                    else:
                        # Invalid escape - escape the backslash
                        result.append('\\\\')
                else:
                    # Backslash at end of string
                    result.append('\\\\')
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
    def _extract_json_with_regex(self, text: str) -> Optional[Dict[Any, Any]]:
        """Extract JSON using regex patterns."""
        patterns = [
            r'\{.*?\}',  # Basic pattern
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested objects
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
        
        return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean and normalize JSON string."""
        # Remove extra whitespace
        json_str = json_str.strip()
        
        # Remove non-printable characters
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        
        # Find JSON boundaries
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = json_str[start_idx:end_idx]
        
        return json_str
    
    def _validate_json(self, json_obj: Dict[Any, Any], expected_keys: Optional[list] = None) -> bool:
        """Validate that the JSON object has the expected structure."""
        if not isinstance(json_obj, dict):
            return False
        
        if expected_keys:
            for key in expected_keys:
                if key not in json_obj:
                    self.logger.warning(f"Missing expected key: {key}")
                    return False
        
        return True
    
    def create_fallback_structure(self, structure_type: str, content: str = "") -> Dict[Any, Any]:
        """Create fallback JSON structures when parsing fails."""
        if structure_type == "project_plan":
            return {
                "project_name": "Generated Project",
                "description": "AI-generated Python project",
                "dependencies": ["streamlit"],
                "gui_framework": "streamlit",
                "files": [
                    {
                        "path": "main.py",
                        "purpose": "Main application entry point",
                        "functions": ["main"],
                        "imports": ["streamlit"]
                    }
                ],
                "main_file": "main.py",
                "architecture": "Simple application structure"
            }
        elif structure_type == "code_files":
            return {
                "files": [
                    {
                        "path": "main.py",
                        "content": f"""# Generated Project
import streamlit as st

def main():
    st.title("Generated Project")
    st.write("This is a fallback project generated due to parsing issues.")
    st.write("Original content preview:")
    st.code({repr(content[:500])})

if __name__ == "__main__":
    main()
"""
                    }
                ]
            }
        
        return {}

# Global parser instance
json_parser = RobustJSONParser()
