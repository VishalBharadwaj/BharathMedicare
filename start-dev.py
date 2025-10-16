#!/usr/bin/env python3
"""
Development startup script for Medical Records System
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_services():
    """Check if required services are running"""
    services_ok = True
    
    # Check MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB is running")
        client.close()
    except Exception:
        print("❌ MongoDB is not running. Please start MongoDB first.")
        services_ok = False

    
    return services_ok

def start_backend():
    """Start the Flask backend"""
    print("🚀 Starting Flask backend...")
    backend_dir = Path('backend')
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    # Start Flask app
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    env['PYTHONPATH'] = str(backend_dir.absolute())
    
    process = subprocess.Popen([
        sys.executable, 'run.py'
    ], cwd=backend_dir, env=env)
    
    return process

def start_frontend_server():
    """Start a simple HTTP server for frontend"""
    print("🌐 Starting frontend server...")
    frontend_dir = Path('frontend')
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Start simple HTTP server
    process = subprocess.Popen([
        sys.executable, '-m', 'http.server', '3000'
    ], cwd=frontend_dir)
    
    return process

def main():
    """Main function"""
    print("🏥 Medical Records System - Development Startup")
    print("=" * 50)
    
    # Check if services are running
    if not check_services():
        print("\n❌ Required services are not running.")
        print("Please start MongoDB and Redis, then try again.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        sys.exit(1)
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend server
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        backend_process.terminate()
        sys.exit(1)
    
    # Wait a moment for frontend to start
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎉 Medical Records System is running!")
    print("=" * 50)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:5000")
    print("📚 API Docs: http://localhost:5000/api")
    print("\nPress Ctrl+C to stop all services")
    print("=" * 50)
    
    # Open browser
    try:
        webbrowser.open('http://localhost:3000')
    except:
        pass
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ Services stopped successfully")

if __name__ == '__main__':
    main()