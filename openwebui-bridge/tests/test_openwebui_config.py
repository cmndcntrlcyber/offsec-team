#!/usr/bin/env python3
"""
Test script to verify OpenWebUI configuration endpoint is working correctly.

This script tests the new /OPEN_WEBUI_CONFIG.js endpoint to ensure it resolves
the connection error that OpenWebUI was experiencing.
"""

import requests
import json
from typing import Dict, Any

def test_openwebui_config_endpoint():
    """Test the OpenWebUI configuration endpoint"""
    
    # Test configuration
    config_url = "https://tools.attck.nexus/OPEN_WEBUI_CONFIG.js"
    fallback_url = "http://localhost:3000/OPEN_WEBUI_CONFIG.js"  # For local testing
    
    print("🧪 Testing OpenWebUI Configuration Endpoint")
    print("=" * 60)
    
    # Test 1: Try the production endpoint
    print("1. Testing production endpoint...")
    try:
        response = requests.get(config_url, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Production endpoint successful: {response.status_code}")
            print(f"   📄 Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            print(f"   🔒 CORS Headers: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
            
            # Verify content format
            content = response.text
            if content.startswith('window.OPEN_WEBUI_CONFIG = '):
                print(f"   ✅ Correct JavaScript format detected")
                
                # Extract JSON from JavaScript
                json_start = content.find('{')
                json_end = content.rfind(';}')
                if json_start > 0 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    try:
                        config_data = json.loads(json_content)
                        print(f"   ✅ Valid JSON configuration parsed")
                        
                        # Check key configuration elements
                        if 'agent_tool_bridge' in config_data:
                            bridge_config = config_data['agent_tool_bridge']
                            print(f"   📊 Bridge URL: {bridge_config.get('url', 'Not set')}")
                            print(f"   🔧 Available endpoints: {list(bridge_config.get('endpoints', {}).keys())}")
                            
                            if bridge_config.get('url') == 'https://tools.attck.nexus':
                                print(f"   ✅ Correct production URL configured")
                                return True
                            else:
                                print(f"   ⚠️  URL mismatch - expected https://tools.attck.nexus")
                        else:
                            print(f"   ❌ Missing agent_tool_bridge configuration")
                    except json.JSONDecodeError as e:
                        print(f"   ❌ Invalid JSON in configuration: {e}")
                else:
                    print(f"   ❌ Could not extract JSON from JavaScript")
            else:
                print(f"   ❌ Incorrect format - should start with 'window.OPEN_WEBUI_CONFIG = '")
                print(f"   📄 Actual content start: {content[:100]}...")
        else:
            print(f"   ❌ Production endpoint failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Production endpoint connection error: {str(e)}")
    
    # Test 2: Try local fallback endpoint
    print("\n2. Testing local fallback endpoint...")
    try:
        response = requests.get(fallback_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Local endpoint successful: {response.status_code}")
            return True
        else:
            print(f"   ❌ Local endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Local endpoint connection error: {str(e)}")
    
    return False

def test_cors_preflight():
    """Test CORS preflight request"""
    
    print("\n3. Testing CORS preflight request...")
    config_url = "https://tools.attck.nexus/OPEN_WEBUI_CONFIG.js"
    
    try:
        # Send OPTIONS request to test CORS preflight
        response = requests.options(config_url, timeout=5)
        if response.status_code == 200:
            print(f"   ✅ CORS preflight successful: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   🔒 {header}: {value}")
                else:
                    print(f"   ⚠️  {header}: Not set")
            
            return True
        else:
            print(f"   ❌ CORS preflight failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CORS preflight error: {str(e)}")
    
    return False

def simulate_openwebui_request():
    """Simulate how OpenWebUI would request the configuration"""
    
    print("\n4. Simulating OpenWebUI request...")
    config_url = "https://tools.attck.nexus/OPEN_WEBUI_CONFIG.js"
    
    # Headers that OpenWebUI might send
    headers = {
        'User-Agent': 'Mozilla/5.0 (OpenWebUI Configuration Loader)',
        'Accept': 'application/javascript, text/javascript, */*',
        'Origin': 'https://chat.attck.nexus',
        'Referer': 'https://chat.attck.nexus/',
    }
    
    try:
        response = requests.get(config_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ OpenWebUI simulation successful: {response.status_code}")
            print(f"   📏 Content length: {len(response.text)} bytes")
            
            # Verify the response can be processed as expected
            content = response.text
            if 'window.OPEN_WEBUI_CONFIG' in content and 'agent_tool_bridge' in content:
                print(f"   ✅ Configuration structure verified")
                return True
            else:
                print(f"   ❌ Configuration structure invalid")
        else:
            print(f"   ❌ OpenWebUI simulation failed: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ OpenWebUI simulation error: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🔧 OpenWebUI Configuration Endpoint Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    tests = [
        ("Configuration Endpoint", test_openwebui_config_endpoint),
        ("CORS Preflight", test_cors_preflight),
        ("OpenWebUI Simulation", simulate_openwebui_request),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} Test: PASSED")
            else:
                print(f"❌ {test_name} Test: FAILED")
        except Exception as e:
            print(f"❌ {test_name} Test: ERROR - {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ All tests passed! OpenWebUI configuration endpoint is working correctly.")
        print("\n🎉 The connection error should now be resolved!")
        print("\nNext steps:")
        print("1. Restart the tools.attck.nexus server if needed")
        print("2. Try connecting from OpenWebUI again")
        print("3. The configuration should now load successfully")
    elif passed_tests > 0:
        print("⚠️  Some tests passed, but there may be issues to resolve.")
        print("Check the failed tests above for specific problems.")
    else:
        print("❌ All tests failed. The configuration endpoint needs attention.")
        print("\nTroubleshooting steps:")
        print("1. Ensure tools.attck.nexus server is running")
        print("2. Check network connectivity")
        print("3. Verify the /OPEN_WEBUI_CONFIG.js route is properly registered")
        print("4. Check server logs for detailed error information")
    
    print("=" * 60)
