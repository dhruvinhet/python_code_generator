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

