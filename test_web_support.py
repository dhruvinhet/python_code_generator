#!/usr/bin/env python3
"""
Test script for the enhanced Python Code Generator with web application support.
This script tests both Python application and web application generation.
"""

import sys
import os
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from project_manager import ProjectManager
import uuid

def test_web_application():
    """Test web application generation"""
    print("Testing Web Application Generation...")
    print("="*50)
    
    # Create a project manager instance
    project_manager = ProjectManager()
    
    # Test prompt for a web application
    web_prompt = "Create a vehicle rental website where users can browse available cars, select rental dates, and calculate rental costs. Include a responsive design with modern styling."
    
    # Generate unique project ID
    project_id = str(uuid.uuid4())
    
    print(f"Generating web application for prompt: {web_prompt}")
    print(f"Project ID: {project_id}")
    print("-" * 50)
    
    try:
        # Generate the project
        result = project_manager.generate_project(web_prompt, project_id)
        
        if result and result.get('success'):
            print("✅ Web application generated successfully!")
            print(f"Project Type: {result.get('project_type', 'Unknown')}")
            print(f"Frontend Framework: {result.get('frontend_framework', 'Unknown')}")
            print(f"Backend Framework: {result.get('backend_framework', 'Unknown')}")
            print(f"Project Directory: {result.get('project_dir', 'Unknown')}")
            
            # List generated files
            project_dir = result.get('project_dir')
            if project_dir and os.path.exists(project_dir):
                print("\nGenerated Files:")
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        relative_path = os.path.relpath(os.path.join(root, file), project_dir)
                        print(f"  - {relative_path}")
            
            return True
        else:
            print("❌ Web application generation failed!")
            print(f"Error: {result.get('error', 'Unknown error') if result else 'No result returned'}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during web application generation: {str(e)}")
        return False

def test_python_application():
    """Test Python application generation (existing functionality)"""
    print("\nTesting Python Application Generation...")
    print("="*50)
    
    # Create a project manager instance
    project_manager = ProjectManager()
    
    # Test prompt for a Python application
    python_prompt = "Create a simple calculator application using streamlit that can perform basic arithmetic operations."
    
    # Generate unique project ID
    project_id = str(uuid.uuid4())
    
    print(f"Generating Python application for prompt: {python_prompt}")
    print(f"Project ID: {project_id}")
    print("-" * 50)
    
    try:
        # Generate the project
        result = project_manager.generate_project(python_prompt, project_id)
        
        if result and result.get('success'):
            print("✅ Python application generated successfully!")
            print(f"Project Directory: {result.get('project_dir', 'Unknown')}")
            
            # List generated files
            project_dir = result.get('project_dir')
            if project_dir and os.path.exists(project_dir):
                print("\nGenerated Files:")
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        relative_path = os.path.relpath(os.path.join(root, file), project_dir)
                        print(f"  - {relative_path}")
            
            return True
        else:
            print("❌ Python application generation failed!")
            print(f"Error: {result.get('error', 'Unknown error') if result else 'No result returned'}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during Python application generation: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Python Code Generator - Web Application Support Test")
    print("=" * 60)
    print()
    
    # Test web application generation
    web_success = test_web_application()
    
    # Test Python application generation
    python_success = test_python_application()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Web Application Test: {'✅ PASSED' if web_success else '❌ FAILED'}")
    print(f"Python Application Test: {'✅ PASSED' if python_success else '❌ FAILED'}")
    
    if web_success and python_success:
        print("\n🎉 All tests passed! Your enhanced system supports both Python and Web applications.")
    elif web_success:
        print("\n⚠️  Web application support is working, but Python application test failed.")
    elif python_success:
        print("\n⚠️  Python application support is working, but Web application test failed.")
    else:
        print("\n❌ Both tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
