#!/usr/bin/env python3
"""
Script to run the InsuraWise Swagger Frontend
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting InsuraWise Swagger Frontend...")
    print("📋 This will display JSON body information and API documentation")
    print("🌐 The frontend will be available at: http://localhost:8501")
    print("🔗 Make sure the FastAPI backend is running at: http://localhost:8000")
    print("-" * 60)
    
    try:
        # Change to the InsuraWise directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "swagger_frontend.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 Swagger frontend stopped by user")
    except Exception as e:
        print(f"❌ Error running Swagger frontend: {e}")

if __name__ == "__main__":
    main() 