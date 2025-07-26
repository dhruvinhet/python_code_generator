#!/usr/bin/env python3
"""
Main entry point for Scientific Calculator
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
            from src import user_interface
            user_interface.main()
        else:
            # Try to run with streamlit
            try:
                import streamlit
                print("Streamlit app detected. Starting with streamlit run...")
                print("Visit the URL shown above to interact with the application.")
                
                # Find the streamlit file to run
                streamlit_file_path = "src/user_interface.py"
                if not os.path.exists(streamlit_file_path):
                    # Look for any .py file with streamlit imports
                    for root, dirs, files in os.walk('.'):
                        for file in files:
                            if file.endswith('.py') and file != 'main.py':
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        if 'streamlit' in content:
                                            streamlit_file_path = file_path
                                            break
                                except:
                                    continue
                        if streamlit_file_path != "src/user_interface.py":
                            break
                
                # Run streamlit
                print(f"Running: streamlit run {streamlit_file_path}")
                result = subprocess.run([
                    sys.executable, '-m', 'streamlit', 'run', streamlit_file_path,
                    '--server.headless', 'true',
                    '--server.port', '8501'
                ], check=True)
                
            except ImportError:
                print("Streamlit not installed. Installing...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
                    print("Streamlit installed. Please run 'python main.py' again.")
                except Exception as install_error:
                    print(f"Failed to install streamlit: {install_error}")
                    print("Please manually install with: pip install streamlit")
                    print(f"Then run: streamlit run {streamlit_file_path}")
            except subprocess.CalledProcessError as e:
                print(f"Streamlit process failed: {e}")
                print(f"You can manually run: streamlit run {streamlit_file_path}")
            except Exception as e:
                print(f"Error running streamlit app: {e}")
                print(f"You can manually run: streamlit run {streamlit_file_path}")
                return 1
                
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
