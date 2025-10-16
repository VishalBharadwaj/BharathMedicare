#!/usr/bin/env python3
"""
Test script to verify server can start properly
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    print("Testing server startup...")
    from app import create_app
    
    app = create_app('development')
    print("✅ App created successfully")
    
    # Test if all blueprints are registered
    routes = []
    for rule in app.url_map.iter_rules():
        if '/api/' in str(rule):
            routes.append(str(rule))
    
    print(f"✅ Found {len(routes)} API routes:")
    for route in sorted(routes):
        print(f"  - {route}")
    
    # Test if we can access the database (without actually connecting)
    print(f"✅ MongoDB URI: {app.config['MONGODB_URI']}")
    print(f"✅ Redis URL: {app.config['REDIS_URL']}")
    
    print("\n🚀 Server should be ready to start!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()