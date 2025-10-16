#!/usr/bin/env python3
"""Test if patients blueprint can be imported"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path('backend')
sys.path.insert(0, str(backend_dir))

try:
    print("Attempting to import patients blueprint...")
    from app.blueprints.patients import patients_bp
    print("✅ Patients blueprint imported successfully")
    print(f"Blueprint name: {patients_bp.name}")
    print(f"Blueprint import name: {patients_bp.import_name}")
    
    # Check if blueprint has routes
    if hasattr(patients_bp, 'deferred_functions'):
        print(f"Deferred functions: {len(patients_bp.deferred_functions)}")
    
except ImportError as e:
    print(f"❌ Failed to import patients blueprint: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
