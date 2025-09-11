#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import webbrowser

def install_requirements():
    try:
        print('Installing Python dependencies...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        if os.path.exists('backend/requirements.txt'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'])
        print('Dependencies installed successfully.')
    except subprocess.CalledProcessError as e:
        print(f'Error installing dependencies: {e}')
        sys.exit(1)

def start_backend():
    try:
        print('Starting backend server on port 7000...')
        os.chdir('backend'); subprocess.Popen([sys.executable, 'app.py']); os.chdir('..')
        print('Backend server started on http://localhost:7000')
    except Exception as e:
        print(f'Error starting backend server: {e}')
        sys.exit(1)

def start_frontend():
    try:
        print('Starting frontend on port 4000...')
        os.chdir('frontend'); subprocess.call(['npm', 'install']); os.environ['PORT'] = '4000'; subprocess.Popen(['npm', 'start']); os.chdir('..')
        print('Frontend setup completed')
        time.sleep(5)
        open_browser('http://localhost:4000')
    except Exception as e:
        print(f'Error starting frontend: {e}')

def open_browser(url):
    try:
        print(f'Opening {url} in browser...')
        webbrowser.open(url)
    except Exception as e:
        print(f'Error opening browser: {e}')

def main():
    print('Starting project setup...')
    print('Backend will run on port 7000, Frontend on port 4000')
    install_requirements()
    start_backend()
    start_frontend()
    print('Project is running! Check your browser.')

if __name__ == '__main__':
    main()
