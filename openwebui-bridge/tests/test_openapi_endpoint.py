#!/usr/bin/env python3
"""
Test script to validate OpenAPI endpoint for OpenWebUI integration
"""

import json
import requests
from pathlib import Path

def test_openapi_json_file():
    """Test that the OpenAPI JSON file is valid"""
    openapi_file = Path(__file__).parent / "openapi.json"
    
    print("🔍 Testing OpenAPI JSON file...")
    
    if not openapi_file.exists():
        print(f"❌ OpenAPI file not found: {openapi_file}")
        return False
    
    try:
        with open(openapi_file, 'r') as f:
            openapi_spec = json.load(f)
        
        # Validate basic OpenAPI structure
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            if field not in openapi_spec:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check OpenAPI version
        if not openapi_spec["openapi"].startswith("3."):
            print(f"❌ Invalid OpenAPI version: {openapi_spec['openapi']}")
            return False
        
        # Check for essential endpoints
        essential_paths = ["/", "/health", "/agents", "/execute"]
        for path in essential_paths:
            if path not in openapi_spec["paths"]:
                print(f"❌ Missing essential path: {path}")
                return False
        
        # Check execute endpoint has proper structure
        execute_path = openapi_spec["paths"]["/execute"]
        if "post" not in execute_path:
            print("❌ Execute endpoint missing POST method")
            return False
        
        print("✅ OpenAPI JSON file is valid")
        print(f"   - OpenAPI version: {openapi_spec['openapi']}")
        print(f"   - Title: {openapi_spec['info']['title']}")
        print(f"   - Version: {openapi_spec['info']['version']}")
        print(f"   - Paths: {len(openapi_spec['paths'])}")
        print(f"   - Servers: {len(openapi_spec.get('servers', []))}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return False
    except Exception as e:
        print(f"❌ Error validating OpenAPI file: {e}")
        return False

def test_openapi_endpoint():
    """Test the /openapi.json endpoint"""
    print("\n🌐 Testing OpenAPI endpoint...")
    
    endpoints = [
        "http://localhost:8001/openapi.json",
        "https://tools.attck.nexus/openapi.json"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ✅ Content-Type: {response.headers.get('content-type')}")
                
                # Validate JSON response
                try:
                    openapi_data = response.json()
                    if "openapi" in openapi_data and "info" in openapi_data:
                        print(f"   ✅ Valid OpenAPI response")
                        print(f"   📋 Title: {openapi_data['info']['title']}")
                        print(f"   📋 Paths: {len(openapi_data.get('paths', {}))}")
                    else:
                        print(f"   ⚠️  Response doesn't look like OpenAPI spec")
                except json.JSONDecodeError:
                    print(f"   ❌ Response is not valid JSON")
            else:
                print(f"   ❌ Status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except requests.ConnectionError:
            print(f"   ⚠️  Could not connect to {endpoint}")
        except requests.Timeout:
            print(f"   ⚠️  Timeout connecting to {endpoint}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_openwebui_integration():
    """Test OpenWebUI integration setup"""
    print("\n🔧 Testing OpenWebUI Integration Setup...")
    
    # Check if backup was created
    backup_file = Path(__file__).parent / "OPEN_WEBUI_CONFIG.json.backup"
    if backup_file.exists():
        print("✅ Backup of original config created")
    else:
        print("⚠️  No backup of original config found")
    
    # Check if new openapi.json exists
    openapi_file = Path(__file__).parent / "openapi.json"
    if openapi_file.exists():
        print("✅ New openapi.json file created")
    else:
        print("❌ OpenAPI JSON file missing")
    
    # Check if old config still exists (shouldn't after rename)
    old_config = Path(__file__).parent / "OPEN_WEBUI_CONFIG.json"
    if old_config.exists():
        print("⚠️  Old OPEN_WEBUI_CONFIG.json still exists")
        with open(old_config, 'r') as f:
            content = f.read()
            if '"openapi"' in content:
                print("   ✅ File appears to contain OpenAPI spec")
            else:
                print("   ⚠️  File appears to contain old custom format")
    else:
        print("✅ Old config file properly renamed")

if __name__ == "__main__":
    print("🧪 OpenAPI Endpoint Validation Suite")
    print("=" * 50)
    
    # Run tests
    file_valid = test_openapi_json_file()
    test_openapi_endpoint()
    test_openwebui_integration()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"   OpenAPI file: {'✅ Valid' if file_valid else '❌ Invalid'}")
    print("   Next steps:")
    print("   1. Update OpenWebUI to use: https://tools.attck.nexus/openapi.json")
    print("   2. Remove old URL reference if any")
    print("   3. Test tool discovery in OpenWebUI interface")
    print("   4. Verify cybersecurity tools are accessible")
    print("=" * 50)
