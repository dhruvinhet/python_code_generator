import os
import json
import subprocess
import sys
import shutil
import zipfile
import webbrowser
import time
import logging
import psutil
import signal
from datetime import datetime
from agents import (
    PlanningAgent, SrDeveloper1Agent, SrDeveloper2Agent, 
    TesterAgent, DetailedTesterAgent, DocumentCreatorAgent
)
from web_agents import (
    WebPlanningAgent, FrontendDeveloperAgent, BackendAPIAgent,
    FullStackIntegratorAgent, WebTesterAgent
)
from config import Config
from json_parser import json_parser

class ProjectManager:
    def __init__(self, socketio=None):
        self.socketio = socketio
        # Python application agents
        self.planning_agent = PlanningAgent()
        self.sr_developer1 = SrDeveloper1Agent()
        self.sr_developer2 = SrDeveloper2Agent()
        self.tester = TesterAgent()
        self.detailed_tester = DetailedTesterAgent()
        self.document_creator = DocumentCreatorAgent()
        
        # Web application agents
        self.web_planning_agent = WebPlanningAgent()
        self.frontend_developer = FrontendDeveloperAgent()
        self.backend_api_developer = BackendAPIAgent()
        self.fullstack_integrator = FullStackIntegratorAgent()
        self.web_tester = WebTesterAgent()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        os.makedirs(Config.GENERATED_PROJECTS_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
        
        # Clean up any leftover processes on startup
        self.cleanup_leftover_processes()
    
    def cleanup_leftover_processes(self):
        """Clean up any leftover Streamlit or web server processes"""
        try:
            self.logger.info("Cleaning up any leftover processes...")
            
            # Kill any processes on commonly used ports
            ports_to_clean = [8501, 8502, 8503, 8504, 8080]
            for port in ports_to_clean:
                self.kill_processes_on_port(port)
                
        except Exception as e:
            self.logger.warning(f"Could not clean up leftover processes: {e}")
    
    def kill_processes_on_port(self, port):
        """Kill any processes using the specified port"""
        try:
            if hasattr(self, 'emit_progress'):
                self.emit_progress("execution", f"Checking for processes on port {port}...")
            else:
                self.logger.info(f"Checking for processes on port {port}...")
                
            killed_any = False
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Get connections for this process
                    connections = proc.connections()
                    if connections:
                        for conn in connections:
                            if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                                message = f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) using port {port}"
                                if hasattr(self, 'emit_progress'):
                                    self.emit_progress("execution", message)
                                else:
                                    self.logger.info(message)
                                proc.kill()
                                killed_any = True
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception as e:
                    continue
            
            if killed_any:
                time.sleep(2)  # Give killed processes time to clean up
                message = f"Cleaned up processes on port {port}"
                if hasattr(self, 'emit_progress'):
                    self.emit_progress("execution", message)
                else:
                    self.logger.info(message)
            else:
                message = f"Port {port} is available"
                if hasattr(self, 'emit_progress'):
                    self.emit_progress("execution", message)
                else:
                    self.logger.info(message)
                
        except Exception as e:
            message = f"Warning: Could not check port {port}: {str(e)}"
            if hasattr(self, 'emit_progress'):
                self.emit_progress("execution", message)
            else:
                self.logger.warning(message)
            # Continue anyway - this is not critical
    
    def emit_progress(self, stage, message, data=None):
        """Emit progress updates to frontend via WebSocket"""
        if self.socketio:
            self.socketio.emit('progress_update', {
                'stage': stage,
                'message': message,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        print(f"[{stage}] {message}")
    
    def generate_project(self, user_prompt, project_id):
        """Main method to generate a complete project (Python or Web Application)"""
        try:
            project_dir = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Stage 1: Planning - Determine project type and create plan
            self.emit_progress("planning", "Analyzing requirements and creating project plan...")
            plan_result = self.planning_agent.create_plan(user_prompt)
            
            # Parse the plan result using robust parser
            self.logger.info(f"Parsing plan result, type: {type(plan_result)}, length: {len(str(plan_result)) if plan_result else 0}")
            project_plan = json_parser.parse_json_response(
                plan_result, 
                expected_keys=['project_name', 'description', 'project_type'],
                agent_type="planning",
                project_id=project_id
            )
            
            if not project_plan:
                self.logger.warning("Plan parsing failed, using fallback plan")
                self.emit_progress("planning", "Error parsing plan - using fallback plan")
                project_plan = json_parser.create_fallback_structure("project_plan", user_prompt)
            else:
                self.logger.info("Plan parsed successfully")
            
            # Determine project type and route to appropriate generation method
            project_type = project_plan.get('project_type', 'python_application')
            
            if project_type == 'web_application':
                return self.generate_web_application(user_prompt, project_id, project_plan)
            else:
                return self.generate_python_application(user_prompt, project_id, project_plan)
                
        except Exception as e:
            self.logger.error(f"Error in generate_project: {str(e)}")
            self.emit_progress("error", f"Project generation failed: {str(e)}")
            return None
    
    def generate_python_application(self, user_prompt, project_id, project_plan=None):
        """Generate a Python application (existing logic)"""
        try:
            project_dir = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
            
            if not project_plan:
                # Create plan if not provided
                self.emit_progress("planning", "Creating Python application plan...")
                plan_result = self.planning_agent.create_plan(user_prompt)
                project_plan = json_parser.parse_json_response(
                    plan_result, 
                    expected_keys=['project_name', 'description', 'files', 'main_file'],
                    agent_type="planning",
                    project_id=project_id
                )
            
            self.emit_progress("planning", "Python application plan created successfully", project_plan)
            
            # Stage 2: Code Generation
            self.emit_progress("coding", "Generating Python code...")
            code_result = self.sr_developer1.generate_code(json.dumps(project_plan))
            
            # Parse the code result using robust parser
            self.logger.info(f"Parsing code result, type: {type(code_result)}, length: {len(str(code_result)) if code_result else 0}")
            generated_code = json_parser.parse_json_response(
                code_result,
                expected_keys=['files'],
                agent_type="coding",
                project_id=project_id
            )
            
            if not generated_code:
                self.logger.warning("Code parsing failed, using fallback code")
                self.emit_progress("coding", "Error parsing generated code - using fallback")
                generated_code = json_parser.create_fallback_structure("code_files", str(code_result)[:500])
                if not generated_code:
                    return {"success": False, "error": "Code generation failed: Unable to parse or create fallback code"}
            else:
                self.logger.info("Code parsed successfully")
            
            self.emit_progress("coding", "Code generated successfully")
            
            # Stage 3: Code Review and Bug Fixing
            self.emit_progress("reviewing", "Reviewing and fixing code...")
            fixed_code_result = self.sr_developer2.review_and_fix(
                json.dumps(project_plan), 
                json.dumps(generated_code)
            )
            
            # Parse the fixed code result using robust parser
            fixed_code = json_parser.parse_json_response(
                fixed_code_result,
                expected_keys=['files'],
                agent_type="review",
                project_id=project_id
            )
            
            if fixed_code:
                # Use the fixed code
                final_code = fixed_code.get('files', generated_code.get('files', []))
                self.emit_progress("reviewing", "Code review and fixes applied successfully")
            else:
                # Fallback to original code if parsing fails
                self.emit_progress("reviewing", "Using original code due to parsing error in fixed code")
                final_code = generated_code.get('files', [])
            
            self.emit_progress("reviewing", "Code review completed")
            
            # Stage 4: Write files to disk
            self.emit_progress("writing", "Writing project files...")
            self._write_project_files(project_dir, final_code)
            
            # Stage 4.5: Ensure main.py exists and is properly configured
            self._ensure_main_file(project_dir, project_plan, final_code)
            
            self.emit_progress("writing", "Project files written successfully")
            
            # Stage 5: Runtime Testing
            self.emit_progress("testing", "Testing project runtime...")
            main_file = project_plan.get('main_file', 'main.py')
            runtime_success, error_traceback = self._test_runtime(project_dir, main_file)
            
            if not runtime_success and error_traceback:
                self.emit_progress("testing", "Runtime errors found, fixing...")
                # Try to fix runtime errors
                fixed_code_result = self.sr_developer2.review_and_fix(
                    json.dumps(project_plan), 
                    json.dumps({"files": final_code}),
                    error_traceback
                )
                
                # Parse the runtime-fixed code using robust parser
                fixed_code = json_parser.parse_json_response(
                    fixed_code_result,
                    expected_keys=['files'],
                    agent_type="runtime_fix",
                    project_id=project_id
                )
                
                if fixed_code:
                    final_code = fixed_code.get('files', final_code)
                    # Rewrite files and test again
                    self._write_project_files(project_dir, final_code)
                    runtime_success, error_traceback = self._test_runtime(project_dir, main_file)
            
            if runtime_success:
                self.emit_progress("testing", "Runtime testing passed")
            else:
                self.emit_progress("testing", f"Runtime testing failed: {error_traceback}")
            
            # Stage 6: Functional Testing
            self.emit_progress("functional_testing", "Performing functional testing...")
            functional_test_result = self.detailed_tester.test_functionality(
                json.dumps(project_plan), 
                json.dumps({"files": final_code}),
                runtime_success
            )
            self.emit_progress("functional_testing", "Functional testing completed")
            
            # Stage 7: Documentation
            self.emit_progress("documenting", "Creating project documentation...")
            documentation = self.document_creator.create_documentation(
                json.dumps(project_plan), 
                json.dumps({"files": final_code})
            )
            
            # Write documentation to file
            doc_path = os.path.join(project_dir, "README.md")
            try:
                doc_content = str(documentation) if documentation else "# Project Documentation\n\nNo documentation available"
                with open(doc_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(doc_content)
            except UnicodeDecodeError as e:
                print(f"Unicode error writing documentation: {e}")
                # Fallback to ASCII-safe content
                with open(doc_path, 'w', encoding='ascii', errors='replace') as f:
                    f.write("# Project Documentation\n\nDocumentation encoding error - content not available")
            except Exception as e:
                print(f"Error writing documentation: {e}")
            
            self.emit_progress("documenting", "Documentation created successfully")
            
            # Stage 8: Create requirements.txt
            self._create_requirements_file(project_dir, project_plan.get('dependencies', []))
            
            # Stage 9: Package project
            self.emit_progress("packaging", "Packaging project...")
            zip_path = self._create_project_zip(project_dir, project_id)
            self.emit_progress("packaging", "Project packaged successfully")
            
            return {
                "success": True,
                "project_id": project_id,
                "project_plan": project_plan,
                "runtime_success": runtime_success,
                "functional_test": functional_test_result,
                "zip_path": zip_path,
                "project_dir": project_dir
            }
            
        except Exception as e:
            self.emit_progress("error", f"Python application generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_web_application(self, user_prompt, project_id, project_plan=None):
        """Generate a web application with HTML, CSS, JavaScript and backend API"""
        try:
            project_dir = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
            
            if not project_plan:
                # Create web-specific plan if not provided
                self.emit_progress("planning", "Creating web application plan...")
                plan_result = self.web_planning_agent.create_web_plan(user_prompt)
                project_plan = json_parser.parse_json_response(
                    plan_result, 
                    expected_keys=['project_name', 'description', 'project_type', 'frontend_framework'],
                    agent_type="web_planning",
                    project_id=project_id
                )
                
                if not project_plan:
                    self.logger.warning("Web plan parsing failed, using fallback plan")
                    project_plan = self._create_fallback_web_plan(user_prompt)
            
            self.emit_progress("planning", "Web application plan created successfully", project_plan)
            
            # Stage 2: Frontend Generation
            self.emit_progress("frontend", "Generating frontend code (HTML, CSS, JavaScript)...")
            frontend_result = self.frontend_developer.generate_frontend_code(json.dumps(project_plan))
            
            frontend_code = json_parser.parse_json_response(
                frontend_result,
                expected_keys=['files'],
                agent_type="frontend",
                project_id=project_id
            )
            
            if not frontend_code:
                self.logger.warning("Frontend parsing failed, using fallback")
                frontend_code = self._create_fallback_frontend(project_plan)
            
            self.emit_progress("frontend", "Frontend code generated successfully")
            
            # Stage 3: Backend API Generation
            self.emit_progress("backend", "Generating backend API...")
            backend_result = self.backend_api_developer.generate_backend_code(json.dumps(project_plan))
            
            backend_code = json_parser.parse_json_response(
                backend_result,
                expected_keys=['files'],
                agent_type="backend",
                project_id=project_id
            )
            
            if not backend_code:
                self.logger.warning("Backend parsing failed, using fallback")
                backend_code = self._create_fallback_backend(project_plan)
            
            self.emit_progress("backend", "Backend API generated successfully")
            
            # Stage 4: Full-Stack Integration
            self.emit_progress("integration", "Integrating frontend and backend...")
            integration_result = self.fullstack_integrator.integrate_fullstack(
                json.dumps(project_plan),
                json.dumps(frontend_code),
                json.dumps(backend_code)
            )
            
            integrated_code = json_parser.parse_json_response(
                integration_result,
                expected_keys=['files'],
                agent_type="integration",
                project_id=project_id
            )
            
            if integrated_code:
                final_files = integrated_code.get('files', [])
                self.emit_progress("integration", "Integration completed successfully")
            else:
                # Combine frontend and backend files if integration fails
                final_files = frontend_code.get('files', []) + backend_code.get('files', [])
                self.emit_progress("integration", "Using combined files due to integration parsing error")
            
            # Stage 5: Write files to disk
            self.emit_progress("writing", "Writing web application files...")
            self._write_project_files(project_dir, final_files)
            
            # Create web-specific directories if they don't exist
            self._create_web_directories(project_dir)
            
            self.emit_progress("writing", "Web application files written successfully")
            
            # Stage 6: Web Application Testing
            self.emit_progress("testing", "Testing web application...")
            test_result = self.web_tester.test_web_application(
                json.dumps({"files": final_files}),
                json.dumps(project_plan)
            )
            
            web_test_results = json_parser.parse_json_response(
                test_result,
                expected_keys=['test_results'],
                agent_type="web_testing",
                project_id=project_id
            )
            
            if web_test_results:
                self.emit_progress("testing", "Web application testing completed", web_test_results)
            else:
                self.emit_progress("testing", "Testing completed with parsing issues")
            
            # Stage 7: Create web documentation
            self.emit_progress("documenting", "Creating web application documentation...")
            documentation = self.document_creator.create_documentation(
                json.dumps(project_plan), 
                json.dumps({"files": final_files})
            )
            
            # Write documentation to file
            doc_path = os.path.join(project_dir, "README.md")
            try:
                doc_content = str(documentation) if documentation else self._create_web_readme(project_plan)
                with open(doc_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(doc_content)
            except Exception as e:
                print(f"Error writing web documentation: {e}")
                # Create basic web README
                with open(doc_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(self._create_web_readme(project_plan))
            
            self.emit_progress("documenting", "Web documentation created successfully")
            
            # Stage 8: Create web-specific configuration files
            self._create_web_config_files(project_dir, project_plan)
            
            # Stage 9: Package web project
            self.emit_progress("packaging", "Packaging web application...")
            zip_path = self._create_project_zip(project_dir, project_id)
            self.emit_progress("packaging", "Web application packaged successfully")
            
            return {
                "success": True,
                "project_id": project_id,
                "project_type": "web_application",
                "project_plan": project_plan,
                "frontend_framework": project_plan.get('frontend_framework', 'vanilla_js'),
                "backend_framework": project_plan.get('backend_framework', 'flask'),
                "test_results": web_test_results,
                "zip_path": zip_path,
                "project_dir": project_dir
            }
            
        except Exception as e:
            self.emit_progress("error", f"Web application generation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_fallback_plan(self, user_prompt):
        """Create a basic fallback plan if AI planning fails"""
        return {
            "project_name": "python_project",
            "description": f"Python project based on: {user_prompt}",
            "dependencies": [""],
            "gui_framework": "none",
            "files": [
                {
                    "path": "main.py",
                    "purpose": "Main entry point of the application",
                    "functions": ["main"],
                    "imports": []
                }
            ],
            "main_file": "main.py",
            "architecture": "Simple single-file Python application"
        }
    
    def _ensure_main_file(self, project_dir, project_plan, files):
        """Ensure a main.py file exists that can run the project"""
        main_path = os.path.join(project_dir, "main.py")
        
        # Check if main.py already exists in the generated files
        main_exists = any(file_info.get('path') == 'main.py' for file_info in files)
        
        if not main_exists:
            # Generate main.py based on project type
            gui_framework = project_plan.get('gui_framework', 'none').lower()
            project_files = [f.get('path', '') for f in files]
            
            main_content = self._generate_main_content(gui_framework, project_files, project_plan)
            
            try:
                with open(main_path, 'w', encoding='utf-8') as f:
                    f.write(main_content)
            except Exception as e:
                print(f"Error creating main.py: {e}")
    
    def _generate_main_content(self, gui_framework, project_files, project_plan):
        """Generate content for main.py based on project type"""
        
        if gui_framework == 'streamlit':
            # Find the streamlit interface file
            streamlit_file = None
            for file_path in project_files:
                if 'interface' in file_path.lower() or 'ui' in file_path.lower() or 'app' in file_path.lower():
                    streamlit_file = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
                    if streamlit_file.startswith('.'):
                        streamlit_file = streamlit_file[1:]
                    break
            
            if not streamlit_file:
                streamlit_file = project_files[0].replace('.py', '').replace('/', '.').replace('\\', '.') if project_files else 'app'
                if streamlit_file.startswith('.'):
                    streamlit_file = streamlit_file[1:]
            
            return f'''#!/usr/bin/env python3
"""
Main entry point for {project_plan.get('project_name', 'the project')}
This file automatically detects the execution environment and runs the application appropriately.
"""

import sys
import os
import subprocess
import importlib.util

def main():
    """Main function to run the application"""
    try:
        # Check if we're running in a streamlit context
        if 'streamlit' in sys.modules or any('streamlit' in str(arg) for arg in sys.argv):
            # Already running under streamlit
            import {streamlit_file}
            {streamlit_file}.main()
        else:
            # Try to run with streamlit
            try:
                import streamlit
                print("Streamlit app detected. Starting with streamlit run...")
                print("Visit the URL shown above to interact with the application.")
                
                # Find the streamlit file to run
                streamlit_file_path = "{streamlit_file.replace('.', os.sep)}.py"
                if not os.path.exists(streamlit_file_path):
                    # Look for any .py file with streamlit imports
                    for file in os.listdir('.'):
                        if file.endswith('.py') and file != 'main.py':
                            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if 'streamlit' in content:
                                    streamlit_file_path = file
                                    break
                
                # Run streamlit
                result = subprocess.run([
                    sys.executable, '-m', 'streamlit', 'run', streamlit_file_path,
                    '--server.headless', 'true',
                    '--server.port', '8501'
                ], check=True)
                
            except ImportError:
                print("Streamlit not installed. Installing...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
                print("Please run 'python main.py' again after installation.")
            except Exception as e:
                print(f"Error running streamlit app: {{e}}")
                print(f"You can manually run: streamlit run {{streamlit_file_path}}")
                return 1
                
    except Exception as e:
        print(f"Error starting application: {{e}}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        elif gui_framework == 'tkinter':
            # Find the main GUI file
            gui_file = None
            for file_path in project_files:
                if 'gui' in file_path.lower() or 'interface' in file_path.lower() or 'ui' in file_path.lower():
                    gui_file = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
                    if gui_file.startswith('.'):
                        gui_file = gui_file[1:]
                    break
            
            if not gui_file:
                gui_file = project_files[0].replace('.py', '').replace('/', '.').replace('\\', '.') if project_files else 'app'
                if gui_file.startswith('.'):
                    gui_file = gui_file[1:]
            
            return f'''#!/usr/bin/env python3
"""
Main entry point for {project_plan.get('project_name', 'the project')}
This file runs the Tkinter GUI application.
"""

import sys
import os

def main():
    """Main function to run the application"""
    try:
        # Import and run the GUI application
        import {gui_file}
        
        # Look for a main function or run method
        if hasattr({gui_file}, 'main'):
            {gui_file}.main()
        elif hasattr({gui_file}, 'run'):
            {gui_file}.run()
        else:
            # Try to find and instantiate the main class
            for attr_name in dir({gui_file}):
                attr = getattr({gui_file}, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '__init__') and 
                    'tk' in str(attr).lower()):
                    app = attr()
                    if hasattr(app, 'mainloop'):
                        app.mainloop()
                    elif hasattr(app, 'run'):
                        app.run()
                    break
            else:
                print("Could not find a way to run the GUI application")
                return 1
                
    except Exception as e:
        print(f"Error starting application: {{e}}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        else:
            # Console application or other
            main_module = None
            for file_path in project_files:
                if 'main' in file_path.lower() and file_path != 'main.py':
                    main_module = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
                    if main_module.startswith('.'):
                        main_module = main_module[1:]
                    break
            
            if not main_module and project_files:
                main_module = project_files[0].replace('.py', '').replace('/', '.').replace('\\', '.')
                if main_module.startswith('.'):
                    main_module = main_module[1:]
            
            return f'''#!/usr/bin/env python3
"""
Main entry point for {project_plan.get('project_name', 'the project')}
This file runs the console application.
"""

import sys
import os

def main():
    """Main function to run the application"""
    try:
        # Import and run the main application
        {f"import {main_module}" if main_module else "pass"}
        
        # Look for a main function to call
        {f"""
        if hasattr({main_module}, 'main'):
            {main_module}.main()
        elif hasattr({main_module}, 'run'):
            {main_module}.run()
        else:
            print("Application loaded successfully. Check the imported modules for functionality.")
        """ if main_module else 'print("No main module found to execute")'}
        
    except Exception as e:
        print(f"Error starting application: {{e}}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''

    def _write_project_files(self, project_dir, files):
        """Write generated code files to disk"""
        for file_info in files:
            try:
                file_path = os.path.join(project_dir, file_info['path'])
                file_dir = os.path.dirname(file_path)
                
                # Create directory if it doesn't exist
                if file_dir:
                    os.makedirs(file_dir, exist_ok=True)
                
                # Get file content and handle potential encoding issues
                content = file_info.get('content', '')
                if not isinstance(content, str):
                    content = str(content)
                
                # Write file content with explicit UTF-8 encoding
                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
                    
            except UnicodeDecodeError as e:
                print(f"Unicode error writing file {file_info.get('path', 'unknown')}: {e}")
                # Try writing with different encoding or skip
                try:
                    with open(file_path, 'w', encoding='latin-1') as f:
                        f.write(content)
                except Exception as e2:
                    print(f"Failed to write file with fallback encoding: {e2}")
                    continue
            except Exception as e:
                print(f"Error writing file {file_info.get('path', 'unknown')}: {e}")
                continue
    
    def _test_runtime(self, project_dir, main_file):
        """Test if the project runs without runtime errors"""
        try:
            main_path = os.path.join(project_dir, "main.py")  # Always use main.py
            if not os.path.exists(main_path):
                return False, f"Main file main.py not found"
            
            # Run the main file in a subprocess with a timeout
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd=project_dir,
                capture_output=True,
                text=True,
                timeout=10  # Reduced timeout for quick validation
            )
            
            if result.returncode == 0:
                return True, None
            else:
                # Check if it's a streamlit app that needs special handling
                if "streamlit run" in result.stderr or "streamlit run" in result.stdout:
                    return True, "Streamlit app detected - would run with streamlit run"
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            # For GUI apps or long-running apps, timeout might be expected
            return True, "Process timeout - likely interactive application"
        except Exception as e:
            return False, str(e)
    
    def _create_requirements_file(self, project_dir, dependencies):
        """Create requirements.txt file"""
        req_path = os.path.join(project_dir, "requirements.txt")
        try:
            with open(req_path, 'w', encoding='utf-8', errors='replace') as f:
                for dep in dependencies:
                    if dep and dep.strip():  # Only write non-empty dependencies
                        # Ensure dependency is a string and clean it
                        dep_str = str(dep).strip()
                        f.write(f"{dep_str}\n")
        except Exception as e:
            print(f"Error creating requirements.txt: {e}")
            # Create an empty requirements.txt as fallback
            try:
                with open(req_path, 'w', encoding='utf-8') as f:
                    f.write("# Requirements file - error during generation\n")
            except Exception as e2:
                print(f"Failed to create fallback requirements.txt: {e2}")
    
    def _create_project_zip(self, project_dir, project_id):
        """Create a zip file of the project"""
        zip_path = os.path.join(Config.TEMP_DIR, f"{project_id}.zip")
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_dir)
                        
                        # Add error handling for individual files
                        try:
                            zipf.write(file_path, arcname)
                        except UnicodeDecodeError as e:
                            print(f"Unicode error with file {file_path}: {e}")
                            # Skip problematic files or handle them differently
                            continue
                        except Exception as e:
                            print(f"Error adding file {file_path} to zip: {e}")
                            continue
            
            return zip_path
        except Exception as e:
            print(f"Error creating zip file: {e}")
            raise

    def analyze_project_structure(self, project_path):
        """
        Dynamically analyze project structure and determine the best execution method.
        This method inspects the actual files and creates appropriate run configurations.
        """
        try:
            analysis = {
                'project_type': 'unknown',
                'entry_points': [],
                'frameworks': [],
                'structure': {},
                'run_method': 'python',
                'recommended_command': None,
                'port': None
            }
            
            # Get all files in the project
            all_files = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith(('.py', '.html', '.js', '.css', '.json', '.txt', '.md')):
                        rel_path = os.path.relpath(os.path.join(root, file), project_path)
                        all_files.append(rel_path)
            
            analysis['structure']['all_files'] = all_files
            
            # Analyze Python files for frameworks and patterns
            python_files = [f for f in all_files if f.endswith('.py')]
            html_files = [f for f in all_files if f.endswith('.html')]
            js_files = [f for f in all_files if f.endswith('.js')]
            css_files = [f for f in all_files if f.endswith('.css')]
            
            analysis['structure']['python_files'] = python_files
            analysis['structure']['html_files'] = html_files
            analysis['structure']['js_files'] = js_files
            analysis['structure']['css_files'] = css_files
            
            # Check for specific framework indicators
            frameworks_found = set()
            entry_points = []
            
            for py_file in python_files:
                file_path = os.path.join(project_path, py_file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                        # Framework detection
                        if 'streamlit' in content or 'st.' in content:
                            frameworks_found.add('streamlit')
                            entry_points.append({'file': py_file, 'type': 'streamlit'})
                        
                        if 'fastapi' in content:
                            frameworks_found.add('fastapi')
                            entry_points.append({'file': py_file, 'type': 'fastapi'})
                        
                        if 'flask' in content:
                            frameworks_found.add('flask')
                            entry_points.append({'file': py_file, 'type': 'flask'})
                        
                        if 'django' in content:
                            frameworks_found.add('django')
                            entry_points.append({'file': py_file, 'type': 'django'})
                        
                        if 'tkinter' in content or 'tk' in content:
                            frameworks_found.add('tkinter')
                            entry_points.append({'file': py_file, 'type': 'tkinter'})
                        
                        if 'pygame' in content:
                            frameworks_found.add('pygame')
                            entry_points.append({'file': py_file, 'type': 'pygame'})
                        
                        # Check for uvicorn.run calls (FastAPI)
                        if 'uvicorn.run' in content:
                            frameworks_found.add('fastapi')
                            entry_points.append({'file': py_file, 'type': 'fastapi_uvicorn'})
                        
                        # Check for app.run calls (Flask)
                        if 'app.run(' in content:
                            frameworks_found.add('flask')
                            entry_points.append({'file': py_file, 'type': 'flask_run'})
                            
                except Exception as e:
                    continue
            
            analysis['frameworks'] = list(frameworks_found)
            analysis['entry_points'] = entry_points
            
            # Determine project type and run method
            if 'streamlit' in frameworks_found:
                analysis['project_type'] = 'streamlit'
                analysis['run_method'] = 'streamlit'
                # Find the main streamlit file
                streamlit_files = [ep['file'] for ep in entry_points if ep['type'] == 'streamlit']
                if streamlit_files:
                    analysis['recommended_command'] = f"streamlit run {streamlit_files[0]}"
                    analysis['port'] = 8501
                    
            elif 'fastapi' in frameworks_found:
                analysis['project_type'] = 'fastapi'
                analysis['run_method'] = 'fastapi'
                # Check for uvicorn runner files
                fastapi_files = [ep['file'] for ep in entry_points if 'fastapi' in ep['type']]
                if fastapi_files:
                    # Look for run.py or main.py with uvicorn
                    if 'run.py' in all_files:
                        analysis['recommended_command'] = "python run.py"
                    else:
                        # Try to determine the app location
                        app_location = self._find_fastapi_app_location(project_path, fastapi_files[0])
                        analysis['recommended_command'] = f"uvicorn {app_location} --reload --port 8080"
                    analysis['port'] = 8080
                    
            elif 'flask' in frameworks_found:
                analysis['project_type'] = 'flask'
                analysis['run_method'] = 'web'
                # Check for run.py or app.py
                if 'run.py' in all_files:
                    analysis['recommended_command'] = "python run.py"
                elif 'app.py' in all_files:
                    analysis['recommended_command'] = "python app.py"
                analysis['port'] = 8080
                
            elif 'django' in frameworks_found:
                analysis['project_type'] = 'django'
                analysis['run_method'] = 'django'
                analysis['recommended_command'] = "python manage.py runserver"
                analysis['port'] = 8000
                
            elif html_files and (js_files or css_files):
                analysis['project_type'] = 'web_frontend'
                analysis['run_method'] = 'static'
                # Static web project
                if 'index.html' in all_files:
                    analysis['recommended_command'] = "serve index.html"
                    
            elif 'tkinter' in frameworks_found or 'pygame' in frameworks_found:
                analysis['project_type'] = 'desktop'
                analysis['run_method'] = 'python'
                # Desktop application
                desktop_files = [ep['file'] for ep in entry_points if ep['type'] in ['tkinter', 'pygame']]
                if desktop_files:
                    analysis['recommended_command'] = f"python {desktop_files[0]}"
                    
            else:
                # Generic Python project
                analysis['project_type'] = 'python'
                analysis['run_method'] = 'python'
                # Look for main.py, run.py, or app.py
                if 'main.py' in all_files:
                    analysis['recommended_command'] = "python main.py"
                elif 'run.py' in all_files:
                    analysis['recommended_command'] = "python run.py"
                elif 'app.py' in all_files:
                    analysis['recommended_command'] = "python app.py"
                elif python_files:
                    analysis['recommended_command'] = f"python {python_files[0]}"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing project structure: {e}")
            return {
                'project_type': 'python',
                'run_method': 'python',
                'error': str(e)
            }
    
    def _find_fastapi_app_location(self, project_path, main_file):
        """Find the FastAPI app instance location for uvicorn"""
        try:
            file_path = os.path.join(project_path, main_file)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Look for app = FastAPI() or similar patterns
                import re
                app_patterns = [
                    r'(\w+)\s*=\s*FastAPI\(',
                    r'app\s*=\s*FastAPI\(',
                ]
                
                for pattern in app_patterns:
                    match = re.search(pattern, content)
                    if match:
                        app_name = match.group(1) if match.groups() else 'app'
                        # Convert file path to module path
                        module_path = main_file.replace('.py', '').replace('/', '.').replace('\\', '.')
                        return f"{module_path}:{app_name}"
                
                # Default assumption
                module_path = main_file.replace('.py', '').replace('/', '.').replace('\\', '.')
                return f"{module_path}:app"
                
        except Exception:
            return "app:app"
    
    def create_dynamic_run_script(self, project_path, analysis):
        """
        Create a dynamic run script based on project analysis.
        This replaces hardcoded run.py files with intelligent, adaptive scripts.
        """
        try:
            project_type = analysis.get('project_type', 'python')
            frameworks = analysis.get('frameworks', [])
            entry_points = analysis.get('entry_points', [])
            
            if project_type == 'streamlit':
                return self._create_streamlit_runner(project_path, analysis)
            elif project_type == 'fastapi':
                return self._create_fastapi_runner(project_path, analysis)
            elif project_type == 'flask':
                return self._create_flask_runner(project_path, analysis)
            elif project_type == 'django':
                return self._create_django_runner(project_path, analysis)
            elif project_type == 'web_frontend':
                return self._create_static_web_runner(project_path, analysis)
            elif project_type == 'desktop':
                return self._create_desktop_runner(project_path, analysis)
            else:
                return self._create_generic_python_runner(project_path, analysis)
                
        except Exception as e:
            self.logger.error(f"Error creating dynamic run script: {e}")
            return self._create_fallback_runner(project_path)
    
    def _create_streamlit_runner(self, project_path, analysis):
        """Create a Streamlit-specific runner"""
        entry_points = [ep for ep in analysis.get('entry_points', []) if ep['type'] == 'streamlit']
        main_file = entry_points[0]['file'] if entry_points else 'main.py'
        
        runner_content = f'''#!/usr/bin/env python3
"""
Auto-generated Streamlit application runner
Project Type: Streamlit Web App
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading

def main():
    """Run the Streamlit application"""
    print("Starting Streamlit application...")
    print("Dashboard will open automatically in your browser")
    print("-" * 50)
    
    try:
        # Import streamlit to check if it's available
        import streamlit
        
        # Define the streamlit file to run
        streamlit_file = "{main_file}"
        
        # Start streamlit server
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', streamlit_file,
            '--server.port', '8501',
            '--server.headless', 'false'
        ]
        
        print(f"Running: {{' '.join(cmd)}}")
        
        # Open browser after a delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8501')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run streamlit
        process = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
        process.wait()
        
    except ImportError:
        print("Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
        print("Please run again after installation.")
    except KeyboardInterrupt:
        print("\\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running Streamlit app: {{e}}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        run_py_path = os.path.join(project_path, 'run.py')
        with open(run_py_path, 'w', encoding='utf-8') as f:
            f.write(runner_content)
        
        return {'success': True, 'runner_type': 'streamlit', 'entry_file': main_file}
    
    def _create_fastapi_runner(self, project_path, analysis):
        """Create a FastAPI-specific runner"""
        entry_points = [ep for ep in analysis.get('entry_points', []) if 'fastapi' in ep['type']]
        
        # Check if run.py already exists and is properly configured
        existing_run = os.path.join(project_path, 'run.py')
        if os.path.exists(existing_run):
            try:
                with open(existing_run, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'uvicorn' in content and 'fastapi' in content.lower():
                        # Existing run.py looks good, just ensure __init__.py exists
                        self._ensure_package_structure(project_path)
                        return {'success': True, 'runner_type': 'fastapi_existing', 'entry_file': 'run.py'}
            except Exception:
                pass
        
        # Create new FastAPI runner
        app_location = analysis.get('recommended_command', 'app:app')
        if 'uvicorn' in app_location:
            app_location = app_location.split()[-1]  # Extract just the app location
        
        runner_content = f'''#!/usr/bin/env python3
"""
Auto-generated FastAPI application runner
Project Type: FastAPI Web API
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading

def main():
    """Run the FastAPI application"""
    print("Starting FastAPI application...")
    print("API will be available at http://localhost:8080")
    print("Documentation at http://localhost:8080/docs")
    print("-" * 50)
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try to import required modules
        try:
            import uvicorn
            import fastapi
        except ImportError as e:
            print(f"Missing dependencies: {{e}}")
            print("Installing required packages...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fastapi', 'uvicorn[standard]'])
        
        # Start FastAPI server
        app_location = "{app_location}"
        
        print(f"Starting server with app: {{app_location}}")
        
        # Open browser after a delay
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8080/docs')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run uvicorn
        uvicorn.run(app_location, host="0.0.0.0", port=8080, reload=True)
        
    except KeyboardInterrupt:
        print("\\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running FastAPI app: {{e}}")
        print("Trying alternative startup method...")
        try:
            # Fallback method
            cmd = [sys.executable, '-m', 'uvicorn', app_location, '--host', '0.0.0.0', '--port', '8080', '--reload']
            subprocess.run(cmd, cwd=current_dir)
        except Exception as e2:
            print(f"Fallback method failed: {{e2}}")
            return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        run_py_path = os.path.join(project_path, 'run.py')
        with open(run_py_path, 'w', encoding='utf-8') as f:
            f.write(runner_content)
        
        # Ensure package structure
        self._ensure_package_structure(project_path)
        
        return {'success': True, 'runner_type': 'fastapi', 'app_location': app_location}
    
    def _create_flask_runner(self, project_path, analysis):
        """Create a Flask-specific runner using WSGI server for Windows compatibility"""
        entry_points = [ep for ep in analysis.get('entry_points', []) if ep['type'] in ['flask', 'flask_run']]
        
        # Find the Flask app
        app_file = 'app.py'
        if entry_points:
            app_file = entry_points[0]['file']
        elif 'app.py' in analysis.get('structure', {}).get('python_files', []):
            app_file = 'app.py'
        
        # Check if it's using app factory pattern
        app_import = "from app import app"
        app_obj = "app"
        
        try:
            app_path = os.path.join(project_path, app_file)
            if os.path.exists(app_path):
                with open(app_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'def create_app(' in content:
                        app_import = "from app import create_app"
                        app_obj = "create_app()"
        except Exception:
            pass
        
        runner_content = f'''#!/usr/bin/env python3
"""
Auto-generated Flask application runner
Project Type: Flask Web Application
Uses WSGI server for Windows compatibility
"""

import os
import sys
import time
import webbrowser
import threading
from wsgiref.simple_server import make_server, WSGIServer

class QuietWSGIServer(WSGIServer):
    """A quieter WSGI server"""
    def log_message(self, format, *args):
        pass

def main():
    """Run the Flask application"""
    print("Starting Flask web application...")
    print("Application will be available at http://localhost:8080")
    print("-" * 50)
    
    try:
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import the Flask app
        {app_import}
        app = {app_obj}
        
        port = 8080
        host = '0.0.0.0'
        
        # Create WSGI server
        with make_server(host, port, app, server_class=QuietWSGIServer) as httpd:
            print(f"Server started successfully on http://localhost:{{port}}")
            
            # Open browser after delay
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{{port}}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Serve forever
            httpd.serve_forever()
            
    except ImportError as e:
        print(f"Import error: {{e}}")
        print("Installing Flask...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask'])
        print("Please run again after installation.")
    except KeyboardInterrupt:
        print("\\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running Flask app: {{e}}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
'''
        
        run_py_path = os.path.join(project_path, 'run.py')
        with open(run_py_path, 'w', encoding='utf-8') as f:
            f.write(runner_content)
        
        return {'success': True, 'runner_type': 'flask', 'app_file': app_file}
    
    def _ensure_package_structure(self, project_path):
        """Ensure proper Python package structure with __init__.py files"""
        try:
            # Find all directories with Python files
            python_dirs = set()
            for root, dirs, files in os.walk(project_path):
                if any(f.endswith('.py') for f in files):
                    rel_dir = os.path.relpath(root, project_path)
                    if rel_dir != '.':
                        python_dirs.add(rel_dir)
            
            # Create __init__.py files
            for py_dir in python_dirs:
                init_path = os.path.join(project_path, py_dir, '__init__.py')
                if not os.path.exists(init_path):
                    with open(init_path, 'w', encoding='utf-8') as f:
                        f.write('# This file makes the directory a Python package\\n')
                        
        except Exception as e:
            self.logger.warning(f"Could not ensure package structure: {e}")

    def determine_run_method(self, project_path):
        """
        New intelligent project detection system.
        Uses dynamic analysis instead of hardcoded patterns.
        """
        try:
            # First, analyze the project structure dynamically
            analysis = self.analyze_project_structure(project_path)
            
            # Create or update the run script based on analysis
            runner_result = self.create_dynamic_run_script(project_path, analysis)
            
            # Log the analysis for debugging
            self.logger.info(f"Project analysis for {project_path}:")
            self.logger.info(f"  Type: {analysis.get('project_type', 'unknown')}")
            self.logger.info(f"  Frameworks: {analysis.get('frameworks', [])}")
            self.logger.info(f"  Run method: {analysis.get('run_method', 'python')}")
            self.logger.info(f"  Recommended command: {analysis.get('recommended_command', 'N/A')}")
            
            return analysis.get('run_method', 'python')
            
        except Exception as e:
            self.logger.error(f"Error in dynamic project analysis: {e}")
            # Fallback to simple detection
            return self._fallback_run_method_detection(project_path)
    
    def _fallback_run_method_detection(self, project_path):
        """Fallback method for when dynamic analysis fails"""
        try:
            # Simple file-based detection as fallback
            files = os.listdir(project_path)
            
            # Check for streamlit
            for file in files:
                if file.endswith('.py'):
                    try:
                        with open(os.path.join(project_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            if 'streamlit' in content:
                                return 'streamlit'
                    except:
                        continue
            
            # Check for web applications
            has_templates = 'templates' in files or any('template' in f for f in files)
            has_static = 'static' in files
            has_html = any(f.endswith('.html') for f in files)
            has_app_py = 'app.py' in files
            has_run_py = 'run.py' in files
            
            if (has_app_py or has_run_py) and (has_templates or has_static or has_html):
                return 'web'
            
            # Default to python
            return 'python'
            
        except Exception as e:
            self.logger.error(f"Error in fallback detection: {e}")
            return 'python'
        """Determine how to run the project (python, streamlit, or web)"""
        try:
            # Check if it's a web application first
            run_py_path = os.path.join(project_path, 'run.py')
            app_py_path = os.path.join(project_path, 'app.py')
            index_html_path = os.path.join(project_path, 'index.html')
            templates_dir = os.path.join(project_path, 'templates')
            static_dir = os.path.join(project_path, 'static')
            
            # Enhanced web application detection
            has_run_py = os.path.exists(run_py_path)
            has_app_py = os.path.exists(app_py_path)
            has_templates = os.path.exists(templates_dir)
            has_static = os.path.exists(static_dir)
            has_index_html = os.path.exists(index_html_path)
            
            # Check if it's a Flask web application
            if has_run_py and has_app_py and (has_templates or has_static or has_index_html):
                try:
                    with open(app_py_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if 'flask' in content:
                            return 'web'
                except:
                    pass
            
            # Alternative web detection - check if run.py imports app and app.py contains Flask
            if has_run_py and has_app_py:
                try:
                    # Check if app.py contains Flask
                    with open(app_py_path, 'r', encoding='utf-8', errors='ignore') as f:
                        app_content = f.read().lower()
                        if 'flask' in app_content and ('routes' in app_content or 'blueprint' in app_content or '@app.route' in app_content):
                            return 'web'
                except:
                    pass
            
            # Check main.py for streamlit imports
            main_py_path = os.path.join(project_path, 'main.py')
            if os.path.exists(main_py_path):
                with open(main_py_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'streamlit' in content or 'st.' in content:
                        return 'streamlit'
            
            # Check requirements.txt for streamlit
            requirements_path = os.path.join(project_path, 'requirements.txt')
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'streamlit' in content:
                        return 'streamlit'
            
            # Default to python
            return 'python'
            
        except Exception as e:
            print(f"Error determining run method: {e}")
            return 'python'

    def execute_project(self, project_id, project_path, run_method):
        """Execute the project and capture output with dynamic detection"""
        original_cwd = os.getcwd()
        try:
            self.emit_progress("execution", f"Analyzing project structure...")
            
            # Dynamically analyze the project structure
            analysis = self.analyze_project_structure(project_path)
            actual_run_method = analysis.get('run_method', run_method)
            project_type = analysis.get('project_type', 'python')
            
            self.emit_progress("execution", f"Detected project type: {project_type}")
            self.emit_progress("execution", f"Using run method: {actual_run_method}")
            
            # Create or update dynamic run script
            runner_result = self.create_dynamic_run_script(project_path, analysis)
            
            if runner_result.get('success'):
                self.emit_progress("execution", f"Created dynamic runner: {runner_result.get('runner_type', 'generic')}")
            else:
                self.emit_progress("execution", "Using existing project structure")
            
            # Store process reference for potential termination
            if not hasattr(self, 'running_processes'):
                self.running_processes = {}
            
            # Stop any existing process for this project first
            if project_id in self.running_processes:
                self.emit_progress("execution", "Stopping existing process for this project...")
                self.stop_project_execution(project_id)
                time.sleep(1)  # Give it a moment to clean up
            
            # Change to project directory
            os.chdir(project_path)
            
            # Install dependencies first
            self.emit_progress("execution", "Installing project dependencies...")
            requirements_path = os.path.join(project_path, 'requirements.txt')
            
            if os.path.exists(requirements_path):
                try:
                    # Install requirements
                    self.emit_progress("execution", "Installing dependencies (this may take a moment)...")
                    pip_result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--user', '--quiet'
                    ], capture_output=True, text=True, timeout=300)
                    
                    if pip_result.returncode != 0:
                        self.emit_progress("execution", f"Warning: Some dependencies may not have installed properly")
                        self.emit_progress("execution", f"Pip stderr: {pip_result.stderr[:200]}...")
                        # Continue anyway - many projects can run with partial dependencies
                    else:
                        self.emit_progress("execution", "Dependencies installed successfully")
                        
                except subprocess.TimeoutExpired:
                    self.emit_progress("execution", "Warning: Dependency installation timed out, proceeding anyway")
                except Exception as e:
                    self.emit_progress("execution", f"Warning: Could not install dependencies: {str(e)[:100]}...")
            else:
                self.emit_progress("execution", "No requirements.txt found, proceeding without dependency installation")
            
            
        except Exception as e:
            self.emit_progress("execution", f"Execution failed: {str(e)}")
            return {
                'success': False,
                'method': actual_run_method,
                'error': str(e),
                'output': '',
                'status': 'failed'
            }
        finally:
            # Restore original working directory
            try:
                os.chdir(original_cwd)
            except Exception:
                pass
        """Execute project using the dynamically determined method"""
        try:
            recommended_command = analysis.get('recommended_command', 'python run.py')
            port = analysis.get('port', 8080)
            
            self.emit_progress("execution", f"Executing: {recommended_command}")
            
            # Always try to run run.py first (our dynamic runner)
            run_py_path = os.path.join(project_path, 'run.py')
            if os.path.exists(run_py_path):
                cmd = [sys.executable, 'run.py']
                self.emit_progress("execution", f"Starting with dynamic runner: {' '.join(cmd)}")
                
                # Start the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=project_path
                )
                
                self.running_processes[project_id] = process
                
                # Monitor process startup
                startup_checks = 5
                for i in range(startup_checks):
                    time.sleep(1)
                    
                    # Check if process terminated early
                    if process.poll() is not None:
                        stdout, stderr = process.communicate()
                        self.emit_progress("execution", f"Process failed to start. Exit code: {process.returncode}")
                        if stdout:
                            self.emit_progress("execution", f"Stdout: {stdout[:500]}")
                        if stderr:
                            self.emit_progress("execution", f"Stderr: {stderr[:500]}")
                        return {
                            'success': False,
                            'method': run_method,
                            'error': f"Process failed to start: {stderr or 'Process terminated unexpectedly'}",
                            'output': stdout or '',
                            'status': 'failed'
                        }
                    
                    self.emit_progress("execution", f"Checking startup... ({i+1}/{startup_checks})")
                
                if process.poll() is None:  # Process is still running
                    self.emit_progress("execution", f"Application started successfully!")
                    
                    # For web applications, test connectivity and open browser
                    if run_method in ['web', 'streamlit', 'fastapi', 'flask']:
                        try:
                            time.sleep(2)  # Give server time to be ready
                            self.emit_progress("execution", f"Server should be available on port {port}")
                            
                            # Open browser automatically
                            def open_browser():
                                time.sleep(1)
                                url = f'http://localhost:{port}'
                                if run_method == 'fastapi':
                                    url += '/docs'  # Open API docs for FastAPI
                                webbrowser.open(url)
                                self.emit_progress("execution", f"Browser opened automatically: {url}")
                            
                            import threading
                            browser_thread = threading.Thread(target=open_browser)
                            browser_thread.daemon = True
                            browser_thread.start()
                            
                        except Exception as e:
                            self.emit_progress("execution", f"Could not open browser automatically: {str(e)}")
                    
                    return {
                        'success': True,
                        'method': run_method,
                        'message': f'{analysis.get("project_type", "Application").title()} started successfully',
                        'url': f'http://localhost:{port}' if port else None,
                        'status': 'running',
                        'pid': process.pid,
                        'port': port,
                        'output': f'Application is running on port {port}' if port else 'Application started successfully',
                        'auto_opened': True,
                        'project_type': analysis.get('project_type', 'unknown')
                    }
                else:
                    # Final check - process terminated after startup monitoring
                    stdout, stderr = process.communicate()
                    self.emit_progress("execution", f"Application stopped unexpectedly after startup")
                    return {
                        'success': False,
                        'method': run_method,
                        'error': f"Application stopped unexpectedly: {stderr or 'Unknown error'}",
                        'output': stdout or '',
                        'status': 'failed'
                    }
            else:
                # No run.py found, try direct execution based on analysis
                return self._execute_direct_command(project_id, project_path, recommended_command, analysis)
                
        except Exception as e:
            self.emit_progress("execution", f"Dynamic execution failed: {str(e)}")
            return {
                'success': False,
                'method': run_method,
                'error': str(e),
                'output': '',
                'status': 'failed'
            }
    
    def _execute_direct_command(self, project_id, project_path, command, analysis):
        """Execute project using direct command when no run.py is available"""
        try:
            # Parse the command
            if isinstance(command, str):
                cmd_parts = command.split()
            else:
                cmd_parts = command
            
            self.emit_progress("execution", f"Direct execution: {' '.join(cmd_parts)}")
            
            # Start the process
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=project_path
            )
            
            self.running_processes[project_id] = process
            
            # For quick-running scripts, get output
            if analysis.get('project_type') in ['python', 'desktop']:
                try:
                    stdout, stderr = process.communicate(timeout=30)
                    return {
                        'success': process.returncode == 0,
                        'method': analysis.get('run_method', 'python'),
                        'error': stderr if process.returncode != 0 else None,
                        'output': stdout,
                        'status': 'completed',
                        'exit_code': process.returncode
                    }
                except subprocess.TimeoutExpired:
                    # Long-running process
                    return {
                        'success': True,
                        'method': analysis.get('run_method', 'python'),
                        'message': 'Long-running application started',
                        'status': 'running',
                        'pid': process.pid
                    }
            else:
                # Web applications - monitor like before
                time.sleep(3)
                if process.poll() is None:
                    return {
                        'success': True,
                        'method': analysis.get('run_method', 'web'),
                        'message': 'Web application started',
                        'status': 'running',
                        'pid': process.pid,
                        'port': analysis.get('port', 8080)
                    }
                else:
                    stdout, stderr = process.communicate()
                    return {
                        'success': False,
                        'method': analysis.get('run_method', 'web'),
                        'error': stderr,
                        'output': stdout,
                        'status': 'failed'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'method': analysis.get('run_method', 'python'),
                'error': str(e),
                'output': '',
                'status': 'failed'
            }
            
            if os.path.exists(requirements_path):
                try:
                    # Install requirements
                    self.emit_progress("execution", "Installing dependencies (this may take a moment)...")
                    pip_result = subprocess.run([
                        sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--user', '--quiet'
                    ], capture_output=True, text=True, timeout=300)
                    
                    if pip_result.returncode != 0:
                        self.emit_progress("execution", f"Warning: Some dependencies may not have installed properly")
                        self.emit_progress("execution", f"Pip stderr: {pip_result.stderr[:200]}...")
                        # Continue anyway - many projects can run with partial dependencies
                    else:
                        self.emit_progress("execution", "Dependencies installed successfully")
                        
                except subprocess.TimeoutExpired:
                    self.emit_progress("execution", "Warning: Dependency installation timed out, proceeding anyway")
                except Exception as e:
                    self.emit_progress("execution", f"Warning: Could not install dependencies: {str(e)[:100]}...")
            else:
                self.emit_progress("execution", "No requirements.txt found, proceeding without dependency installation")
            
            # Prepare execution command
            if run_method == 'web':
                # Web application - use run.py
                # Kill any existing processes on port 8080
                self.kill_processes_on_port(8080)
                
                cmd = [sys.executable, 'run.py']
                self.emit_progress("execution", f"Starting Flask web server with command: {' '.join(cmd)}")
                
                # Start the web server as a background process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=project_path
                )
                
                self.running_processes[project_id] = process
                
                # Monitor process startup with better error handling
                startup_checks = 5
                for i in range(startup_checks):
                    time.sleep(1)
                    
                    # Check if process terminated early
                    if process.poll() is not None:
                        stdout, stderr = process.communicate()
                        self.emit_progress("execution", f"Web server failed to start. Exit code: {process.returncode}")
                        if stdout:
                            self.emit_progress("execution", f"Stdout: {stdout[:500]}")
                        if stderr:
                            self.emit_progress("execution", f"Stderr: {stderr[:500]}")
                        return {
                            'success': False,
                            'method': run_method,
                            'error': f"Web server failed to start: {stderr or 'Process terminated unexpectedly'}",
                            'output': stdout or '',
                            'status': 'failed'
                        }
                    
                    self.emit_progress("execution", f"Checking web server startup... ({i+1}/{startup_checks})")
                
                if process.poll() is None:  # Process is still running
                    self.emit_progress("execution", "Web server started successfully!")
                    
                    # Test if the server is actually responding
                    try:
                        import requests
                        time.sleep(2)  # Give server time to be ready
                        response = requests.get('http://localhost:8080', timeout=5)
                        self.emit_progress("execution", f"Server responding with status: {response.status_code}")
                    except Exception as e:
                        self.emit_progress("execution", f"Server may still be starting up: {str(e)}")
                    
                    # Automatically open browser after a short delay
                    def open_browser():
                        time.sleep(2)  # Give server time to fully start
                        try:
                            webbrowser.open('http://localhost:8080')
                            self.emit_progress("execution", "Browser opened automatically for web application on port 8080")
                        except Exception as e:
                            self.emit_progress("execution", f"Could not open browser automatically: {str(e)}")
                    
                    import threading
                    browser_thread = threading.Thread(target=open_browser)
                    browser_thread.daemon = True
                    browser_thread.start()
                    
                    result = {
                        'success': True,
                        'method': run_method,
                        'message': 'Web application started successfully',
                        'url': 'http://localhost:8080',
                        'status': 'running',
                        'pid': process.pid,
                        'port': 8080,
                        'output': f'Web server is running on http://localhost:8080\n\nBrowser opened automatically!',
                        'auto_opened': True
                    }
                else:
                    # Final check - process terminated after startup monitoring
                    stdout, stderr = process.communicate()
                    self.emit_progress("execution", f"Web server stopped unexpectedly after startup")
                    result = {
                        'success': False,
                        'method': run_method,
                        'error': f"Web server stopped unexpectedly: {stderr or 'Unknown error'}",
                        'output': stdout or '',
                        'status': 'failed'
                    }
            elif run_method == 'streamlit':
                # Streamlit application
                # Find the main streamlit file
                streamlit_file = 'main.py'
                for file in os.listdir(project_path):
                    if file.endswith('.py') and file != 'main.py':
                        with open(os.path.join(project_path, file), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            if 'streamlit' in content or 'st.' in content:
                                streamlit_file = file
                                break
                
                # Check if streamlit file exists
                if not os.path.exists(os.path.join(project_path, streamlit_file)):
                    self.emit_progress("execution", f"Error: {streamlit_file} not found in project directory")
                    return {
                        'success': False,
                        'method': run_method,
                        'error': f"Main file {streamlit_file} not found",
                        'status': 'failed'
                    }
                
                # Check if streamlit is installed
                try:
                    import streamlit
                    self.emit_progress("execution", f"Found Streamlit version {streamlit.__version__}")
                except ImportError:
                    self.emit_progress("execution", "Installing Streamlit...")
                    try:
                        subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit', '--user'], 
                                     check=True, capture_output=True, text=True)
                        self.emit_progress("execution", "Streamlit installed successfully")
                    except subprocess.CalledProcessError as e:
                        return {
                            'success': False,
                            'method': run_method,
                            'error': f"Failed to install Streamlit: {e.stderr}",
                            'status': 'failed'
                        }
                
                # Always use port 8501 for consistency and kill any existing processes
                port = 8501
                self.emit_progress("execution", f"Checking for processes on port {port}...")
                self.kill_processes_on_port(port)
                
                cmd = [
                    sys.executable, '-m', 'streamlit', 'run', streamlit_file,
                    '--server.headless', 'true',
                    '--server.port', str(port),
                    '--server.address', '127.0.0.1',
                    '--server.enableCORS', 'false',
                    '--server.enableXsrfProtection', 'false'
                ]
                
                self.emit_progress("execution", f"Starting Streamlit server with command: {' '.join(cmd)}")
                
                # Start streamlit as a background process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=project_path
                )
                
                self.running_processes[project_id] = process
                
                # Give process a moment to start
                time.sleep(1)
                
                # Check if process started successfully
                if process.poll() is not None:
                    # Process terminated early, get error
                    stdout, stderr = process.communicate()
                    self.emit_progress("execution", f"Streamlit failed to start. Exit code: {process.returncode}")
                    self.emit_progress("execution", f"Stderr: {stderr}")
                    return {
                        'success': False,
                        'method': run_method,
                        'error': f"Streamlit failed to start: {stderr}",
                        'output': stdout,
                        'status': 'failed'
                    }
                
                self.emit_progress("execution", "Streamlit server started successfully!")
                
                # Automatically open browser
                def open_browser():
                    time.sleep(2)  # Brief delay for server to be ready
                    try:
                        webbrowser.open(f'http://localhost:{port}')
                        self.emit_progress("execution", f"Browser opened automatically for Streamlit app on port {port}")
                    except Exception as e:
                        self.emit_progress("execution", f"Could not open browser automatically: {str(e)}")
                
                import threading
                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()
                
                result = {
                    'success': True,
                    'method': run_method,
                    'message': 'Streamlit application started successfully',
                    'url': f'http://localhost:{port}',
                    'status': 'running',
                    'pid': process.pid,
                    'port': port,
                    'output': f'Streamlit server is running on http://localhost:{port}\n\nBrowser opened automatically!',
                    'auto_opened': True
                }
            
            else:
                # For regular Python scripts, run and capture output
                cmd = [sys.executable, 'main.py']
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60 second timeout for regular scripts
                        cwd=project_path
                    )
                    
                    if result.returncode == 0:
                        execution_result = {
                            'success': True,
                            'method': run_method,
                            'output': result.stdout,
                            'error': result.stderr if result.stderr else None,
                            'status': 'completed',
                            'exit_code': result.returncode
                        }
                    else:
                        execution_result = {
                            'success': False,
                            'method': run_method,
                            'output': result.stdout,
                            'error': result.stderr,
                            'status': 'failed',
                            'exit_code': result.returncode
                        }
                        
                    result = execution_result
                    
                except subprocess.TimeoutExpired:
                    result = {
                        'success': False,
                        'method': run_method,
                        'error': 'Execution timed out after 60 seconds',
                        'status': 'timeout'
                    }
                except Exception as e:
                    result = {
                        'success': False,
                        'method': analysis.get('run_method', 'python'),
                        'error': str(e),
                        'status': 'error'
                    }
            
            return result
    
    def _execute_with_dynamic_method(self, project_id, project_path, run_method, analysis):
        """Execute project using the dynamically determined method"""
        try:
            recommended_command = analysis.get('recommended_command', 'python run.py')
            port = analysis.get('port', 8080)
            
            self.emit_progress("execution", f"Executing: {recommended_command}")
            
            # Always try to run run.py first (our dynamic runner)
            run_py_path = os.path.join(project_path, 'run.py')
            if os.path.exists(run_py_path):
                cmd = [sys.executable, 'run.py']
                self.emit_progress("execution", f"Starting with dynamic runner: {' '.join(cmd)}")
                
                # Start the process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=project_path
                )
                
                self.running_processes[project_id] = process
                
                # Monitor process startup
                startup_checks = 5
                for i in range(startup_checks):
                    time.sleep(1)
                    
                    # Check if process terminated early
                    if process.poll() is not None:
                        stdout, stderr = process.communicate()
                        self.emit_progress("execution", f"Process failed to start. Exit code: {process.returncode}")
                        if stdout:
                            self.emit_progress("execution", f"Stdout: {stdout[:500]}")
                        if stderr:
                            self.emit_progress("execution", f"Stderr: {stderr[:500]}")
                        return {
                            'success': False,
                            'method': run_method,
                            'error': f"Process failed to start: {stderr or 'Process terminated unexpectedly'}",
                            'output': stdout or '',
                            'status': 'failed'
                        }
                    
                    self.emit_progress("execution", f"Checking startup... ({i+1}/{startup_checks})")
                
                if process.poll() is None:  # Process is still running
                    self.emit_progress("execution", f"Application started successfully!")
                    
                    # For web applications, test connectivity and open browser
                    if run_method in ['web', 'streamlit', 'fastapi', 'flask']:
                        try:
                            time.sleep(2)  # Give server time to be ready
                            self.emit_progress("execution", f"Server should be available on port {port}")
                            
                            # Open browser automatically
                            def open_browser():
                                time.sleep(1)
                                url = f'http://localhost:{port}'
                                if run_method == 'fastapi':
                                    url += '/docs'  # Open API docs for FastAPI
                                webbrowser.open(url)
                                self.emit_progress("execution", f"Browser opened automatically: {url}")
                            
                            import threading
                            browser_thread = threading.Thread(target=open_browser)
                            browser_thread.daemon = True
                            browser_thread.start()
                            
                        except Exception as e:
                            self.emit_progress("execution", f"Could not open browser automatically: {str(e)}")
                    
                    return {
                        'success': True,
                        'method': run_method,
                        'message': f'{analysis.get("project_type", "Application").title()} started successfully',
                        'url': f'http://localhost:{port}' if port else None,
                        'status': 'running',
                        'pid': process.pid,
                        'port': port,
                        'output': f'Application is running on port {port}' if port else 'Application started successfully',
                        'auto_opened': True,
                        'project_type': analysis.get('project_type', 'unknown')
                    }
                else:
                    # Final check - process terminated after startup monitoring
                    stdout, stderr = process.communicate()
                    self.emit_progress("execution", f"Application stopped unexpectedly after startup")
                    return {
                        'success': False,
                        'method': run_method,
                        'error': f"Application stopped unexpectedly: {stderr or 'Unknown error'}",
                        'output': stdout or '',
                        'status': 'failed'
                    }
            else:
                # No run.py found, try direct execution based on analysis
                return self._execute_direct_command(project_id, project_path, recommended_command, analysis)
                
        except Exception as e:
            self.emit_progress("execution", f"Dynamic execution failed: {str(e)}")
            return {
                'success': False,
                'method': run_method,
                'error': str(e),
                'output': '',
                'status': 'failed'
            }
    
    def _execute_direct_command(self, project_id, project_path, command, analysis):
        """Execute project using direct command when no run.py is available"""
        try:
            # Parse the command
            if isinstance(command, str):
                cmd_parts = command.split()
            else:
                cmd_parts = command
            
            self.emit_progress("execution", f"Direct execution: {' '.join(cmd_parts)}")
            
            # Start the process
            process = subprocess.Popen(
                cmd_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=project_path
            )
            
            self.running_processes[project_id] = process
            
            # For quick-running scripts, get output
            if analysis.get('project_type') in ['python', 'desktop']:
                try:
                    stdout, stderr = process.communicate(timeout=30)
                    return {
                        'success': process.returncode == 0,
                        'method': analysis.get('run_method', 'python'),
                        'error': stderr if process.returncode != 0 else None,
                        'output': stdout,
                        'status': 'completed',
                        'exit_code': process.returncode
                    }
                except subprocess.TimeoutExpired:
                    # Long-running process
                    return {
                        'success': True,
                        'method': analysis.get('run_method', 'python'),
                        'message': 'Long-running application started',
                        'status': 'running',
                        'pid': process.pid
                    }
            else:
                # Web applications - monitor like before
                time.sleep(3)
                if process.poll() is None:
                    return {
                        'success': True,
                        'method': analysis.get('run_method', 'web'),
                        'message': 'Web application started',
                        'status': 'running',
                        'pid': process.pid,
                        'port': analysis.get('port', 8080)
                    }
                else:
                    stdout, stderr = process.communicate()
                    return {
                        'success': False,
                        'method': analysis.get('run_method', 'web'),
                        'error': stderr,
                        'output': stdout,
                        'status': 'failed'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'method': analysis.get('run_method', 'python'),
                'error': str(e),
                'output': '',
                'status': 'failed'
            }
    
    def stop_project(self, project_id):
        """Stop a running project"""
        try:
            if hasattr(self, 'running_processes') and project_id in self.running_processes:
                process = self.running_processes[project_id]
                if process and process.poll() is None:
                    process.terminate()
                    # Wait a bit for graceful termination
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()  # Force kill if still running
                    del self.running_processes[project_id]
                    return True
            return False
        except Exception as e:
            print(f"Error stopping project {project_id}: {e}")
            return False

    def stop_project_execution(self, project_id):
        """Stop a running project execution"""
        try:
            if not hasattr(self, 'running_processes'):
                return {'success': False, 'message': 'No running processes found'}
            
            if project_id not in self.running_processes:
                return {'success': False, 'message': 'Project is not currently running'}
            
            process = self.running_processes[project_id]
            
            if process.poll() is None:  # Process is still running
                # Immediate termination - don't wait
                process.terminate()
                
                # Force kill immediately for faster response
                try:
                    process.kill()
                except:
                    pass  # Process might already be dead
                
                # Remove from running processes immediately
                del self.running_processes[project_id]
                self.emit_progress("execution", "Project execution stopped")
                return {'success': True, 'message': 'Project execution stopped successfully'}
            else:
                del self.running_processes[project_id]
                return {'success': False, 'message': 'Project was not running'}
                
        except Exception as e:
            # Even if there's an error, remove from running processes to unblock UI
            if hasattr(self, 'running_processes') and project_id in self.running_processes:
                del self.running_processes[project_id]
            return {'success': False, 'error': f"Failed to stop project: {str(e)}"}

    def get_running_projects(self):
        """Get list of currently running projects"""
        if not hasattr(self, 'running_processes'):
            return []
        
        running = []
        for project_id, process in list(self.running_processes.items()):
            if process.poll() is None:  # Still running
                running.append({
                    'project_id': project_id,
                    'pid': process.pid,
                    'status': 'running'
                })
            else:
                # Clean up finished process
                del self.running_processes[project_id]
        
        return running

    def find_available_port(self, start_port=8501):
        """Find an available port starting from start_port"""
        import socket
        port = start_port
        while port <= start_port + 10:  # Try up to 10 ports
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    port += 1
        return start_port  # Fallback to original port

    def kill_existing_streamlit_processes(self):
        """Kill any existing Streamlit processes to free up ports"""
        try:
            import psutil
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('streamlit' in str(cmd).lower() for cmd in cmdline):
                            proc.kill()
                            killed_count += 1
                            self.emit_progress("execution", f"Cleaned up existing Streamlit process: {proc.info['pid']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed_count > 0:
                self.emit_progress("execution", f"Cleaned up {killed_count} existing Streamlit process(es)")
            
        except ImportError:
            # psutil not available, try basic approach
            import subprocess
            import sys
            try:
                if sys.platform == "win32":
                    result = subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                                          capture_output=True, check=False)
                    if result.returncode == 0:
                        self.emit_progress("execution", "Cleaned up existing Python processes")
                else:
                    result = subprocess.run(['pkill', '-f', 'streamlit'], 
                                          capture_output=True, check=False)
                    if result.returncode == 0:
                        self.emit_progress("execution", "Cleaned up existing Streamlit processes")
            except Exception as e:
                self.emit_progress("execution", f"Could not clean up processes: {str(e)}")

    # Web Application Helper Methods
    
    def _create_fallback_web_plan(self, user_prompt):
        """Create a basic fallback web plan if AI planning fails"""
        return {
            "project_name": "web_application",
            "description": f"Web application based on: {user_prompt}",
            "project_type": "web_application",
            "frontend_framework": "vanilla_js",
            "backend_framework": "flask",
            "database": "none",
            "features": ["responsive design", "interactive interface"],
            "pages": [
                {
                    "name": "Home",
                    "route": "/",
                    "purpose": "Main landing page",
                    "components": ["header", "main content", "footer"]
                }
            ],
            "api_endpoints": [
                {
                    "method": "GET",
                    "route": "/api/data",
                    "purpose": "Get application data",
                    "data": "JSON response"
                }
            ],
            "files": [
                {
                    "path": "index.html",
                    "type": "html",
                    "purpose": "Main HTML page",
                    "dependencies": ["style.css", "script.js"]
                },
                {
                    "path": "static/css/style.css",
                    "type": "css",
                    "purpose": "Main stylesheet",
                    "dependencies": []
                },
                {
                    "path": "static/js/script.js",
                    "type": "js",
                    "purpose": "Main JavaScript file",
                    "dependencies": []
                },
                {
                    "path": "app.py",
                    "type": "py",
                    "purpose": "Backend API server",
                    "dependencies": ["flask", "flask-cors"]
                }
            ],
            "styling": "css",
            "responsive": True,
            "main_file": "app.py"
        }
    
    def _create_fallback_frontend(self, project_plan):
        """Create basic frontend files if generation fails"""
        project_name = project_plan.get('project_name', 'Web Application')
        
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <header>
        <h1>{project_name}</h1>
    </header>
    <main>
        <div class="container">
            <h2>Welcome to {project_name}</h2>
            <p>This is a web application generated by the Python Code Generator.</p>
            <button id="actionBtn">Click Me</button>
            <div id="result"></div>
        </div>
    </main>
    <footer>
        <p>&copy; 2025 {project_name}</p>
    </footer>
    <script src="static/js/script.js"></script>
</body>
</html>'''

        css_content = '''/* Modern CSS Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 1rem 0;
    text-align: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

header h1 {
    color: white;
    font-size: 2.5rem;
    font-weight: 300;
}

main {
    padding: 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: calc(100vh - 160px);
}

.container {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    text-align: center;
    max-width: 600px;
    width: 100%;
}

.container h2 {
    color: #333;
    margin-bottom: 1rem;
}

.container p {
    color: #666;
    margin-bottom: 2rem;
}

#actionBtn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 25px;
    cursor: pointer;
    font-size: 1rem;
    transition: transform 0.3s ease;
}

#actionBtn:hover {
    transform: translateY(-2px);
}

#result {
    margin-top: 2rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 5px;
    min-height: 50px;
}

footer {
    background: rgba(0, 0, 0, 0.2);
    color: white;
    text-align: center;
    padding: 1rem;
    position: fixed;
    bottom: 0;
    width: 100%;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 2rem;
    }
    
    main {
        padding: 1rem;
    }
    
    .container {
        padding: 1.5rem;
    }
}'''

        js_content = '''// Modern JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const actionBtn = document.getElementById('actionBtn');
    const result = document.getElementById('result');
    
    actionBtn.addEventListener('click', async function() {
        try {
            // Show loading state
            result.innerHTML = '<p>Loading...</p>';
            
            // Simulate API call
            const response = await fetch('/api/data');
            
            if (response.ok) {
                const data = await response.json();
                result.innerHTML = `<h3>API Response:</h3><pre>${JSON.stringify(data, null, 2)}</pre>`;
            } else {
                result.innerHTML = '<p style="color: red;">Error: Could not fetch data from API</p>';
            }
        } catch (error) {
            result.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    });
});'''

        return {
            "files": [
                {
                    "path": "index.html",
                    "content": html_content
                },
                {
                    "path": "static/css/style.css",
                    "content": css_content
                },
                {
                    "path": "static/js/script.js",
                    "content": js_content
                }
            ]
        }
    
    def _create_fallback_backend(self, project_plan):
        """Create basic backend files if generation fails"""
        project_name = project_plan.get('project_name', 'Web Application')
        
        app_content = f'''from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# API endpoints
@app.route('/api/data')
def get_data():
    return jsonify({{
        "message": "Hello from {project_name} API!",
        "status": "success",
        "data": {{
            "timestamp": "2025-01-01T00:00:00Z",
            "version": "1.0.0"
        }}
    }})

@app.route('/api/health')
def health_check():
    return jsonify({{
        "status": "healthy",
        "service": "{project_name}"
    }})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)'''

        requirements_content = '''Flask==2.3.3
Flask-CORS==4.0.0'''

        return {
            "files": [
                {
                    "path": "app.py",
                    "content": app_content
                },
                {
                    "path": "requirements.txt",
                    "content": requirements_content
                }
            ]
        }
    
    def _create_web_directories(self, project_dir):
        """Create necessary directories for web projects"""
        directories = [
            os.path.join(project_dir, 'static'),
            os.path.join(project_dir, 'static', 'css'),
            os.path.join(project_dir, 'static', 'js'),
            os.path.join(project_dir, 'static', 'images'),
            os.path.join(project_dir, 'templates')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _create_web_readme(self, project_plan):
        """Create README content for web applications"""
        project_name = project_plan.get('project_name', 'Web Application')
        description = project_plan.get('description', 'A web application')
        frontend_framework = project_plan.get('frontend_framework', 'vanilla_js')
        backend_framework = project_plan.get('backend_framework', 'flask')
        
        return f'''# {project_name}

{description}

## Project Structure

This is a full-stack web application built with:
- **Frontend**: {frontend_framework.title()}
- **Backend**: {backend_framework.title()}

## Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone or extract the project files
2. Navigate to the project directory
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
{project_name}/
├── index.html          # Main HTML page
├── app.py             # Backend Flask server
├── requirements.txt   # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css  # Stylesheets
│   ├── js/
│   │   └── script.js  # JavaScript files
│   └── images/        # Image assets
└── README.md          # This file
```

## Features

{chr(10).join([f"- {feature}" for feature in project_plan.get('features', ['Responsive design', 'Interactive interface'])])}

## API Endpoints

{chr(10).join([f"- {endpoint.get('method', 'GET')} {endpoint.get('route', '/')}: {endpoint.get('purpose', 'API endpoint')}" for endpoint in project_plan.get('api_endpoints', [])])}

## Development

To modify the application:
1. Edit HTML in `index.html`
2. Update styles in `static/css/style.css`
3. Modify JavaScript in `static/js/script.js`
4. Add API endpoints in `app.py`

## Deployment

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server like Gunicorn
3. Configure environment variables for sensitive data

## Generated by Python Code Generator

This project was automatically generated by the AI-powered Python Code Generator system.
'''
    
    def _create_web_config_files(self, project_dir, project_plan):
        """Create configuration files for web applications"""
        # Create .env.example file
        env_example_path = os.path.join(project_dir, '.env.example')
        env_content = '''# Environment Variables
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
API_BASE_URL=http://localhost:5000/api
'''
        
        try:
            with open(env_example_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
        except Exception as e:
            print(f"Error creating .env.example: {e}")
        
        # Create run.py for easy development
        run_py_path = os.path.join(project_dir, 'run.py')
        run_content = '''#!/usr/bin/env python3
"""
Development server runner for the web application.
Run this file to start the development server.
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("Starting web application development server...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
'''
        
        try:
            with open(run_py_path, 'w', encoding='utf-8') as f:
                f.write(run_content)
        except Exception as e:
            print(f"Error creating run.py: {e}")

    # Web Application Helper Methods
    
    def _create_fallback_web_plan(self, user_prompt):
        """Create a basic fallback plan for web applications"""
        return {
            "project_name": "web_application",
            "description": f"Web application based on: {user_prompt}",
            "project_type": "web_application",
            "frontend_framework": "vanilla_js",
            "backend_framework": "flask",
            "database": "sqlite",
            "features": ["home page", "responsive design", "API endpoints"],
            "pages": [
                {
                    "name": "Home",
                    "route": "/",
                    "purpose": "Main landing page",
                    "components": ["header", "hero section", "content area", "footer"]
                }
            ],
            "api_endpoints": [
                {
                    "method": "GET",
                    "route": "/api/health",
                    "purpose": "Health check endpoint"
                }
            ],
            "files": [
                {
                    "path": "index.html",
                    "type": "html",
                    "purpose": "Main HTML page"
                },
                {
                    "path": "static/css/style.css",
                    "type": "css", 
                    "purpose": "Main stylesheet"
                },
                {
                    "path": "static/js/script.js",
                    "type": "js",
                    "purpose": "Main JavaScript file"
                },
                {
                    "path": "app.py",
                    "type": "py",
                    "purpose": "Flask backend application"
                }
            ],
            "styling": "css",
            "responsive": True,
            "main_file": "app.py"
        }
    
    def _create_fallback_frontend(self, project_plan):
        """Create fallback frontend files if generation fails"""
        return {
            "files": [
                {
                    "path": "index.html",
                    "content": self._get_fallback_html(project_plan)
                },
                {
                    "path": "static/css/style.css",
                    "content": self._get_fallback_css()
                },
                {
                    "path": "static/js/script.js", 
                    "content": self._get_fallback_js()
                }
            ]
        }
    
    def _create_fallback_backend(self, project_plan):
        """Create fallback backend files if generation fails"""
        return {
            "files": [
                {
                    "path": "database.py",
                    "content": self._get_fallback_database()
                },
                {
                    "path": "models.py",
                    "content": self._get_fallback_models()
                },
                {
                    "path": "routes.py",
                    "content": self._get_fallback_routes()
                },
                {
                    "path": "app.py",
                    "content": self._get_fallback_app()
                },
                {
                    "path": "run.py",
                    "content": self._get_fallback_run()
                },
                {
                    "path": "requirements.txt",
                    "content": "Flask==2.3.2\\nFlask-SQLAlchemy==3.1.1\\nFlask-CORS==4.0.0\\nWerkzeug==2.3.7"
                }
            ]
        }
    
    def _create_web_directories(self, project_dir):
        """Create necessary directories for web application"""
        directories = [
            os.path.join(project_dir, 'static'),
            os.path.join(project_dir, 'static', 'css'),
            os.path.join(project_dir, 'static', 'js'),
            os.path.join(project_dir, 'static', 'images'),
            os.path.join(project_dir, 'templates')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _create_web_config_files(self, project_dir, project_plan):
        """Create web-specific configuration files"""
        # Create .env.example
        env_content = """# Environment Variables for Web Application
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
API_BASE_URL=http://localhost:8080/api
"""
        env_path = os.path.join(project_dir, '.env.example')
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
        except Exception as e:
            print(f"Error creating .env.example: {e}")
    
    def _create_web_readme(self, project_plan):
        """Create README content for web applications"""
        project_name = project_plan.get('project_name', 'Web Application')
        description = project_plan.get('description', 'A web application')
        
        return f"""# {project_name}

{description}

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   ```bash
   python run.py
   ```

3. **Open Your Browser:**
   ```
   http://localhost:8080
   ```

## Features

- Responsive web design
- Modern HTML, CSS, and JavaScript
- Flask backend with REST API
- SQLite database integration
- Cross-browser compatibility

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/vehicles` - List vehicles
- `POST /api/bookings` - Create booking

## Development

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask with SQLAlchemy
- **Database**: SQLite
- **Port**: 8080

## Project Structure

```
{project_name.lower().replace(' ', '_')}/
├── index.html              # Main HTML page
├── app.py                  # Flask backend
├── run.py                  # Development server
├── database.py             # Database configuration
├── models.py               # Database models
├── routes.py               # API routes
├── requirements.txt        # Dependencies
├── .env.example           # Environment variables
├── static/
│   ├── css/style.css      # Stylesheets
│   ├── js/script.js       # JavaScript
│   └── images/            # Images
└── templates/             # HTML templates
```

## Troubleshooting

If you encounter any issues:

1. **Port Already in Use**: Try changing the port in `run.py`
2. **API Connection Failed**: Check that the backend is running
3. **Database Issues**: Delete the database file and restart

## Next Steps

1. Customize the styling in `static/css/style.css`
2. Add more features in `static/js/script.js`
3. Extend the API in `routes.py`
4. Deploy to a web server for production use
"""

    def _get_fallback_html(self, project_plan):
        """Get fallback HTML content"""
        project_name = project_plan.get('project_name', 'Web Application')
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{project_name}">
    <title>{project_name}</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <h1>{project_name}</h1>
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <h2>Welcome to {project_name}</h2>
            <p>A modern web application built with HTML, CSS, JavaScript, and Flask.</p>
            <button onclick="testAPI()">Test API Connection</button>
        </section>

        <section id="content">
            <h3>Features</h3>
            <div class="feature-grid">
                <div class="feature-card">
                    <h4>Responsive Design</h4>
                    <p>Works on all devices and screen sizes.</p>
                </div>
                <div class="feature-card">
                    <h4>Modern Tech Stack</h4>
                    <p>Built with the latest web technologies.</p>
                </div>
                <div class="feature-card">
                    <h4>RESTful API</h4>
                    <p>Clean and efficient backend API.</p>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2024 {project_name}. All rights reserved.</p>
    </footer>

    <script src="static/js/script.js"></script>
</body>
</html>"""

    def _get_fallback_css(self):
        """Get fallback CSS content"""
        return """/* Modern CSS Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

/* Header and Navigation */
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

nav {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
}

nav h1 {
    font-size: 1.8rem;
    font-weight: 600;
}

nav ul {
    display: flex;
    list-style: none;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.3s ease;
}

nav a:hover {
    opacity: 0.8;
}

/* Main Content */
main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.hero {
    text-align: center;
    padding: 4rem 0;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    margin-bottom: 3rem;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
}

.hero p {
    font-size: 1.2rem;
    color: #7f8c8d;
    margin-bottom: 2rem;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 25px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* Feature Grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-card h4 {
    color: #2c3e50;
    margin-bottom: 1rem;
}

.feature-card p {
    color: #7f8c8d;
}

/* Footer */
footer {
    background: #2c3e50;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    nav {
        flex-direction: column;
        gap: 1rem;
    }
    
    nav ul {
        gap: 1rem;
    }
    
    .hero h2 {
        font-size: 2rem;
    }
    
    main {
        padding: 1rem;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}

/* Loading and Success States */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

.success {
    background: #27ae60 !important;
}

.error {
    background: #e74c3c !important;
}"""

    def _get_fallback_js(self):
        """Get fallback JavaScript content"""
        return """// Main JavaScript for Web Application

// Configuration
const API_BASE_URL = 'http://localhost:8080/api';

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Web Application Loaded Successfully');
    initializeApp();
});

// Initialize application features
function initializeApp() {
    setupNavigation();
    setupAPITesting();
    loadContent();
}

// Setup smooth navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Setup API testing functionality
function setupAPITesting() {
    // API test button already exists in HTML
    console.log('API testing ready');
}

// Load dynamic content
async function loadContent() {
    try {
        // Try to load any dynamic content from API
        await testAPIConnection();
    } catch (error) {
        console.log('Using static content (API not available)');
    }
}

// Test API connection
async function testAPI() {
    const button = event.target;
    const originalText = button.textContent;
    
    // Show loading state
    button.textContent = 'Testing...';
    button.classList.add('loading');
    
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        
        if (response.ok) {
            const data = await response.json();
            button.textContent = 'API Connected!';
            button.classList.remove('loading');
            button.classList.add('success');
            
            // Show success message
            showMessage(`API Status: ${data.message || 'Connected'}`, 'success');
            
            // Reset button after 3 seconds
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('success');
            }, 3000);
            
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
        
    } catch (error) {
        button.textContent = 'Connection Failed';
        button.classList.remove('loading');
        button.classList.add('error');
        
        // Show error message
        showMessage(`API Connection Failed: ${error.message}`, 'error');
        
        // Reset button after 3 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('error');
        }, 3000);
    }
}

// Show user messages
function showMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        max-width: 300px;
        word-wrap: break-word;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(messageEl);
    
    // Remove message after 5 seconds
    setTimeout(() => {
        messageEl.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(messageEl);
        }, 300);
    }, 5000);
}

// Add CSS animations for messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Utility function for API calls
async function apiCall(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Test API connection (can be called programmatically)
async function testAPIConnection() {
    try {
        const data = await apiCall('/health');
        console.log('API connected:', data);
        return true;
    } catch (error) {
        console.log('API not available:', error.message);
        return false;
    }
}"""

    def _get_fallback_database(self):
        """Get fallback database.py content"""
        return """\"\"\"
Database configuration and initialization module.
This module creates the SQLAlchemy instance to avoid circular imports.
\"\"\"

from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

def init_db(app):
    \"\"\"Initialize the database with the Flask app.\"\"\"
    db.init_app(app)
    with app.app_context():
        # Import models here to ensure they are registered
        from models import User, Vehicle, Booking
        db.create_all()
        
        # Add sample data if tables are empty
        if Vehicle.query.count() == 0:
            add_sample_data()

def add_sample_data():
    \"\"\"Add sample data for testing\"\"\"
    from models import Vehicle, User
    
    # Sample vehicles
    vehicles = [
        Vehicle(
            make='Toyota',
            model='Camry',
            year=2023,
            rental_price=45.00,
            availability=True,
            image_url='https://via.placeholder.com/300x200',
            description='A comfortable sedan for everyday use.'
        ),
        Vehicle(
            make='Honda',
            model='CR-V',
            year=2023,
            rental_price=65.00,
            availability=True,
            image_url='https://via.placeholder.com/300x200',
            description='A spacious SUV for family adventures.'
        ),
        Vehicle(
            make='Ford',
            model='F-150',
            year=2022,
            rental_price=85.00,
            availability=False,
            image_url='https://via.placeholder.com/300x200',
            description='A rugged truck for heavy-duty tasks.'
        )
    ]
    
    for vehicle in vehicles:
        db.session.add(vehicle)
    
    # Sample user
    sample_user = User(
        username='demo_user',
        email='demo@example.com'
    )
    sample_user.set_password('demo123')
    db.session.add(sample_user)
    
    db.session.commit()
    print('Sample data added successfully!')"""

    def _get_fallback_models(self):
        """Get fallback models.py content"""
        return """\"\"\"
Database models for the web application.
\"\"\"

from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    \"\"\"User model for authentication and bookings\"\"\"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def set_password(self, password):
        \"\"\"Set password hash\"\"\"
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        \"\"\"Check password against hash\"\"\"
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        \"\"\"Convert to dictionary\"\"\"
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Vehicle(db.Model):
    \"\"\"Vehicle model for rental inventory\"\"\"
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rental_price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='vehicle', lazy=True)

    def to_dict(self):
        \"\"\"Convert to dictionary\"\"\"
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'rental_price': self.rental_price,
            'availability': self.availability,
            'image_url': self.image_url,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Booking(db.Model):
    \"\"\"Booking model for rental transactions\"\"\"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        \"\"\"Convert to dictionary\"\"\"
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vehicle_id': self.vehicle_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_cost': self.total_cost,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }"""

    def _get_fallback_routes(self):
        """Get fallback routes.py content"""
        return """\"\"\"
API routes for the web application.
\"\"\"

from flask import Blueprint, request, jsonify
from database import db
from models import User, Vehicle, Booking
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the blueprint
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/health', methods=['GET'])
def health_check():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({
        'status': 'healthy',
        'message': 'Backend API is running successfully',
        'timestamp': datetime.utcnow().isoformat()
    })

@api.route('/vehicles', methods=['GET'])
def get_vehicles():
    \"\"\"Get all vehicles\"\"\"
    try:
        vehicles = Vehicle.query.all()
        return jsonify([vehicle.to_dict() for vehicle in vehicles])
    except Exception as e:
        logger.error(f'Error fetching vehicles: {e}')
        return jsonify({'error': 'Failed to fetch vehicles'}), 500

@api.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    \"\"\"Get specific vehicle\"\"\"
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        return jsonify(vehicle.to_dict())
    except Exception as e:
        logger.error(f'Error fetching vehicle {vehicle_id}: {e}')
        return jsonify({'error': 'Vehicle not found'}), 404

@api.route('/vehicles', methods=['POST'])
def create_vehicle():
    \"\"\"Create new vehicle\"\"\"
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['make', 'model', 'year', 'rental_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            year=int(data['year']),
            rental_price=float(data['rental_price']),
            availability=data.get('availability', True),
            image_url=data.get('image_url'),
            description=data.get('description')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify(vehicle.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating vehicle: {e}')
        return jsonify({'error': 'Failed to create vehicle'}), 500

@api.route('/bookings', methods=['GET'])
def get_bookings():
    \"\"\"Get all bookings\"\"\"
    try:
        bookings = Booking.query.all()
        return jsonify([booking.to_dict() for booking in bookings])
    except Exception as e:
        logger.error(f'Error fetching bookings: {e}')
        return jsonify({'error': 'Failed to fetch bookings'}), 500

@api.route('/bookings', methods=['POST'])
def create_booking():
    \"\"\"Create new booking\"\"\"
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['vehicle_id', 'start_date', 'end_date', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if vehicle exists and is available
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return jsonify({'error': 'Vehicle not found'}), 404
        
        if not vehicle.availability:
            return jsonify({'error': 'Vehicle not available'}), 400
        
        # Parse dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        # Calculate total cost
        days = (end_date - start_date).days
        if days <= 0:
            return jsonify({'error': 'Invalid date range'}), 400
        
        total_cost = days * vehicle.rental_price
        
        booking = Booking(
            user_id=data['user_id'],
            vehicle_id=data['vehicle_id'],
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify(booking.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating booking: {e}')
        return jsonify({'error': 'Failed to create booking'}), 500

@api.route('/users', methods=['POST'])
def create_user():
    \"\"\"Create new user\"\"\"
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify(user.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating user: {e}')
        return jsonify({'error': 'Failed to create user'}), 500

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500"""

    def _get_fallback_app(self):
        """Get fallback app.py content"""
        return """\"\"\"
Flask web application with frontend and API routes.
\"\"\"

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
from database import db, init_db

# Initialize Flask application with template and static folders
app = Flask(__name__, 
            template_folder='.',  # Look for templates in current directory
            static_folder='static')  # Static files in static folder

# Configure the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database
init_db(app)

# Enable CORS for all routes
CORS(app)

# Import and register routes after db is initialized
from routes import api
app.register_blueprint(api)

# Frontend routes
@app.route('/')
def index():
    \"\"\"Serve the main HTML page\"\"\"
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    \"\"\"Handle favicon requests\"\"\"
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Basic API route for testing
@app.route('/test')
def test_backend():
    \"\"\"Test endpoint to verify backend is running\"\"\"
    return {
        'message': 'Backend is running successfully!',
        'status': 'ok',
        'framework': 'Flask'
    }

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    \"\"\"Handle 404 errors\"\"\"
    return {'error': 'Page not found'}, 404

@app.errorhandler(500)
def internal_server_error(e):
    \"\"\"Handle 500 errors\"\"\"
    return {'error': 'Internal server error'}, 500

# Run the application if this script is executed
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True, use_reloader=False)"""

    def _get_fallback_run(self):
        """Get fallback run.py content"""
        return """#!/usr/bin/env python3
\"\"\"
Development server runner for the web application.
Run this file to start the development server.
\"\"\"

import os
import sys
from app import app
from wsgiref.simple_server import make_server, WSGIServer
import threading
import webbrowser
import time

class QuietWSGIServer(WSGIServer):
    \"\"\"A quieter WSGI server that doesn't log every request\"\"\"
    def log_message(self, format, *args):
        pass  # Suppress request logs

def main():
    \"\"\"Main function to run the development server\"\"\"
    port = 8080
    host = '0.0.0.0'
    
    print("Starting web application development server...")
    print(f"Open your browser and go to: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Use Python's built-in WSGI server instead of Flask's development server
        with make_server(host, port, app, server_class=QuietWSGIServer) as httpd:
            print(f"Server started successfully on http://localhost:{port}")
            
            # Open browser in a separate thread
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\\nServer stopped by user.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\\nError: Port {port} is already in use.")
            print("Try stopping other applications using this port.")
        else:
            print(f"\\nError starting server: {e}")
    except Exception as e:
        print(f"\\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()"""

