import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CrewAI Configuration
    CREWAI_MODEL = "gemini/gemini-2.0-flash-exp"
    
    # Project Generation Settings
    MAX_PROJECT_SIZE = 50  # Maximum number of files
    SUPPORTED_GUI_FRAMEWORKS = ['streamlit', 'tkinter']
    
    # File paths
    GENERATED_PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'generated_projects')
    TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')

