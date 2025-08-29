import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module='pydantic')

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from project_manager import PPTProjectManager
from themes import PPTThemes
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure project_manager logger to suppress INFO messages
project_manager_logger = logging.getLogger('project_manager')
project_manager_logger.setLevel(logging.WARNING)

# Validate configuration
try:
    Config.validate_config()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO with eventlet for better performance and no duplication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

# Initialize project manager as a global singleton
project_manager = PPTProjectManager(socketio=socketio)

# Download routes
@app.route('/api/presentations/<presentation_id>/download/pdf', methods=['GET'])
def download_pdf(presentation_id):
    try:
        pdf_path = project_manager.get_pdf_path(presentation_id)
        if pdf_path and os.path.exists(pdf_path):
            # Try to get the topic name for a better filename
            download_name = f'presentation_{presentation_id}.pdf'
            
            # Check if we have project data with topic information
            if presentation_id in project_manager.projects:
                topic = project_manager.projects[presentation_id].get('topic', '')
                if topic:
                    sanitized_topic = PPTProjectManager.sanitize_filename(topic)
                    download_name = f'{sanitized_topic}.pdf'
            else:
                # Try to get topic from JSON file
                json_path = project_manager.get_response_path(presentation_id)
                if json_path and os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                            topic = json_data.get('topic') or json_data.get('title', '')
                            if topic:
                                sanitized_topic = PPTProjectManager.sanitize_filename(topic)
                                download_name = f'{sanitized_topic}.pdf'
                    except Exception as e:
                        logger.warning(f"Could not load topic from JSON for download: {e}")
            
            return send_file(pdf_path, 
                           mimetype='application/pdf',
                           as_attachment=True,
                           download_name=download_name)
        return jsonify({'error': 'PDF not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/presentations/<presentation_id>/download/response', methods=['GET'])
def download_response(presentation_id):
    try:
        response_path = project_manager.get_response_path(presentation_id)
        if response_path and os.path.exists(response_path):
            return send_file(response_path,
                           mimetype='application/json',
                           as_attachment=True,
                           download_name=f'response_{presentation_id}.json')
        return jsonify({'error': 'Response file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Create new presentation route
@app.route('/api/presentations', methods=['POST'])
def create_presentation():
    try:
        data = request.json
        logger.info(f"Received presentation data: {data}")
        
        # Support both 'topic' and 'title' for backward compatibility
        title = data.get('topic') or data.get('title', 'Untitled Presentation')
        description = data.get('description', '')
        style_preferences = data.get('style_preferences', {})
        
        # Ensure num_slides is an integer
        num_slides = data.get('num_slides') or style_preferences.get('num_slides', 5)
        num_slides = int(num_slides) if isinstance(num_slides, str) else num_slides
        
        theme_name = data.get('theme') or style_preferences.get('theme', 'corporate_blue')
        
        logger.info(f"Processing presentation: title='{title}', num_slides={num_slides}, theme='{theme_name}'")
        
        # Start generation process
        try:
            result = project_manager.generate_presentation(
                user_prompt=title,
                num_slides=num_slides,
                theme_name=theme_name,
            )
            
            if result['success']:
                project_id = result['project_id']
                output_path = result['file_path']
            else:
                raise Exception(result.get('error', 'Unknown error occurred'))
            
            return jsonify({
                'status': 'success',
                'project_id': project_id,
                'output_path': output_path,
                'themes': []
            }), 200
            
        except Exception as gen_error:
            logger.error(f"Generation error: {str(gen_error)}")
            return jsonify({
                'status': 'error',
                'message': str(gen_error)
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to create presentation: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Get presentation route
@app.route('/api/presentations/<project_id>', methods=['GET'])
def get_presentation(project_id):
    try:
        # Instead of using project_manager.presentation_generator (which doesn't exist),
        # just fetch the project info from project_manager.projects
        presentation = project_manager.projects.get(project_id)

        if not presentation:
            return jsonify({
                'status': 'error',
                'message': f'Presentation with ID {project_id} not found'
            }), 404

        return jsonify({
            'status': 'success',
            'presentation': presentation
        }), 200

    except Exception as e:
        logger.error(f"Failed to get presentation: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Generate presentation route
@app.route('/api/presentations/<project_id>/generate', methods=['POST'])
def generate_presentation(project_id):
    try:
        data = request.json
        topic = data.get('topic', '')
        
        # Emit starting status
        socketio.emit('status_update', {
            'type': 'info',
            'message': 'Starting presentation generation',
            'agent': 'system',
            'timestamp': datetime.now().isoformat()
        }, room=project_id)
        
        # Generate the presentation
        result = project_manager.generate_presentation(
            user_prompt=topic,
            num_slides=5,
            project_id=project_id
        )
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'output_path': result['file_path']
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': result['user_message']
            }), 500
            
    except Exception as e:
        logger.error(f"Failed to generate presentation: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



# Websocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('status_update', {
        'type': 'info',
        'message': 'Connected to server',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    if room:
        join_room(room)
        logger.info(f"Client {request.sid} joined room {room}")
        # Removed the joined room message as requested

@socketio.on('leave')
def handle_leave(data):
    room = data.get('room')
    if room:
        emit('status_update', {
            'type': 'info',
            'message': f'Leaving room: {room}',
            'timestamp': datetime.now().isoformat()
        }, room=room)
        leave_room(room)
        logger.info(f"Client {request.sid} left room {room}")


@app.route('/')
def index():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'PPT Generator API',
        'version': '1.0.0',
        'available_themes': PPTThemes.get_theme_display_info(),
        'endpoints': {
            'generate': '/api/generate',
            'themes': '/api/themes',
            'status': '/api/projects/<id>/status',
            'download': '/api/projects/<id>/download',
            'list': '/api/projects',
            'delete': '/api/projects/<id>'
        }
    })



@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Get available presentation themes"""
    try:
        themes = PPTThemes.get_theme_display_info()
        return jsonify({
            'success': True,
            'themes': themes,
            'default_theme': 'corporate_blue',
            'total': len(themes)
        })
    except Exception as e:
        logger.error(f"Error getting themes: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>/status', methods=['GET'])
def get_project_status(project_id):
    """Get project status"""
    try:
        status = project_manager.get_project_status(project_id)
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>/download', methods=['GET'])
def download_project(project_id):
    """Download generated presentation"""
    try:
        file_path = project_manager.download_project(project_id)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Project not found or not ready'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f'presentation_{project_id}.json',
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error downloading project: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects"""
    try:
        projects = project_manager.list_projects()
        return jsonify({'success': True, 'projects': projects})
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        success = project_manager.delete_project(project_id)
        if success:
            return jsonify({'success': True, 'message': 'Project deleted'})
        else:
            return jsonify({'error': 'Project not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to PPT Generator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_project')
def handle_join_project(data):
    """Join a project room for real-time updates"""
    project_id = data.get('project_id')
    if project_id:
        join_room(project_id)
        logger.info(f"Client {request.sid} joined project room: {project_id}")
        emit('joined_project', {'project_id': project_id})

@socketio.on('leave_project')
def handle_leave_project(data):
    """Leave a project room"""
    project_id = data.get('project_id')
    if project_id:
        leave_room(project_id)
        logger.info(f"Client {request.sid} left project room: {project_id}")
        emit('left_project', {'project_id': project_id})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting PPT Generator API server...")
    logger.info(f"Configuration: {Config.CREWAI_MODEL}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Auto-reload: {Config.USE_RELOADER}")
    
    # Run the application
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True
    )

