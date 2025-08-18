#!/usr/bin/env python3
"""
Test script for parallel request functionality in intelligent_routing_filter.py

This script tests the new simultaneous multi-endpoint request orchestrator.
"""

import json
import time
import requests
from typing import Dict, Any

def test_parallel_requests():
    """Test the parallel request functionality"""
    
    # Test configuration
    filter_url = "http://localhost:8001"  # tools.attck.nexus
    bearer_token = "sk-755ea70d07874c7d9e0b46d3966eb145"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "X-Chat-Thread-ID": f"test_thread_{int(time.time())}",
        "X-User-ID": "test_user",
        "X-Session-ID": f"test_session_{int(time.time())}",
        "X-Origin-Endpoint": "https://chat.attck.nexus"
    }
    
    # Test payload that should trigger parallel requests
    test_payload = {
        "tool_name": "detect_framework",
        "agent": "bug_hunter",
        "parameters": {
            "target_url": "https://example.com",
            "scan_depth": "medium"
        },
        "request_id": f"parallel_test_{int(time.time())}"
    }
    
    print("🚀 Testing Parallel Request Orchestrator")
    print("=" * 60)
    
    print(f"Test Configuration:")
    print(f"  - Filter URL: {filter_url}")
    print(f"  - Thread ID: {headers['X-Chat-Thread-ID']}")
    print(f"  - Agent: {test_payload['agent']}")
    print(f"  - Tool: {test_payload['tool_name']}")
    print()
    
    # Test 1: Check if server is running
    print("1. Checking server health...")
    try:
        response = requests.get(f"{filter_url}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Server healthy - {health_data.get('agents_loaded', 0)} agents loaded")
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server not reachable: {str(e)}")
        return False
    
    # Test 2: List available agents
    print("\n2. Checking available agents...")
    try:
        response = requests.get(f"{filter_url}/agents", headers=headers, timeout=10)
        if response.status_code == 200:
            agents_data = response.json()
            print(f"   ✅ Found {agents_data.get('total_agents', 0)} agent categories")
            
            # Check if our test agent exists
            agents = agents_data.get('agents', {})
            if 'bug_hunter' in agents:
                tools = agents['bug_hunter'].get('available_tools', [])
                print(f"   ✅ Bug Hunter has {len(tools)} available tools")
                
                if any('detect_framework' in tool for tool in tools):
                    print(f"   ✅ Target tool 'detect_framework' is available")
                else:
                    print(f"   ⚠️  Target tool 'detect_framework' not found in available tools")
            else:
                print(f"   ❌ Bug Hunter agent not found")
        else:
            print(f"   ❌ Failed to list agents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed to list agents: {str(e)}")
    
    # Test 3: Execute tool with parallel routing
    print("\n3. Executing tool with parallel routing...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{filter_url}/execute",
            headers=headers,
            json=test_payload,
            timeout=60  # Extended timeout for parallel requests
        )
        
        execution_time = time.time() - start_time
        print(f"   ⏱️  Total request time: {execution_time:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Request successful!")
            print(f"   📊 Response summary:")
            print(f"      - Success: {result.get('success', False)}")
            print(f"      - Agent: {result.get('agent', 'unknown')}")
            print(f"      - Tool: {result.get('tool_name', 'unknown')}")
            print(f"      - Execution time: {result.get('execution_time_ms', 0)}ms")
            
            # Check if this looks like a parallel response
            result_data = result.get('result', {})
            if isinstance(result_data, dict):
                if 'parallel_execution' in str(result_data):
                    print(f"   🚀 Parallel execution detected!")
                elif 'synthesis' in result_data:
                    print(f"   🧠 Multi-endpoint analysis detected!")
                elif 'combined_results' in result_data:
                    print(f"   📊 Combined results from multiple endpoints!")
                else:
                    print(f"   📝 Standard tool execution result")
            
            return True
            
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ⏱️  Request time before error: {execution_time:.2f}s")
        print(f"   ❌ Request failed with exception: {str(e)}")
        return False

def test_filter_simulation():
    """Simulate how the OpenWebUI filter would work"""
    
    print("\n" + "=" * 60)
    print("🎭 Simulating OpenWebUI Filter Request")
    print("=" * 60)
    
    # Simulate OpenWebUI message format
    openwebui_body = {
        "messages": [
            {
                "role": "user",
                "content": "Please scan https://example.com for vulnerabilities"
            }
        ],
        "model": "offsec-tools",
        "stream": False
    }
    
    print("Simulated OpenWebUI message:")
    print(json.dumps(openwebui_body, indent=2))
    print()
    
    # This would normally be processed by the intelligent_routing_filter.py inlet() method
    print("Expected filter processing:")
    print("1. ✅ Detect tool indicator: 'scan', 'vulnerabilities'")
    print("2. ✅ Detect intent: 'bug_hunter' (vulnerability scanning)")
    print("3. ✅ Select tool: 'test_injection_vulnerabilities'")
    print("4. ✅ Extract parameters: {'target_url': 'https://example.com', 'scan_depth': 'medium'}")
    print("5. ✅ Create thread context with UUID")
    print("6. 🚀 Execute parallel requests to:")
    print("   - tools.attck.nexus/execute")
    print("   - researcher.c3s.nexus/analyze")
    print("   - research-agent-mcp.attck-community.workers.dev/research")
    print("7. ✅ Aggregate responses and return formatted result")
    print()

if __name__ == "__main__":
    print("🧪 Parallel Request Orchestrator Test Suite")
    print("=" * 60)
    print()
    
    # Run the tests
    success = test_parallel_requests()
    test_filter_simulation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Parallel request testing completed successfully!")
        print("\nNext steps:")
        print("1. Deploy the updated intelligent_routing_filter.py to OpenWebUI")
        print("2. Test with actual chat messages at https://chat.attck.nexus")
        print("3. Monitor logs for parallel request execution")
        print("4. Verify multi-endpoint response aggregation")
    else:
        print("❌ Parallel request testing encountered issues")
        print("\nTroubleshooting steps:")
        print("1. Ensure tools.attck.nexus server is running on port 8001")
        print("2. Check network connectivity to all endpoints")
        print("3. Verify bearer token authentication")
        print("4. Review server logs for detailed error information")
    
    print("=" * 60)
