import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    CREWAI_MODEL = "gemini/gemini-2.5-flash"
    FALLBACK_MODEL = "gemini/gemini-2.5-flash"  # Fallback model for when primary is overloaded
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = 'production'  # Force production mode to prevent auto-reload
    DEBUG = False  # Disable debug mode to prevent duplicate processes
    USE_RELOADER = False  # Explicitly disable reloader
    
    # PPT Generation Configuration
    MAX_SLIDES = 20  # Maximum number of slides allowed
    DEFAULT_SLIDES = 5  # Default number of slides if not specified
    
    # File paths
    GENERATED_PPTS_DIR = 'generated_ppts'
    TEMP_DIR = 'temp'
    HTML_OUTPUTS_DIR = 'temp/html_outputs'
    
    # Supported formats
    SUPPORTED_FORMATS = ['pptx', 'pdf']
    
    # Agent Configuration
    AGENT_TIMEOUT = 300  # 5 minutes timeout for each agent
    
    # Retry Configuration for API calls
    MAX_RETRIES = 5  # Maximum number of retry attempts (increased from 3)
    RETRY_DELAY = 3  # Initial delay between retries in seconds (increased from 2)
    RETRY_BACKOFF = 1.5  # Exponential backoff multiplier (reduced for more frequent retries)
    MAX_RETRY_DELAY = 30  # Maximum delay between retries
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not set")
        return True

