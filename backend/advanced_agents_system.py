"""
Advanced Multi-Agent Project Generation System
Custom implementation without LangGraph - builds complete full-stack projects with AI models automatically.
"""

import asyncio
import json
import os
import re
import uuid
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import requests
import subprocess

load_dotenv()

import google.generativeai as genai
from config import Config

class ProjectState:
    """State management for multi-agent workflow"""
    def __init__(self, user_request: str, project_id: str = None, project_name: str = "", project_folder: str = ""):
        self.user_request = user_request
        self.project_name = project_name
        self.project_id = project_id or str(uuid.uuid4())
        self.project_folder = project_folder
        self.plan = {}
        self.domain_research = {}
        self.selected_model = {}
        self.backend_code = {}
        self.frontend_code = {}
        self.main_runner = ""
        self.requirements = []
        self.code_check_results = {}
        self.documentation = ""
        self.shared_memory = {}
        self.current_agent = ""
        self.logs = []
        self.status = "starting"
        self.created_at = datetime.now()


class AdvancedAgentsSystem:
    """Custom multi-agent system without LangGraph"""
    
    def __init__(self):
        """Initialize the advanced agents system"""
        self.config = Config()
        
        # Configure Gemini API with AI Studio key
        api_key = self.config.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for AI Studio Gemini API")
            
        genai.configure(api_key=api_key)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Using faster, more efficient model
        
        # Project directories
        self.base_projects_dir = Path("generated_projects")
        self.base_projects_dir.mkdir(exist_ok=True)
        self.project_dir = self.base_projects_dir  # Initialize project_dir attribute
        
    async def _api_call(self, prompt: str, state: ProjectState) -> str:
        """Make direct API call without any rate limiting"""
        try:
            self.log_event(state, f"🤖 Making API call for {state.current_agent}...", "info")
            
            # Add context from shared memory
            context_prompt = f"""
            Project Context:
            - User Request: {state.user_request}
            - Project Name: {state.project_name}
            - Shared Memory: {json.dumps(state.shared_memory, indent=2)}
            
            Current Task:
            {prompt}
            
            Respond with clear, structured information. Be concise but comprehensive.
            """
            
            response = self.model.generate_content(context_prompt)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            self.log_event(state, f"❌ API Error: {error_msg}", "error")
            return f"Error: {error_msg}"
    
    def log_event(self, state: ProjectState, message: str, level: str = "info"):
        """Add log entry to project state"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": state.current_agent,
            "message": message,
            "level": level
        }
        state.logs.append(log_entry)
        print(f"[{level.upper()}] {state.current_agent}: {message}")
    
    async def planner_agent(self, state: ProjectState) -> ProjectState:
        """Agent 1: Project Planning and Task Breakdown"""
        state.current_agent = "Planner"
        self.log_event(state, "🎯 Starting project planning phase...", "info")
        
        # Create project structure
        user_request = state.user_request
        
        # Extract project name from request
        project_name = await self._extract_project_name(user_request)
        project_folder = self.base_projects_dir / state.project_id
        project_folder.mkdir(exist_ok=True)
        
        # Create subdirectories
        (project_folder / "backend").mkdir(exist_ok=True)
        (project_folder / "frontend").mkdir(exist_ok=True)
        (project_folder / "docs").mkdir(exist_ok=True)
        (project_folder / "models").mkdir(exist_ok=True)
        
        state.project_name = project_name
        state.project_folder = str(project_folder)
        
        # Generate detailed project plan
        plan_prompt = f"""
        As a senior project planner, create a comprehensive plan for: {user_request}
        
        Provide a detailed breakdown including:
        1. Project overview and objectives
        2. Technical requirements and constraints
        3. Sub-tasks and milestones
        4. Technology stack recommendations
        5. Timeline estimation
        6. Success criteria
        
        Return as structured JSON format.
        """
        
        try:
            response = await self._api_call(plan_prompt, state)
            plan = self._extract_json_from_response(response)
            
            state.plan = plan
            state.shared_memory["project_requirements"] = plan.get("technical_requirements", {})
            
            self.log_event(state, f"✅ Project plan created for: {project_name}", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Planning failed: {str(e)}", "error")
            state.plan = {"error": str(e)}
        
        return state
    
    async def domain_expert_agent(self, state: ProjectState) -> ProjectState:
        """Agent 2: Domain Research and Exploration"""
        state.current_agent = "Domain Expert"
        self.log_event(state, "🔬 Starting domain research...", "info")
        
        research_prompt = f"""
        As a domain expert researcher, conduct comprehensive research for: {state.user_request}
        
        Research and provide:
        1. Domain introduction and overview
        2. Existing methods, models, and approaches
        3. Pros and cons of different solutions
        4. Real-world use cases and applications
        5. Current trends and challenges
        6. State-of-the-art solutions
        7. Recommended approach with justification
        8. Limitations and future scope
        
        Make it comprehensive but easy to understand.
        Return as structured format.
        """
        
        try:
            response = await self._api_call(research_prompt, state)
            research_data = self._format_research_data(response)
            
            # Create project_exploration.md
            exploration_content = self._format_exploration_document(research_data)
            exploration_path = Path(state.project_folder) / "docs" / "project_exploration.md"
            
            with open(exploration_path, 'w', encoding='utf-8') as f:
                f.write(exploration_content)
            
            state.domain_research = research_data
            state.shared_memory["domain_insights"] = research_data
            
            self.log_event(state, "✅ Domain research completed and saved", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Domain research failed: {str(e)}", "error")
            state.domain_research = {"error": str(e)}
        
        return state
    
    async def model_selector_agent(self, state: ProjectState) -> ProjectState:
        """Agent 3: AI Model Selection"""
        state.current_agent = "Model Selector"
        self.log_event(state, "🤖 Starting model selection...", "info")
        
        model_selection_prompt = f"""
        As an AI model selection expert, choose the best FREE model for this project.
        
        Project: {state.user_request}
        Domain Insights: {state.shared_memory.get("domain_insights", {})}
        
        Select from platforms like:
        1. HuggingFace (preferred for free models)
        2. GitHub repositories with pretrained models
        3. Open source model repositories
        
        Provide:
        1. Selected model name and platform
        2. Model download URL/identifier
        3. Installation requirements
        4. Code example for downloading/loading
        5. Model capabilities and limitations
        6. Alternative models as backup
        7. Hardware requirements
        
        Return as structured format with all necessary details.
        """
        
        try:
            response = await self._api_call(model_selection_prompt, state)
            model_info = self._format_model_info(response)
            
            state.selected_model = model_info
            state.shared_memory["model_requirements"] = model_info
            
            self.log_event(state, f"✅ Model selected: {model_info.get('model_name', 'AI Model')}", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Model selection failed: {str(e)}", "error")
            state.selected_model = {"error": str(e)}
        
        return state
    
    async def backend_developer_agent(self, state: ProjectState) -> ProjectState:
        """Agent 4: Backend Development"""
        state.current_agent = "Backend Developer"
        self.log_event(state, "⚙️ Starting backend development...", "info")
        
        backend_prompt = f"""
        As a senior backend developer, create a complete Python backend for this project:
        
        Project: {state.user_request}
        Selected Model: {state.selected_model}
        Domain Research: {state.domain_research}
        
        Create these files:
        1. app.py - Main Flask/FastAPI application
        2. model_setup.py - AI model download and setup
        3. utils.py - Utility functions
        4. requirements.txt - Dependencies
        
        Requirements:
        - Use the selected AI model
        - Implement automatic model downloading
        - Create robust API endpoints
        - Add error handling and logging
        - Include advanced features for the domain
        
        Return each file as a separate section with clear file names.
        """
        
        try:
            response = await self._api_call(backend_prompt, state)
            backend_files = self._extract_code_files(response)
            
            # Save backend files
            backend_dir = Path(state.project_folder) / "backend"
            for filename, content in backend_files.items():
                try:
                    # Ensure safe filename
                    safe_filename = self._sanitize_filename(filename)
                    file_path = backend_dir / safe_filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as file_error:
                    self.log_event(state, f"⚠️ Failed to save backend file '{filename}': {str(file_error)}", "warning")
                    # Try with a fallback filename
                    fallback_name = f"backend_file_{len(backend_files)}.py"
                    try:
                        fallback_path = backend_dir / fallback_name
                        with open(fallback_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Original filename: {filename}\n# Error: {str(file_error)}\n\n{content}")
                        self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                    except:
                        self.log_event(state, f"❌ Could not save backend file at all: {filename}", "error")
            
            state.backend_code = backend_files
            state.shared_memory["backend_api"] = self._extract_api_info(backend_files)
            
            self.log_event(state, f"✅ Backend created with {len(backend_files)} files", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Backend development failed: {str(e)}", "error")
            state.backend_code = {"error": str(e)}
        
        return state
    
    async def frontend_developer_agent(self, state: ProjectState) -> ProjectState:
        """Agent 5: Frontend Development"""
        state.current_agent = "Frontend Developer"
        self.log_event(state, "🎨 Starting frontend development...", "info")
        
        frontend_prompt = f"""
        As a senior React frontend developer, create a beautiful and functional UI:
        
        Project: {state.user_request}
        Backend API Info: {state.shared_memory.get("backend_api", {})}
        
        Create a complete React application with:
        1. Modern, responsive UI design
        2. Integration with backend APIs
        3. File upload/download functionality where needed
        4. Real-time features if applicable
        5. Error handling and loading states
        6. Professional styling
        
        Files needed:
        - package.json
        - src/App.js
        - src/components/ (various components)
        - public/index.html
        
        Ensure all backend features are accessible through the UI.
        Return each file content clearly separated.
        """
        
        try:
            response = await self._api_call(frontend_prompt, state)
            frontend_files = self._extract_code_files(response)
            
            # Save frontend files
            frontend_dir = Path(state.project_folder) / "frontend"
            for file_path, content in frontend_files.items():
                try:
                    # Ensure safe file path
                    safe_file_path = self._sanitize_filename(file_path)
                    full_path = frontend_dir / safe_file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as file_error:
                    self.log_event(state, f"⚠️ Failed to save frontend file '{file_path}': {str(file_error)}", "warning")
                    # Try with a fallback filename
                    fallback_name = f"frontend_file_{len(frontend_files)}.txt"
                    try:
                        fallback_path = frontend_dir / fallback_name
                        fallback_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(fallback_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Original filename: {file_path}\n# Error: {str(file_error)}\n\n{content}")
                        self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                    except:
                        self.log_event(state, f"❌ Could not save frontend file at all: {file_path}", "error")
            
            state.frontend_code = frontend_files
            
            self.log_event(state, f"✅ Frontend created with {len(frontend_files)} files", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Frontend development failed: {str(e)}", "error")
            state.frontend_code = {"error": str(e)}
        
        return state
    
    async def main_file_creator_agent(self, state: ProjectState) -> ProjectState:
        """Agent 6: Main Runner File Creation"""
        state.current_agent = "Main File Creator"
        self.log_event(state, "🚀 Creating main runner file...", "info")
        
        main_file_prompt = f"""
        Create a main runner file (run_project.py) that:
        
        1. Installs all requirements automatically
        2. Sets up the backend server
        3. Sets up the frontend development server
        4. Opens the application in browser
        5. Handles both development and production modes
        6. Includes proper error handling
        
        Also create:
        - requirements.txt (comprehensive)
        - README.md (setup instructions)
        
        Make it user-friendly and handle all setup automatically.
        Return each file content clearly.
        """
        
        try:
            response = await self._api_call(main_file_prompt, state)
            main_files = self._extract_code_files(response)
            
            # Save main files to project root
            project_dir = Path(state.project_folder)
            for filename, content in main_files.items():
                try:
                    # Double-check filename sanitization
                    safe_filename = self._sanitize_filename(filename)
                    file_path = project_dir / safe_filename
                    
                    # Ensure parent directory exists
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                except Exception as file_error:
                    self.log_event(state, f"⚠️ Failed to save file '{filename}': {str(file_error)}", "warning")
                    # Try with a fallback filename
                    fallback_name = f"generated_file_{len(main_files)}.txt"
                    try:
                        fallback_path = project_dir / fallback_name
                        with open(fallback_path, 'w', encoding='utf-8') as f:
                            f.write(f"# Original filename: {filename}\n# Error: {str(file_error)}\n\n{content}")
                        self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                    except:
                        self.log_event(state, f"❌ Could not save file at all: {filename}", "error")
            
            state.main_runner = main_files.get("run_project.py", "")
            state.requirements = main_files.get("requirements.txt", "").split('\n')
            
            self.log_event(state, "✅ Main runner and setup files created", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Main file creation failed: {str(e)}", "error")
            state.main_runner = f"# Error: {str(e)}"
            state.requirements = []
        
        return state
    
    async def code_checker_agent(self, state: ProjectState) -> ProjectState:
        """Agent 7: Code Quality and Syntax Checking"""
        state.current_agent = "Code Checker"
        self.log_event(state, "🔍 Starting code quality checks...", "info")
        
        project_dir = Path(state.project_folder)
        issues_found = []
        fixes_applied = []
        
        # Check Python syntax
        for py_file in project_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic syntax check
                compile(content, str(py_file), 'exec')
                
            except SyntaxError as e:
                issue = f"Syntax error in {py_file.name}: {str(e)}"
                issues_found.append(issue)
                self.log_event(state, f"⚠️ {issue}", "warning")
        
        state.code_check_results = {
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "status": "passed" if not issues_found else "issues_found"
        }
        
        self.log_event(state, f"✅ Code check completed: {len(issues_found)} issues found", "success")
        
        return state
    
    async def documentation_agent(self, state: ProjectState) -> ProjectState:
        """Agent 8: Documentation Generation"""
        state.current_agent = "Documentation"
        self.log_event(state, "📚 Creating project documentation...", "info")
        
        documentation_prompt = f"""
        Create comprehensive README.md documentation for this project:
        
        Project: {state.user_request}
        Project Name: {state.project_name}
        Tech Stack: Backend Python, Frontend React
        Selected Model: {state.selected_model.get("model_name", "AI Model")}
        
        Include:
        1. Project title and description
        2. Features and capabilities
        3. Technology stack used
        4. Prerequisites and requirements
        5. Installation instructions (step-by-step)
        6. Usage guide with examples
        7. Project structure explanation
        8. Troubleshooting guide
        
        Make it professional, clear, and beginner-friendly.
        """
        
        try:
            response = await self._api_call(documentation_prompt, state)
            documentation = response
            
            # Save README.md
            readme_path = Path(state.project_folder) / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            
            state.documentation = documentation
            state.status = "completed"
            
            self.log_event(state, "✅ Project documentation completed", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Documentation failed: {str(e)}", "error")
            state.documentation = f"# Documentation Error\n\n{str(e)}"
            state.status = "failed"
        
        return state
    
    # Helper methods
    def _extract_json_from_response(self, response: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            # Find JSON in response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # If no JSON found, create structured response
                return {"content": response}
        except Exception:
            return {"content": response, "error": "Failed to parse JSON"}
    
    async def _extract_project_name(self, user_request: str) -> str:
        """Extract project name from user request"""
        # Simple extraction logic
        words = user_request.lower().split()
        if "build" in words and len(words) > 2:
            idx = words.index("build")
            if idx + 1 < len(words):
                return "_".join(words[idx+1:idx+4])
        
        # Fallback to first few words
        return "_".join(words[:3]).replace(" ", "_")
    
    def _format_exploration_document(self, research_data: Dict) -> str:
        """Format research data into markdown document"""
        content = f"""# Project Domain Exploration

## Domain Overview
{research_data.get('domain_overview', 'Domain overview not available')}

## Existing Solutions
{research_data.get('existing_solutions', 'Solutions analysis not available')}

## Recommended Approach
{research_data.get('recommended_approach', 'Recommendation not available')}

## Limitations and Future Scope
{research_data.get('limitations', 'Limitations not specified')}

---
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return content
    
    def _extract_api_info(self, backend_files: Dict) -> Dict:
        """Extract API endpoint information from backend code"""
        api_info = {"endpoints": [], "base_url": "http://localhost:5000"}
        
        # Simple parsing for API endpoints
        for filename, content in backend_files.items():
            if "app.py" in filename or "server.py" in filename:
                lines = content.split('\n')
                for line in lines:
                    if '@app.route' in line or '@router.' in line:
                        api_info["endpoints"].append(line.strip())
        
        return api_info
    
    async def _fix_syntax_issues(self, content: str, error_msg: str) -> str:
        """Attempt to fix common syntax issues"""
        # Add basic syntax fixes here
        fixed_content = content
        
        # Fix common indentation issues
        if "IndentationError" in error_msg:
            lines = content.split('\n')
            fixed_lines = []
            for line in lines:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # Add basic indentation for function/class definitions
                    if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ']):
                        fixed_lines.append(line)
                    else:
                        fixed_lines.append('    ' + line)
                else:
                    fixed_lines.append(line)
            fixed_content = '\n'.join(fixed_lines)
        
        return fixed_content
    
    async def _create_api_documentation(self, state: ProjectState) -> str:
        """Create API documentation"""
        return f"""# API Documentation

## Base URL
`http://localhost:5000`

## Endpoints

### Health Check
- **GET** `/health`
- **Description**: Check if the API is running
- **Response**: `{{"status": "healthy"}}`

### Main Features
(API endpoints will be documented based on the generated backend)

---
Generated for: {state["project_name"]}
"""
    
    async def _create_development_guide(self, state: ProjectState) -> str:
        """Create development guide"""
        return f"""# Development Guide

## Project Structure
```
{state["project_name"]}/
├── backend/          # Python backend
├── frontend/         # React frontend
├── docs/            # Documentation
├── models/          # AI models
├── run_project.py   # Main runner
└── README.md        # Main documentation
```

## Development Setup
1. Run `python run_project.py` to start the full application
2. Backend will be available at `http://localhost:5000`
3. Frontend will be available at `http://localhost:3000`

## Adding Features
- Backend: Modify files in `backend/` directory
- Frontend: Modify files in `frontend/src/` directory

---
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    
    async def run_workflow(self, user_request: str, project_id: str = None) -> Dict[str, Any]:
        """
        Main workflow that runs all 8 agents sequentially
        """
        # Initialize project state
        state = ProjectState(
            user_request=user_request,
            project_id=project_id or str(uuid.uuid4()),
            project_name=self._sanitize_project_name(user_request),
            project_folder=self.base_projects_dir / (project_id or str(uuid.uuid4()))
        )
        
        # Create project directory structure
        self._create_project_structure(state)
        
        try:
            # Agent 1: Project Planner
            state = await self.planner_agent(state)
            
            # Agent 2: Domain Expert
            state = await self.domain_expert_agent(state)
            
            # Agent 3: Model Selector
            state = await self.model_selector_agent(state)
            
            # Agent 4: Backend Developer
            state = await self.backend_developer_agent(state)
            
            # Agent 5: Frontend Developer
            state = await self.frontend_developer_agent(state)
            
            # Agent 6: Main File Creator
            state = await self.main_file_creator_agent(state)
            
            # Agent 7: Code Checker
            state = await self.code_checker_agent(state)
            
            # Agent 8: Documentation
            state = await self.documentation_agent(state)
            
            # Final status
            if state.status != "failed":
                state.status = "completed"
            
            self.log_event(state, "🎉 Multi-agent workflow completed successfully!", "success")
            
            return {
                "status": state.status,
                "project_id": state.project_id,
                "project_folder": str(state.project_folder),
                "files_created": self._count_project_files(state.project_folder),
                "logs": state.logs,
                "errors": [log for log in state.logs if log.get("level") == "error"]
            }
            
        except Exception as e:
            self.log_event(state, f"💥 Workflow failed: {str(e)}", "error")
            state.status = "failed"
            
            return {
                "status": "failed",
                "project_id": state.project_id,
                "error": str(e),
                "logs": state.logs
            }
    
    def _create_project_structure(self, state: ProjectState):
        """Create basic project directory structure"""
        try:
            # Create main project directory
            state.project_folder.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (state.project_folder / "backend").mkdir(exist_ok=True)
            (state.project_folder / "frontend").mkdir(exist_ok=True)
            (state.project_folder / "docs").mkdir(exist_ok=True)
            
            self.log_event(state, f"📁 Project structure created at {state.project_folder}", "info")
            
        except Exception as e:
            self.log_event(state, f"Failed to create project structure: {str(e)}", "error")
            raise
    
    def _sanitize_project_name(self, user_request: str) -> str:
        """Convert user request to valid project name"""
        # Extract key words and create a project name
        name = re.sub(r'[^a-zA-Z0-9\s]', '', user_request.lower())
        name = '_'.join(name.split()[:3])  # Take first 3 words
        return name or "ai_project"
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to be valid for Windows file system"""
        if not filename or not filename.strip():
            return "untitled.txt"
        
        # Remove or replace invalid characters for Windows
        invalid_chars = '<>:"/\\|?*'
        sanitized = filename.strip()
        
        # Remove HTML tags if present
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Replace invalid characters
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty
        if not sanitized:
            return "untitled.txt"
        
        # Limit length to avoid path too long errors
        if len(sanitized) > 100:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:95] + ext
        
        return sanitized

    def _extract_code_files(self, response: str) -> Dict[str, str]:
        """Extract file contents from LLM response"""
        files = {}
        
        # Look for code blocks with filenames
        pattern = r'```(\w+)?\s*(?:filename?[:\s]+)?([^\n]+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        for i, (lang, filename, content) in enumerate(matches):
            if filename and filename.strip():
                clean_filename = filename.strip().replace('filename:', '').replace('file:', '').strip()
                # Sanitize the filename to avoid invalid characters
                sanitized_filename = self._sanitize_filename(clean_filename)
                files[sanitized_filename] = content.strip()
            else:
                # Try to guess filename from content
                if 'def ' in content or 'import ' in content:
                    files[f"file_{i}.py"] = content.strip()
                elif 'function ' in content or 'const ' in content:
                    files[f"file_{i}.js"] = content.strip()
                else:
                    files[f"file_{i}.txt"] = content.strip()
        
        # If no code blocks found, try to extract from plain text
        if not files:
            # Look for common file patterns
            file_patterns = [
                (r'(app\.py|main\.py|server\.py)[:\s]*\n(.*?)(?=\n\n|\Z)', 'python'),
                (r'(package\.json)[:\s]*\n(.*?)(?=\n\n|\Z)', 'json'),
                (r'(requirements\.txt)[:\s]*\n(.*?)(?=\n\n|\Z)', 'text')
            ]
            
            for pattern, file_type in file_patterns:
                matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
                for filename, content in matches:
                    # Sanitize filename even for pattern matches
                    sanitized_filename = self._sanitize_filename(filename)
                    files[sanitized_filename] = content.strip()
        
        return files
    
    def _count_project_files(self, project_folder: Path) -> int:
        """Count total files created in project"""
        try:
            return len(list(project_folder.rglob("*"))) if project_folder.exists() else 0
        except:
            return 0

    def _format_research_data(self, response: str) -> dict:
        """Format research response into structured data"""
        try:
            # Try to extract structured information from the response
            lines = response.strip().split('\n')
            research_data = {
                'overview': '',
                'key_concepts': [],
                'technologies': [],
                'challenges': [],
                'recommendations': '',
                'raw_response': response
            }
            
            current_section = 'overview'
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if any(keyword in line.lower() for keyword in ['concept', 'technology', 'tech']):
                    current_section = 'technologies'
                elif any(keyword in line.lower() for keyword in ['challenge', 'limitation', 'issue']):
                    current_section = 'challenges'
                elif any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'approach']):
                    current_section = 'recommendations'
                
                if line.startswith('-') or line.startswith('*'):
                    if current_section == 'technologies':
                        research_data['technologies'].append(line[1:].strip())
                    elif current_section == 'challenges':
                        research_data['challenges'].append(line[1:].strip())
                    else:
                        research_data['key_concepts'].append(line[1:].strip())
                else:
                    if current_section == 'overview':
                        research_data['overview'] += line + ' '
                    elif current_section == 'recommendations':
                        research_data['recommendations'] += line + ' '
            
            return research_data
        except:
            return {'raw_response': response, 'overview': response[:500]}

    def _format_model_info(self, response: str) -> dict:
        """Format model selection response into structured data"""
        try:
            model_info = {
                'selected_models': [],
                'frameworks': [],
                'justification': '',
                'alternatives': [],
                'raw_response': response
            }
            
            lines = response.strip().split('\n')
            current_section = 'justification'
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if any(keyword in line.lower() for keyword in ['model', 'ai', 'ml', 'framework']):
                    if line.startswith('-') or line.startswith('*'):
                        model_info['selected_models'].append(line[1:].strip())
                elif any(keyword in line.lower() for keyword in ['framework', 'library', 'tool']):
                    if line.startswith('-') or line.startswith('*'):
                        model_info['frameworks'].append(line[1:].strip())
                elif any(keyword in line.lower() for keyword in ['alternative', 'option']):
                    if line.startswith('-') or line.startswith('*'):
                        model_info['alternatives'].append(line[1:].strip())
                else:
                    model_info['justification'] += line + ' '
            
            return model_info
        except:
            return {'raw_response': response, 'justification': response[:500]}

    async def generate_project(self, user_request: str) -> Dict:
        """Main entry point to generate a complete project using the custom workflow"""
        return await self.run_workflow(user_request)
    
    async def _fallback_generate_project(self, user_request: str) -> Dict:
        """Deprecated - now using custom workflow directly"""
        return await self.run_workflow(user_request)


# API endpoint for integration
async def create_advanced_project(user_request: str) -> Dict:
    """Main API function to create advanced projects"""
    system = AdvancedAgentsSystem()
    return await system.generate_project(user_request)


if __name__ == "__main__":
    # Test the system
    async def test_system():
        user_request = "Build a text-to-image generator using AI models"
        result = await create_advanced_project(user_request)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_system())
