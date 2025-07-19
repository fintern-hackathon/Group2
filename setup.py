#!/usr/bin/env python3
"""
FinTree API Setup Script
Simple setup and removal for development environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=shell, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_project():
    """Setup the FinTree project"""
    print("🌳 FinTree API Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment
    print("\n📦 Creating virtual environment...")
    success, output = run_command("python -m venv venv")
    if not success:
        print(f"❌ Failed to create venv: {output}")
        return False
    print("✅ Virtual environment created")
    
    # Activate venv and install dependencies
    print("\n📥 Installing dependencies...")
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    # Install requirements
    success, output = run_command(f"{pip_path} install fastapi uvicorn sqlalchemy aiosqlite python-multipart pydantic email-validator google-generativeai requests")
    if not success:
        print(f"❌ Failed to install dependencies: {output}")
        return False
    print("✅ Dependencies installed")
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    success, output = run_command(f"{python_path} -c \"import asyncio; from app.database.connection import init_db; asyncio.run(init_db())\"")
    if success:
        print("✅ Database initialized")
    else:
        print("⚠️ Database may already exist")
    
    # Load sample data if JSON exists
    if os.path.exists("ekstre_dataset_realistic_4_months_final_clean.json"):
        print("\n📊 Loading sample data...")
        success, output = run_command(f"{python_path} load_data.py")
        if success:
            print("✅ Sample data loaded")
        else:
            print("⚠️ Sample data loading failed (may already exist)")
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 Start the server:")
    if os.name == 'nt':
        print("   venv\\Scripts\\python working_main.py")
    else:
        print("   venv/bin/python working_main.py")
    
    print("\n📚 API Documentation: http://localhost:8002/docs")
    return True

def remove_project():
    """Remove the FinTree project completely"""
    print("🗑️ FinTree API Removal")
    print("=" * 50)
    
    # Confirm removal
    confirm = input("⚠️ This will remove ALL project files. Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Removal cancelled")
        return False
    
    current_dir = Path.cwd()
    parent_dir = current_dir.parent
    project_name = current_dir.name
    
    print(f"\n🔥 Removing project directory: {current_dir}")
    
    try:
        # Go to parent directory
        os.chdir(parent_dir)
        
        # Remove the entire project directory
        shutil.rmtree(current_dir, ignore_errors=True)
        
        print(f"✅ Project '{project_name}' removed successfully")
        print("📍 You are now in:", parent_dir)
        return True
        
    except Exception as e:
        print(f"❌ Removal failed: {e}")
        return False

def main():
    """Main setup script"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "remove":
            remove_project()
        elif sys.argv[1] == "setup":
            setup_project()
        else:
            print("Usage: python setup.py [setup|remove]")
    else:
        print("FinTree API Setup & Removal")
        print("=" * 30)
        print("1. Setup project: python setup.py setup")
        print("2. Remove project: python setup.py remove")

if __name__ == "__main__":
    main() 