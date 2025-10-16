#!/usr/bin/env python3
"""
Medical Records Management System - Setup Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = ['pip', 'git']
    missing = []
    
    for dep in dependencies:
        if not shutil.which(dep):
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Please install the missing dependencies and try again")
        sys.exit(1)
    
    print("✅ System dependencies check passed")

def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'uploads',
        'backend/logs',
        'backend/uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")

def setup_environment():
    """Setup environment file"""
    env_example = Path('backend/.env.example')
    env_file = Path('backend/.env')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("⚠️  Please edit backend/.env with your configuration")
    else:
        print("ℹ️  Environment file already exists")

def install_python_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing Python dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'
        ], check=True, capture_output=True)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        sys.exit(1)

def check_mongodb():
    """Check if MongoDB is available"""
    try:
        import pymongo
        # Try to connect to default MongoDB instance
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB connection successful")
        client.close()
    except Exception:
        print("⚠️  MongoDB not detected. Please ensure MongoDB is installed and running")
        print("   Installation guide: https://docs.mongodb.com/manual/installation/")

def check_redis():
    """Check if Redis is available"""
    try:
        import redis
        # Try to connect to default Redis instance
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
        print("✅ Redis connection successful")
    except Exception:
        print("⚠️  Redis not detected. Please ensure Redis is installed and running")
        print("   Installation guide: https://redis.io/download")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Configure your database connections in backend/.env")
    print("2. Start MongoDB and Redis services")
    print("3. Run the application:")
    print("   cd backend && python run.py")
    print("\n4. Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")
    print("\n5. Create your first admin user through the registration page")
    print("\nFor more information, see README.md")

def main():
    """Main setup function"""
    print("🏥 Medical Records Management System - Setup")
    print("="*50)
    
    check_python_version()
    check_dependencies()
    create_directories()
    setup_environment()
    install_python_dependencies()
    check_mongodb()
    check_redis()
    print_next_steps()

if __name__ == '__main__':
    main()