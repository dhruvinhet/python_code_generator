#!/usr/bin/env python3
"""
Debug script to identify Unicode decode errors in the Python Code Generator
"""
import os
import sys
import traceback
import zipfile
from config import Config

def test_file_operations():
    """Test various file operations that might cause Unicode errors"""
    print("Testing file operations...")
    
    # Test 1: Check if temp and generated projects directories exist
    print(f"1. Temp directory: {Config.TEMP_DIR}")
    print(f"   Exists: {os.path.exists(Config.TEMP_DIR)}")
    
    print(f"2. Generated projects directory: {Config.GENERATED_PROJECTS_DIR}")
    print(f"   Exists: {os.path.exists(Config.GENERATED_PROJECTS_DIR)}")
    
    # Test 2: List files in generated projects
    try:
        for root, dirs, files in os.walk(Config.GENERATED_PROJECTS_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"3. Found file: {file_path}")
                
                # Try to read file info
                try:
                    stat = os.stat(file_path)
                    print(f"   Size: {stat.st_size} bytes")
                    
                    # Try to detect if it's a text or binary file
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(4)
                        print(f"   First 4 bytes: {first_bytes}")
                        
                        # Check if it might be a zip file
                        if first_bytes.startswith(b'PK'):
                            print("   -> Detected as ZIP file")
                            try:
                                with zipfile.ZipFile(file_path, 'r') as zf:
                                    print(f"   -> ZIP contents: {zf.namelist()}")
                            except Exception as e:
                                print(f"   -> ZIP read error: {e}")
                        else:
                            print("   -> Detected as text/other file")
                            # Try to read as text
                            try:
                                f.seek(0)
                                sample = f.read(100)
                                decoded = sample.decode('utf-8')
                                print(f"   -> UTF-8 sample: {decoded[:50]}...")
                            except UnicodeDecodeError as e:
                                print(f"   -> UTF-8 decode error: {e}")
                                # Try other encodings
                                for encoding in ['latin-1', 'cp1252', 'ascii']:
                                    try:
                                        f.seek(0)
                                        sample = f.read(100)
                                        decoded = sample.decode(encoding, errors='replace')
                                        print(f"   -> {encoding} sample: {decoded[:50]}...")
                                        break
                                    except Exception:
                                        continue
                        
                except Exception as e:
                    print(f"   Error reading file {file_path}: {e}")
                    traceback.print_exc()
    
    except Exception as e:
        print(f"Error walking directory: {e}")
        traceback.print_exc()

def test_zip_operations():
    """Test zip file operations"""
    print("\nTesting ZIP operations...")
    
    # Create a test zip file
    test_zip_path = os.path.join(Config.TEMP_DIR, "test_unicode.zip")
    
    try:
        # Create test content with various encodings
        test_content = {
            "test.txt": "Hello World!\nThis is a test file.",
            "unicode_test.txt": "Unicode test: héllo wørld 🌍",
            "requirements.txt": "flask\nrequests\nnumpy"
        }
        
        with zipfile.ZipFile(test_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in test_content.items():
                zipf.writestr(filename, content.encode('utf-8'))
        
        print(f"Created test zip: {test_zip_path}")
        
        # Test reading the zip
        with zipfile.ZipFile(test_zip_path, 'r') as zipf:
            print(f"ZIP contents: {zipf.namelist()}")
            
            for filename in zipf.namelist():
                content = zipf.read(filename)
                print(f"File {filename}: {len(content)} bytes")
                try:
                    decoded = content.decode('utf-8')
                    print(f"  Content: {decoded[:50]}...")
                except UnicodeDecodeError as e:
                    print(f"  Unicode error: {e}")
        
        # Clean up
        os.remove(test_zip_path)
        print("Test zip cleaned up successfully")
        
    except Exception as e:
        print(f"Error in zip operations: {e}")
        traceback.print_exc()

def main():
    """Main debug function"""
    print("Python Code Generator - Unicode Debug Tool")
    print("=" * 50)
    
    try:
        test_file_operations()
        test_zip_operations()
        
        print("\nDebug completed successfully!")
        
    except Exception as e:
        print(f"Critical error during debug: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
