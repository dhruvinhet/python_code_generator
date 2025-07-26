from crewai import Agent, Task, Crew, Process
import google.generativeai as genai
from config import Config
import os
import json

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

class PlanningAgent:
    def __init__(self):
        self.agent = Agent(
            role='Project Planning Specialist',
            goal='Analyze user requirements and create comprehensive project plans for Python applications',
            backstory="""You are an expert software architect with years of experience in Python development. 
            You excel at breaking down complex requirements into structured, implementable plans. You understand 
            the nuances of different Python frameworks and can recommend the best approach for any given project.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_plan(self, user_prompt):
        task = Task(
            description=f"""
            Analyze the following user requirement and create a comprehensive project plan:
            
            User Requirement: {user_prompt}
            
            Create a detailed plan that includes:
            1. Project overview and purpose
            2. Required Python libraries and dependencies
            3. Complete folder and file structure
            4. Detailed description of what each file should contain
            5. Main entry point (main.py) functionality
            6. GUI framework recommendation (Streamlit or Tkinter) if needed
            7. Key functions and their purposes
            8. Data flow and architecture
            
            Return the plan as a structured JSON with the following format:
            {{
                "project_name": "string",
                "description": "string",
                "dependencies": ["list", "of", "packages"],
                "gui_framework": "streamlit|tkinter|none",
                "files": [
                    {{
                        "path": "relative/path/to/file.py",
                        "purpose": "description of what this file does",
                        "functions": ["list", "of", "main", "functions"],
                        "imports": ["required", "imports"]
                    }}
                ],
                "main_file": "main.py",
                "architecture": "description of overall architecture"
            }}
            """,
            agent=self.agent,
            expected_output="A comprehensive JSON project plan"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

class SrDeveloper1Agent:
    def __init__(self):
        self.agent = Agent(
            role='Senior Python Developer - Code Generator',
            goal='Generate high-quality Python code based on project plans',
            backstory="""You are a senior Python developer with expertise in writing clean, efficient, 
            and well-structured code. You excel at implementing complex functionality while maintaining 
            code readability and following Python best practices. You understand how to create reusable 
            functions and proper module imports.""",
            verbose=True,
            allow_delegation=False
        )
    
    def generate_code(self, project_plan):
        task = Task(
            description=f"""
            Based on the following project plan, generate complete Python code for all files:
            
            Project Plan: {project_plan}
            
            Generate complete, functional Python code for each file specified in the plan. Ensure:
            1. All imports are correct and necessary
            2. Functions are well-documented with docstrings
            3. Code follows Python best practices (PEP 8)
            4. Reusable functions are created where appropriate
            5. Main file serves as the entry point
            6. GUI implementation uses the recommended framework
            7. Error handling is included where necessary
            8. Code is production-ready and functional
            
            Return the code as a JSON structure:
            {{
                "files": [
                    {{
                        "path": "relative/path/to/file.py",
                        "content": "complete file content as string"
                    }}
                ]
            }}
            """,
            agent=self.agent,
            expected_output="Complete Python code for all project files in JSON format"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

class SrDeveloper2Agent:
    def __init__(self):
        self.agent = Agent(
            role='Senior Python Developer - Code Reviewer & Bug Fixer',
            goal='Review, debug, and fix Python code to ensure quality and functionality',
            backstory="""You are a meticulous senior Python developer specializing in code review 
            and debugging. You have an eye for detail and can quickly identify logic errors, syntax 
            issues, and potential bugs. You excel at fixing code while maintaining its original intent 
            and improving its quality.""",
            verbose=True,
            allow_delegation=False
        )
    
    def review_and_fix(self, project_plan, generated_code, error_traceback=None):
        error_context = f"\n\nError encountered:\n{error_traceback}" if error_traceback else ""
        
        task = Task(
            description=f"""
            Review and fix the following Python code based on the project plan:
            
            Project Plan: {project_plan}
            
            Generated Code: {generated_code}
            {error_context}
            
            Your tasks:
            1. Review code for alignment with the project plan
            2. Check for syntax errors and logic issues
            3. Fix any bugs or errors found
            4. Ensure proper imports and dependencies
            5. Verify code functionality and completeness
            6. Improve code quality while maintaining functionality
            
            If an error traceback is provided, focus on fixing that specific issue.
            
            Return the fixed code in the same JSON format:
            {{
                "files": [
                    {{
                        "path": "relative/path/to/file.py",
                        "content": "fixed and improved file content"
                    }}
                ],
                "fixes_applied": ["list", "of", "fixes", "made"]
            }}
            """,
            agent=self.agent,
            expected_output="Fixed and improved Python code in JSON format"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

class TesterAgent:
    def __init__(self):
        self.agent = Agent(
            role='Python Code Tester - Runtime Validation',
            goal='Test Python code for runtime errors and basic functionality',
            backstory="""You are a quality assurance specialist focused on testing Python applications. 
            You excel at identifying runtime errors, import issues, and basic functionality problems. 
            You understand how to execute code safely and capture meaningful error information.""",
            verbose=True,
            allow_delegation=False
        )
    
    def test_runtime(self, project_files, main_file):
        # This method will be called by the main application logic
        # to actually execute the code and capture any runtime errors
        pass

class DetailedTesterAgent:
    def __init__(self):
        self.agent = Agent(
            role='Python Code Tester - Functional Validation',
            goal='Perform comprehensive functional testing of Python applications',
            backstory="""You are an expert QA engineer specializing in functional testing of Python 
            applications. You understand different types of applications and can create appropriate 
            test scenarios. You excel at validating that applications work as intended and meet 
            user requirements.""",
            verbose=True,
            allow_delegation=False
        )
    
    def test_functionality(self, project_plan, project_files, runtime_success=True):
        task = Task(
            description=f"""
            Perform functional testing of the Python project based on the plan and requirements:
            
            Project Plan: {project_plan}
            
            Project Files: {project_files}
            
            Runtime Status: {"Passed" if runtime_success else "Failed"}
            
            Create comprehensive test scenarios based on the project type:
            1. Identify the main functionality of the application
            2. Create test cases for key features
            3. Validate user interaction flows (if GUI)
            4. Test edge cases and error conditions
            5. Verify data processing and outputs
            6. Check for usability and user experience
            
            Return your testing analysis:
            {{
                "test_scenarios": [
                    {{
                        "scenario": "description",
                        "expected_result": "what should happen",
                        "test_method": "how to test this"
                    }}
                ],
                "functional_issues": ["list", "of", "issues", "found"],
                "recommendations": ["list", "of", "improvements"],
                "overall_assessment": "pass|fail|needs_improvement"
            }}
            """,
            agent=self.agent,
            expected_output="Comprehensive functional testing analysis in JSON format"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

class DocumentCreatorAgent:
    def __init__(self):
        self.agent = Agent(
            role='Technical Documentation Specialist',
            goal='Create comprehensive documentation for Python projects',
            backstory="""You are a technical writer specializing in software documentation. You excel 
            at creating clear, comprehensive, and user-friendly documentation that helps users understand 
            and use software projects effectively. You understand both technical and non-technical audiences.""",
            verbose=True,
            allow_delegation=False
        )
    
    def create_documentation(self, project_plan, project_files):
        task = Task(
            description=f"""
            Create comprehensive documentation for the Python project:
            
            Project Plan: {project_plan}
            
            Project Files: {project_files}
            
            Create a well-formatted documentation file that includes:
            1. Project Overview and Purpose
            2. Features and Functionality
            3. Installation and Setup Instructions
            4. Required Libraries and Dependencies
            5. How to Run the Project
            6. Usage Instructions and Examples
            7. File Structure Explanation
            8. Troubleshooting Common Issues
            9. Future Feature Suggestions
            10. Contributing Guidelines (if applicable)
            
            Format the documentation in a clear, professional manner suitable for a README.txt file.
            Use proper headings, bullet points, and formatting for readability.
            
            Return the documentation as a string.
            """,
            agent=self.agent,
            expected_output="Comprehensive project documentation as formatted text"
        )
        
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result

