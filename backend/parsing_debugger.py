import os
import json
import datetime
from typing import Dict, Any, Optional

class JSONParsingDebugger:
    """
    Debug utility to log and analyze JSON parsing failures.
    """
    
    def __init__(self, log_dir: str = "debug_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def log_parsing_failure(self, 
                          response: str, 
                          agent_type: str, 
                          project_id: str = None, 
                          error_msg: str = None) -> str:
        """
        Log a parsing failure for debugging.
        
        Args:
            response: The raw response that failed to parse
            agent_type: Type of agent that generated the response (planning, coding, review, etc.)
            project_id: ID of the project being generated
            error_msg: Error message from the parser
            
        Returns:
            Path to the log file created
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"parse_failure_{agent_type}_{timestamp}.json"
        filepath = os.path.join(self.log_dir, filename)
        
        log_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent_type": agent_type,
            "project_id": project_id,
            "error_message": error_msg,
            "response_length": len(response) if response else 0,
            "response_type": type(response).__name__,
            "response_preview": response[:500] if response else None,
            "full_response": response,
            "analysis": self._analyze_response(response)
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Fallback to safe encoding
            log_data["full_response"] = str(response)
            log_data["encoding_error"] = str(e)
            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def _analyze_response(self, response: str) -> Dict[str, Any]:
        """Analyze the response to identify common issues."""
        if not response:
            return {"issue": "empty_response"}
        
        analysis = {
            "has_json_brackets": "{" in response and "}" in response,
            "has_markdown_wrapper": "```" in response,
            "has_unescaped_quotes": self._count_unescaped_quotes(response),
            "has_unescaped_backslashes": self._count_unescaped_backslashes(response),
            "line_count": response.count('\n') + 1,
            "potential_json_start": response.find('{'),
            "potential_json_end": response.rfind('}'),
            "contains_code_keywords": any(keyword in response.lower() for keyword in 
                                        ['import', 'def ', 'class ', 'if __name__']),
        }
        
        # Try to identify the main issue
        if not analysis["has_json_brackets"]:
            analysis["likely_issue"] = "no_json_structure"
        elif analysis["has_unescaped_quotes"] > 0:
            analysis["likely_issue"] = "unescaped_quotes"
        elif analysis["has_unescaped_backslashes"] > 0:
            analysis["likely_issue"] = "unescaped_backslashes"
        elif analysis["has_markdown_wrapper"]:
            analysis["likely_issue"] = "markdown_wrapper"
        else:
            analysis["likely_issue"] = "unknown"
        
        return analysis
    
    def _count_unescaped_quotes(self, text: str) -> int:
        """Count potentially unescaped quotes in the text."""
        count = 0
        i = 0
        while i < len(text):
            if text[i] == '"' and (i == 0 or text[i-1] != '\\'):
                count += 1
            i += 1
        return count
    
    def _count_unescaped_backslashes(self, text: str) -> int:
        """Count potentially unescaped backslashes in the text."""
        # This is a simplified check - real analysis would be more complex
        single_backslashes = text.count('\\')
        double_backslashes = text.count('\\\\')
        return single_backslashes - (double_backslashes * 2)
    
    def get_failure_stats(self) -> Dict[str, Any]:
        """Get statistics about parsing failures."""
        stats = {
            "total_failures": 0,
            "by_agent_type": {},
            "by_issue_type": {},
            "recent_failures": []
        }
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.startswith("parse_failure_") and filename.endswith(".json"):
                    filepath = os.path.join(self.log_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                        
                        stats["total_failures"] += 1
                        
                        agent_type = log_data.get("agent_type", "unknown")
                        stats["by_agent_type"][agent_type] = stats["by_agent_type"].get(agent_type, 0) + 1
                        
                        issue_type = log_data.get("analysis", {}).get("likely_issue", "unknown")
                        stats["by_issue_type"][issue_type] = stats["by_issue_type"].get(issue_type, 0) + 1
                        
                        # Keep only recent failures (last 10)
                        if len(stats["recent_failures"]) < 10:
                            stats["recent_failures"].append({
                                "timestamp": log_data.get("timestamp"),
                                "agent_type": agent_type,
                                "issue_type": issue_type,
                                "file": filename
                            })
                    
                    except Exception as e:
                        print(f"Error reading log file {filename}: {e}")
        
        except Exception as e:
            print(f"Error accessing log directory: {e}")
        
        return stats

# Global debugger instance
debug_logger = JSONParsingDebugger()
