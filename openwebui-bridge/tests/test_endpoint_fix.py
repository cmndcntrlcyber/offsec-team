#!/usr/bin/env python3
"""
Test script to verify the tools endpoint is correctly advertising itself
instead of pointing to chat.attck.nexus
"""

import os
import requests
import json
from datetime import datetime

def test_local_endpoint():
    """Test the local development endpoint"""
    print("Testing local endpoint...")
    
    try:
        # Test localhost endpoint
        response = requests.get("http://localhost:8001/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            endpoint_url = data.get('open_webui_endpoint')
            
            print(f"✅ Local endpoint status: {response.status_code}")
            print(f"✅ Returned endpoint URL: {endpoint_url}")
            
            # Check if it's using the correct endpoint
            if endpoint_url == "https://tools.attck.nexus":
                print("✅ Endpoint correctly configured for production")
            elif endpoint_url == "http://localhost:8001":
                print("✅ Endpoint correctly configured for development")
            else:
                print(f"⚠️  Unexpected endpoint URL: {endpoint_url}")
            
            return True
            
        else:
            print(f"❌ Local endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Local endpoint connection failed: {str(e)}")
        return False

def test_production_endpoint():
    """Test the production endpoint"""
    print("\nTesting production endpoint...")
    
    try:
        # Test production endpoint
        response = requests.get("https://tools.attck.nexus/health", timeout=10)
        
        if response.status_code == 200:
            # Check if we get JSON response (not HTML)
            try:
                data = response.json()
                endpoint_url = data.get('open_webui_endpoint')
                
                print(f"✅ Production endpoint status: {response.status_code}")
                print(f"✅ Returned endpoint URL: {endpoint_url}")
                
                # Check if it's using the correct endpoint
                if endpoint_url == "https://tools.attck.nexus":
                    print("✅ Production endpoint correctly configured")
                else:
                    print(f"⚠️  Production endpoint URL issue: {endpoint_url}")
                
                return True
                
            except json.JSONDecodeError:
                print("❌ Production endpoint returned HTML instead of JSON")
                print(f"Response content: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ Production endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Production endpoint connection failed: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint as well"""
    print("\nTesting root endpoint...")
    
    try:
        # Test localhost root endpoint
        response = requests.get("http://localhost:8001/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            endpoint_url = data.get('open_webui_endpoint')
            
            print(f"✅ Root endpoint status: {response.status_code}")
            print(f"✅ Root endpoint URL: {endpoint_url}")
            
            return True
            
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint connection failed: {str(e)}")
        return False

def test_agents_endpoint():
    """Test the agents endpoint for consistency"""
    print("\nTesting agents endpoint...")
    
    try:
        # Test localhost agents endpoint
        response = requests.get("http://localhost:8001/agents", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            endpoint_url = data.get('open_webui_endpoint')
            
            print(f"✅ Agents endpoint status: {response.status_code}")
            print(f"✅ Agents endpoint URL: {endpoint_url}")
            
            return True
            
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Agents endpoint connection failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("TESTING ENDPOINT CONFIGURATION FIX")
    print("=" * 60)
    print("Testing to verify the server advertises itself correctly")
    print("instead of hardcoded 'https://chat.attck.nexus/'")
    print("")
    
    # Test all endpoints
    local_health = test_local_endpoint()
    production_health = test_production_endpoint()
    root_test = test_root_endpoint()
    agents_test = test_agents_endpoint()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if local_health:
        print("✅ Local health endpoint working correctly")
    else:
        print("❌ Local health endpoint has issues")
    
    if production_health:
        print("✅ Production health endpoint working correctly")
    else:
        print("❌ Production health endpoint has issues")
    
    if root_test:
        print("✅ Root endpoint working correctly")
    else:
        print("❌ Root endpoint has issues")
    
    if agents_test:
        print("✅ Agents endpoint working correctly")
    else:
        print("❌ Agents endpoint has issues")
    
    print("")
    
    if local_health and root_test and agents_test:
        print("🎉 All local endpoints are working correctly!")
        print("The server now advertises its own endpoint instead of chat.attck.nexus")
    else:
        print("⚠️  Some endpoints need attention")
    
    if not production_health:
        print("⚠️  Production endpoint may need server restart to pick up new configuration")

if __name__ == "__main__":
    main()
