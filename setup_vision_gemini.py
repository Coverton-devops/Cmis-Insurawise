#!/usr/bin/env python3
"""
Setup script for InsuraWise Vision API + Gemini AI integration
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing required dependencies...")
    
    dependencies = [
        "google-cloud-vision",
        "google-generativeai", 
        "PyMuPDF",
        "Pillow",
        "pandas"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def verify_installation():
    """Verify that all required packages are installed"""
    print("\n🔍 Verifying installation...")
    
    try:
        import google.cloud.vision
        print("✅ Google Cloud Vision API - OK")
    except ImportError:
        print("❌ Google Cloud Vision API - Not installed")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI - OK")
    except ImportError:
        print("❌ Google Generative AI - Not installed")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF - OK")
    except ImportError:
        print("❌ PyMuPDF - Not installed")
        return False
    
    try:
        import PIL
        print("✅ Pillow - OK")
    except ImportError:
        print("❌ Pillow - Not installed")
        return False
    
    try:
        import pandas
        print("✅ Pandas - OK")
    except ImportError:
        print("❌ Pandas - Not installed")
        return False
    
    return True

def main():
    print("🚀 InsuraWise Vision API + Gemini AI Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the FastAPI backend: uvicorn main:app --reload")
    print("2. Start the Swagger frontend: python run_swagger_frontend.py")
    print("3. Access the frontend at: http://localhost:8501")
    print("4. Go to 'PDF Processing' section to test the new functionality")

if __name__ == "__main__":
    main() 