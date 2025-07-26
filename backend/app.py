from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import uuid
import os
import threading
import zipfile
from datetime import datetime
from project_manager import ProjectManager
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global project manager instance
project_manager = ProjectManager(socketio)

# Store active projects
active_projects = {}

@app.route('/')
def index():
    return jsonify({
        "message": "Python Code Generator API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route('/api/generate', methods=['POST'])
def generate_project():
    """Start project generation process"""
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        
        if not user_prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Store project info
        active_projects[project_id] = {
            "id": project_id,
            "prompt": user_prompt,
            "status": "started",
            "created_at": datetime.now().isoformat()
        }
        
        # Start project generation in background thread
        def generate_in_background():
            try:
                result = project_manager.generate_project(user_prompt, project_id)
                active_projects[project_id].update({
                    "status": "completed" if result["success"] else "failed",
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                })
                
                # Emit completion event
                socketio.emit('project_completed', {
                    "project_id": project_id,
                    "success": result["success"],
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
        
        # Check for main.py
        main_py_path = os.path.join(project_path, 'main.py')
        if not os.path.exists(main_py_path):
            return jsonify({"error": "main.py not found in project"}), 404
        
        # Determine run method by analyzing main.py and requirements.txt
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

if __name__ == '__main__':
    print("Starting Python Code Generator API...")
    print(f"Gemini API Key configured: {'Yes' if Config.GEMINI_API_KEY else 'No'}")
    print(f"Generated projects directory: {Config.GENERATED_PROJECTS_DIR}")
    
    # Run with eventlet for WebSocket support
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=Config.FLASK_DEBUG
    )

