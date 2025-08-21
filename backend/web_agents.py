import google.generativeai as genai
from config import Config
import json
import re

# Configure Gemini API
genai.configure(api_key=Config.GOOGLE_API_KEY)

class BaseWebAgent:
    """Base web agent class using Google Generative AI directly"""
    
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

class WebPlanningAgent(BaseWebAgent):
    def __init__(self):
        super().__init__(
            role='Full-Stack Web Development Planning Specialist',
            goal='Analyze user requirements and create comprehensive plans for web applications including frontend and backend',
            backstory="""You are an expert full-stack web architect with years of experience in modern web development. 
            You excel at breaking down complex web application requirements into structured, implementable plans. 
            You understand frontend frameworks (React, Vue, vanilla JS), backend APIs (Flask, FastAPI), databases, 
            and modern web development best practices including responsive design, accessibility, and performance optimization."""
        )
    
    def create_web_plan(self, user_prompt):
        description = f"""
        Analyze the following user requirement and create a comprehensive web application plan:
        
        User Requirement: {user_prompt}
        
        Create a detailed plan in JSON format that includes:
        1. project_name: A suitable name for the project
        2. description: Brief description of what the web application does
        3. project_type: 'web_application' for full web apps
        4. frontend_framework: 'react', 'vue', 'vanilla_js' based on complexity
        5. backend_framework: 'flask', 'fastapi', 'django' based on needs
        6. database: 'sqlite', 'json_file', 'mongodb', or 'none'
        7. features: Array of main features to implement
        8. pages: Array of page objects with:
           - name: page name
           - route: URL route
           - purpose: what this page does
           - components: list of UI components needed
        9. api_endpoints: Array of API endpoint objects with:
           - method: GET, POST, PUT, DELETE
           - route: API route
           - purpose: what this endpoint does
           - data: expected data format
        10. files: Array of file objects with:
           - path: relative file path
           - type: 'html', 'css', 'js', 'py', 'json'
           - purpose: what this file does
           - dependencies: list of required imports/includes
        11. styling: 'css', 'tailwind', 'bootstrap' based on requirements
        12. responsive: true/false for mobile responsiveness
        13. main_file: Set to "app.py" for backend, "index.html" for frontend entry
        
        IMPORTANT: 
        - For simple websites, use vanilla JS
        - For complex apps with state management, use React or Vue
        - Always include responsive design considerations
        - Structure files properly (static/, templates/, src/, etc.)
        
        CRITICAL JSON FORMAT REQUIREMENTS:
        - Return ONLY valid JSON, no additional text or markdown
        - Escape all backslashes in strings (use \\\\ instead of \\)
        - Escape all quotes in strings (use \\" instead of ")
        - Do NOT include any code examples or multi-line strings in the JSON
        - Keep all content simple and JSON-safe
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class FrontendDeveloperAgent(BaseWebAgent):
    def __init__(self):
        super().__init__(
            role='Senior Frontend Developer - HTML/CSS/JavaScript',
            goal='Generate modern, responsive frontend code using HTML, CSS, and JavaScript',
            backstory="""You are a senior frontend developer with expertise in creating beautiful, responsive, 
            and interactive web interfaces. You excel at writing clean HTML, efficient CSS (including Flexbox, Grid, 
            and modern CSS features), and vanilla JavaScript or React/Vue components. You understand accessibility, 
            performance optimization, and modern web standards. You can create both simple static sites and complex 
            interactive applications."""
        )
    
    def generate_frontend_code(self, project_plan):
        description = f"""
        Based on the following project plan, generate complete frontend code (HTML, CSS, JavaScript):
        
        Project Plan: {project_plan}
        
        CRITICAL REQUIREMENTS FOR PRODUCTION-READY CODE:

        1. **COMPLETE PROJECT STRUCTURE** - Generate ALL necessary files:
        - Main index.html with navigation to ALL pages mentioned
        - Create ACTUAL HTML files for every navigation link (about.html, contact.html, login.html, etc.)
        - Each page must have identical navigation and relevant content
        - All pages must be fully functional, not placeholder pages

        2. **HTML REQUIREMENTS**:
        - Use semantic HTML5 elements (header, nav, main, section, article, footer)
        - Include proper DOCTYPE and meta tags for responsive design
        - Add accessibility attributes (alt text, ARIA labels, proper headings)
        - Ensure all images have fallback alt text
        - Use proper form validation attributes where needed
        - Every navigation link MUST have a corresponding HTML file

        3. **CSS REQUIREMENTS**:
        - Create mobile-first responsive design with proper breakpoints
        - Use modern CSS features (Flexbox, Grid, CSS Variables)
        - Include hover states and smooth transitions
        - Ensure proper contrast ratios for accessibility
        - Add loading states and visual feedback for user interactions
        - ALL CSS classes must exactly match HTML class names
        - ALL CSS IDs must exactly match HTML element IDs

        4. **JAVASCRIPT REQUIREMENTS**:
        - Use modern ES6+ syntax (async/await, arrow functions, const/let)
        - Implement proper error handling with try-catch blocks
        - Add loading states during API calls
        - Include fallback data if API is unavailable
        - Add proper event listeners and DOM manipulation
        - Configure correct API endpoints (use http://localhost:8080/api as base URL)
        - Add console logging for debugging
        - Include form validation and user feedback

        5. **API INTEGRATION REQUIREMENTS**:
        - Configure API base URL as http://localhost:8080/api
        - Implement GET /api/vehicles endpoint calls
        - Add error handling for network failures
        - Include loading indicators during API calls
        - Provide fallback sample data if API is unavailable
        - Add proper HTTP status code handling

        6. **USER EXPERIENCE REQUIREMENTS**:
        - Add smooth scrolling navigation
        - Include interactive buttons and hover effects
        - Provide clear visual feedback for user actions
        - Display information clearly
        - Add functional buttons with proper event handling
        - Include a test API connection button for debugging

        **MANDATORY: COMPLETE PAGE GENERATION**
        If your navigation includes links like:
        - "About" -> create about.html
        - "Contact" -> create contact.html  
        - "Services" -> create services.html
        - "Login" -> create login.html
        - "Register" -> create register.html

        Each page must have:
        - Same navigation as index.html
        - Relevant content for that page
        - Same CSS styling
        - Professional appearance

        Generate complete, functional frontend code in JSON format with this structure:
        {{
            "files": [
                {{
                    "path": "index.html",
                    "content": "COMPLETE HTML with proper structure, meta tags, and semantic elements"
                }},
                {{
                    "path": "about.html",
                    "content": "COMPLETE about page with same navigation and relevant content"
                }},
                {{
                    "path": "contact.html",
                    "content": "COMPLETE contact page with same navigation and contact form"
                }},
                {{
                    "path": "static/css/style.css", 
                    "content": "COMPLETE responsive CSS with modern styling, mobile-first design, and professional appearance"
                }},
                {{
                    "path": "static/js/script.js",
                    "content": "COMPLETE JavaScript with API integration, error handling, fallback data, and proper event listeners"
                }}
            ]
        }}
        
        CRITICAL JSON FORMAT REQUIREMENTS:
        - Return ONLY valid JSON, no additional text or markdown
        - Escape all backslashes in code strings (use \\\\ for each \\)
        - Escape all quotes in code strings (use \\" for each ")
        - Be extra careful with HTML attributes and CSS selectors
        - Test JSON validity before returning
        - Do NOT wrap in markdown code blocks
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class BackendAPIAgent(BaseWebAgent):
    def __init__(self):
        super().__init__(
            role='Senior Backend Developer - API Development',
            goal='Generate robust backend APIs using Flask, FastAPI, or Django',
            backstory="""You are a senior backend developer specializing in API development and server-side logic. 
            You excel at creating RESTful APIs, handling data persistence, implementing authentication, and building 
            scalable backend architectures. You understand database integration, error handling, security best practices, 
            and API documentation. You can work with Flask, FastAPI, Django, and various databases."""
        )
    
    def generate_backend_code(self, project_plan):
        description = f"""
        Based on the following project plan, generate complete backend code:
        
        Project Plan: {project_plan}
        
        CRITICAL REQUIREMENTS FOR PRODUCTION-READY BACKEND:

        1. ARCHITECTURE REQUIREMENTS (PREVENT CIRCULAR IMPORTS):
        - Create a separate database.py file with SQLAlchemy instance
        - Use proper Flask application factory pattern
        - Import order: database.py -> models.py -> routes.py -> app.py
        - Never import app.py from other modules to avoid circular imports

        2. FILE STRUCTURE REQUIREMENTS:
        - database.py: Contains db = SQLAlchemy() and init_db() function
        - models.py: Contains all database models, imports from database.py
        - routes.py: Contains API endpoints, imports from database.py and models.py
        - app.py: Main application file, imports from database.py, models.py, routes.py
        - run.py: Development server runner that imports from app.py

        3. FLASK APPLICATION REQUIREMENTS:
        - Configure template_folder='.' and static_folder='static'
        - Use port 8080 instead of 5000 (avoid conflicts)
        - Enable CORS for frontend integration
        - Include both API routes and frontend serving routes
        - Add proper error handling and logging

        4. DATABASE REQUIREMENTS:
        - Use SQLite with proper file path configuration
        - Create all required models (User, Vehicle, Booking)
        - Include proper relationships and constraints
        - Add sample data insertion for testing

        5. API ENDPOINTS REQUIREMENTS:
        - GET /api/health - Health check endpoint
        - GET /api/vehicles - List all vehicles
        - POST /api/vehicles - Add new vehicle
        - GET /api/vehicles/<id> - Get specific vehicle
        - POST /api/bookings - Create booking
        - GET /api/bookings - List bookings
        - Include proper HTTP status codes and error responses

        6. FRONTEND SERVING REQUIREMENTS:
        - Route '/' should serve index.html using render_template
        - Static files should be served from /static/ directory
        - Include favicon handling
        - Add test route for backend verification

        Generate complete, functional backend code in JSON format with this structure:
        {{
            "files": [
                {{
                    "path": "database.py",
                    "content": "COMPLETE database configuration module with SQLAlchemy instance and init function"
                }},
                {{
                    "path": "models.py",
                    "content": "COMPLETE database models with proper relationships and methods"
                }},
                {{
                    "path": "routes.py",
                    "content": "COMPLETE API routes with proper error handling and validation"
                }},
                {{
                    "path": "app.py",
                    "content": "COMPLETE Flask application with frontend serving and API integration"
                }},
                {{
                    "path": "run.py",
                    "content": "COMPLETE development server runner with proper configuration"
                }},
                {{
                    "path": "requirements.txt",
                    "content": "ALL required Python dependencies with specific versions"
                }}
            ]
        }}
        
        MANDATORY CODE QUALITY REQUIREMENTS:
        - NO CIRCULAR IMPORTS - Follow strict import hierarchy
        - All endpoints must be functional and tested
        - Include comprehensive error handling
        - Add proper HTTP status codes (200, 400, 404, 500)
        - Include CORS configuration for frontend integration
        - Use port 8080 for development server
        - Add proper logging and debugging information
        - Include sample data for testing
        - Ensure database tables are created automatically
        - Add proper validation for all inputs

        CRITICAL ARCHITECTURAL PATTERN:
        
        database.py:
        ```
        from flask_sqlalchemy import SQLAlchemy
        db = SQLAlchemy()
        def init_db(app): ...
        ```
        
        models.py:
        ```
        from database import db
        class User(db.Model): ...
        ```
        
        routes.py:
        ```
        from database import db
        from models import User, Vehicle
        api = Blueprint('api', __name__, url_prefix='/api')
        ```
        
        app.py:
        ```
        from database import db, init_db
        from models import User, Vehicle
        from routes import api
        app.register_blueprint(api)
        ```

        CRITICAL JSON FORMAT REQUIREMENTS:
        - Return ONLY valid JSON, no additional text or markdown
        - Escape all backslashes in code strings (use \\\\ for each \\)
        - Escape all quotes in code strings (use \\" for each ")
        - Be extra careful with Python string formatting and JSON
        - Test JSON validity before returning
        - Do NOT wrap in markdown code blocks
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class FullStackIntegratorAgent(BaseWebAgent):
    def __init__(self):
        super().__init__(
            role='Full-Stack Integration Specialist',
            goal='Integrate frontend and backend components into a cohesive web application',
            backstory="""You are a full-stack integration expert who specializes in connecting frontend and backend 
            components seamlessly. You understand API integration, data flow, state management, and deployment 
            configurations. You excel at creating cohesive applications where frontend and backend work together 
            perfectly, handling edge cases, error states, and providing smooth user experiences."""
        )
    
    def integrate_fullstack(self, project_plan, frontend_code, backend_code):
        description = f"""
        Integrate the following frontend and backend code into a cohesive web application:
        
        Project Plan: {project_plan}
        Frontend Code: {frontend_code}
        Backend Code: {backend_code}
        
        CRITICAL INTEGRATION REQUIREMENTS:

        1. VERIFY AND FIX ARCHITECTURAL ISSUES:
        - Ensure NO circular imports in backend code
        - Verify database.py -> models.py -> routes.py -> app.py import hierarchy
        - Check that app.py serves both frontend and API routes
        - Confirm port 8080 is used consistently

        2. FRONTEND-BACKEND CONNECTION:
        - Verify JavaScript uses correct API base URL (http://localhost:8080/api)
        - Ensure all API endpoints are properly defined in backend
        - Check that CORS is enabled for frontend requests
        - Validate API response formats match frontend expectations

        3. ERROR HANDLING AND RESILIENCE:
        - Add comprehensive error handling in JavaScript
        - Include fallback data when API is unavailable
        - Implement proper loading states during API calls
        - Add user-friendly error messages

        4. DEVELOPMENT CONFIGURATION:
        - Create .env.example with all required environment variables
        - Add run.py with proper development server configuration
        - Include README.md with clear setup and run instructions
        - Add sample data insertion for immediate testing

        5. PRODUCTION READINESS:
        - Ensure all dependencies are in requirements.txt
        - Add proper security configurations
        - Include error logging and debugging
        - Verify responsive design works correctly

        Tasks to complete:
        1. Fix any circular import issues in backend
        2. Ensure frontend API calls match backend endpoints
        3. Add comprehensive error handling
        4. Create configuration files (.env.example)
        5. Add README with setup instructions
        6. Include sample data for testing
        7. Verify all components work together seamlessly

        Return the integrated code in JSON format:
        {{
            "files": [
                {{
                    "path": "filename",
                    "content": "COMPLETE integrated and tested code"
                }},
                ...
            ]
        }}
        
        MANDATORY INTEGRATION FIXES:
        - Fix any circular imports using proper module structure
        - Ensure API endpoints work correctly
        - Add sample data for immediate testing
        - Include comprehensive error handling
        - Add environment configuration
        - Create clear documentation
        - Verify frontend-backend communication

        Additional files to include:
        - .env.example: Environment variables template
        - README.md: Setup and run instructions
        - sample_data.py: Script to populate database with test data
        - Updated requirements.txt with all dependencies

        CRITICAL JSON FORMAT REQUIREMENTS:
        - Return ONLY valid JSON, no additional text or markdown
        - Escape all backslashes in code strings (use \\\\ for each \\)
        - Escape all quotes in code strings (use \\" for each ")
        - Test JSON validity before returning
        - Do NOT wrap in markdown code blocks
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result

class WebTesterAgent(BaseWebAgent):
    def __init__(self):
        super().__init__(
            role='Web Application Tester - Frontend & Backend Validation',
            goal='Test web applications for functionality, responsiveness, and integration issues',
            backstory="""You are a web application testing specialist who excels at identifying issues in both 
            frontend and backend components. You understand browser compatibility, responsive design testing, 
            API testing, performance optimization, and user experience validation. You can create comprehensive 
            test plans and identify potential issues before deployment."""
        )
    
    def test_web_application(self, project_files, project_plan):
        description = f"""
        Test the following web application files for issues and improvements:
        
        Project Plan: {project_plan}
        Project Files: {project_files}
        
        Perform comprehensive testing and return results in JSON format:
        {{
            "test_results": {{
                "frontend_tests": [
                    {{
                        "test": "HTML validation",
                        "status": "pass/fail/warning",
                        "details": "description of findings"
                    }}
                ],
                "backend_tests": [
                    {{
                        "test": "API endpoint validation", 
                        "status": "pass/fail/warning",
                        "details": "description of findings"
                    }}
                ],
                "integration_tests": [
                    {{
                        "test": "Frontend-Backend integration",
                        "status": "pass/fail/warning", 
                        "details": "description of findings"
                    }}
                ],
                "overall_score": 85,
                "recommendations": [
                    "List of improvements and fixes"
                ]
            }}
        }}
        
        Test categories:
        - HTML semantic structure and validation
        - CSS responsiveness and cross-browser compatibility
        - JavaScript functionality and error handling
        - API endpoint correctness and error responses
        - Frontend-backend data flow
        - Security considerations
        - Performance optimization opportunities
        - Accessibility compliance
        - User experience assessment
        
        Return ONLY valid JSON, no additional text.
        """
        
        result = self.execute_task(description)
        return result
