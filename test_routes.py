#!/usr/bin/env python3
"""
Test script to verify backend routes are properly registered
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path('backend')
sys.path.insert(0, str(backend_dir))

from app import create_app

def test_routes():
    """Test that all routes are properly registered"""
    app = create_app('development')
    
    print("=" * 60)
    print("REGISTERED ROUTES")
    print("=" * 60)
    
    # Get all routes
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
                'path': str(rule)
            })
    
    # Sort by path
    routes.sort(key=lambda x: x['path'])
    
    # Print routes grouped by prefix
    current_prefix = None
    for route in routes:
        path = route['path']
        
        # Determine prefix
        if path.startswith('/api/'):
            prefix = path.split('/')[2] if len(path.split('/')) > 2 else 'api'
        else:
            prefix = 'root'
        
        # Print header for new prefix
        if prefix != current_prefix:
            print(f"\n{prefix.upper()}:")
            print("-" * 60)
            current_prefix = prefix
        
        # Print route
        methods = ', '.join(route['methods'])
        print(f"  {methods:10} {path}")
    
    print("\n" + "=" * 60)
    
    # Check for patients routes specifically
    patients_routes = [r for r in routes if '/patients' in r['path']]
    print(f"\nPATIENTS ROUTES FOUND: {len(patients_routes)}")
    for route in patients_routes:
        methods = ', '.join(route['methods'])
        print(f"  {methods:10} {route['path']}")
    
    print("=" * 60)

if __name__ == '__main__':
    test_routes()
