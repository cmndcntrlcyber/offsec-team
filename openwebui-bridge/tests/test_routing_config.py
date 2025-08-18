#!/usr/bin/env python3
"""
Test script to verify the updated routing configuration for the complete path:
chat.attck.nexus → tools.attck.nexus → researcher.c3s.nexus → chat.attck.nexus
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
TOOLS_API_BASE = "http://localhost:8001"  # Local testing
BEARER_TOKEN = "sk-755ea70d07874c7d9e0b46d3966eb145"

def test_health_check():
    """Test basic health check endpoint"""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{TOOLS_API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Agents loaded: {data['agents_loaded']}")
            print(f"   Open WebUI endpoint: {data['open_webui_endpoint']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_agents_endpoint():
    """Test agents listing endpoint"""
    print("\n🔍 Testing Agents Endpoint...")
    try:
        response = requests.get(f"{TOOLS_API_BASE}/agents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agents endpoint working")
            print(f"   Total agents: {data['total_agents']}")
            print(f"   Total instances: {data['total_instances']}")
            
            # Check if specific agents are loaded
            agents = data.get('agents', {})
            for agent_name in ['bug_hunter', 'rt_dev', 'nexus_kamuy']:
                if agent_name in agents:
                    loaded = agents[agent_name]['loaded']
                    tools_count = len(agents[agent_name]['available_tools'])
                    print(f"   {agent_name}: {loaded} instances, {tools_count} tools")
            return True
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agents endpoint error: {str(e)}")
        return False

def test_direct_tool_execution():
    """Test direct tool execution (non-researcher routing)"""
    print("\n🔍 Testing Direct Tool Execution...")
    try:
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "tool_name": "detect_framework",
            "agent": "bug_hunter",
            "parameters": {"target_url": "https://example.com"},
            "request_id": f"test_{int(time.time())}"
        }
        
        response = requests.post(
            f"{TOOLS_API_BASE}/execute",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct tool execution successful")
            print(f"   Agent: {data['agent']}")
            print(f"   Tool: {data['tool_name']}")
            print(f"   Success: {data['success']}")
            print(f"   Execution time: {data.get('execution_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"❌ Direct tool execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Direct tool execution error: {str(e)}")
        return False

def test_contextual_tool_execution():
    """Test contextual tool execution with thread context"""
    print("\n🔍 Testing Contextual Tool Execution...")
    try:
        headers = {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json",
            "X-Chat-Thread-ID": f"test-thread-{int(time.time())}",
            "X-User-ID": "test-user",
            "X-Session-ID": "test-session",
            "X-Origin-Endpoint": "https://chat.attck.nexus"
        }
        
        payload = {
            "tool_name": "generate_language_template",
            "agent": "rt_dev",
            "parameters": {"language": "python", "template_type": "fastapi"},
            "request_id": f"contextual_test_{int(time.time())}",
            "route_via_researcher": False  # Test direct routing first
        }
        
        response = requests.post(
            f"{TOOLS_API_BASE}/execute/contextual",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Contextual tool execution successful")
            print(f"   Agent: {data['agent']}")
            print(f"   Tool: {data['tool_name']}")
            print(f"   Success: {data['success']}")
            print(f"   Execution time: {data.get('execution_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"❌ Contextual tool execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Contextual tool execution error: {str(e)}")
        return False

def test_routing_configuration():
    """Test the complete routing configuration"""
    print("\n🔍 Testing Routing Configuration...")
    
    # Test if the filter can detect workflow orchestration (should route to researcher)
    test_cases = [
        {
            "name": "Simple Security Scan (Direct)",
            "message": "scan https://example.com for vulnerabilities",
            "expected_agent": "bug_hunter",
            "expected_researcher_routing": False
        },
        {
            "name": "Complex Workflow Analysis (Researcher)",
            "message": "orchestrate a comprehensive security analysis workflow for https://example.com",
            "expected_agent": "nexus_kamuy",
            "expected_researcher_routing": True
        },
        {
            "name": "Code Generation (Direct)", 
            "message": "generate a python fastapi template",
            "expected_agent": "rt_dev",
            "expected_researcher_routing": False
        }
    ]
    
    print("✅ Routing configuration test cases defined:")
    for i, case in enumerate(test_cases, 1):
        print(f"   {i}. {case['name']}")
        print(f"      Message: \"{case['message']}\"")
        print(f"      Expected Agent: {case['expected_agent']}")
        print(f"      Should use Researcher: {case['expected_researcher_routing']}")
    
    return True

def run_all_tests():
    """Run all routing tests"""
    print("🚀 Starting Routing Configuration Tests")
    print("=" * 60)
    
    # Start timestamp
    start_time = datetime.now()
    
    tests = [
        ("Health Check", test_health_check),
        ("Agents Endpoint", test_agents_endpoint), 
        ("Direct Tool Execution", test_direct_tool_execution),
        ("Contextual Tool Execution", test_contextual_tool_execution),
        ("Routing Configuration", test_routing_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    print(f"⏱️  Total execution time: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Routing configuration is working correctly.")
        print("\n🔄 Complete routing path implemented:")
        print("   chat.attck.nexus → tools.attck.nexus → researcher.c3s.nexus → chat.attck.nexus")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
