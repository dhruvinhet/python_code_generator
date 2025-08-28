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
            else:
                self.logger.debug(f"Strategy 1: Direct parsing succeeded but validation failed")
        except json.JSONDecodeError as e:
            self.logger.debug(f"Strategy 1: Direct JSON parsing failed: {e}")
        
        # Strategy 2: Extract JSON from text wrapper
        try:
            result = self._extract_json_from_text(response)
            if result and self._validate_json(result, expected_keys):
                return result
            else:
                self.logger.debug(f"Strategy 2: Text extraction succeeded but validation failed")
        except Exception as e:
            self.logger.debug(f"Strategy 2: Text extraction failed: {e}")
        
        # Strategy 3: Fix common JSON issues and retry
        try:
            fixed_response = self._fix_common_json_issues(response)
            result = json.loads(fixed_response)
            if self._validate_json(result, expected_keys):
                return result
            else:
                self.logger.debug(f"Strategy 3: JSON fixing succeeded but validation failed")
        except Exception as e:
            self.logger.debug(f"Strategy 3: JSON fixing failed: {e}")
        
        # Strategy 4: Extract using regex patterns
        try:
            result = self._extract_json_with_regex(response)
            if result and self._validate_json(result, expected_keys):
                return result
            else:
                self.logger.debug(f"Strategy 4: Regex extraction succeeded but validation failed")
        except Exception as e:
            self.logger.debug(f"Strategy 4: Regex extraction failed: {e}")
        
        # Strategy 5: Clean and normalize the JSON string
        try:
            cleaned_response = self._clean_json_string(response)
            result = json.loads(cleaned_response)
            if self._validate_json(result, expected_keys):
                return result
            else:
                self.logger.debug(f"Strategy 5: String cleaning succeeded but validation failed")
        except Exception as e:
            self.logger.debug(f"Strategy 5: String cleaning failed: {e}")
        
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
        self.logger.debug(f"Extracting JSON from text: {text[:200]}...")
        
        # First try to remove markdown code blocks more aggressively
        original_text = text
        
        # Remove markdown code blocks with various patterns
        patterns = [
            r'```json\s*\n?(.+?)\n?\s*```',  # ```json ... ```
            r'```\s*\n?(.+?)\n?\s*```',      # ``` ... ```
            r'`([^`]+)`',                     # `...`
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    self.logger.debug(f"Trying pattern match: {match[:100]}...")
                    # Clean up the match
                    clean_match = match.strip()
                    result = json.loads(clean_match)
                    self.logger.debug(f"Successfully parsed JSON from pattern match")
                    return result
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Pattern match failed to parse: {e}")
                    continue
                except Exception as e:
                    self.logger.debug(f"Unexpected error with pattern match: {e}")
                    continue
        
        # Fallback: Remove code blocks manually and try multiple extraction methods
        cleaned_text = text
        
        # Remove various markdown patterns
        cleaned_text = re.sub(r'```(?:json)?\s*\n?', '', cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r'\n?\s*```\s*$', '', cleaned_text, flags=re.MULTILINE)
        cleaned_text = re.sub(r'\n?\s*```', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        self.logger.debug(f"After removing code blocks: {cleaned_text[:200]}...")
        
        # Method 1: Find the first { and last } with proper brace matching
        brace_count = 0
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(cleaned_text):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    end_idx = i + 1
                    break
        
        if start_idx != -1 and end_idx != -1:
            json_str = cleaned_text[start_idx:end_idx]
            try:
                self.logger.debug(f"Trying brace-matched JSON: {json_str[:100]}...")
                result = json.loads(json_str)
                self.logger.debug(f"Successfully parsed brace-matched JSON")
                return result
            except json.JSONDecodeError as e:
                self.logger.debug(f"Brace-matched JSON parsing failed: {e}")
        
        # Method 2: Try parsing the entire cleaned text
        try:
            self.logger.debug(f"Trying to parse entire cleaned text...")
            result = json.loads(cleaned_text)
            self.logger.debug(f"Successfully parsed entire cleaned text")
            return result
        except json.JSONDecodeError as e:
            self.logger.debug(f"Entire text parsing failed: {e}")
        
        # Method 3: Look for JSON objects within the text using regex
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, cleaned_text, re.DOTALL)
        
        for match in matches:
            try:
                self.logger.debug(f"Trying regex-found JSON: {match[:100]}...")
                result = json.loads(match)
                self.logger.debug(f"Successfully parsed regex-found JSON")
                return result
            except json.JSONDecodeError:
                continue
        
        self.logger.debug(f"All JSON extraction methods failed")
        return None
        
        if start_idx == -1 or end_idx == -1:
            self.logger.debug(f"Could not find valid JSON boundaries")
            return None
            
        json_str = text[start_idx:end_idx]
        self.logger.debug(f"Extracted JSON string: {json_str[:200]}...")
        
        try:
            result = json.loads(json_str)
            self.logger.debug(f"Successfully parsed extracted JSON")
            return result
        except Exception as e:
            self.logger.debug(f"Failed to parse extracted JSON: {e}")
            return None
    
    def _fix_common_json_issues(self, json_str: str) -> str:
        """Fix common JSON formatting issues."""
        # Remove markdown code blocks more aggressively
        # Remove opening code blocks
        json_str = re.sub(r'```(?:json)?\s*\n?', '', json_str, flags=re.IGNORECASE)
        # Remove closing code blocks
        json_str = re.sub(r'\n?\s*```\s*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'\n?\s*```', '', json_str)
        
        # Remove any leading/trailing non-JSON text
        json_str = json_str.strip()
        
        # Find the JSON boundaries more carefully
        brace_count = 0
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(json_str):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    end_idx = i + 1
                    break
        
        if start_idx != -1 and end_idx != -1:
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
            self.logger.debug(f"Validation failed: Object is not a dict, got {type(json_obj)}")
            return False
        
        if not expected_keys:
            self.logger.debug(f"No expected keys specified, validation passed for object with keys: {list(json_obj.keys())}")
            return True
        
        available_keys = list(json_obj.keys())
        self.logger.debug(f"Validating JSON with expected keys: {expected_keys}, available keys: {available_keys}")
        
        # More tolerant validation - check if any expected keys are present rather than all
        missing_keys = []
        found_keys = []
        
        for key in expected_keys:
            if key in json_obj:
                found_keys.append(key)
            else:
                missing_keys.append(key)
        
        # If we found at least one expected key, consider it valid
        # This is more tolerant than requiring ALL expected keys
        if found_keys:
            if missing_keys:
                self.logger.warning(f"Some expected keys missing: {missing_keys}. But found: {found_keys}")
            else:
                self.logger.debug(f"All expected keys found: {found_keys}")
            return True
        else:
            self.logger.warning(f"No expected keys found. Missing: {missing_keys}. Available: {available_keys}")
            self.logger.debug(f"JSON content preview: {str(json_obj)[:500]}...")
            # Even if no expected keys found, still return True if the object looks valid
            # This allows the fallback mechanisms in the agents to handle the structure
            return len(available_keys) > 0
    
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
        elif structure_type == "code_files" or structure_type == "Backend Developer" or structure_type == "Frontend Developer" or structure_type == "Main File Creator":
            # Try to extract code files from the content first
            files = self._extract_code_files_from_text(content)
            if files:
                return {
                    "files": [
                        {"filename": filename, "content": file_content}
                        for filename, file_content in files.items()
                    ]
                }
            else:
                return {
                    "files": [
                        {
                            "filename": "main.py",
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

    def _extract_code_files_from_text(self, text: str) -> Dict[str, str]:
        """Extract code files from text content using patterns."""
        import re
        files = {}
        
        # Look for code blocks with filenames
        pattern = r'```(\w+)?\s*(?:filename?[:\s]+)?([^\n]+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        for i, (lang, filename, content) in enumerate(matches):
            if filename and filename.strip():
                clean_filename = filename.strip().replace('filename:', '').replace('file:', '').strip()
                # Remove any markdown formatting
                clean_filename = re.sub(r'[*`#]', '', clean_filename).strip()
                files[clean_filename] = content.strip()
            else:
                # Try to guess filename from content
                if 'def ' in content or 'import ' in content:
                    files[f"file_{i}.py"] = content.strip()
                elif 'function ' in content or 'const ' in content:
                    files[f"file_{i}.js"] = content.strip()
                elif '"name"' in content and '"version"' in content:
                    files[f"package.json"] = content.strip()
                else:
                    files[f"file_{i}.txt"] = content.strip()
        
        # If no code blocks found, try to extract from plain text patterns
        if not files:
            file_patterns = [
                (r'(app\.py|main\.py|server\.py)[:\s]*\n(.*?)(?=\n\n|\n[A-Za-z]|\Z)', 'python'),
                (r'(package\.json)[:\s]*\n(.*?)(?=\n\n|\n[A-Za-z]|\Z)', 'json'),
                (r'(requirements\.txt)[:\s]*\n(.*?)(?=\n\n|\n[A-Za-z]|\Z)', 'text'),
                (r'(run_project\.py)[:\s]*\n(.*?)(?=\n\n|\n[A-Za-z]|\Z)', 'python'),
                (r'(README\.md)[:\s]*\n(.*?)(?=\n\n|\n[A-Za-z]|\Z)', 'markdown')
            ]
            
            for pattern, file_type in file_patterns:
                matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
                for filename, content in matches:
                    clean_filename = filename.strip()
                    files[clean_filename] = content.strip()
        
        return files

# Global parser instance
json_parser = RobustJSONParser()
