#!/usr/bin/env python3
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
        streamlit_file = "app.py"
        
        # Start streamlit server
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', streamlit_file,
            '--server.port', '8501',
            '--server.headless', 'false'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
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
        print("\nApplication stopped by user.")
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
