#!/usr/bin/env python3
"""
Test script to identify and resolve Cloudflare Access blocking OpenWebUI connection
"""

import os
import requests
import json
from datetime import datetime

def test_openapi_endpoint_directly():
    """Test the specific OpenAPI endpoint that OpenWebUI needs"""
    print("Testing direct OpenAPI endpoint access...")
    
    try:
        # Test the exact endpoint OpenWebUI is trying to access
        response = requests.get("https://tools.attck.nexus/openapi.json", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ OpenAPI endpoint returned valid JSON")
                print(f"✅ OpenAPI version: {data.get('openapi', 'Not specified')}")
                print(f"✅ Title: {data.get('info', {}).get('title', 'Not specified')}")
                return True
            except json.JSONDecodeError:
                print(f"❌ OpenAPI endpoint returned non-JSON content")
                print(f"Response content preview: {response.text[:200]}...")
                return False
        else:
            print(f"❌ OpenAPI endpoint failed with status {response.status_code}")
            if "cloudflare" in response.text.lower() or "access" in response.text.lower():
                print("❌ Detected Cloudflare Access blocking the request")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_with_different_headers():
    """Test with different headers to see if we can bypass Cloudflare Access"""
    print("\nTesting with different request headers...")
    
    headers_to_try = [
        {
            "User-Agent": "OpenWebUI/1.0",
            "Accept": "application/json"
        },
        {
            "User-Agent": "Mozilla/5.0 (compatible; OpenWebUI)",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
        {
            "User-Agent": "curl/7.68.0",
            "Accept": "*/*"
        }
    ]
    
    for i, headers in enumerate(headers_to_try, 1):
        print(f"  Attempt {i} with headers: {headers}")
        try:
            response = requests.get("https://tools.attck.nexus/openapi.json", headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response.json()
                    print(f"    ✅ Success with attempt {i}")
                    return headers
                except:
                    print(f"    ❌ Non-JSON response")
            else:
                print(f"    ❌ Failed")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
    
    return None

def test_alternative_paths():
    """Test alternative paths that might not be behind Cloudflare Access"""
    print("\nTesting alternative endpoint paths...")
    
    paths_to_try = [
        "/docs",  # FastAPI auto-generated docs
        "/redoc", # ReDoc documentation
        "/health", # Health endpoint
        "/",      # Root endpoint
        "/agents" # Agents listing
    ]
    
    working_paths = []
    
    for path in paths_to_try:
        try:
            response = requests.get(f"https://tools.attck.nexus{path}", timeout=10)
            print(f"  {path}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    if path in ["/health", "/", "/agents"]:
                        data = response.json()
                        print(f"    ✅ JSON response received")
                        working_paths.append(path)
                    else:
                        print(f"    ✅ HTML response received (documentation)")
                        working_paths.append(path)
                except:
                    if "cloudflare" not in response.text.lower():
                        print(f"    ✅ Non-JSON response received (likely HTML docs)")
                        working_paths.append(path)
                    else:
                        print(f"    ❌ Blocked by Cloudflare Access")
            else:
                print(f"    ❌ Failed")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
    
    return working_paths

def check_local_server_running():
    """Check if local server is running and could be used as temporary solution"""
    print("\nChecking local server availability...")
    
    try:
        response = requests.get("http://localhost:8001/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Local server is running and serving OpenAPI spec")
            print("✅ This could be used as a temporary solution")
            return True
        else:
            print(f"❌ Local server responded with status {response.status_code}")
            return False
    except:
        print("❌ Local server is not running")
        return False

def generate_solutions():
    """Generate potential solutions based on test results"""
    print("\n" + "="*60)
    print("POTENTIAL SOLUTIONS")
    print("="*60)
    
    print("\n1. LOCAL DEVELOPMENT SOLUTION:")
    print("   - Start the FastAPI server locally: cd ../offsec-team/openwebui-bridge && python main.py")
    print("   - Configure OpenWebUI to use: http://localhost:8001/openapi.json")
    print("   - This bypasses Cloudflare Access entirely")
    
    print("\n2. CLOUDFLARE ACCESS BYPASS OPTIONS:")
    print("   - Add OpenWebUI's IP to Cloudflare Access bypass rules")
    print("   - Create a bypass rule for /openapi.json endpoint specifically")
    print("   - Use a service token for programmatic access")
    
    print("\n3. ALTERNATIVE ENDPOINT HOSTING:")
    print("   - Host the OpenAPI spec on a different subdomain without Access")
    print("   - Use a CDN or static hosting for the openapi.json file")
    print("   - Implement a public proxy endpoint for the OpenAPI spec")
    
    print("\n4. NGINX CONFIGURATION (if applicable):")
    print("   - Configure nginx to serve openapi.json without authentication")
    print("   - Add specific location block for OpenAPI endpoint")

def main():
    """Main test function"""
    print("=" * 60)
    print("CLOUDFLARE ACCESS BYPASS TESTING")
    print("=" * 60)
    print("Diagnosing why OpenWebUI cannot connect to tools.attck.nexus")
    print("")
    
    # Run all tests
    openapi_works = test_openapi_endpoint_directly()
    bypass_headers = test_with_different_headers()
    working_paths = test_alternative_paths()
    local_available = check_local_server_running()
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    if openapi_works:
        print("✅ Production OpenAPI endpoint is accessible")
    else:
        print("❌ Production OpenAPI endpoint is blocked by Cloudflare Access")
    
    if bypass_headers:
        print(f"✅ Found working headers: {bypass_headers}")
    else:
        print("❌ No header combinations bypass Cloudflare Access")
    
    if working_paths:
        print(f"✅ Alternative paths working: {working_paths}")
    else:
        print("❌ All paths appear to be behind Cloudflare Access")
    
    if local_available:
        print("✅ Local server is available as backup solution")
    else:
        print("❌ Local server is not running")
    
    # Generate solutions
    generate_solutions()

if __name__ == "__main__":
    main()
