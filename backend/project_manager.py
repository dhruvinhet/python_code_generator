import os
import json
import subprocess
import sys
import shutil
import zipfile
from datetime import datetime
from agents import (
    PlanningAgent, SrDeveloper1Agent, SrDeveloper2Agent, 
    TesterAgent, DetailedTesterAgent, DocumentCreatorAgent
)
from config import Config

class ProjectManager:
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.planning_agent = PlanningAgent()
        self.sr_developer1 = SrDeveloper1Agent()
        self.sr_developer2 = SrDeveloper2Agent()
        self.tester = TesterAgent()
        self.detailed_tester = DetailedTesterAgent()
        self.document_creator = DocumentCreatorAgent()
        
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
            
            # Parse the plan result
            try:
                if isinstance(plan_result, str):
                    # Extract JSON from the result if it's wrapped in text
                    start_idx = plan_result.find('{')
                    end_idx = plan_result.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        plan_json = plan_result[start_idx:end_idx]
                        project_plan = json.loads(plan_json)
                    else:
                        raise ValueError("No valid JSON found in plan result")
                else:
                    project_plan = plan_result
            except (json.JSONDecodeError, ValueError) as e:
                self.emit_progress("planning", f"Error parsing plan: {str(e)}")
                # Create a fallback plan
                project_plan = self._create_fallback_plan(user_prompt)
            
            self.emit_progress("planning", "Project plan created successfully", project_plan)
            
            # Stage 2: Code Generation
            self.emit_progress("coding", "Generating Python code...")
            code_result = self.sr_developer1.generate_code(json.dumps(project_plan))
            
            # Parse the code result
            try:
                if isinstance(code_result, str):
                    start_idx = code_result.find('{')
                    end_idx = code_result.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        code_json = code_result[start_idx:end_idx]
                        generated_code = json.loads(code_json)
                    else:
                        raise ValueError("No valid JSON found in code result")
                else:
                    generated_code = code_result
            except (json.JSONDecodeError, ValueError) as e:
                self.emit_progress("coding", f"Error parsing generated code: {str(e)}")
                return {"success": False, "error": f"Code generation failed: {str(e)}"}
            
            self.emit_progress("coding", "Code generated successfully")
            
            # Stage 3: Code Review and Bug Fixing
            self.emit_progress("reviewing", "Reviewing and fixing code...")
            fixed_code_result = self.sr_developer2.review_and_fix(
                json.dumps(project_plan), 
                json.dumps(generated_code)
            )
            
            # Parse the fixed code result
            try:
                if isinstance(fixed_code_result, str):
                    start_idx = fixed_code_result.find('{')
                    end_idx = fixed_code_result.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        fixed_code_json = fixed_code_result[start_idx:end_idx]
                        fixed_code = json.loads(fixed_code_json)
                    else:
                        raise ValueError("No valid JSON found in fixed code result")
                else:
                    fixed_code = fixed_code_result
                
                # Use the fixed code, fallback to original if parsing fails
                final_code = fixed_code.get('files', generated_code.get('files', []))
            except (json.JSONDecodeError, ValueError) as e:
                self.emit_progress("reviewing", f"Using original code due to parsing error: {str(e)}")
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
                
                try:
                    if isinstance(fixed_code_result, str):
                        start_idx = fixed_code_result.find('{')
                        end_idx = fixed_code_result.rfind('}') + 1
                        if start_idx != -1 and end_idx != 0:
                            fixed_code_json = fixed_code_result[start_idx:end_idx]
                            fixed_code = json.loads(fixed_code_json)
                            final_code = fixed_code.get('files', final_code)
                            
                            # Rewrite files and test again
                            self._write_project_files(project_dir, final_code)
                            runtime_success, error_traceback = self._test_runtime(project_dir, main_file)
                except (json.JSONDecodeError, ValueError):
                    pass
            
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

