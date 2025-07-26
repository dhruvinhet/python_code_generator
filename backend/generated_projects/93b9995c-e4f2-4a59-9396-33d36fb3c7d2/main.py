#!/usr/bin/env python3
"""
Main entry point for DataPrepCodeGen
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
            import preprocessing_steps
            preprocessing_steps.main()
        else:
            # Try to run with streamlit
            try:
                import streamlit
                print("Streamlit app detected. Starting with streamlit run...")
                print("Visit the URL shown above to interact with the application.")
                
                # Find the streamlit file to run
                streamlit_file_path = "preprocessing_steps.py"
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
                print(f"Error running streamlit app: {e}")
                print(f"You can manually run: streamlit run {streamlit_file_path}")
                return 1
                
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
