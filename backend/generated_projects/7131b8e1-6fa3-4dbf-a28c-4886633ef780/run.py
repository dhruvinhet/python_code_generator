from app import app
import os
from wsgiref.simple_server import make_server, WSGIServer
import threading
import webbrowser
import time

class QuietWSGIServer(WSGIServer):
    """A quieter WSGI server that doesn't log every request"""
    def log_message(self, format, *args):
        pass  # Suppress request logs

if __name__ == '__main__':
    port = 8080
    host = '0.0.0.0'
    
    print(f"Starting web application on http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Use Python's built-in WSGI server instead of Flask's development server
        with make_server(host, port, app, server_class=QuietWSGIServer) as httpd:
            print(f"Server started successfully on http://localhost:{port}")
            
            # Open browser in a separate thread
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print("Try stopping other applications using this port.")
        else:
            print(f"\nError starting server: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import sys
        sys.exit(1)
