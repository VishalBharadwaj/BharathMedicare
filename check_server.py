#!/usr/bin/env python3
"""Check if backend server is running and what routes are available"""

import requests
import json

def check_server():
    base_url = "http://localhost:5000"
    
    print("=" * 60)
    print("CHECKING BACKEND SERVER")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        print(f"✅ Server is running")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is NOT running on localhost:5000")
        print("   Please start the backend server first")
        return
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return
    
    print("\n" + "=" * 60)
    print("CHECKING AVAILABLE ROUTES")
    print("=" * 60)
    
    # Check debug routes endpoint
    try:
        response = requests.get(f"{base_url}/debug/routes", timeout=2)
        if response.status_code == 200:
            data = response.json()
            routes = data.get('routes', [])
            
            # Filter for patients routes
            patients_routes = [r for r in routes if '/patients' in r.get('rule', '')]
            
            print(f"\nTotal routes: {len(routes)}")
            print(f"Patients routes: {len(patients_routes)}")
            
            if patients_routes:
                print("\nPATIENTS ROUTES:")
                for route in patients_routes:
                    methods = ', '.join(route.get('methods', []))
                    print(f"  {methods:15} {route.get('rule')}")
            else:
                print("\n❌ NO PATIENTS ROUTES FOUND!")
                print("   The patients blueprint may not be registered")
        else:
            print(f"❌ Failed to get routes: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting routes: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING PATIENTS ENDPOINTS")
    print("=" * 60)
    
    # Test patients test endpoint (no auth required)
    try:
        response = requests.get(f"{base_url}/api/patients/test", timeout=2)
        print(f"\nGET /api/patients/test")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ Response: {response.json()}")
        else:
            print(f"  ❌ Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test patients list endpoint (requires auth)
    try:
        response = requests.get(f"{base_url}/api/patients/", timeout=2)
        print(f"\nGET /api/patients/")
        print(f"  Status: {response.status_code}")
        if response.status_code == 401:
            print(f"  ✅ Endpoint exists (requires authentication)")
        elif response.status_code == 404:
            print(f"  ❌ Endpoint NOT FOUND")
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_server()
