import os
import json
import subprocess
import sys
import shutil
import zipfile
import webbrowser
import time
import logging
from datetime import datetime
from agents import (
    PlanningAgent, SrDeveloper1Agent, SrDeveloper2Agent, 
    TesterAgent, DetailedTesterAgent, DocumentCreatorAgent
)
from config import Config
from json_parser import json_parser

class ProjectManager:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.planning_agent = PlanningAgent()
        self.sr_developer1 = SrDeveloper1Agent()
        self.sr_developer2 = SrDeveloper2Agent()
        self.tester = TesterAgent()
        self.detailed_tester = DetailedTesterAgent()
        self.document_creator = DocumentCreatorAgent()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure directories exist
        os.makedirs(Config.GENERATED_PROJECTS_DIR, exist_ok=True)
        os.makedirs(Config.TEMP_DIR, exist_ok=True)
    
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
        """Main method to generate a complete Python project"""
        try:
            project_dir = os.path.join(Config.GENERATED_PROJECTS_DIR, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            # Stage 1: Planning
            self.emit_progress("planning", "Analyzing requirements and creating project plan...")
            plan_result = self.planning_agent.create_plan(user_prompt)
            
            # Parse the plan result using robust parser
            self.logger.info(f"Parsing plan result, type: {type(plan_result)}, length: {len(str(plan_result)) if plan_result else 0}")
            project_plan = json_parser.parse_json_response(
                plan_result, 
                expected_keys=['project_name', 'description', 'files', 'main_file'],
                agent_type="planning",
                project_id=project_id
            )
            
            if not project_plan:
                self.logger.warning("Plan parsing failed, using fallback plan")
                self.emit_progress("planning", "Error parsing plan - using fallback plan")
                project_plan = json_parser.create_fallback_structure("project_plan", user_prompt)
            else:
                self.logger.info("Plan parsed successfully")
            
            self.emit_progress("planning", "Project plan created successfully", project_plan)
            
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
            self.emit_progress("error", f"Project generation failed: {str(e)}")
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

    def determine_run_method(self, project_path):
        """Determine how to run the project (python or streamlit)"""
        try:
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
        """Execute the project and capture output"""
        original_cwd = os.getcwd()
        try:
            self.emit_progress("execution", f"Starting project execution with {run_method}...")
            
            # Store process reference for potential termination
            if not hasattr(self, 'running_processes'):
                self.running_processes = {}
            
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
            
            # Prepare execution command
            if run_method == 'streamlit':
                # We'll set the actual command inside the execution block after finding the port
                pass
            else:
                cmd = [sys.executable, 'main.py']
                self.emit_progress("execution", "Running Python script...")
            
            # Execute the project
            if run_method == 'streamlit':
                # Clean up any existing Streamlit processes first
                self.emit_progress("execution", "Cleaning up any existing Streamlit processes...")
                self.kill_existing_streamlit_processes()
                
                # Wait a moment for processes to fully terminate
                import time
                time.sleep(1)
                
                # Find an available port
                port = self.find_available_port(8501)
                cmd = [sys.executable, '-m', 'streamlit', 'run', 'main.py', '--server.headless', 'true', '--server.port', str(port)]
                self.emit_progress("execution", f"Starting Streamlit application on port {port}...")
                
                # For Streamlit, we start it and return immediately with server info
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_path
                )
                
                self.running_processes[project_id] = process
                
                # Wait a bit to see if it starts successfully
                time.sleep(3)
                
                if process.poll() is None:  # Process is still running
                    self.emit_progress("execution", "Streamlit server started successfully!")
                    
                    # Automatically open browser after a short delay
                    def open_browser():
                        time.sleep(2)  # Give server time to fully start
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
                    # Process terminated, get error
                    stdout, stderr = process.communicate()
                    result = {
                        'success': False,
                        'method': run_method,
                        'error': f"Streamlit failed to start: {stderr}",
                        'output': stdout,
                        'status': 'failed'
                    }
            else:
                # For regular Python scripts, run and capture output
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
                        'error': 'Script execution timed out (60 seconds)',
                        'output': '',
                        'status': 'timeout'
                    }
                except Exception as e:
                    result = {
                        'success': False,
                        'method': run_method,
                        'error': f"Execution error: {str(e)}",
                        'output': '',
                        'status': 'error'
                    }
            
            # Restore original working directory
            os.chdir(original_cwd)
            
            self.emit_progress("execution", f"Project execution completed with status: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            # Restore original working directory
            os.chdir(original_cwd)
            error_result = {
                'success': False,
                'method': run_method,
                'error': f"Execution failed: {str(e)}",
                'output': '',
                'status': 'error'
            }
            self.emit_progress("execution", f"Project execution failed: {str(e)}")
            return error_result

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

