#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Suppress Pydantic deprecation warnings
import warnings
from pydantic._internal._config import PydanticDeprecatedSince20
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

# Configure logging before importing app modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ppt_generator.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Start the PPT Generator API server with optimal configuration."""
    
    # Disable reloader to prevent duplicate logs
    os.environ['FLASK_USE_RELOADER'] = 'False'
    
    
    logger.info("=== PPT Generator API Server ===")
    try:
        # Set environment variables for single-process mode
        os.environ['FLASK_ENV'] = 'production'
        os.environ['FLASK_DEBUG'] = 'False'
        
        # Import after setting environment variables
        from app import app, socketio
        from config import Config
        
        logger.info(f"Model: {Config.CREWAI_MODEL}")
        logger.info("Access the API at: http://localhost:5000")
        
        # Start the server in single-process mode
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            log_output=False,  # Disable additional socketio logging
            allow_unsafe_werkzeug=True
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()