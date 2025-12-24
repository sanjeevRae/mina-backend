#!/usr/bin/env python3
"""
Quick start script for the Telemedicine Backend
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Main quick start function"""
    print("🚀 Telemedicine Backend Quick Start")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return
    
    # Check if .env exists
    if not Path(".env").exists():
        print("📋 Creating .env file from template...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env file created. Please edit it with your configurations.")
        else:
            print("⚠️  .env.example not found. You'll need to create .env manually.")
    
    # Initialize database
    if not run_command("python setup_db.py", "Setting up database"):
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("3. Access API at: http://localhost:8000")
    print("4. View docs at: http://localhost:8000/docs")
    
    print("\n🔑 Sample credentials:")
    print("Admin: admin@telemedicine.com / admin123")
    print("Doctor: doctor@telemedicine.com / doctor123")
    print("Patient: patient@telemedicine.com / patient123")
    
    # Ask if user wants to start the server
    response = input("\n🚀 Start the development server now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n🔄 Starting development server...")
        print("Press Ctrl+C to stop the server")
        os.system("uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")


if __name__ == "__main__":
    main()