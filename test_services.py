#!/usr/bin/env python3
"""
Test script to check if FastAPI and Streamlit services are running
"""

import requests
import time
import subprocess
import sys

def test_fastapi():
    """Test if FastAPI server is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is running at http://localhost:8000")
            return True
        else:
            print(f"❌ FastAPI server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing FastAPI: {e}")
        return False

def test_streamlit():
    """Test if Streamlit server is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit server is running at http://localhost:8501")
            return True
        else:
            print(f"❌ Streamlit server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Streamlit server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing Streamlit: {e}")
        return False

def start_services():
    """Start both services"""
    print("🚀 Starting services...")
    
    # Start FastAPI
    print("Starting FastAPI server...")
    try:
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], cwd=".")
        time.sleep(3)
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")
    
    # Start Streamlit
    print("Starting Streamlit server...")
    try:
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "swagger_frontend.py",
            "--server.port", "8501", "--server.headless", "true"
        ], cwd=".")
        time.sleep(5)
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

def main():
    print("🔍 Testing InsuraWise Services")
    print("=" * 40)
    
    # Test existing services
    fastapi_ok = test_fastapi()
    streamlit_ok = test_streamlit()
    
    if not fastapi_ok or not streamlit_ok:
        print("\n🔄 Starting services...")
        start_services()
        time.sleep(8)
        
        print("\n🔍 Testing again...")
        fastapi_ok = test_fastapi()
        streamlit_ok = test_streamlit()
    
    print("\n📋 Summary:")
    if fastapi_ok and streamlit_ok:
        print("✅ All services are running!")
        print("\n🌐 Access URLs:")
        print("   Swagger Frontend: http://localhost:8501")
        print("   FastAPI Backend: http://localhost:8000")
        print("   FastAPI Docs: http://localhost:8000/docs")
    else:
        print("❌ Some services failed to start")
        if not fastapi_ok:
            print("   - FastAPI server is not running")
        if not streamlit_ok:
            print("   - Streamlit server is not running")

if __name__ == "__main__":
    main() 