#!/usr/bin/env python3
"""
Development server runner for the web application.
Run this file to start the development server.
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("Starting web application development server...")
    print("Open your browser and go to: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='127.0.0.1', port=8080)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Try running on a different port: python run.py --port 8081")
        sys.exit(1)
