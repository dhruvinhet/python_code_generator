import os
import json
import re
from datetime import datetime
from .agents import PPTCrew
import sys
sys.path.append('..')
from config import Config
import logging
from .themes import ThemeConfig, PPTThemes
from flask import render_template_string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PPTProjectManager:

    @staticmethod
    def sanitize_filename(text: str) -> str:
        """
        Sanitize a string to be safe for use as a filename.
        Removes special characters and replaces spaces with underscores.
        """
        if not text:
            return "untitled"
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]*>', '', text)
        
        # Replace spaces with underscores and remove special characters
        sanitized = re.sub(r'[^\w\s-]', '', text.strip())
        sanitized = re.sub(r'[\s_-]+', '_', sanitized)
        
        # Limit length to 50 characters
        sanitized = sanitized[:50].strip('_')
        
        # Ensure it's not empty
        return sanitized.lower() if sanitized else "untitled"

    @staticmethod
    def generate_project_id_from_topic(topic: str, existing_projects: dict = None) -> str:
        """
        Generate a unique project ID based on the topic name.
        If a duplicate exists, append a counter.
        """
        base_name = PPTProjectManager.sanitize_filename(topic)
        project_id = base_name
        
        # Check for existing files in the generated_ppts directory
        counter = 1
        while True:
            pdf_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.pdf")
            json_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.json")
            
            # Also check if it's in the current projects dict
            exists_in_memory = existing_projects and project_id in existing_projects
            exists_as_file = os.path.exists(pdf_path) or os.path.exists(json_path)
            
            if not exists_in_memory and not exists_as_file:
                break
                
            counter += 1
            project_id = f"{base_name}_{counter}"
        
        return project_id

    @staticmethod
    def clean_html_code_block(content: str) -> str:
        """
        Removes leading ```html and trailing ``` from a string, returning the cleaned HTML content.
        """
        if not isinstance(content, str):
            return content
        content = content.strip()
        if content.startswith('```html'):
            content = content[len('```html'):]
        elif content.startswith('```'):
            content = content[len('```'):]
        if content.endswith('```'):
            content = content[:-3]
        return content.strip()

    def __init__(self, socketio=None):
        self.socketio = socketio
        self.crew = PPTCrew()
        self.projects = {}
        self.state_file = os.path.join(Config.TEMP_DIR, 'project_states.json')
        os.makedirs(Config.GENERATED_PPTS_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        self._load_project_states()
        
    def get_pdf_path(self, project_id: str) -> str:
        """Get the path where the PDF file should be saved"""
        return os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.pdf")

    def get_response_path(self, project_id: str) -> str:
        """Get the path where the response JSON file should be saved"""
        json_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.json")
        # If JSON doesn't exist, create it from project data
        if project_id in self.projects and not os.path.exists(json_path):
            try:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(self.projects[project_id], f, indent=2, default=str)
            except Exception as e:
                logger.warning(f"Could not create JSON file for project {project_id}: {e}")
        return json_path if os.path.exists(json_path) else None

    def list_projects(self):
        """List all projects with their metadata"""
        try:
            projects = []
            
            # Check for PDF files in the generated_ppts directory
            for filename in os.listdir(Config.GENERATED_PPTS_DIR):
                if filename.endswith('.pdf') and filename.startswith('presentation_'):
                    # Extract project ID from filename
                    project_id = filename.replace('presentation_', '').replace('.pdf', '')
                    
                    pdf_path = os.path.join(Config.GENERATED_PPTS_DIR, filename)
                    json_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.json")
                    
                    # Skip empty PDF files
                    if os.path.getsize(pdf_path) == 0:
                        continue
                    
                    project_info = {
                        'id': project_id,
                        'created_at': datetime.fromtimestamp(os.path.getctime(pdf_path)).isoformat(),
                        'pdf_size': os.path.getsize(pdf_path),
                        'status': 'completed'
                    }
                    
                    # Try to load additional metadata from JSON file
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                json_data = json.load(f)
                                project_info.update({
                                    'topic': json_data.get('topic', json_data.get('title', 'Untitled')),
                                    'title': json_data.get('title', json_data.get('topic', 'Untitled')),
                                    'description': json_data.get('description', ''),
                                    'num_slides': json_data.get('num_slides', len(json_data.get('slides', []))),
                                    'theme': json_data.get('theme', 'corporate_blue'),
                                    'theme_color': json_data.get('theme_color', '#3b82f6')
                                })
                        except Exception as e:
                            logger.warning(f"Could not load metadata for project {project_id}: {e}")
                            project_info.update({
                                'topic': f'Presentation {project_id}',
                                'title': f'Presentation {project_id}',
                                'description': 'Generated presentation',
                                'num_slides': 5,
                                'theme': 'corporate_blue',
                                'theme_color': '#3b82f6'
                            })
                    else:
                        # Use defaults if no JSON file
                        project_info.update({
                            'topic': f'Presentation {project_id}',
                            'title': f'Presentation {project_id}',
                            'description': 'Generated presentation',
                            'num_slides': 5,
                            'theme': 'corporate_blue',
                            'theme_color': '#3b82f6'
                        })
                    
                    projects.append(project_info)
            
            # Sort by creation date (newest first)
            projects.sort(key=lambda x: x['created_at'], reverse=True)
            
            logger.info(f"Listed {len(projects)} projects")
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            raise

    def delete_project(self, project_id: str):
        """Delete a project and its associated files"""
        try:
            deleted = False
            
            # Delete PDF file
            pdf_path = self.get_pdf_path(project_id)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                deleted = True
                logger.info(f"Deleted PDF: {pdf_path}")
            
            # Delete JSON file
            json_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.json")
            if os.path.exists(json_path):
                os.remove(json_path)
                deleted = True
                logger.info(f"Deleted JSON: {json_path}")
            
            # Remove from memory
            if project_id in self.projects:
                del self.projects[project_id]
                deleted = True
            
            # Delete project folder if it exists
            project_folder = os.path.join(Config.TEMP_DIR, project_id)
            if os.path.exists(project_folder):
                import shutil
                shutil.rmtree(project_folder)
                deleted = True
                logger.info(f"Deleted project folder: {project_folder}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False

    def get_project_status(self, project_id: str) -> dict:
        """Get the status of a specific project."""
        project = self.projects.get(project_id)
        if not project:
            return {'status': 'not_found', 'message': 'Project not found'}
        
        status_info = {
            'status': project.get('status', 'unknown'),
            'current_step': 'No current step available', # Default value
            'progress': 0 # Default value
        }
        
        # Extract the last stage as the current step
        if 'stages' in project and project['stages']:
            status_info['current_step'] = project['stages'][-1].get('message', 'No message available')
        
        # Simple progress simulation
        if status_info['status'] == 'started':
            status_info['progress'] = 10
        elif status_info['status'] == 'planning':
            status_info['progress'] = 30
        elif status_info['status'] == 'generation':
            status_info['progress'] = 60
        elif status_info['status'] == 'processing':
            status_info['progress'] = 80
        elif status_info['status'] == 'completed':
            status_info['progress'] = 100
            
        return status_info

    def _load_project_states(self):
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    self.projects = json.load(f)
                logger.info(f"Loaded {len(self.projects)} project states from disk")
        except Exception as e:
            logger.warning(f"Failed to load project states: {e}")
            self.projects = {}

    def emit_progress(self, project_id, stage, message, type='info'):
        if self.socketio:
            data = {'stage': stage, 'message': message, 'type': type, 'timestamp': datetime.now().isoformat()}
            self.socketio.emit('status_update', data, room=project_id)
            if project_id in self.projects:
                self.projects[project_id]['stages'].append(data)

    @staticmethod
    def _log_agent_response(project_id: str, agent_name: str, response: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check if the response contains HTML code blocks
        if "```html" in response or "<!DOCTYPE html" in response or "<html" in response:
            # Create timestamp folder for this project
            html_project_dir = os.path.join(Config.HTML_OUTPUTS_DIR, project_id)
            os.makedirs(html_project_dir, exist_ok=True)
            
            # Split response into separate HTML code blocks
            slides = []
            if "```html" in response:
                # Split by ```html and ``` markers
                parts = response.split("```html")
                for part in parts[1:]:  # Skip first part (before first ```html)
                    end = part.find("```")
                    if end != -1:
                        slides.append(part[:end].strip())
            else:
                # Single HTML content
                slides = [response.strip()]
            
            html_files = []
            for i, slide_content in enumerate(slides, 1):
                html_file = os.path.join(html_project_dir, f"slide{i}.html")
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(slide_content)
                html_files.append(html_file)
            logger.info(f"Saved {len(slides)} HTML slides to {html_project_dir}")
        else:
            # Save non-HTML responses to log file
            log_dir = Config.TEMP_DIR
            os.makedirs(log_dir, exist_ok=True)
            file_name = f"agent_response_{project_id}_{timestamp}.log"
            file_path = os.path.join(log_dir, file_name)
            
            with open(file_path, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] Agent: {agent_name}\n")
                f.write(f"Response:\n{response}\n\n")
            logger.info(f"Logged agent response to {file_path}")

    def create_project(self, topic, theme_name='corporate_blue', tone='professional', audience='general', length='medium', focus_areas=[], additional_requirements='', num_slides=5):
        project_id = self.generate_project_id_from_topic(topic, self.projects)
        
        try:
            logger.info(f"🎯 STARTING PRESENTATION GENERATION FOR TOPIC: '{topic}' (ID: {project_id})")
            
            self.projects[project_id] = {
                'id': project_id, 
                'prompt': topic,
                'topic': topic,
                'title': topic,
                'theme_name': theme_name, 
                'status': 'started',
                'created_at': datetime.now().isoformat(), 
                'stages': []
            }
            
            self.emit_progress(project_id, 'initialization', f'Starting presentation generation for: {topic}')
            
            self.emit_progress(project_id, 'planning', f'AI agents researching: {topic}')
            
            # Create presentation with the required arguments
            style_prefs = {
                'num_slides': num_slides,
                'project_id': project_id,
                'theme': theme_name,
                'tone': tone,
                'audience': audience,
                'focus_areas': focus_areas,
                'additional_requirements': additional_requirements
            }
            
            logger.info(f"🤖 Calling AI agents to research and create presentation about: '{topic}'")
            presentation_plan = self.crew.create_presentation(
                topic=topic,
                style_preferences=style_prefs
            )
            
            logger.info(f"✅ AI agents completed. Processing results for topic: '{topic}'")
            PPTProjectManager._log_agent_response(project_id, "Presentation Generator", str(presentation_plan))
            self.emit_progress(project_id, 'generation', f'AI generation complete for: {topic}, processing results...')

            theme = PPTThemes.get_theme(theme_name)
            if not theme:
                logger.warning(f"Theme '{theme_name}' not found, using default corporate_blue")
                theme = PPTThemes.get_theme('corporate_blue')
            
            logger.info(f"Using theme: {theme.display_name}")
            
            logger.info(f"Received presentation_plan type: {type(presentation_plan)}")
            logger.info(f"Presentation plan raw data: {str(presentation_plan)[:500]}")
            
            raw_result = self._extract_crew_result(presentation_plan)
            logger.info(f"Raw result type after extraction: {type(raw_result)}")
            logger.info(f"Raw result content: {str(raw_result)[:500]}")
            
            def clean_html_code_block(content: str) -> str:
                """
                Removes leading ```html and trailing ``` from a string, returning the cleaned HTML content.
                """
                if not isinstance(content, str):
                    return content
                content = content.strip()
                if content.startswith('```html'):
                    content = content[len('```html'):]
                elif content.startswith('```'):
                    content = content[len('```'):]
                if content.endswith('```'):
                    content = content[:-3]
                return content.strip()

            if isinstance(raw_result, str):
                # First try to clean HTML code block format
                if "```html" in raw_result or raw_result.strip().startswith("```"):
                    raw_result = PPTProjectManager.clean_html_code_block(raw_result)
                    logger.info("Cleaned HTML code block formatting")
                    # If it's HTML, we can process it directly
                    if raw_result.strip().startswith("<!DOCTYPE html") or raw_result.strip().startswith("<html"):
                        logger.info("Found valid HTML content")
                        html_content = raw_result
                        
                        # Store the cleaned HTML response for debugging
                        debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
                        os.makedirs(debug_dir, exist_ok=True)
                        html_file_path = os.path.join(debug_dir, f"presentation_{project_id}_cleaned.html")
                        
                        with open(html_file_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        logger.info(f"Stored cleaned HTML content in: {html_file_path}")
                        
                        self.emit_progress(project_id, 'processing', 'Processing HTML content...')
                        self.projects[project_id]['html_path'] = html_file_path  # Store the path in project data
                        return self._generate_pdf_from_html(project_id, html_content)
                
                # If not HTML, try to find JSON structure
                json_start = raw_result.find('{')
                json_end = raw_result.rfind('}')
                if json_start != -1 and json_end != -1:
                    potential_json = raw_result[json_start:json_end + 1]
                    logger.info(f"Found potential JSON: {potential_json[:200]}...")
                    try:
                        json.loads(potential_json)
                        raw_result = potential_json
                        logger.info("Successfully extracted JSON structure")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Found JSON-like structure but failed to parse: {e}")
                
                cleaned_result = self._clean_json_content(raw_result)
                logger.info(f"Cleaned result: {cleaned_result[:500]}")
                
                try:
                    plan_data = json.loads(cleaned_result)
                except json.JSONDecodeError as json_err:
                    logger.warning(f"CrewOutput result is not valid JSON: {json_err}")
                    
                    plan_data = {}
            elif isinstance(raw_result, dict):
                plan_data = raw_result
            else:
                logger.warning(f"Unknown CrewOutput format: {type(raw_result)}, using empty plan")
                logger.debug(f"Raw result content: {str(raw_result)[:200]}...")
                plan_data = {}
            
            self._validate_plan_data(plan_data)
            # PPTProjectManager._log_agent_response(project_id, "Planner Agent", json.dumps(plan_data, indent=2))
            
            self.emit_progress(project_id, 'packaging', 'Creating presentation assets...')
            pdf_path = self._create_html_presentation(plan_data, project_id, theme)
            
            self.emit_progress(project_id, 'pdf_generation', 'PDF generated successfully.')

            self.emit_progress(project_id, 'finalization', 'Finalizing your presentation...')
            
            self.projects[project_id].update({
                'status': 'completed', 'plan': plan_data,
                'pdf_path': pdf_path,
                'completed_at': datetime.now().isoformat()
            })
            
            self.emit_progress(project_id, 'completed', 'Presentation generated successfully!')
            
            if self.socketio:
                self.socketio.emit('project_completed', {
                    'project_id': project_id,
                    'result': {'success': True, 'file_path': pdf_path, 'pdf_path': pdf_path}
                }, room=project_id)
            
            return {'success': True, 'project_id': project_id, 'file_path': pdf_path, 'pdf_path': pdf_path}
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"Error generating presentation: {error_str}", exc_info=True)
            user_message = f"An error occurred during generation: {error_str}"
            self.emit_progress(project_id, 'failed', user_message)
            self.projects[project_id]['status'] = 'failed'
            self.projects[project_id]['error'] = error_str
            
            if self.socketio:
                self.socketio.emit('project_failed', {'project_id': project_id, 'error': error_str}, room=project_id)
            
            return {'success': False, 'project_id': project_id, 'error': error_str}

    def generate_presentation(self, user_prompt, num_slides=5, theme_name='corporate_blue'):
        """
        Generate a presentation with specified parameters.
        This method wraps create_project for API compatibility.
        """
        try:
            result = self.create_project(
                topic=user_prompt,
                theme_name=theme_name,
                num_slides=num_slides
            )
            
            if result and result.get('success'):
                return {
                    'success': True,
                    'project_id': result.get('project_id'),
                    'file_path': result.get('file_path'),
                    'message': 'Presentation generated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Failed to generate presentation'),
                    'user_message': 'An error occurred during presentation generation'
                }
        except Exception as e:
            logger.error(f"Error in generate_presentation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'user_message': 'An error occurred during presentation generation'
            }

    def _extract_crew_result(self, crew_output):
        logger.info(f"CrewOutput type: {type(crew_output)}")
        available_attrs = [attr for attr in dir(crew_output) if not attr.startswith('_')]
        logger.info(f"CrewOutput public attributes: {available_attrs}")
        extraction_methods = [
            ('raw', lambda x: x.raw), ('result', lambda x: x.result),
            ('output', lambda x: x.output), ('text', lambda x: x.text),
            ('content', lambda x: x.content), ('str', lambda x: str(x))
        ]
        for method_name, method_func in extraction_methods:
            try:
                if method_name == 'str' or hasattr(crew_output, method_name.replace('str', '__str__')):
                    result = method_func(crew_output)
                    logger.info(f"Successfully extracted using method: {method_name}")
                    return result
            except Exception as e:
                logger.warning(f"Method {method_name} failed: {e}")
        logger.warning("All extraction methods failed, returning string representation")
        return str(crew_output)

    def _clean_json_content(self, content):
        if not isinstance(content, str):
            return content
            
        content = content.strip()
        
        # Handle various markdown code block formats
        code_block_starts = ['```json', '```html', '```javascript', '```js', '```']
        for start in code_block_starts:
            if content.startswith(start):
                content = content[len(start):]
                break
                
        # Remove ending code block markers
        if content.endswith('```'):
            content = content[:-3]
            
        # Clean the content and try to find JSON content
        content = content.strip()
        
        return content

    def _validate_plan_data(self, plan_data):
        if not isinstance(plan_data, dict):
            return False
        for key in ['presentation_title', 'presentation_description', 'slides']:
            if key not in plan_data:
                plan_data[key] = [] if key == 'slides' else 'Generated'
        if not isinstance(plan_data.get('slides'), list):
            plan_data['slides'] = []
        for i, slide in enumerate(plan_data['slides']):
            if not isinstance(slide, dict):
                plan_data['slides'][i] = {'title': f'Slide {i + 1}', 'content': 'Generated content'}
        return True

    def _create_html_presentation(self, plan_data: dict, project_id: str, theme: ThemeConfig) -> str:
        """Process and combine separate HTML slides into a PDF presentation"""
        logger.info(f"Processing HTML slides for theme: {theme.display_name}")
        
        # Check for project-specific HTML slides first
        html_project_dir = os.path.join(Config.HTML_OUTPUTS_DIR, project_id)
        
        if os.path.exists(html_project_dir):
            slide_files = sorted([f for f in os.listdir(html_project_dir) if f.startswith('slide') and f.endswith('.html')])
            
            if slide_files:
                logger.info(f"Found {len(slide_files)} slide files in project directory")
                combined_slides = []
                
                for slide_file in slide_files:
                    slide_path = os.path.join(html_project_dir, slide_file)
                    with open(slide_path, 'r', encoding='utf-8') as f:
                        slide_content = f.read().strip()
                        
                        # Wrap each slide in a page container for proper PDF pagination
                        slide_wrapped = f"""
                        <div class="slide-page" style="
                            width: 1920px; 
                            height: 1080px; 
                            page-break-after: always; 
                            box-sizing: border-box;
                            padding: 40px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                            background: {theme.color_scheme.background_start};
                            color: {theme.color_scheme.text_primary};
                            font-family: {theme.font_scheme.title_font};
                            position: relative;
                            overflow: hidden;
                        ">
                            {slide_content}
                        </div>
                        """
                        combined_slides.append(slide_wrapped)
                
                # Create complete HTML document with proper PDF styling
                html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan_data.get('presentation_title', 'Generated Presentation')}</title>
    <style>
        {theme.get_css()}
        
        @page {{
            size: 1920px 1080px;
            margin: 0;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        html, body {{
            margin: 0;
            padding: 0;
            width: 1920px;
            font-family: {theme.font_scheme.title_font};
            line-height: 1.6;
        }}
        
        .slide-page:last-child {{
            page-break-after: auto;
        }}
        
        /* Enhanced styling for better visual presentation */
        h1, h2, h3, h4, h5, h6 {{
            font-family: {theme.font_scheme.title_font};
            font-weight: bold;
            margin-bottom: 20px;
            color: {theme.color_scheme.primary};
        }}
        
        h1 {{ font-size: 3.5rem; }}
        h2 {{ font-size: 2.8rem; }}
        h3 {{ font-size: 2.2rem; }}
        
        p {{
            font-size: 1.5rem;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        ul, ol {{
            font-size: 1.4rem;
            margin-left: 30px;
            margin-bottom: 20px;
        }}
        
        li {{
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-left: 5px solid {theme.color_scheme.accent};
        }}
        
        .center {{
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
        }}
        
        .two-column {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            height: 100%;
            align-items: center;
        }}
        
        .visual-element {{
            display: inline-block;
            background: {theme.color_scheme.accent};
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 1.2rem;
            margin: 5px;
        }}
    </style>
</head>
<body>
    {''.join(combined_slides)}
</body>
</html>"""
                
                # Store the HTML for debugging
                debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
                os.makedirs(debug_dir, exist_ok=True)
                html_path = os.path.join(debug_dir, f"presentation_{project_id}.html")
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Saved combined HTML presentation to: {html_path}")
                
                # Generate PDF from the combined HTML
                return self._generate_pdf_from_html(project_id, html_content)
        
        # Fallback to old method if no project-specific slides found
        logger.error("No project-specific slides found for PDF generation.")
        raise ValueError("No project-specific HTML slides found to create presentation.")

    # def _create_html_presentation_fallback(self, plan_data: dict, project_id: str, theme: ThemeConfig) -> str:
    #     """
    #     Creates an HTML presentation from the plan data and converts it to PDF.
        
    #     Args:
    #         plan_data (dict): The presentation plan data containing slides and content
    #         project_id (str): The unique identifier for the presentation
    #         theme (ThemeConfig): The theme configuration to use
            
    #     Returns:
    #         str: Path to the generated PDF file
    #     """
    #     logger.info(f"Creating HTML presentation data with theme: {theme.display_name}")

    #     # Structure the presentation data for the template
    #     presentation_data = {
    #         'id': project_id,
    #         'title': plan_data.get('presentation_title', 'Generated Presentation'),
    #         'theme': theme.name,
    #         'metadata': {
    #             'description': plan_data.get('presentation_description', 'Created with AI'),
    #             'author': plan_data.get('author', 'AI Presentation Generator'),
    #             'date': datetime.now().strftime("%Y-%m-%d")
    #         },
    #         'slides': []
    #     }

    #     # Process each slide
    #     for slide_data in plan_data.get('slides', []):
    #         html_slide = {
    #             "type": slide_data.get("content_type", "content"),
    #             "title": slide_data.get("title", ""),
    #             "subtitle": slide_data.get("subtitle", ""),
    #             "layout": slide_data.get("layout_style", "standard"),
    #             "background": {
    #                 "type": "solid",
    #                 "value": theme.color_scheme.background_start
    #             },
    #             "content": []
    #         }

    #         # Convert content based on type
    #         if slide_data.get("content_type") == "bullet_points" and slide_data.get("bullet_points"):
    #             html_slide["content"].append({
    #                 "type": "list",
    #                 "value": slide_data["bullet_points"]
    #             })
    #         elif slide_data.get("content_type") == "paragraph" and slide_data.get("content"):
    #             html_slide["content"].append({
    #                 "type": "text",
    #                 "value": slide_data["content"]
    #             })
    #         elif slide_data.get("content_type") == "two_column" and (slide_data.get("left_content") or slide_data.get("right_content")):
    #             html_slide["content"].append({
    #                 "type": "columns",
    #                 "value": {
    #                     "left": slide_data.get("left_content", ""),
    #                     "right": slide_data.get("right_content", "")
    #                 }
    #             })
    #         elif slide_data.get("content"):
    #             # Default text content
    #             html_slide["content"].append({
    #                 "type": "text",
    #                 "value": slide_data["content"]
    #             })

    #         presentation_data['slides'].append(html_slide)

    #     # Generate HTML using the template
    #     html_content = render_template_string(
    #         PRESENTATION_TEMPLATE,
    #         presentation=presentation_data,
    #         theme_css=theme.get_css()
    #     )

    #     # Store the HTML for debugging
    #     debug_dir = os.path.join(Config.TEMP_DIR, "debug_html")
    #     os.makedirs(debug_dir, exist_ok=True)
    #     html_path = os.path.join(debug_dir, f"presentation_{project_id}.html")
        
    #     with open(html_path, 'w', encoding='utf-8') as f:
    #         f.write(html_content)
    #     logger.info(f"Saved HTML presentation to: {html_path}")
        
    #     # Generate PDF from the HTML
    #     try:
    #         pdf_path = self._generate_pdf_from_html(project_id, html_content)
    #         logger.info(f"Generated PDF at: {pdf_path}")
    #         return pdf_path
    #     except Exception as e:
    #         logger.error(f"Error generating PDF: {str(e)}")
    #         raise
    def _generate_pdf_from_html(self, project_id: str, html_content: str) -> str:
        """Generate PDF from HTML content, allowing pages to size dynamically"""
        from weasyprint import HTML, CSS
        from bs4 import BeautifulSoup
        
        # Clean HTML
        html_content = PPTProjectManager.clean_html_code_block(html_content)
        logger.info(f"Processing cleaned HTML content for PDF generation: {html_content[:200]}...")

        soup = BeautifulSoup(html_content, "html.parser")

        # (Optional) Remove scaling logic entirely, since dynamic sizing handles it
        scaled_html = str(soup)

        pdf_css = """
        @page { 
            margin: 0; 
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }

        .slide-page { 
            break-after: page;
            page-break-after: always;
        }
        .slide-page:last-child {
            break-after: auto;
            page-break-after: auto;
        }

        * {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
        """

        output_path = os.path.join(Config.GENERATED_PPTS_DIR, f"presentation_{project_id}.pdf")

        try:
            HTML(string=scaled_html, base_url=os.getcwd()).write_pdf(
                output_path, 
                stylesheets=[CSS(string=pdf_css)],
                presentational_hints=True,
                optimize_images=True
            )
            logger.info(f"Successfully generated PDF at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
