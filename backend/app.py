from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import os
import threading
import zipfile
import re
import json
import logging
from datetime import datetime
from project_manager import ProjectManager
from advanced_agents_system import create_advanced_project
from config import Config
from parsing_debugger import debug_logger

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set json_parser to DEBUG level for detailed parsing logs
logging.getLogger('json_parser').setLevel(logging.DEBUG)

# Try to import data_cleaner, but don't crash if dependencies are missing
try:
    from data_cleaner import data_cleaner
    DATA_CLEANER_AVAILABLE = True
except ImportError as e:
    print(f"Data cleaner not available: {e}")
    data_cleaner = None
    DATA_CLEANER_AVAILABLE = False

# Try to import PPT functionality, but don't crash if dependencies are missing
try:
    # Suppress Pydantic warnings for PPT components
    import warnings
    from pydantic._internal._config import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
    warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
    
    from ppt.project_manager import PPTProjectManager
    from ppt.themes import PPTThemes
    PPT_AVAILABLE = True
    print("✅ PPT functionality is available")
except ImportError as e:
    print(f"⚠️  PPT functionality not available: {e}")
    PPTProjectManager = None
    PPTThemes = None
    PPT_AVAILABLE = False
except Exception as e:
    print(f"⚠️  PPT functionality disabled due to error: {e}")
    print("📋 Creating fallback PPT functionality...")
    PPTProjectManager = None
    PPTThemes = None
    PPT_AVAILABLE = "FALLBACK"  # Use fallback mode

# Try to import blog functionality
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'blog'))
    
    from blog.youtube_blog_generator import generate_blog_from_youtube
    from blog.blog_main import AccuracyResearcher, InterviewBlogGenerator, quick_generate, youtube_generate
    
    BLOG_AVAILABLE = True
    print("✅ Blog functionality is available")
except ImportError as e:
    print(f"⚠️  Blog functionality not available: {e}")
    BLOG_AVAILABLE = False
    generate_blog_from_youtube = None
    AccuracyResearcher = None
    InterviewBlogGenerator = None
    quick_generate = None
    youtube_generate = None

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global project manager instance
project_manager = ProjectManager(socketio)

# Initialize PPT project manager if available
if PPT_AVAILABLE == True:
    ppt_project_manager = PPTProjectManager(socketio=socketio)
    print("PPT Project Manager initialized")
elif PPT_AVAILABLE == "FALLBACK":
    # Create simple fallback functionality
    class FallbackPPTManager:
        def __init__(self):
            self.projects = {}
            
        def get_all_projects(self):
            return []
            
        def create_project(self, **kwargs):
            return {"success": False, "error": "PPT functionality temporarily unavailable due to dependency issues"}
            
        def get_project_status(self, project_id):
            return {"success": False, "error": "PPT functionality temporarily unavailable"}
    
    class FallbackThemes:
        @staticmethod
        def get_all_themes():
            return {
                "corporate_blue": {
                    "name": "Corporate Blue",
                    "description": "Professional blue theme",
                    "primary_color": "#2563eb",
                    "secondary_color": "#1e40af"
                },
                "modern_purple": {
                    "name": "Modern Purple", 
                    "description": "Contemporary purple theme",
                    "primary_color": "#7c3aed",
                    "secondary_color": "#5b21b6"
                },
                "clean_green": {
                    "name": "Clean Green",
                    "description": "Fresh green theme",
                    "primary_color": "#059669", 
                    "secondary_color": "#047857"
                }
            }
    
    ppt_project_manager = FallbackPPTManager()
    PPTThemes = FallbackThemes
    print("📋 Fallback PPT functionality initialized")
else:
    ppt_project_manager = None

# Store active projects
active_projects = {}

@app.route('/')
def index():
    return jsonify({
        "message": "Python Code Generator API",
        "version": "1.0.0",
        "status": "running",
        "data_endpoints": [
            "/api/data/upload",
            "/api/data/analyze", 
            "/api/data/graphs",
            "/api/data/clean",
            "/api/data/download/<filename>"
        ]
    })

@app.route('/api/generate', methods=['POST'])
def generate_project():
    """Start project generation process"""
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        mode = data.get('mode', 'simple')

        if not user_prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Generate unique project ID
        project_id = str(uuid.uuid4())

        # Store project info
        active_projects[project_id] = {
            "id": project_id,
            "prompt": user_prompt,
            "mode": mode,
            "status": "started",
            "created_at": datetime.now().isoformat()
        }

        # Start project generation in background thread
        def generate_in_background():
            try:
                if mode == 'multi_agent':
                    # Use new advanced agents system with LangGraph
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        create_advanced_project(user_prompt)
                    )
                    
                    # Update project status
                    active_projects[project_id].update({
                        "status": "completed" if result.get('success') else "failed",
                        "result": result,
                        "project_folder": result.get("project_folder"),
                        "project_name": result.get("project_name"),
                        "completed_at": datetime.now().isoformat()
                    })
                else:
                    # Use simple generation
                    result = project_manager.generate_project(user_prompt, project_id, mode=mode)
                    active_projects[project_id].update({
                        "status": "completed" if result.get("success") else "failed",
                        "result": result,
                        "completed_at": datetime.now().isoformat()
                    })

                # Emit completion event
                socketio.emit('project_completed', {
                    "project_id": project_id,
                    "success": result.get("success"),
                    "result": result
                })

            except Exception as e:
                active_projects[project_id].update({
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat()
                })

                socketio.emit('project_failed', {
                    "project_id": project_id,
                    "error": str(e)
                })

        thread = threading.Thread(target=generate_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({
            "project_id": project_id,
            "status": "started",
            "message": "Project generation started"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/projects/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """Get project status"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    return jsonify(active_projects[project_id])

@app.route('/api/projects/<project_id>/download', methods=['GET'])
def download_project(project_id):
    """Download project zip file"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = active_projects[project_id]
    if project["status"] != "completed":
        return jsonify({"error": "Project not completed"}), 400
    
    result = project.get("result", {})
    zip_path = result.get("zip_path")
    
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({"error": "Project file not found"}), 404
    
    try:
        # Verify the zip file is valid before sending
        with zipfile.ZipFile(zip_path, 'r') as test_zip:
            # This will raise an exception if the zip is corrupted
            test_zip.testzip()
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"python_project_{project_id}.zip",
            mimetype='application/zip'
        )
    except zipfile.BadZipFile:
        return jsonify({"error": "Project file is corrupted"}), 500
    except Exception as e:
        return jsonify({"error": f"Error accessing project file: {str(e)}"}), 500

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    return jsonify(list(active_projects.values()))

@app.route('/api/projects/history', methods=['GET'])
def get_project_history():
    """Get project history with additional metadata"""
    try:
        projects = []
        projects_dir = Config.GENERATED_PROJECTS_DIR
        
        if not os.path.exists(projects_dir):
            return jsonify([])
        
        # Scan the filesystem for all project directories
        for project_folder in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_folder)
            if os.path.isdir(project_path):
                try:
                    # Initialize default values
                    project_name = "Python Project"
                    description = "No description available"
                    
                    # Try to read project metadata from README.md
                    readme_path = os.path.join(project_path, "README.md")
                    if os.path.exists(readme_path):
                        try:
                            with open(readme_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                lines = content.split('\n')
                                
                                # Extract project name from first heading
                                for line in lines:
                                    if line.strip().startswith('# '):
                                        project_name = line.strip()[2:]
                                        break
                                
                                # Extract description from content
                                for i, line in enumerate(lines):
                                    if line.strip() and not line.startswith('#') and not line.startswith('```'):
                                        description = line.strip()
                                        break
                                        
                                # Limit description length
                                if len(description) > 100:
                                    description = description[:100] + "..."
                                    
                        except Exception as e:
                            print(f"Error reading README for {project_folder}: {e}")
                    
                    # Get creation time from directory
                    creation_time = os.path.getctime(project_path)
                    created_at = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Count files in the project
                    file_count = 0
                    for root, dirs, files in os.walk(project_path):
                        # Skip __pycache__ directories
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        # Count only non-pyc files
                        file_count += len([f for f in files if not f.endswith('.pyc')])
                    
                    # Check if this project is in active_projects (recently generated)
                    status = 'completed'
                    if project_folder in active_projects:
                        status = active_projects[project_folder].get('status', 'completed')
                    
                    project_info = {
                        'id': project_folder,
                        'name': project_name,
                        'description': description,
                        'status': status,
                        'created_at': created_at,
                        'file_count': file_count
                    }
                    projects.append(project_info)
                    
                except Exception as e:
                    print(f"Error processing project {project_folder}: {e}")
                    continue
        
        # Sort by creation time (newest first)
        projects.sort(key=lambda x: x['created_at'], reverse=True)
        return jsonify(projects)
        
    except Exception as e:
        print(f"Error in get_project_history: {e}")
        return jsonify({"error": f"Failed to get project history: {str(e)}"}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    if project_id not in active_projects:
        return jsonify({"error": "Project not found"}), 404
    
    # Clean up files
    project = active_projects[project_id]
    result = project.get("result", {})
    
    # Remove zip file
    zip_path = result.get("zip_path")
    if zip_path and os.path.exists(zip_path):
        os.remove(zip_path)
    
    # Remove project directory
    project_dir = result.get("project_dir")
    if project_dir and os.path.exists(project_dir):
        import shutil
        shutil.rmtree(project_dir)
    
    # Remove from active projects
    del active_projects[project_id]
    
    return jsonify({"message": "Project deleted successfully"})

@app.route('/api/projects/<project_id>/files', methods=['GET'])
def get_project_files(project_id):
    """Get all files in a project"""
    try:
        project_path = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
        
        if not os.path.exists(project_path):
            return jsonify({"error": "Project not found"}), 404
        
        files = []
        for root, dirs, filenames in os.walk(project_path):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for filename in filenames:
                if filename.endswith('.pyc'):
                    continue
                    
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, project_path)
                
                files.append({
                    'name': filename,
                    'path': relative_path,
                    'full_path': file_path,
                    'size': os.path.getsize(file_path)
                })
        
        return jsonify(files)
        
    except Exception as e:
        return jsonify({"error": f"Failed to get project files: {str(e)}"}), 500

@app.route('/api/projects/<project_id>/files/<path:file_path>', methods=['GET'])
def get_file_content(project_id, file_path):
    """Get content of a specific file"""
    try:
        project_path = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
        full_file_path = os.path.join(project_path, file_path)
        
        if not os.path.exists(project_path):
            return jsonify({"error": "Project not found"}), 404
            
        if not os.path.exists(full_file_path):
            return jsonify({"error": "File not found"}), 404
        
        # Security check - ensure file is within project directory
        if not os.path.abspath(full_file_path).startswith(os.path.abspath(project_path)):
            return jsonify({"error": "Access denied"}), 403
        
        try:
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding for binary files
            try:
                with open(full_file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                content = "[Binary file - cannot display content]"
        
        return jsonify({
            'content': content,
            'path': file_path,
            'size': os.path.getsize(full_file_path)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get file content: {str(e)}"}), 500

@app.route('/api/projects/<project_id>/run', methods=['POST'])
def run_project(project_id):
    """Run the project and return execution output"""
    try:
        # Check if project exists on filesystem (don't require it to be in active_projects)
        project_path = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
        
        if not os.path.exists(project_path):
            return jsonify({"error": "Project directory not found"}), 404
        
        # Check for entry point files in order of preference
        entry_files = ['main.py', 'run.py']
        entry_file = None
        
        for file in entry_files:
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path):
                entry_file = file
                break
        
        if not entry_file:
            return jsonify({"error": "No entry point file found (main.py, app.py, or run.py)"}), 404
        
        # Determine run method by analyzing project structure and requirements.txt
        run_method = project_manager.determine_run_method(project_path)
        
        # If project is not in active_projects, add a basic entry for execution tracking
        if project_id not in active_projects:
            active_projects[project_id] = {
                "id": project_id,
                "status": "completed",  # Assume existing projects are completed
                "created_at": datetime.now().isoformat()
            }
        
        # Start project execution in background
        def run_project_async():
            try:
                result = project_manager.execute_project(project_id, project_path, run_method)
                active_projects[project_id]["execution"] = result
                socketio.emit('execution_complete', {
                    'project_id': project_id,
                    'result': result
                })
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': str(e),
                    'output': '',
                    'method': run_method
                }
                active_projects[project_id]["execution"] = error_result
                socketio.emit('execution_error', {
                    'project_id': project_id,
                    'error': error_result
                })
        
        thread = threading.Thread(target=run_project_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "message": "Project execution started",
            "run_method": run_method,
            "project_id": project_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to run project: {str(e)}"}), 500

@app.route('/api/projects/<project_id>/execution', methods=['GET'])
def get_execution_status(project_id):
    """Get current execution status and output"""
    try:
        if project_id not in active_projects:
            return jsonify({"error": "Project not found"}), 404
        
        project = active_projects[project_id]
        execution = project.get("execution", {"status": "not_started"})
        
        return jsonify(execution)
        
    except Exception as e:
        return jsonify({"error": f"Failed to get execution status: {str(e)}"}), 500

@app.route('/api/projects/<project_id>/stop', methods=['POST'])
def stop_project(project_id):
    """Stop running project"""
    try:
        # Stop the project execution
        result = project_manager.stop_project_execution(project_id)
        
        # Also remove from active_projects execution tracking
        if project_id in active_projects and "execution" in active_projects[project_id]:
            del active_projects[project_id]["execution"]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Failed to stop project: {str(e)}"}), 500

@app.route('/api/projects/running', methods=['GET'])
def get_running_projects():
    """Get list of currently running projects"""
    try:
        running = project_manager.get_running_projects()
        return jsonify(running)
    except Exception as e:
        return jsonify({"error": f"Failed to get running projects: {str(e)}"}), 500

@app.route('/api/projects/<project_id>/is-running', methods=['GET'])
def is_project_running(project_id):
    """Check if a specific project is currently running"""
    try:
        if not hasattr(project_manager, 'running_processes'):
            return jsonify({"running": False})
        
        if project_id not in project_manager.running_processes:
            return jsonify({"running": False})
        
        process = project_manager.running_processes[project_id]
        is_running = process.poll() is None
        
        if not is_running:
            # Clean up finished process
            del project_manager.running_processes[project_id]
        
        return jsonify({"running": is_running, "pid": process.pid if is_running else None})
        
    except Exception as e:
        return jsonify({"error": f"Failed to check project status: {str(e)}"}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'message': 'Connected to Python Code Generator'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_project')
def handle_join_project(data):
    project_id = data.get('project_id')
    if project_id:
        # Join room for project-specific updates
        from flask_socketio import join_room
        join_room(project_id)
        emit('joined_project', {'project_id': project_id})

@app.route('/api/debug/parsing-stats', methods=['GET'])
def get_parsing_stats():
    """Get JSON parsing failure statistics for debugging"""
    try:
        stats = debug_logger.get_failure_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": f"Failed to get parsing stats: {str(e)}"}), 500

# Blog Generation Routes - Updated to use blog_main_system
@app.route('/api/blog/interview', methods=['POST'])
def blog_interview():
    """Start or continue blog interview process"""
    try:
        # Import blog system locally
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'blog'))
        from blog.blog_main import InterviewBlogGenerator
        blog_generator = InterviewBlogGenerator(session=session)
        
        data = request.get_json()
        topic = data.get('topic', '').strip()
        user_answer = data.get('answer', '').strip() if data.get('answer') else None
        
        if not topic and not session.get("topic"):
            return jsonify({"error": "Topic is required"}), 400
        
        # Use the blog generator's interview step
        response = blog_generator.interview_step(topic, user_answer)
        
        return jsonify({
            "success": True,
            "response": response,
            "topic": session.get("topic", topic)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to process interview: {str(e)}"
        }), 500

@app.route('/api/blog/generate', methods=['POST'])
def generate_blog():
    """Generate complete blog post"""
    try:
        # Import blog system locally
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'blog'))
        from blog.blog_main import InterviewBlogGenerator
        blog_generator = InterviewBlogGenerator(session=session)
        
        data = request.get_json()
        
        # Support both new and legacy formats
        topic = data.get('topic', '').strip() or data.get('mainTopic', '').strip()
        additional_info = data.get('additional_info', '').strip()
        subtopics = data.get('subtopics', [])
        title = data.get('title', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # For legacy compatibility, simulate quick generation using the existing pattern
        # Research the topic first
        research_data = blog_generator.researcher_tool.research_topic(topic)
        if not research_data:
            research_data = {"sources": [], "content": f"General information about {topic}"}
        
        # Create context similar to the original quick_generate function
        context_info = additional_info
        if subtopics:
            context_info += f"\nSubtopics to cover: {', '.join(subtopics)}"
        if title:
            context_info += f"\nSuggested title: {title}"
            
        context = f"""Create a detailed, expert-level blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

REQUIREMENTS:
- Use research data to provide accurate, specific information with facts and statistics
- Write as a subject matter expert with deep knowledge of {topic}
- Provide specific, actionable information rather than generic advice
- Include real-world examples, case studies, or practical scenarios
- Use appropriate industry terminology and concepts
- Make it comprehensive but accessible
- Include step-by-step guidance where applicable
- Add tables, lists, or structured information when relevant
- Ensure all claims are accurate and supportable

Additional user requirements: {context_info if context_info else 'None - cover the topic comprehensively with research-backed information'}

Target length: 1000-1200 words with proper structure, formatting, and research-backed accuracy."""
        
        # Use the blog crew to generate content
        result = blog_generator.blog_crew.kickoff(inputs={
            "topic": topic,
            "context": context
        }, research_data=research_data)
        
        raw_output = result.raw if hasattr(result, "raw") else str(result)
        clean_json = re.sub(r"```json\n|\n```|```", "", raw_output).strip()
        
        # More aggressive JSON cleaning
        start_idx = clean_json.find('{')
        end_idx = clean_json.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_json = clean_json[start_idx:end_idx+1]
        
        try:
            blog_data = json.loads(clean_json)
            # Ensure all required fields exist
            if not isinstance(blog_data.get('blogContent'), str):
                raise ValueError("Invalid blogContent")
            if not isinstance(blog_data.get('summary'), str):
                blog_data['summary'] = f"A comprehensive, research-backed guide about {topic}"
            if not isinstance(blog_data.get('keywords'), list):
                blog_data['keywords'] = [topic.lower(), "guide", "research", "facts", "expert analysis"]
            
            # Clean up the blog content formatting
            blog_data['blogContent'] = blog_generator.clean_blog_formatting(blog_data['blogContent'])
                
        except (json.JSONDecodeError, ValueError):
            # Clean fallback without research sources
            cleaned_content = blog_generator.clean_blog_formatting(f"# {topic}\n\n{raw_output}")
            blog_data = {
                "blogContent": cleaned_content,
                "summary": f"A comprehensive, research-backed guide about {topic}",
                "keywords": [topic.lower(), "guide", "research", "facts", "expert analysis"]
            }
        
        return jsonify({
            "success": True,
            "blogContent": blog_data.get("blogContent", ""),
            "blog": blog_data.get("blogContent", ""),  # Legacy compatibility
            "summary": blog_data.get("summary", ""),
            "keywords": blog_data.get("keywords", []),
            "title": title or f"Guide to {topic}",
            "wordCount": len(blog_data.get("blogContent", "").split())
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to generate blog: {str(e)}"
        }), 500

@app.route('/api/blog/quick-generate', methods=['POST'])
def quick_generate_blog():
    """Generate blog post directly without interview"""
    try:
        # Import blog system locally
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'blog'))
        from blog.blog_main import InterviewBlogGenerator
        blog_generator = InterviewBlogGenerator(session=session)
        
        data = request.get_json()
        topic = data.get('topic', '').strip()
        additional_info = data.get('additional_info', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Use quick generation
        result = blog_generator.quick_generate(topic, additional_info)
        
        return jsonify({
            "success": True,
            "blogContent": result.get("blogContent", ""),
            "summary": result.get("summary", ""),
            "keywords": result.get("keywords", []),
            "wordCount": len(result.get("blogContent", "").split())
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to quick generate blog: {str(e)}"
        }), 500

# Legacy route for compatibility
@app.route('/api/blog/plan', methods=['POST'])
def plan_blog():
    """Plan blog structure based on topic - redirects to interview"""
    try:
        # Import blog system locally
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'blog'))
        from blog.blog_main import InterviewBlogGenerator
        blog_generator = InterviewBlogGenerator(session=session)
        
        data = request.get_json()
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Start interview process
        response = blog_generator.interview_step(topic)
        
        return jsonify({
            "success": True,
            "title": f"Comprehensive Guide to {topic}",
            "outline": response,
            "subtopics": ["Introduction", "Background", "Key Concepts", "Applications", "Future Trends", "Conclusion"],
            "interview_response": response
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to plan blog: {str(e)}"
        }), 500

# Data Cleaning Endpoints
@app.route('/api/data/test', methods=['GET'])
def test_data_endpoint():
    """Test endpoint to verify data cleaning module"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "success": False,
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy openpyxl xlrd"
            }), 500
            
        return jsonify({
            "success": True,
            "message": "Data cleaning endpoints are working",
            "supported_formats": data_cleaner.supported_formats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/data/upload', methods=['POST'])
def upload_data():
    """Upload and analyze data file"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy openpyxl xlrd"
            }), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Analyze the file
        result = data_cleaner.analyze_file(file)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

@app.route('/api/data/analyze', methods=['POST'])
def analyze_data():
    """Perform AI analysis on uploaded data"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy openpyxl xlrd"
            }), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Perform AI analysis
        result = data_cleaner.ai_analysis(file)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to analyze data: {str(e)}"}), 500

@app.route('/api/data/graphs', methods=['POST'])
def generate_data_graphs():
    """Generate matplotlib/seaborn graphs for data visualization"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy matplotlib seaborn openpyxl xlrd"
            }), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Generate graphs
        result = data_cleaner.generate_data_quality_graphs(file)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to generate graphs: {str(e)}"}), 500

@app.route('/api/data/clean', methods=['POST'])
def clean_data():
    """Clean data based on selected options"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy openpyxl xlrd"
            }), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get cleaning options
        options = {
            'removeDuplicates': request.form.get('removeDuplicates', 'true').lower() == 'true',
            'handleMissingValues': request.form.get('handleMissingValues', 'true').lower() == 'true',
            'standardizeFormats': request.form.get('standardizeFormats', 'true').lower() == 'true',
            'detectOutliers': request.form.get('detectOutliers', 'true').lower() == 'true',
            'validateDataTypes': request.form.get('validateDataTypes', 'true').lower() == 'true'
        }
        
        # Clean the data
        result = data_cleaner.clean_data(file, options)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to clean data: {str(e)}"}), 500

@app.route('/api/data/manual-clean', methods=['POST'])
def manual_clean_data():
    """Perform manual cleaning operations on data"""
    try:
        if not DATA_CLEANER_AVAILABLE or data_cleaner is None:
            return jsonify({
                "error": "Data cleaning module not available. Please install required dependencies: pip install pandas numpy openpyxl xlrd"
            }), 500
            
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Get operation and parameters
        operation = request.form.get('operation')
        parameters = {}
        
        # Parse parameters based on operation type
        if operation == 'filter_rows':
            parameters = {
                'column': request.form.get('column'),
                'condition': request.form.get('condition'),
                'value': request.form.get('value')
            }
        elif operation == 'find_replace':
            parameters = {
                'column': request.form.get('column'),
                'find_value': request.form.get('find_value'),
                'replace_value': request.form.get('replace_value')
            }
        elif operation == 'remove_columns':
            columns_str = request.form.get('columns', '')
            parameters = {
                'columns': [col.strip() for col in columns_str.split(',') if col.strip()]
            }
        elif operation == 'transform_data':
            parameters = {
                'column': request.form.get('column'),
                'transformation': request.form.get('transformation')
            }
        
        # Perform manual cleaning
        result = data_cleaner.manual_clean_data(file, operation, parameters)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify({"error": result['error']}), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to perform manual cleaning: {str(e)}"}), 500

@app.route('/api/data/download/<filename>', methods=['GET'])
def download_cleaned_data(filename):
    """Download cleaned data file"""
    try:
        # In a real implementation, you would store the cleaned data temporarily
        # and retrieve it here. For now, we'll return a placeholder response
        return jsonify({
            "message": "Download functionality would be implemented here",
            "filename": filename
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to download file: {str(e)}"}), 500

# ================================
# PPT/SmartSlides Routes
# ================================

if PPT_AVAILABLE == True or PPT_AVAILABLE == "FALLBACK":
    
    # Download routes for presentations
    @app.route('/api/ppt/presentations/<presentation_id>/download/pdf', methods=['GET'])
    def download_presentation_pdf(presentation_id):
        try:
            pdf_path = ppt_project_manager.get_pdf_path(presentation_id)
            if pdf_path and os.path.exists(pdf_path):
                # Try to get the topic name for a better filename
                download_name = f'presentation_{presentation_id}.pdf'
                
                # Check if we have project data with topic information
                if presentation_id in ppt_project_manager.projects:
                    topic = ppt_project_manager.projects[presentation_id].get('topic', '')
                    if topic:
                        sanitized_topic = PPTProjectManager.sanitize_filename(topic)
                        download_name = f'{sanitized_topic}.pdf'
                else:
                    # Try to get topic from JSON file
                    json_path = ppt_project_manager.get_response_path(presentation_id)
                    if json_path and os.path.exists(json_path):
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                json_data = json.load(f)
                                topic = json_data.get('topic') or json_data.get('title', '')
                                if topic:
                                    sanitized_topic = PPTProjectManager.sanitize_filename(topic)
                                    download_name = f'{sanitized_topic}.pdf'
                        except Exception as e:
                            logging.warning(f"Could not load topic from JSON for download: {e}")
                
                return send_file(pdf_path, 
                               mimetype='application/pdf',
                               as_attachment=True,
                               download_name=download_name)
            return jsonify({'error': 'PDF not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/ppt/presentations/<presentation_id>/download/response', methods=['GET'])
    def download_presentation_response(presentation_id):
        try:
            response_path = ppt_project_manager.get_response_path(presentation_id)
            if response_path and os.path.exists(response_path):
                return send_file(response_path,
                               mimetype='application/json',
                               as_attachment=True,
                               download_name=f'response_{presentation_id}.json')
            return jsonify({'error': 'Response file not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Create new presentation route
    @app.route('/api/ppt/presentations', methods=['POST'])
    def create_presentation():
        try:
            if PPT_AVAILABLE == "FALLBACK":
                return jsonify({
                    'success': False,
                    'error': 'PPT functionality is temporarily unavailable due to dependency compatibility issues. Please check server logs for details.'
                }), 503
                
            data = request.json
            logging.info(f"Received presentation data: {data}")
            
            # Validate required fields
            if not data or 'topic' not in data:
                return jsonify({'error': 'Topic is required'}), 400
            
            # Extract data
            topic = data['topic']
            theme_name = data.get('theme', 'corporate_blue')
            tone = data.get('tone', 'professional')
            audience = data.get('audience', 'general')
            length = data.get('length', 'medium')
            focus_areas = data.get('focus_areas', [])
            additional_requirements = data.get('additional_requirements', '')
            
            # Create project
            result = ppt_project_manager.create_project(
                topic=topic,
                theme_name=theme_name,
                tone=tone,
                audience=audience,
                length=length,
                focus_areas=focus_areas,
                additional_requirements=additional_requirements
            )
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'project_id': result['project_id'],
                    'message': 'Presentation project created successfully'
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            logging.error(f"Error creating presentation: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Get presentation data route
    @app.route('/api/ppt/presentations/<project_id>', methods=['GET'])
    def get_presentation(project_id):
        try:
            result = ppt_project_manager.get_project_data(project_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'data': result['data']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 404
                
        except Exception as e:
            logging.error(f"Error getting presentation {project_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Generate presentation route
    @app.route('/api/ppt/presentations/<project_id>/generate', methods=['POST'])
    def generate_presentation(project_id):
        try:
            # Check if project exists
            if project_id not in ppt_project_manager.projects:
                return jsonify({'error': 'Project not found'}), 404
            
            # Start generation in background
            result = ppt_project_manager.start_generation(project_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Generation started',
                    'project_id': project_id
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
                
        except Exception as e:
            logging.error(f"Error generating presentation {project_id}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    # Get themes route
    @app.route('/api/ppt/themes', methods=['GET'])
    def get_themes():
        try:
            themes = list(PPTThemes.get_all_themes().values())
            return jsonify({
                'success': True,
                'themes': themes
            })
        except Exception as e:
            logging.error(f"Error getting themes: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Get project status route
    @app.route('/api/ppt/projects/<project_id>/status', methods=['GET'])
    def get_ppt_project_status(project_id):
        try:
            status = ppt_project_manager.get_project_status(project_id)
            return jsonify(status)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Download project route
    @app.route('/api/ppt/projects/<project_id>/download', methods=['GET'])
    def download_ppt_project(project_id):
        try:
            result = ppt_project_manager.get_download_files(project_id)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'files': result['files']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Get all projects route
    @app.route('/api/ppt/projects', methods=['GET'])
    def get_all_ppt_projects():
        try:
            projects = ppt_project_manager.list_projects()
            return jsonify({
                'success': True,
                'projects': projects
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Delete project route
    @app.route('/api/ppt/projects/<project_id>', methods=['DELETE'])
    def delete_ppt_project(project_id):
        try:
            result = ppt_project_manager.delete_project(project_id)
            
            if result['success']:
                return jsonify({'success': True, 'message': 'Project deleted successfully'})
            else:
                return jsonify({'success': False, 'error': result['error']}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # PPT SocketIO events
    @socketio.on('ppt_connect')
    def handle_ppt_connect():
        """Handle PPT client connection"""
        logging.info(f"PPT Client connected: {request.sid}")
        emit('ppt_connected', {'status': 'Connected to PPT service'})

    @socketio.on('ppt_disconnect')
    def handle_ppt_disconnect():
        """Handle PPT client disconnection"""
        logging.info(f"PPT Client disconnected: {request.sid}")

    @socketio.on('join_ppt_project')
    def handle_join_ppt_project(data):
        """Join a PPT project room for real-time updates"""
        project_id = data.get('project_id')
        if project_id:
            join_room(f"ppt_{project_id}")
            logging.info(f"Client {request.sid} joined PPT project room: {project_id}")
            emit('joined_ppt_project', {'project_id': project_id})

    @socketio.on('leave_ppt_project')
    def handle_leave_ppt_project(data):
        """Leave a PPT project room"""
        project_id = data.get('project_id')
        if project_id:
            leave_room(f"ppt_{project_id}")
            logging.info(f"Client {request.sid} left PPT project room: {project_id}")
            emit('left_ppt_project', {'project_id': project_id})

else:
    # PPT functionality not available routes
    @app.route('/api/ppt/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def ppt_not_available(path):
        return jsonify({
            'error': 'PPT functionality is not available. Please install required dependencies.'
        }), 503

# Blog functionality routes
if BLOG_AVAILABLE:
    # Import blog routes here to avoid circular imports
    from blog.blog_main import quick_generate as blog_quick_generate
    from blog.blog_main import youtube_generate as blog_youtube_generate
    
    @app.route('/quick-generate', methods=['POST'])
    def quick_generate():
        """Generate detailed, research-backed blog directly without interview - for faster results"""
        try:
            data = request.get_json()
            topic = data.get("topic")
            additional_info = data.get("info", "")
            detailed = data.get("detailed", True)  # Default to True for backward compatibility
            
            if not topic:
                return jsonify({"error": "Topic is required"}), 400
            
            # Create generator instance with detailed flag
            generator = InterviewBlogGenerator(detailed=detailed)
            
            # Research the topic for accuracy
            print(f"🔍 Quick research for: {topic}")
            research_data = generator.researcher_tool.research_topic(topic)
            
            if not research_data:
                research_data = {"sources": [], "content": f"General information about {topic}"}
            
            # Create enhanced context for quick generation with research data
            if detailed:
                context = f"""Create a detailed, expert-level blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

REQUIREMENTS:
- Use research data to provide accurate, specific information with facts and statistics
- Write as a subject matter expert with deep knowledge of {topic}
- Provide specific, actionable information rather than generic advice
- Include real-world examples, case studies, or practical scenarios
- Use appropriate industry terminology and concepts
- Make it comprehensive but accessible
- Include step-by-step guidance where applicable
- Add tables, lists, or structured information when relevant
- Ensure all claims are accurate and supportable

Additional user requirements: {additional_info if additional_info else 'None - cover the topic comprehensively with research-backed information'}

Target length: 1000-1200 words with proper structure, formatting, and research-backed accuracy."""
            else:
                context = f"""Create a concise, factual blog post about: {topic}

RESEARCH DATA AVAILABLE:
{research_data.get('content', '')}

REQUIREMENTS:
- Use ONLY the research data provided - DO NOT add any information not in the research
- Stick strictly to facts, dates, and verifiable information from the sources
- Write in a journalistic, factual tone without creative embellishment
- Keep it concise and focused on the available data
- Include specific facts, statistics, and details from research sources
- Avoid speculation, predictions, or "extra masala"
- If research data is limited, keep the blog correspondingly brief

Additional user requirements: {additional_info if additional_info else 'None - stick to research data only'}

Target length: 600-800 words maximum, focused on facts from research data."""
            
            result = generator.blog_crew.kickoff(inputs={
                "topic": topic,
                "context": context
            }, research_data=research_data)
            
            raw_output = result.raw if hasattr(result, "raw") else str(result)
            clean_json = re.sub(r"```json\n|\n```|```", "", raw_output).strip()
            
            # More aggressive JSON cleaning
            start_idx = clean_json.find('{')
            end_idx = clean_json.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_json = clean_json[start_idx:end_idx+1]
            
            try:
                data = json.loads(clean_json)
                # Ensure all required fields exist
                if not isinstance(data.get('blogContent'), str):
                    raise ValueError("Invalid blogContent")
                if not isinstance(data.get('summary'), str):
                    data['summary'] = f"A comprehensive, research-backed guide about {topic}"
                if not isinstance(data.get('keywords'), list):
                    data['keywords'] = [topic.lower(), "guide", "research", "facts", "expert analysis"]
                
                # Clean up the blog content formatting
                data['blogContent'] = generator.clean_blog_formatting(data['blogContent'])
                
                # DO NOT add source attribution to visible content - keep research internal
                    
            except (json.JSONDecodeError, ValueError):
                # Clean fallback without research sources
                cleaned_content = generator.clean_blog_formatting(f"# {topic}\n\n{raw_output}")
                data = {
                    "blogContent": cleaned_content,
                    "summary": f"A comprehensive, research-backed guide about {topic}",
                    "keywords": [topic.lower(), "guide", "research", "facts", "expert analysis"]
                }
            
            print("✅ Quick research-backed blog generated!")
            return jsonify(data)
            
        except Exception as e:
            print(f"❌ Error in quick generate: {str(e)}")
            return jsonify({
                "blogContent": f"# Error\n\nError generating blog: {str(e)}",
                "summary": "Error generating blog",
                "keywords": ["error"]
            }), 500

    @app.route('/youtube-generate', methods=['POST'])
    def youtube_generate():
        """
        Robust YouTube blog generation endpoint using the new robust function
        Handles all edge cases and always returns a proper response
        """
        try:
            # Get request data
            data = request.json if request.json else {}
            youtube_url = data.get("youtubeUrl", "").strip()
            additional_context = data.get("additionalContext", "").strip()
            detailed = data.get("detailed", True)  # Default to True for backward compatibility
            
            # Validate input
            if not youtube_url:
                return jsonify({
                    "success": False,
                    "error": "YouTube URL is required",
                    "blogContent": None
                }), 400
            
            print(f"🎥 Processing YouTube video: {youtube_url} (Detailed: {detailed})")
            
            # Get API keys from existing configuration
            google_search_api_key = "AIzaSyBulaFMZql3n6-mtJnHF55371CYtJu_9R8"  # Using your existing key
            search_engine_ids = [
                "a65b8e8b1cf564e44",
                "91e458efa2c6a4c49", 
                "507e20da4ca5248b6"
            ]
            
            # Call the robust blog generation function
            result = generate_blog_from_youtube(
                video_url=youtube_url,
                additional_context=additional_context,
                gemini_api_key=Config.GOOGLE_API_KEY,  # Use existing configured API key
                google_search_api_key=google_search_api_key,
                search_engine_id=search_engine_ids[0],  # Use first search engine
                detailed=detailed
            )
            
            # Check if generation was successful
            if result['success']:
                # Success case - format response to match existing frontend expectations
                response_data = {
                    "success": True,
                    "blogContent": result['blog_content'],
                    "summary": f"Blog generated from YouTube video: '{result['video_info']['title']}' by {result['video_info']['author']}",
                    "keywords": [],  # Extract from metadata if available
                    "source": {
                        "type": "YouTube Video",
                        "title": result['video_info']['title'],
                        "author": result['video_info']['author'],
                        "url": youtube_url,
                        "duration": f"{result['video_info']['duration_minutes']} minutes",
                        "views": result['video_info']['views'],
                        "transcript_available": result['generation_info']['transcript_available'],
                        "generation_method": result['generation_info']['method']
                    },
                    "generation_info": result['generation_info'],
                    "metadata": {
                        "generated_at": result['timestamp'],
                        "method": result['generation_info']['method'],
                        "research_sources": result['generation_info'].get('research_sources', 0)
                    }
                }
                
                # Save the blog to file (maintaining compatibility with existing code)
                try:
                    with open("latest_youtube_blog.md", "w", encoding="utf-8") as f:
                        f.write(f"# {result['video_info']['title']}\n\n")
                        f.write(f"**Source:** YouTube Video by {result['video_info']['author']}\n")
                        f.write(f"**URL:** {youtube_url}\n")
                        f.write(f"**Duration:** {result['video_info']['duration_minutes']} minutes\n")
                        f.write(f"**Generation Method:** {result['generation_info']['method']}\n\n")
                        f.write("---\n\n")
                        f.write(result['blog_content'])
                    print("💾 Blog saved to latest_youtube_blog.md")
                except Exception as save_error:
                    print(f"⚠️ Warning: Could not save blog to file: {save_error}")
                
                print(f"✅ Blog generated successfully using {result['generation_info']['method']}")
                return jsonify(response_data), 200
                
            else:
                # Error case - but still return structured response
                error_response = {
                    "success": False,
                    "error": result['error'],
                    "blogContent": None,
                    "video_info": result.get('video_info', {}),
                    "timestamp": result['timestamp']
                }
                
                print(f"❌ Blog generation failed: {result['error']}")
                return jsonify(error_response), 400
        
        except Exception as e:
            # Ultimate fallback for any unexpected errors
            print(f"❌ Unexpected error in YouTube endpoint: {e}")
            return jsonify({
                "success": False,
                "error": f"Server error: {str(e)}",
                "blogContent": None
            }), 500

else:
    # Blog functionality not available routes
    @app.route('/quick-generate', methods=['POST'])
    def blog_not_available_quick():
        return jsonify({
            'error': 'Blog functionality is not available. Please check dependencies.'
        }), 503
    
    @app.route('/youtube-generate', methods=['POST'])
    def blog_not_available_youtube():
        return jsonify({
            'error': 'Blog functionality is not available. Please check dependencies.'
        }), 503

if __name__ == '__main__':
    print("Starting Python Code Generator API...")
    print(f"Gemini API Key configured: {'Yes' if Config.GOOGLE_API_KEY else 'No'}")
    print(f"Generated projects directory: {Config.GENERATED_PROJECTS_DIR}")
    
    if PPT_AVAILABLE == True:
        print("PPT/SmartSlides functionality: ✅ Fully Available")
    elif PPT_AVAILABLE == "FALLBACK":
        print("PPT/SmartSlides functionality: ⚠️  Fallback Mode (Limited functionality due to dependency issues)")
    else:
        print("PPT/SmartSlides functionality: ❌ Not Available")
    
    # Run with eventlet for WebSocket support - Debug disabled to prevent auto-restart
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=False,  # Disabled to prevent server auto-restart
        use_reloader=False,  # Explicitly disable file watching
        allow_unsafe_werkzeug=True  # Allow running with Werkzeug
    )