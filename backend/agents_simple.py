import google.generativeai as genai
from config import Config
import json
import re

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

class BaseAgent:
    """Base agent class using Google Generative AI directly"""
    
    def __init__(self, role, goal, backstory):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def execute_task(self, description):
        """Execute a task using the Gemini model"""
        try:
            prompt = f"""
Role: {self.role}
Goal: {self.goal}
Background: {self.backstory}

Task: {description}

Please provide a comprehensive response following the task requirements.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error executing task: {str(e)}"

class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Project Planning Specialist',
            goal='Analyze user requirements and create comprehensive project plans for Python applications',
            backstory="""You are an expert software architect with years of experience in Python development. 
            You excel at breaking down complex requirements into structured, implementable plans. You understand 
            the nuances of different Python frameworks and can recommend the best approach for any given project."""
        )
    
    def create_plan(self, user_prompt):
        description = f"""
        Analyze the following user requirement and create a comprehensive project plan:
        
        User Requirement: {user_prompt}
        
        Create a detailed plan in JSON format that includes:
        1. project_name: A suitable name for the project
        2. description: Brief description of what the project does
        3. dependencies: List of Python packages needed
        4. gui_framework: 'streamlit', 'tkinter', or 'none'
        5. files: Array of file objects with:
           - path: relative file path
           - purpose: what this file does
           - functions: list of main functions to implement
           - imports: list of required imports
        6. main_file: name of the main entry point file
        7. architecture: brief description of the project structure
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class SrDeveloper1Agent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Senior Python Developer - Code Generator',
            goal='Generate high-quality Python code based on project plans',
            backstory="""You are a senior Python developer with expertise in writing clean, efficient, 
            and well-structured code. You excel at implementing complex functionality while maintaining 
            code readability and following Python best practices. You understand how to create reusable 
            functions and proper module imports."""
        )
    
    def generate_code(self, project_plan):
        description = f"""
        Based on the following project plan, generate complete Python code for all files:
        
        Project Plan: {project_plan}
        
        Generate complete, functional Python code in JSON format with this structure:
        {{
            "files": [
                {{
                    "path": "filename.py",
                    "content": "complete Python code content"
                }},
                ...
            ]
        }}
        
        Requirements:
        - All code must be complete and functional
        - Include proper imports at the top of each file
        - Add comprehensive comments explaining the code
        - Implement all functions mentioned in the plan
        - Follow PEP 8 style guidelines
        - Include error handling where appropriate
        - Make sure the main file can be executed successfully
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class SrDeveloper2Agent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Senior Python Developer - Code Reviewer & Bug Fixer',
            goal='Review, debug, and fix Python code to ensure quality and functionality',
            backstory="""You are a meticulous senior Python developer specializing in code review 
            and debugging. You have an eye for detail and can quickly identify logic errors, syntax 
            issues, and potential bugs. You excel at fixing code while maintaining its original intent 
            and improving its quality."""
        )
    
    def review_and_fix(self, project_plan, generated_code, error_traceback=None):
        error_context = f"\n\nError encountered:\n{error_traceback}" if error_traceback else ""
        
        description = f"""
        Review and fix the following Python code based on the project plan:
        
        Project Plan: {project_plan}
        
        Generated Code: {generated_code}
        {error_context}
        
        Tasks:
        1. Review all code for syntax errors, logic issues, and potential bugs
        2. Fix any identified problems
        3. Improve code quality and efficiency
        4. Ensure all imports are correct and necessary
        5. Add missing error handling
        6. Verify that the code implements all requirements from the plan
        
        Return the improved code in JSON format:
        {{
            "files": [
                {{
                    "path": "filename.py",
                    "content": "improved Python code content"
                }},
                ...
            ]
        }}
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class TesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Python Code Tester - Runtime Validation',
            goal='Test Python code for runtime errors and basic functionality',
            backstory="""You are a quality assurance specialist focused on testing Python applications. 
            You excel at identifying runtime errors, import issues, and basic functionality problems. 
            You understand how to execute code safely and capture meaningful error information."""
        )
    
    def test_runtime(self, project_files, main_file):
        # This method will be called by the main application logic
        # to actually execute the code and capture any runtime errors
        pass

class DetailedTesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Python Code Tester - Functional Validation',
            goal='Perform comprehensive functional testing of Python applications',
            backstory="""You are an expert QA engineer specializing in functional testing of Python 
            applications. You understand different types of applications and can create appropriate 
            test scenarios. You excel at validating that applications work as intended and meet 
            user requirements."""
        )
    
    def test_functionality(self, project_plan, project_files, runtime_success=True):
        description = f"""
        Perform functional testing of the Python project based on the plan and requirements:
        
        Project Plan: {project_plan}
        
        Project Files: {project_files}
        
        Runtime Status: {"Passed" if runtime_success else "Failed"}
        
        Create a comprehensive test report that includes:
        1. Overall assessment of the project functionality
        2. Whether the code meets the original requirements
        3. Potential issues or limitations found
        4. Suggestions for improvements
        5. Test scenarios that were considered
        6. Recommended next steps
        
        Provide a detailed analysis of how well the generated code fulfills the user's requirements.
        """
        
        result = self.execute_task(description)
        return result

class DocumentCreatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role='Technical Documentation Specialist',
            goal='Create comprehensive documentation for Python projects',
            backstory="""You are a technical writer specializing in software documentation. You excel 
            at creating clear, comprehensive, and user-friendly documentation that helps users understand 
            and use software projects effectively. You understand both technical and non-technical audiences."""
        )
    
    def create_documentation(self, project_plan, project_files):
        description = f"""
        Create comprehensive documentation for the Python project:
        
        Project Plan: {project_plan}
        
        Project Files: {project_files}
        
        Create a well-formatted documentation file that includes:
        1. Project Overview and Purpose
        2. Installation Requirements
        3. How to Run the Application
        4. Features and Functionality
        5. File Structure Explanation
        6. Usage Examples
        7. Configuration Options (if any)
        8. Troubleshooting Tips
        9. Technical Details for Developers
        10. Future Enhancement Possibilities
        
        Make the documentation clear, professional, and user-friendly.
        Include code examples where appropriate.
        """
        
        result = self.execute_task(description)
        return result
