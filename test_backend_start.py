#!/usr/bin/env python3
"""
Test script to start the backend server correctly
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

try:
    print("🚀 Testing backend startup...")
    
    # Import and create the app
    from backend.app import create_app
    from backend.app.models.database import db_manager
    
    app = create_app('development')
    db_manager.init_app(app)
    
    print("✅ App created successfully")
    
    # List all API routes
    api_routes = []
    for rule in app.url_map.iter_rules():
        if '/api/' in str(rule):
            api_routes.append(str(rule))
    
    print(f"✅ Found {len(api_routes)} API routes:")
    for route in sorted(api_routes):
        print(f"  - {route}")
    
    print("\n🚀 Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()