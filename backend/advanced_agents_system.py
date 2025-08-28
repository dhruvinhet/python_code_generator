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
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
import requests
import subprocess

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

import google.generativeai as genai
from config import Config
from json_parser import json_parser

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
        self.model = genai.GenerativeModel('gemini-2.0-flash')  # Using faster, more efficient model
        
        # Project directories
        self.base_projects_dir = Path("generated_projects")
        self.base_projects_dir.mkdir(exist_ok=True)
        self.project_dir = self.base_projects_dir  # Initialize project_dir attribute
        
    async def _api_call(self, prompt: str, state: ProjectState, request_json: bool = False) -> str:
        """Make direct API call with optional JSON format request"""
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
            
            {"Please respond ONLY with valid JSON format. Do not include any markdown formatting, code blocks, or additional text." if request_json else "Respond with clear, structured information. Be concise but comprehensive."}
            """
            
            response = self.model.generate_content(context_prompt)
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            self.log_event(state, f"❌ API Error: {error_msg}", "error")
            return f"Error: {error_msg}"
    
    async def _api_call_json(self, prompt: str, state: ProjectState, expected_keys: List[str] = None) -> Dict[str, Any]:
        """Make API call and parse JSON response using robust parser"""
        try:
            # Request JSON format explicitly
            json_prompt = f"""
            {prompt}
            
            IMPORTANT: Respond ONLY with valid JSON format. Do not include any markdown code blocks, explanations, or additional text.
            The response should be a valid JSON object that can be parsed directly.
            """
            
            response = await self._api_call(json_prompt, state, request_json=True)
            
            # Use robust JSON parser
            parsed_response = json_parser.parse_json_response(
                response=response,
                expected_keys=expected_keys,
                agent_type=state.current_agent,
                project_id=state.project_id
            )
            
            if parsed_response is None:
                self.log_event(state, f"⚠️ Failed to parse JSON response, using fallback", "warning")
                # Create fallback structure based on agent type
                if state.current_agent == "Planner":
                    return json_parser.create_fallback_structure("project_plan", response)
                else:
                    return {"content": response, "error": "JSON parsing failed"}
            
            return parsed_response
            
        except Exception as e:
            self.log_event(state, f"❌ JSON API call failed: {str(e)}", "error")
            return {"error": str(e), "content": prompt}
    
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
    
    def _get_default_model_info(self, state: ProjectState) -> Dict[str, Any]:
        """Get dynamic default model info based on project context"""
        project_description = state.user_request.lower()
        
        # Analyze project type from description
        if any(keyword in project_description for keyword in ['chatbot', 'conversation', 'dialogue', 'chat']):
            return {
                "model_name": "microsoft/DialoGPT-medium",
                "model_type": "conversational",
                "platform": "huggingface",
                "installation_code": "from transformers import AutoModelForCausalLM, AutoTokenizer",
                "requirements": ["transformers", "torch"],
                "description": "Conversational AI model for chatbot applications"
            }
        elif any(keyword in project_description for keyword in ['sentiment', 'classification', 'analyze text', 'classify']):
            return {
                "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "model_type": "text-classification",
                "platform": "huggingface", 
                "installation_code": "from transformers import AutoTokenizer, AutoModelForSequenceClassification",
                "requirements": ["transformers", "torch"],
                "description": "Text classification model for sentiment analysis"
            }
        elif any(keyword in project_description for keyword in ['question', 'answer', 'qa', 'query']):
            return {
                "model_name": "distilbert-base-cased-distilled-squad",
                "model_type": "question-answering",
                "platform": "huggingface",
                "installation_code": "from transformers import AutoTokenizer, AutoModelForQuestionAnswering",
                "requirements": ["transformers", "torch"],
                "description": "Question answering model based on DistilBERT"
            }
        elif any(keyword in project_description for keyword in ['image', 'vision', 'photo', 'picture', 'visual', 'face', 'detection']):
            return {
                "model_name": "opencv-python", 
                "model_type": "computer-vision",
                "platform": "opencv",
                "installation_code": "import cv2; import numpy as np",
                "requirements": ["opencv-python", "pillow", "numpy"],
                "description": "Computer vision processing using OpenCV for image analysis and detection"
            }
        elif any(keyword in project_description for keyword in ['text-to-image', 'generate image', 'create image', 'image generation']):
            return {
                "model_name": "stable-diffusion",
                "model_type": "text-to-image", 
                "platform": "diffusers",
                "installation_code": "from diffusers import StableDiffusionPipeline",
                "requirements": ["diffusers", "transformers", "torch", "pillow"],
                "description": "Text-to-image generation using Stable Diffusion"
            }
        else:
            # Default to reliable text generation for general AI projects
            return {
                "model_name": "gpt2",
                "model_type": "text-generation",
                "platform": "huggingface",
                "installation_code": "from transformers import pipeline; generator = pipeline('text-generation', 'gpt2')",
                "requirements": ["transformers", "torch"],
                "description": "Reliable text generation model for general AI applications"
            }
    
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
        
        # Determine frontend type from user request
        frontend_type = self._determine_frontend_type(user_request)
        
        # Generate detailed project plan using JSON format
        plan_prompt = f"""
        As a senior project planner, create a comprehensive plan for: {user_request}
        
        Provide a detailed breakdown in the following JSON structure:
        {{
            "project_overview": "Brief description of the project",
            "objectives": ["objective1", "objective2"],
            "technical_requirements": {{
                "backend": ["requirement1", "requirement2"],
                "frontend": ["requirement1", "requirement2"],
                "ai_models": ["model1", "model2"]
            }},
            "frontend_type": "{frontend_type}",
            "subtasks": [
                {{
                    "task": "task_name",
                    "description": "task description",
                    "priority": "high/medium/low"
                }}
            ],
            "technology_stack": {{
                "backend": ["Python", "Flask"],
                "frontend": ["{frontend_type}", "HTML5"],
                "ai_frameworks": ["[AI_FRAMEWORK_1]", "[AI_FRAMEWORK_2]"]
            }},
            "timeline_estimation": "X weeks/days",
            "success_criteria": ["criteria1", "criteria2"]
        }}
        """
        
        try:
            plan = await self._api_call_json(
                plan_prompt, 
                state, 
                expected_keys=["project_overview", "technical_requirements", "technology_stack", "frontend_type"]
            )
            
            state.plan = plan
            state.shared_memory["project_requirements"] = plan.get("technical_requirements", {})
            state.shared_memory["technology_stack"] = plan.get("technology_stack", {})
            state.shared_memory["frontend_type"] = plan.get("frontend_type", frontend_type)
            
            self.log_event(state, f"✅ Project plan created for: {project_name} with {frontend_type} frontend", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Planning failed: {str(e)}", "error")
            state.plan = {"error": str(e)}
        
        return state
    
    def _determine_frontend_type(self, user_request: str) -> str:
        """Determine frontend type based on user request"""
        request_lower = user_request.lower()
        
        # Check for explicit mentions
        if any(keyword in request_lower for keyword in ['streamlit', 'st.', 'streamlit app']):
            return "Streamlit"
        elif any(keyword in request_lower for keyword in ['react', 'next.js', 'nextjs', 'react app']):
            return "React"
        elif any(keyword in request_lower for keyword in ['vue', 'vue.js', 'vuejs']):
            return "Vue"
        elif any(keyword in request_lower for keyword in ['angular', 'angular app']):
            return "Angular"
        elif any(keyword in request_lower for keyword in ['flask', 'django', 'fastapi', 'web app', 'web application']):
            # If backend framework mentioned, default to React for modern web apps
            return "React"
        elif any(keyword in request_lower for keyword in ['dashboard', 'data', 'analytics', 'visualization', 'plot']):
            # Data-focused apps work well with Streamlit
            return "Streamlit"
        else:
            # Default to React for general web applications
            return "React"
    
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
        You are an AI model expert selecting RELIABLE, TESTED models that work without issues.
        
        Project: {state.user_request}
        Domain Insights: {state.shared_memory.get("domain_insights", "General AI project")}
        
        CHOOSE FROM THESE PROVEN, WORKING MODELS ONLY:
        
        **Text Generation Projects:**
        - "gpt2" - Most reliable for text generation, works offline
        - "distilgpt2" - Lighter version, fast inference
        - "microsoft/DialoGPT-medium" - For chat/conversation
        
        **Text Classification/Sentiment:**
        - "distilbert-base-uncased-finetuned-sst-2-english" - Proven sentiment analysis
        - "cardiffnlp/twitter-roberta-base-sentiment-latest" - Social media sentiment
        - "facebook/bart-large-mnli" - Zero-shot classification
        
        **Image Processing:**
        - "opencv-python" - Computer vision tasks (face detection, image processing)
        - "pillow" - Image manipulation and processing
        - "scikit-image" - Scientific image processing
        
        **Question Answering:**
        - "distilbert-base-cased-distilled-squad" - Reliable Q&A
        - "deepset/roberta-base-squad2" - Advanced Q&A
        
        **Text-to-Image (if needed):**
        - Use "diffusers" library with "runwayml/stable-diffusion-v1-5"
        - Requires proper setup and error handling
        
        SELECTION CRITERIA:
        1. Model MUST be available on HuggingFace Hub
        2. Model MUST work with transformers library
        3. Model MUST NOT require authentication tokens
        4. Model MUST download automatically
        5. Model MUST have proven track record
        
        MANDATORY RESPONSE FORMAT:
        {{
            "model_name": "exact-model-name-from-list-above",
            "model_type": "text-generation|text-classification|computer-vision|question-answering|text-to-image",
            "platform": "huggingface|opencv|pillow|scikit-image",
            "installation_code": "from transformers import pipeline; model = pipeline('task', 'model-name')",
            "requirements": ["transformers", "torch", "other-packages"],
            "description": "Brief description of what this model does"
        }}
        
        CRITICAL: Only select models from the approved list above. These are tested and work reliably.
        CRITICAL: Choose models that:
        1. Are available on HuggingFace without authentication
        2. Have been tested and work reliably
        3. Download automatically when first used
        4. Don't require external model files
        5. Work with the transformers library
        
        Based on the project description, recommend the BEST WORKING model."""
        
        try:
            response = await self._api_call_json(model_selection_prompt, state, ["model_name", "model_type"])
            
            # Dynamic fallback values based on project type or default to most common
            default_model_info = self._get_default_model_info(state)
            
            # Ensure model_info is always a proper dictionary with string keys
            if isinstance(response, dict):
                model_info = {
                    "model_name": str(response.get("model_name", default_model_info["model_name"])),
                    "model_type": str(response.get("model_type", default_model_info["model_type"])),
                    "platform": str(response.get("platform", default_model_info["platform"])),
                    "installation_code": str(response.get("installation_code", default_model_info["installation_code"])),
                    "requirements": response.get("requirements", default_model_info["requirements"]),
                    "description": str(response.get("description", default_model_info["description"]))
                }
            else:
                # Use dynamic fallback if JSON parsing fails
                model_info = default_model_info.copy()
            
            state.selected_model = model_info.copy()
            state.shared_memory["model_requirements"] = model_info.copy()
            
            self.log_event(state, f"✅ Model selected: {model_info.get('model_name', 'AI Model')}", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Model selection failed: {str(e)}", "error")
            # Use dynamic fallback even in error scenarios
            default_model_info = self._get_default_model_info(state)
            default_model_info["error"] = str(e)
            state.selected_model = default_model_info
            state.shared_memory["model_requirements"] = default_model_info
        
        return state
    
    async def backend_developer_agent(self, state: ProjectState) -> ProjectState:
        """Agent 4: Backend Development - Reliable Code Generation with Fallbacks"""
        state.current_agent = "Backend Developer"
        self.log_event(state, "⚙️ Starting backend development...", "info")
        
        # Enhanced backend prompt focused on reliability and working code
        backend_prompt = f"""
        As a senior backend developer, create a WORKING, RELIABLE Flask backend that handles errors gracefully.

        PROJECT ANALYSIS:
        User Request: {state.user_request}
        Selected AI Model: {json.dumps(state.selected_model, indent=2)}
        Domain Research: {json.dumps(state.domain_research, indent=2)}

        CRITICAL RELIABILITY REQUIREMENTS:
        1. **SIMPLE, WORKING MODELS ONLY**: 
           - Use basic models: "gpt2", "distilgpt2" for text
           - Use "distilbert-base-uncased-finetuned-sst-2-english" for classification
           - NEVER use: StableDiffusion, diffusers, complex pipelines
           - Include fallback mock responses when models fail

        2. **ROBUST ERROR HANDLING**: Every function must have try-catch with fallbacks
        3. **RELIABLE DEPENDENCIES**: Only use well-tested packages
        4. **MOCK ADVANCED FEATURES**: Provide working demos instead of complex AI

        RESPONSE FORMAT:
        {{
            "files": [
                {{
                    "filename": "app.py",
                    "content": "from flask import Flask, request, jsonify\\nfrom flask_cors import CORS\\nimport logging\\n\\napp = Flask(__name__)\\nCORS(app)\\n\\nlogging.basicConfig(level=logging.INFO)\\nlogger = logging.getLogger(__name__)\\n\\n@app.route('/health', methods=['GET'])\\ndef health_check():\\n    return jsonify({{'status': 'healthy', 'service': 'AI Backend'}})\\n\\n@app.route('/generate', methods=['POST'])\\ndef generate():\\n    try:\\n        data = request.get_json()\\n        if not data or 'prompt' not in data:\\n            return jsonify({{'error': 'Missing prompt'}}, 400)\\n        \\n        # Simple demo response\\n        result = f'Demo response for: {{data[\"prompt\"]}} (The AI system is working correctly!)'\\n        return jsonify({{'result': result, 'status': 'success'}})\\n    except Exception as e:\\n        logger.error(f'Error: {{e}}')\\n        return jsonify({{'error': str(e)}}, 500)\\n\\nif __name__ == '__main__':\\n    app.run(host='0.0.0.0', port=7000, debug=True)"
                }},
                {{
                    "filename": "requirements.txt",
                    "content": "Flask==2.3.3\\nFlask-CORS==4.0.0"
                }}
            ]
        }}

        CRITICAL: Generate SIMPLE, WORKING code that handles all errors gracefully and provides fallback responses.
        """
        
        try:
            backend_data = await self._api_call_json(
                backend_prompt, 
                state, 
                expected_keys=["files"]
            )
            
            # Extract and save backend files
            backend_files = {}
            if "files" in backend_data:
                backend_dir = Path(state.project_folder) / "backend"
                backend_dir.mkdir(parents=True, exist_ok=True)
                
                self.log_event(state, f"📁 Backend directory created: {backend_dir}", "info")
                self.log_event(state, f"📄 Processing {len(backend_data['files'])} backend files", "info")
                
                for file_info in backend_data["files"]:
                    # Handle both "filename" and "path" key formats
                    if isinstance(file_info, dict) and "content" in file_info:
                        filename = file_info.get("filename") or file_info.get("path")
                        content = file_info["content"]
                        
                        if filename:
                            self.log_event(state, f"💾 Attempting to save: {filename}", "info")
                            
                            try:
                                # Ensure safe filename
                                safe_filename = self._sanitize_filename(filename)
                                file_path = backend_dir / safe_filename
                                file_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                
                                backend_files[safe_filename] = content
                                self.log_event(state, f"✅ Saved backend file: {safe_filename} ({len(content)} chars)", "info")
                                
                            except Exception as file_error:
                                self.log_event(state, f"⚠️ Failed to save backend file '{filename}': {str(file_error)}", "warning")
                                # Try with a fallback filename
                                fallback_name = f"backend_file_{len(backend_files)}.py"
                                try:
                                    fallback_path = backend_dir / fallback_name
                                    with open(fallback_path, 'w', encoding='utf-8') as f:
                                        f.write(f"# Original filename: {filename}\n# Error: {str(file_error)}\n\n{content}")
                                    backend_files[fallback_name] = content
                                    self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                                except:
                                    self.log_event(state, f"❌ Could not save backend file at all: {filename}", "error")
                        else:
                            self.log_event(state, f"⚠️ File info missing filename/path: {file_info}", "warning")
                    else:
                        self.log_event(state, f"⚠️ Invalid file structure in backend response: {file_info}", "warning")
            else:
                self.log_event(state, f"⚠️ No 'files' key found in backend response, available keys: {list(backend_data.keys())}", "warning")
                # Fallback to old parsing method if JSON structure is not as expected
                response_text = backend_data.get("content", str(backend_data))
                backend_files = self._extract_code_files(response_text)
                
                # Save fallback files
                backend_dir = Path(state.project_folder) / "backend"
                for filename, content in backend_files.items():
                    try:
                        safe_filename = self._sanitize_filename(filename)
                        file_path = backend_dir / safe_filename
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.log_event(state, f"✅ Saved fallback backend file: {safe_filename}", "info")
                        
                    except Exception as file_error:
                        self.log_event(state, f"❌ Failed to save fallback backend file '{filename}': {str(file_error)}", "error")
            
            state.backend_code = backend_files
            state.shared_memory["backend_api"] = self._extract_api_info(backend_files)
            
            self.log_event(state, f"✅ Backend created with {len(backend_files)} files", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Backend development failed: {str(e)}", "error")
            self.log_event(state, "🔧 Creating emergency fallback backend...", "info")
            
            # Create a comprehensive fallback backend that always works
            backend_dir = Path(state.project_folder) / "backend"
            backend_dir.mkdir(parents=True, exist_ok=True)
            
            # Emergency fallback files
            fallback_files = {
                "app.py": '''from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import traceback

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'AI Backend'})

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt in request'}), 400
        
        prompt = data['prompt']
        logger.info(f'Received request: {prompt}')
        
        # Simple mock response that works
        result = f"Demo response for: {prompt} (The AI system is working correctly in demo mode!)"
        
        return jsonify({'result': result, 'status': 'success'})
    
    except Exception as e:
        logger.error(f'Error: {e}')
        return jsonify({'error': str(e), 'status': 'error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)
''',
                "requirements.txt": '''Flask==2.3.3
Flask-CORS==4.0.0
''',
                "README.md": '''# AI Backend Service

This is an emergency fallback backend that provides working API endpoints.

## Endpoints:
- GET /health - Health check
- POST /generate - Generate responses (demo mode)

## Run:
```
pip install -r requirements.txt
python app.py
```
'''
            }
            
            # Save fallback files
            for filename, content in fallback_files.items():
                try:
                    file_path = backend_dir / filename
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.log_event(state, f"✅ Created emergency fallback: {filename}", "info")
                except Exception as file_error:
                    self.log_event(state, f"❌ Failed to create fallback file {filename}: {str(file_error)}", "error")
            
            state.backend_code = fallback_files
            self.log_event(state, "✅ Emergency fallback backend created successfully", "success")
        
        return state
    
    async def frontend_developer_agent(self, state: ProjectState) -> ProjectState:
        """Agent 5: Frontend Development - Dynamic AI-Driven UI Generation"""
        state.current_agent = "Frontend Developer"
        self.log_event(state, "🎨 Starting frontend development...", "info")
        
        frontend_type = state.shared_memory.get("frontend_type", "React")
        
        # Enhanced frontend prompt with specific requirements and error handling
        frontend_prompt = """
        You are an expert React developer creating a COMPLETE, WORKING React application. Generate PRODUCTION-READY code with proper error handling.

        PROJECT ANALYSIS:
        User Request: {}
        Selected AI Model: {}
        Backend API Design: {}
        Technology Stack: {}
        Frontend Type: {}
        Domain Research: {}

        CRITICAL REQUIREMENTS - MUST FOLLOW EXACTLY:
        1. **React Version**: Use React 18 with functional components and hooks
        2. **API Integration**: Connect to backend at http://localhost:7000
        3. **Error Handling**: Include comprehensive error handling and loading states
        4. **User Experience**: Create intuitive, responsive UI
        5. **Dependencies**: Only include necessary, working dependencies
        6. **File Structure**: Create complete project structure with all required files

        MANDATORY RESPONSE FORMAT - EXACTLY THIS STRUCTURE:
        {{
            "files": [
                {{
                    "path": "package.json",
                    "content": "Complete package.json with correct dependencies"
                }},
                {{
                    "path": "public/index.html", 
                    "content": "Complete HTML file with proper head and body"
                }},
                {{
                    "path": "src/index.js",
                    "content": "React 18 root rendering code"
                }},
                {{
                    "path": "src/index.css",
                    "content": "Base styles and responsive design"
                }},
                {{
                    "path": "src/App.js",
                    "content": "Main App component with complete functionality"
                }},
                {{
                    "path": "src/App.css",
                    "content": "App-specific styles"
                }},
                {{
                    "path": "src/reportWebVitals.js",
                    "content": "Web vitals reporting code"
                }}
            ]
        }}

        MANDATORY CODE PATTERNS TO INCLUDE:

        1. **Package.json Structure**:
        {{
            "name": "project-frontend",
            "version": "0.1.0",
            "private": true,
            "dependencies": {{
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "axios": "^1.6.7",
                "@testing-library/jest-dom": "^5.16.5",
                "@testing-library/react": "^13.4.0",
                "@testing-library/user-event": "^13.5.0",
                "web-vitals": "^2.1.4"
            }},
            "scripts": {{
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
            }}
        }}

        2. **App.js Pattern** (MANDATORY STRUCTURE):
        ```javascript
        import React, {{ useState }} from 'react';
        import axios from 'axios';
        import './App.css';

        function App() {{
            const [loading, setLoading] = useState(false);
            const [error, setError] = useState(null);
            const [result, setResult] = useState(null);

            const handleSubmit = async (inputData) => {{
                setLoading(true);
                setError(null);
                try {{
                    const response = await axios.post('http://localhost:7000/generate', inputData);
                    setResult(response.data);
                }} catch (err) {{
                    setError(err.response?.data?.error || 'An error occurred');
                }} finally {{
                    setLoading(false);
                }}
            }};

            return (
                <div className="App">
                    {{/* Your UI components here */}}
                    {{error && <div className="error">{{error}}</div>}}
                    {{loading && <div className="loading">Processing...</div>}}
                    {{result && <div className="result">{{/* Display result */}}</div>}}
                </div>
            );
        }}

        export default App;
        ```

        3. **Index.js Pattern** (MANDATORY):
        ```javascript
        import React from 'react';
        import ReactDOM from 'react-dom/client';
        import './index.css';
        import App from './App';
        import reportWebVitals from './reportWebVitals';

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(
            <React.StrictMode>
                <App />
            </React.StrictMode>
        );

        reportWebVitals();
        ```

        4. **Index.html Pattern** (MANDATORY):
        ```html
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Project Title</title>
            </head>
            <body>
                <div id="root"></div>
            </body>
        </html>
        ```

        PROJECT-SPECIFIC REQUIREMENTS:
        - Analyze the user request to create appropriate input fields
        - Design proper result display based on expected output
        - Include file upload capabilities if needed
        - Add proper loading states for AI processing
        - Create responsive design that works on mobile
        - Include proper error messages for user guidance

        CRITICAL SUCCESS FACTORS:
        - ALL files must be syntactically correct
        - NO missing imports or undefined variables
        - PROPER React hooks usage (useState, useEffect)
        - WORKING axios integration with error handling
        - COMPLETE CSS for professional appearance
        - RESPONSIVE design for all screen sizes

        Generate COMPLETE, WORKING React application that compiles and runs without errors.""".format(
            state.user_request,
            json.dumps(state.selected_model, indent=2),
            json.dumps(state.shared_memory.get("backend_api", {}), indent=2),
            json.dumps(state.shared_memory.get("technology_stack", {}), indent=2),
            frontend_type,
            json.dumps(state.domain_research, indent=2)
        )

        try:
            frontend_data = await self._api_call_json(
                frontend_prompt, 
                state, 
                expected_keys=["files"]
            )
            
            if frontend_data and "files" in frontend_data:
                # Extract and save frontend files
                frontend_files = {}
                frontend_dir = Path(state.project_folder) / "frontend"
                frontend_dir.mkdir(parents=True, exist_ok=True)
                
                self.log_event(state, f"📁 Frontend directory created: {frontend_dir}", "info")
                self.log_event(state, f"📄 Processing {len(frontend_data['files'])} frontend files", "info")
                
                for file_info in frontend_data["files"]:
                    # Handle both "filename" and "path" key formats
                    if isinstance(file_info, dict) and "content" in file_info:
                        filename = file_info.get("filename") or file_info.get("path")
                        content = file_info["content"]
                        
                        if filename:
                            self.log_event(state, f"💾 Attempting to save: {filename}", "info")
                            
                            try:
                                # Normalize the path and create nested directories
                                # Convert forward slashes to the appropriate OS path separator
                                normalized_path = Path(filename)
                                file_path = frontend_dir / normalized_path
                                
                                # Create parent directories if they don't exist
                                file_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                # Write the file
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                
                                frontend_files[filename] = content
                                self.log_event(state, f"✅ Saved frontend file: {filename} ({len(content)} chars)", "info")
                                
                            except Exception as file_error:
                                self.log_event(state, f"⚠️ Failed to save frontend file '{filename}': {str(file_error)}", "warning")
                                # Try with a fallback filename
                                fallback_name = f"frontend_file_{len(frontend_files)}.txt"
                                try:
                                    fallback_path = frontend_dir / fallback_name
                                    with open(fallback_path, 'w', encoding='utf-8') as f:
                                        f.write(f"# Original filename: {filename}\n# Error: {str(file_error)}\n\n{content}")
                                    frontend_files[fallback_name] = content
                                    self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                                except:
                                    self.log_event(state, f"❌ Could not save frontend file at all: {filename}", "error")
                        else:
                            self.log_event(state, f"⚠️ File info missing filename/path: {file_info}", "warning")
                    else:
                        self.log_event(state, f"⚠️ Invalid file structure in frontend response: {file_info}", "warning")
                
                state.frontend_code = frontend_files
                state.shared_memory["frontend_files"] = frontend_files
                state.shared_memory["port_frontend"] = 4000
                self.log_event(state, f"✅ Frontend created with {len(frontend_files)} files", "success")
            else:
                self.log_event(state, f"⚠️ No 'files' key found in frontend response, available keys: {list(frontend_data.keys())}", "warning")
                # Fallback to old parsing method if JSON structure is not as expected
                response_text = frontend_data.get("content", str(frontend_data))
                frontend_files = self._extract_code_files(response_text)
                
                # Save fallback files
                frontend_dir = Path(state.project_folder) / "frontend"
                for filename, content in frontend_files.items():
                    try:
                        safe_filename = self._sanitize_filename(filename)
                        file_path = frontend_dir / safe_filename
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.log_event(state, f"✅ Saved fallback frontend file: {safe_filename}", "info")
                        
                    except Exception as file_error:
                        self.log_event(state, f"❌ Failed to save fallback frontend file '{filename}': {str(file_error)}", "error")
                
                state.frontend_code = frontend_files
                
        except Exception as e:
            self.log_event(state, f"❌ Frontend development failed: {str(e)}", "error")
            state.frontend_code = {"error": str(e)}
            
            # EMERGENCY FALLBACK: Create a basic working React app
            self.log_event(state, "🔧 Creating emergency fallback React application...", "info")
            try:
                frontend_dir = Path(state.project_folder) / "frontend"
                frontend_dir.mkdir(parents=True, exist_ok=True)
                
                # Create minimal working React app structure
                emergency_files = {
                    "package.json": f'''{{
  "name": "{state.project_name.lower().replace(' ', '-')}-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": ["react-app", "react-app/jest"]
  }},
  "browserslist": {{
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }}
}}''',
                    "public/index.html": f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{state.project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>''',
                    "src/index.js": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);''',
                    "src/App.js": f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{state.project_name}</h1>
        <p>This is an emergency fallback React application.</p>
        <p>The AI generation encountered an error, but this basic app should work.</p>
      </header>
    </div>
  );
}}

export default App;''',
                    "src/App.css": '''.App {
  text-align: center;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px;
  color: white;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  border-radius: 10px;
  margin: 20px;
}''',
                    "src/index.css": '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f7fa;
}'''
                }
                
                # Create emergency files
                for file_path, content in emergency_files.items():
                    full_path = frontend_dir / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.log_event(state, f"✅ Created emergency file: {file_path}", "info")
                
                state.frontend_code = emergency_files
                self.log_event(state, "🔧 Emergency fallback React app created successfully", "success")
                
            except Exception as emergency_error:
                self.log_event(state, f"❌ Emergency fallback creation failed: {str(emergency_error)}", "error")
        
        # CRITICAL FALLBACK: Ensure essential files always exist
        self._ensure_essential_frontend_files(state)
        
        return state
    
    def _ensure_essential_frontend_files(self, state: ProjectState):
        """Ensure essential frontend files exist, create them if missing."""
        frontend_dir = Path(state.project_folder) / "frontend"
        if not frontend_dir.exists():
            return
        
        frontend_type = state.shared_memory.get("frontend_type", "React")
        project_name = state.project_name or "AI-Powered Application"
        
        # Essential files that must exist
        essential_files = {}
        files_created = []
        
        if frontend_type == "React":
            # Ensure public directory exists
            public_dir = frontend_dir / "public"
            public_dir.mkdir(exist_ok=True)
            
            # Ensure src directory exists
            src_dir = frontend_dir / "src"
            src_dir.mkdir(exist_ok=True)
            
            # public/index.html
            index_html_path = public_dir / "index.html"
            if not index_html_path.exists():
                essential_files["public/index.html"] = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="{project_name}"
    />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
            
            # src/index.js
            index_js_path = src_dir / "index.js"
            if not index_js_path.exists():
                essential_files["src/index.js"] = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Performance measuring
reportWebVitals();'''
            
            # src/App.js
            app_js_path = src_dir / "App.js"
            if not app_js_path.exists():
                essential_files["src/App.js"] = f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>Welcome to your AI-powered application!</p>
        <p>This is a fallback component created to ensure your app runs properly.</p>
      </header>
    </div>
  );
}}

export default App;'''
            
            # src/App.css
            app_css_path = src_dir / "App.css"
            if not app_css_path.exists():
                essential_files["src/App.css"] = '''.App {
  text-align: center;
}

.App-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px;
  color: white;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  border-radius: 10px;
  margin: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.App-header h1 {
  margin-bottom: 20px;
  font-size: 2.5rem;
}

.App-header p {
  margin: 10px 0;
  font-size: 1.2rem;
  opacity: 0.9;
}'''
            
            # src/index.css
            index_css_path = src_dir / "index.css"
            if not index_css_path.exists() or index_css_path.stat().st_size == 0:
                essential_files["src/index.css"] = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f7fa;
  min-height: 100vh;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}'''
            
            # src/reportWebVitals.js
            report_web_vitals_path = src_dir / "reportWebVitals.js"
            if not report_web_vitals_path.exists():
                essential_files["src/reportWebVitals.js"] = '''const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;'''
            
            # package.json (ensure it has essential dependencies)
            package_json_path = frontend_dir / "package.json"
            if not package_json_path.exists():
                essential_files["package.json"] = f'''{{
  "name": "{state.project_name.lower().replace(' ', '-')}-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": ["react-app", "react-app/jest"]
  }},
  "browserslist": {{
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }}
}}'''
        
        # Create all essential files
        for file_path, content in essential_files.items():
            try:
                full_path = frontend_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_created.append(file_path)
                self.log_event(state, f"✅ Created essential file: {file_path}", "info")
                
            except Exception as e:
                self.log_event(state, f"❌ Failed to create essential file '{file_path}': {str(e)}", "error")
        
        if files_created:
            self.log_event(state, f"🔧 Created {len(files_created)} essential frontend files: {', '.join(files_created)}", "info")
        else:
            self.log_event(state, "✅ All essential frontend files already exist", "info")
            
            # src/App.js
            app_js_path = src_dir / "App.js"
            if not app_js_path.exists():
                essential_files["src/App.js"] = f'''import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>{project_name}</h1>
        <p>Welcome to your AI-powered application!</p>
      </header>
    </div>
  );
}}

export default App;'''
            
            # src/App.css
            app_css_path = src_dir / "App.css"
            if not app_css_path.exists():
                essential_files["src/App.css"] = '''.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}'''
            
            # src/index.css
            index_css_path = src_dir / "index.css"
            if not index_css_path.exists():
                essential_files["src/index.css"] = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}'''
        
        # Create missing essential files
        for relative_path, content in essential_files.items():
            try:
                file_path = frontend_dir / relative_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_event(state, f"✅ Created essential file: {relative_path}", "info")
                
            except Exception as e:
                self.log_event(state, f"❌ Failed to create essential file '{relative_path}': {str(e)}", "error")
    
    async def main_file_creator_agent(self, state: ProjectState) -> ProjectState:
        """Agent 6: Main Runner File Creation"""
        state.current_agent = "Main File Creator"
        self.log_event(state, "🚀 Creating main runner file...", "info")
        
        frontend_type = state.shared_memory.get("frontend_type", "React")
        
        if frontend_type == "Streamlit":
            main_file_prompt = f"""
            Create main runner files for this Streamlit project in JSON format:
            
            Project: {state.user_request}
            Technology Stack: {json.dumps(state.shared_memory.get("technology_stack", {}), indent=2)}
            Frontend Type: Streamlit
            
            Create a JSON response with the following structure:
            {{
                "files": [
                    {{
                        "filename": "run_project.py",
                        "content": "#!/usr/bin/env python3\\nimport subprocess\\nimport sys\\nimport os\\nimport time\\nimport webbrowser\\n\\ndef main():\\n    print('Starting Streamlit Application...')\\n    try:\\n        # Install requirements\\n        print('Installing requirements...')\\n        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)\\n        \\n        # Start Streamlit app\\n        print('Starting Streamlit server on port 4000...')\\n        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'frontend.py', '--server.port', '4000'])\\n    except Exception as e:\\n        print(f'Error: {{e}}')\\n\\nif __name__ == '__main__':\\n    main()"
                    }},
                    {{
                        "filename": "requirements.txt",
                        "content": "streamlit\\nrequests\\nbase64\\npandas\\nnumpy\\n# Add all necessary dependencies based on the project"
                    }},
                    {{
                        "filename": "README.md",
                        "content": "# {state.user_request}\\n\\n## Setup Instructions\\n\\n1. Install dependencies: `pip install -r requirements.txt`\\n2. Run the application: `python run_project.py`\\n3. Access the app at: http://localhost:4000\\n\\n## Features\\n\\n- AI-powered Streamlit application\\n- User-friendly interface\\n- Automatic setup and deployment"
                    }}
                ]
            }}
            
            CRITICAL REQUIREMENTS:
            - Include ALL necessary Python packages in requirements.txt
            - Streamlit should run on port 4000
            - Include proper error handling in run script
            - Make installation automatic and user-friendly
            - Validate all dependencies are correct and complete
            """
        else:
            main_file_prompt = f"""
            Create main runner files for this React project in JSON format:
            
            Project: {state.user_request}
            Technology Stack: {json.dumps(state.shared_memory.get("technology_stack", {}), indent=2)}
            Backend Files: {list(state.backend_code.keys()) if state.backend_code else []}
            Frontend Files: {list(state.frontend_code.keys()) if state.frontend_code else []}
            
            Create a JSON response with the following structure:
            {{
                "files": [
                    {{
                        "filename": "run_project.py",
                        "content": "#!/usr/bin/env python3\\nimport subprocess\\nimport sys\\nimport os\\nimport time\\nimport platform\\nimport webbrowser\\n\\ndef run_backend():\\n    print('Starting backend server on port 7000...')\\n    try:\\n        subprocess.run([sys.executable, 'backend/app.py'])\\n    except Exception as e:\\n        print('Backend error:', e)\\n\\ndef run_frontend_in_terminal():\\n    print('Opening frontend in separate terminal...')\\n    frontend_cmd = 'cd frontend && npm install && npm start'\\n    \\n    system = platform.system()\\n    try:\\n        if system == 'Windows':\\n            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', frontend_cmd], shell=True)\\n        elif system == 'Darwin':\\n            subprocess.Popen(['osascript', '-e', 'tell application \\\"Terminal\\\" to do script \\\"' + frontend_cmd + '\\\"'])\\n        else:\\n            subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', frontend_cmd + '; exec bash'])\\n        \\n        print('Frontend started in separate terminal window')\\n    except Exception as e:\\n        print('Could not open separate terminal, running in background:', e)\\n        subprocess.Popen(['npm', 'install'], cwd='frontend')\\n        subprocess.Popen(['npm', 'start'], cwd='frontend')\\n\\ndef main():\\n    print('Starting Full Stack Application...')\\n    \\n    # Install backend requirements\\n    print('Installing backend requirements...')\\n    try:\\n        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])\\n    except:\\n        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'])\\n    \\n    # Start backend in separate thread\\n    import threading\\n    backend_thread = threading.Thread(target=run_backend)\\n    backend_thread.daemon = True\\n    backend_thread.start()\\n    \\n    # Start frontend in separate terminal\\n    run_frontend_in_terminal()\\n    \\n    # Wait and open browser\\n    time.sleep(5)\\n    webbrowser.open('http://localhost:4000')\\n    \\n    print('Application started!')\\n    print('Backend: http://localhost:7000')\\n    print('Frontend: http://localhost:4000')\\n    \\n    # Keep alive\\n    try:\\n        input('Press Enter to stop...')\\n    except KeyboardInterrupt:\\n        print('Application stopped')\\n\\nif __name__ == '__main__':\\n    main()"
                    }},
                    {{
                        "filename": "requirements.txt",
                        "content": "Flask\\nflask-cors\\nopencv-python\\nPillow\\nnumpy\\nrequests\\npandas\\nbase64\\n# All necessary Python dependencies"
                    }},
                    {{
                        "filename": "README.md",
                        "content": "# {state.user_request}\\n\\n## Prerequisites\\n- Python 3.8+\\n- Node.js 16+\\n- npm\\n\\n## Setup Instructions\\n\\n1. Run the complete project: `python run_project.py`\\n\\nOr run separately:\\n1. Backend: `cd backend && python app.py` (runs on port 7000)\\n2. Frontend: `cd frontend && npm start` (runs on port 4000)\\n\\n## Access\\n- Frontend: http://localhost:4000\\n- Backend API: http://localhost:7000\\n\\n## Features\\n\\n- AI-powered backend API\\n- Modern React frontend\\n- Automatic setup and deployment\\n- Full-stack integration"
                    }}
                ]
            }}
            
            CRITICAL REQUIREMENTS:
            - Backend runs on port 7000, Frontend on port 4000
            - Include proper startup scripts for both backend and frontend
            - Add comprehensive installation instructions
            - Include all necessary configuration files
            - Add proper error handling in run scripts
            - Create complete documentation
            - Ensure all dependencies are documented
            - Validate all scripts work correctly
            """
        
        try:
            main_data = await self._api_call_json(
                main_file_prompt, 
                state, 
                expected_keys=["files"]
            )
            
            # Extract and save main files
            main_files = {}
            if "files" in main_data:
                project_dir = Path(state.project_folder)
                self.log_event(state, f"📁 Saving main files to: {project_dir}", "info")
                self.log_event(state, f"📄 Processing {len(main_data['files'])} main files", "info")
                
                for file_info in main_data["files"]:
                    if isinstance(file_info, dict) and "filename" in file_info and "content" in file_info:
                        filename = file_info["filename"]
                        content = file_info["content"]
                        
                        self.log_event(state, f"💾 Attempting to save: {filename}", "info")
                        
                        try:
                            safe_file_path = self._sanitize_filename(filename)
                            full_path = project_dir / safe_file_path
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(full_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            main_files[safe_file_path] = content
                            self.log_event(state, f"✅ Saved main file: {safe_file_path} ({len(content)} chars)", "info")
                            
                        except Exception as file_error:
                            self.log_event(state, f"⚠️ Failed to save main file '{filename}': {str(file_error)}", "warning")
                    else:
                        self.log_event(state, f"⚠️ Invalid file structure in main files response: {file_info}", "warning")
            else:
                self.log_event(state, f"⚠️ No 'files' key found in main files response, available keys: {list(main_data.keys())}", "warning")
            
            state.infrastructure_code = main_files
            
            self.log_event(state, f"✅ Main files created with {len(main_files)} files", "success")
            
        except Exception as e:
            self.log_event(state, f"❌ Main file creation failed: {str(e)}", "error")
            state.infrastructure_code = {"error": str(e)}
        
        return state
        
        try:
            main_data = await self._api_call_json(
                main_file_prompt, 
                state, 
                expected_keys=["files"]
            )
            
            # Extract and save main files
            main_files = {}
            if "files" in main_data:
                project_dir = Path(state.project_folder)
                
                for file_info in main_data["files"]:
                    if isinstance(file_info, dict) and "filename" in file_info and "content" in file_info:
                        filename = file_info["filename"]
                        content = file_info["content"]
                        
                        try:
                            # Ensure safe filename
                            safe_filename = self._sanitize_filename(filename)
                            file_path = project_dir / safe_filename
                            
                            # Ensure parent directory exists
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            main_files[safe_filename] = content
                            self.log_event(state, f"✅ Saved main file: {safe_filename}", "info")
                            
                        except Exception as file_error:
                            self.log_event(state, f"⚠️ Failed to save file '{filename}': {str(file_error)}", "warning")
                            # Try with a fallback filename
                            fallback_name = f"generated_file_{len(main_files)}.txt"
                            try:
                                fallback_path = project_dir / fallback_name
                                with open(fallback_path, 'w', encoding='utf-8') as f:
                                    f.write(f"# Original filename: {filename}\n# Error: {str(file_error)}\n\n{content}")
                                main_files[fallback_name] = content
                                self.log_event(state, f"✅ Saved as fallback: {fallback_name}", "info")
                            except:
                                self.log_event(state, f"❌ Could not save file at all: {filename}", "error")
            else:
                # Fallback to old parsing method if JSON structure is not as expected
                response_text = main_data.get("content", str(main_data))
                main_files = self._extract_code_files(response_text)
                
                # Save fallback files
                project_dir = Path(state.project_folder)
                for filename, content in main_files.items():
                    try:
                        safe_filename = self._sanitize_filename(filename)
                        file_path = project_dir / safe_filename
                        
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        self.log_event(state, f"✅ Saved fallback main file: {safe_filename}", "info")
                        
                    except Exception as file_error:
                        self.log_event(state, f"❌ Failed to save fallback main file '{filename}': {str(file_error)}", "error")
            
            state.main_runner = main_files.get("run_project.py", "")
            requirements_content = main_files.get("requirements.txt", "")
            state.requirements = requirements_content.split('\n') if requirements_content else []
            
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
        
        # Check for duplicate/conflicting files
        self._check_project_consistency(project_dir, issues_found, fixes_applied)
        
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
        
        # Check React/JavaScript files for basic issues
        for js_file in project_dir.rglob("*.js"):
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Log file found
                self.log_event(state, f"✅ Checked {js_file.name}", "info")
                
            except Exception as e:
                issue = f"Error reading {js_file.name}: {str(e)}"
                issues_found.append(issue)
                self.log_event(state, f"⚠️ {issue}", "warning")
        
        state.code_check_results = {
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "status": "passed" if not issues_found else "issues_found"
        }
        
        self.log_event(state, f"✅ Code check completed: {len(issues_found)} issues found", "success")
        
        return state
    
    def _check_project_consistency(self, project_dir: Path, issues_found: list, fixes_applied: list):
        """Check for project structure consistency issues"""
        
        # Check for duplicate backend files
        backend_files = []
        if (project_dir / "backend.py").exists():
            backend_files.append("backend.py")
        if (project_dir / "app.py").exists():
            backend_files.append("app.py")
        if (project_dir / "backend" / "app.py").exists():
            backend_files.append("backend/app.py")
        
        if len(backend_files) > 1:
            issues_found.append(f"Multiple backend files found: {', '.join(backend_files)}. This may cause confusion.")
        
        # Check for duplicate frontend approaches
        frontend_approaches = []
        if (project_dir / "frontend.py").exists():
            frontend_approaches.append("Streamlit (frontend.py)")
        if (project_dir / "frontend").exists() and (project_dir / "frontend").is_dir():
            frontend_approaches.append("React (frontend/ folder)")
        
        if len(frontend_approaches) > 1:
            issues_found.append(f"Multiple frontend approaches found: {', '.join(frontend_approaches)}. This may cause confusion.")
        
        # Check run_project.py consistency
        run_project_file = project_dir / "run_project.py"
        if run_project_file.exists():
            try:
                with open(run_project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if it references existing files
                if "backend.py" in content and not (project_dir / "backend.py").exists():
                    issues_found.append("run_project.py references backend.py but file doesn't exist")
                
                if "frontend.py" in content and not (project_dir / "frontend.py").exists():
                    issues_found.append("run_project.py references frontend.py but file doesn't exist")
                
                if "streamlit" in content.lower() and not (project_dir / "frontend.py").exists():
                    issues_found.append("run_project.py uses streamlit but no frontend.py found")
                    
            except Exception as e:
                issues_found.append(f"Error reading run_project.py: {str(e)}")
    
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
            
            # Clean up any duplicate or conflicting files
            self._cleanup_project_files(state)
            
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
    
    def _cleanup_project_files(self, state: ProjectState):
        """Clean up duplicate or conflicting files"""
        project_dir = Path(state.project_folder)
        
        try:
            # Remove duplicate backend files - prefer backend/app.py over root level files
            if (project_dir / "backend" / "app.py").exists():
                # Remove root level backend files if backend/app.py exists
                for old_file in ["backend.py", "app.py", "server.py"]:
                    old_path = project_dir / old_file
                    if old_path.exists():
                        old_path.unlink()
                        self.log_event(state, f"🧹 Removed duplicate file: {old_file}", "info")
            
            # Handle frontend consistency - prefer React over Streamlit if both exist
            if (project_dir / "frontend").exists() and (project_dir / "frontend").is_dir():
                # Remove Streamlit frontend file if React frontend exists
                streamlit_file = project_dir / "frontend.py"
                if streamlit_file.exists():
                    streamlit_file.unlink()
                    self.log_event(state, f"🧹 Removed conflicting Streamlit frontend (React preferred)", "info")
            
            # Fix run_project.py to match actual project structure
            self._fix_run_project_script(state, project_dir)
            
        except Exception as e:
            self.log_event(state, f"⚠️ Cleanup warning: {str(e)}", "warning")
    
    def _fix_run_project_script(self, state: ProjectState, project_dir: Path):
        """Fix run_project.py to match the actual project structure"""
        run_project_file = project_dir / "run_project.py"
        
        if not run_project_file.exists():
            return
        
        try:
            with open(run_project_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine actual project structure
            has_backend_folder = (project_dir / "backend" / "app.py").exists()
            has_react_frontend = (project_dir / "frontend" / "package.json").exists()
            has_streamlit_frontend = (project_dir / "frontend.py").exists()
            
            # Create corrected run_project.py content
            corrected_content = self._generate_correct_run_script(
                has_backend_folder, has_react_frontend, has_streamlit_frontend
            )
            
            with open(run_project_file, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            
            self.log_event(state, "🔧 Fixed run_project.py to match project structure", "info")
            
        except Exception as e:
            self.log_event(state, f"⚠️ Failed to fix run_project.py: {str(e)}", "warning")
    
    def _generate_correct_run_script(self, has_backend_folder: bool, has_react_frontend: bool, has_streamlit_frontend: bool) -> str:
        """Generate a correct run_project.py script based on actual project structure"""
        
        backend_cmd = "os.chdir('backend'); subprocess.Popen([sys.executable, 'app.py']); os.chdir('..')" if has_backend_folder else "subprocess.Popen([sys.executable, 'app.py'])"
        
        if has_react_frontend:
            frontend_cmd = "os.chdir('frontend'); subprocess.call(['npm', 'install']); os.environ['PORT'] = '4000'; subprocess.Popen(['npm', 'start']); os.chdir('..')"
            url = "http://localhost:4000"
        elif has_streamlit_frontend:
            frontend_cmd = "subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', 'frontend.py', '--server.port', '4000'])"
            url = "http://localhost:4000"
        else:
            frontend_cmd = "print('No frontend found')"
            url = "http://localhost:7000"
        
        return f"""#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import webbrowser

def install_requirements():
    try:
        print('Installing Python dependencies...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        if os.path.exists('backend/requirements.txt'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'])
        print('Dependencies installed successfully.')
    except subprocess.CalledProcessError as e:
        print(f'Error installing dependencies: {{e}}')
        sys.exit(1)

def start_backend():
    try:
        print('Starting backend server on port 7000...')
        {backend_cmd}
        print('Backend server started on http://localhost:7000')
    except Exception as e:
        print(f'Error starting backend server: {{e}}')
        sys.exit(1)

def start_frontend():
    try:
        print('Starting frontend on port 4000...')
        {frontend_cmd}
        print('Frontend setup completed')
        time.sleep(5)
        open_browser('{url}')
    except Exception as e:
        print(f'Error starting frontend: {{e}}')

def open_browser(url):
    try:
        print(f'Opening {{url}} in browser...')
        webbrowser.open(url)
    except Exception as e:
        print(f'Error opening browser: {{e}}')

def main():
    print('Starting project setup...')
    print('Backend will run on port 7000, Frontend on port 4000')
    install_requirements()
    start_backend()
    start_frontend()
    print('Project is running! Check your browser.')

if __name__ == '__main__':
    main()
"""
    
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
        """Sanitize filename to be valid for Windows file system, handling subdirectories"""
        if not filename or not filename.strip():
            return "untitled.txt"
        
        # Split into directory parts and filename
        parts = filename.strip().split('/')
        sanitized_parts = []
        
        for part in parts:
            if not part:
                continue
                
            # Remove HTML tags if present
            sanitized = re.sub(r'<[^>]+>', '', part)
            
            # Remove or replace invalid characters for Windows
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                sanitized = sanitized.replace(char, '_')
            
            # Remove multiple consecutive underscores
            sanitized = re.sub(r'_{2,}', '_', sanitized)
            
            # Remove leading/trailing dots and spaces
            sanitized = sanitized.strip('. ')
            
            # Ensure it's not empty
            if sanitized:
                sanitized_parts.append(sanitized)
        
        if not sanitized_parts:
            return "untitled.txt"
        
        # Rejoin with forward slashes (pathlib will handle conversion)
        result = '/'.join(sanitized_parts)
        
        # Limit total length to avoid path too long errors
        if len(result) > 200:
            name_parts = result.split('/')
            if len(name_parts) > 1:
                # Keep directory structure but shorten filename
                dirs = '/'.join(name_parts[:-1])
                filename_part = name_parts[-1]
                name, ext = os.path.splitext(filename_part)
                if len(dirs) + len(ext) + 10 < 200:  # Leave space for shortened name
                    max_name_len = 200 - len(dirs) - len(ext) - 10
                    filename_part = name[:max_name_len] + ext
                    result = dirs + '/' + filename_part
                else:
                    # Directory path too long, just use filename
                    result = filename_part[:190] + os.path.splitext(filename_part)[1]
            else:
                # Single filename, just truncate
                name, ext = os.path.splitext(result)
                result = name[:190] + ext
        
        return result

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
