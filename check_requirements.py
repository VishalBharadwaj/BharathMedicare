#!/usr/bin/env python3
"""
Check if all required packages are installed
"""

import sys
import importlib

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def main():
    """Check all required packages"""
    print("🔍 Checking required packages...")
    print("-" * 40)
    
    packages = [
        ('Flask', 'flask'),
        ('Flask-JWT-Extended', 'flask_jwt_extended'),
        ('Flask-CORS', 'flask_cors'),
        ('PyMongo', 'pymongo'),
        ('Redis', 'redis'),
        ('bcrypt', 'bcrypt'),
        ('cryptography', 'cryptography'),
        ('python-dotenv', 'dotenv'),
        ('marshmallow', 'marshmallow'),
        ('pytest', 'pytest'),
        ('pytest-flask', 'pytest_flask'),
        ('gunicorn', 'gunicorn'),
        ('Werkzeug', 'werkzeug'),
        ('PyOTP', 'pyotp'),
        ('qrcode', 'qrcode'),
        ('bson', 'bson')
    ]
    
    missing = []
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            missing.append(package_name)
    
    print("-" * 40)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nTo install missing packages, run:")
        print("pip install -r backend/requirements.txt")
        return False
    else:
        print("🎉 All required packages are installed!")
        return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)