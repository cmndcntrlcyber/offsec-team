#!/usr/bin/env python3
"""
Comprehensive streaming functionality test for offsec-team infrastructure.

This script tests:
- FastAPI backend streaming endpoints
- Tools service streaming execution
- WebSocket real-time communication
- End-to-end streaming flow
"""

import asyncio
import aiohttp
import websockets
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

class StreamingTester:
    def __init__(self):
        self.base_urls = {
            "backend": "http://localhost:8001",
            "tools": "http://localhost:8001",  # Tools service runs on same port for testing
            "worker": "https://offsec-team.attck.community.workers.dev"
        }
        self.test_results = []
        self.session_id = f"test_session_{int(time.time())}"
        
    async def test_backend_streaming(self) -> Dict[str, Any]:
        """Test FastAPI backend streaming endpoint"""
        print("🧪 Testing FastAPI backend streaming...")
        
        test_request = {
            "tool_name": "enhanced_web_search",
            "agent": "bug_hunter",
            "parameters": {
                "query": "test streaming functionality",
                "max_results": 5
            },
            "request_id": f"test_backend_{int(time.time())}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_urls['backend']}/execute/stream",
                    json=test_request,
                    headers={"Authorization": "Bearer test_token"}
                ) as response:
                    
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
                    
                    chunks_received = []
                    start_time = time.time()
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                chunk_data = json.loads(line_str[6:])
                                chunks_received.append(chunk_data)
                                print(f"  📦 Received chunk: {chunk_data.get('type')} - {chunk_data.get('data', {}).get('message', 'No message')}")
                                
                                # Break on completion
                                if chunk_data.get('type') == 'complete':
                                    break
                                    
                            except json.JSONDecodeError:
                                print(f"  ⚠️ Failed to parse chunk: {line_str}")
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "chunks_received": len(chunks_received),
                        "execution_time": execution_time,
                        "final_chunk": chunks_received[-1] if chunks_received else None
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_tools_service_streaming(self) -> Dict[str, Any]:
        """Test tools service streaming endpoint"""
        print("🔧 Testing Tools service streaming...")
        
        test_request = {
            "tool_name": "get_research_infrastructure_status",
            "agent": "nexus_kamuy",
            "parameters": {},
            "request_id": f"test_tools_{int(time.time())}",
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_urls['tools']}/execute/stream",
                    json=test_request
                ) as response:
                    
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
                    
                    chunks_received = []
                    start_time = time.time()
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                chunk_data = json.loads(line_str[6:])
                                chunks_received.append(chunk_data)
                                print(f"  📦 Tools chunk: {chunk_data.get('type')} - {chunk_data.get('data', {}).get('message', 'No message')}")
                                
                                # Break on completion
                                if chunk_data.get('type') == 'complete':
                                    break
                                    
                            except json.JSONDecodeError:
                                print(f"  ⚠️ Failed to parse tools chunk: {line_str}")
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "chunks_received": len(chunks_received),
                        "execution_time": execution_time,
                        "final_chunk": chunks_received[-1] if chunks_received else None
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_websocket_connection(self) -> Dict[str, Any]:
        """Test WebSocket real-time communication"""
        print("🔌 Testing WebSocket connection...")
        
        websocket_url = f"ws://localhost:8001/ws/{self.session_id}"
        
        try:
            async with websockets.connect(websocket_url) as websocket:
                print("  ✅ WebSocket connected successfully")
                
                # Send ping message
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(ping_message))
                
                # Wait for pong response
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong_response)
                
                if pong_data.get("type") == "pong":
                    print("  ✅ Ping/Pong successful")
                
                # Test tool execution via WebSocket
                tool_execution_message = {
                    "type": "tool_execution",
                    "tool_name": "enhanced_web_search",
                    "agent": "bug_hunter",
                    "parameters": {
                        "query": "websocket test",
                        "max_results": 3
                    },
                    "request_id": f"ws_test_{int(time.time())}"
                }
                
                await websocket.send(json.dumps(tool_execution_message))
                print("  📤 Sent tool execution request via WebSocket")
                
                # Collect streaming responses
                messages_received = []
                start_time = time.time()
                
                try:
                    while True:
                        message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        message_data = json.loads(message)
                        messages_received.append(message_data)
                        
                        print(f"  📨 WebSocket message: {message_data.get('type')} - {message_data.get('chunk_data', {}).get('type', 'N/A') if message_data.get('type') == 'tool_stream_chunk' else message_data.get('type')}")
                        
                        # Break on tool execution completion
                        if message_data.get("type") == "tool_execution_completed":
                            break
                            
                except asyncio.TimeoutError:
                    print("  ⏰ WebSocket timeout - ending test")
                
                execution_time = time.time() - start_time
                
                return {
                    "success": True,
                    "messages_received": len(messages_received),
                    "execution_time": execution_time,
                    "ping_pong_works": pong_data.get("type") == "pong"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_worker_streaming(self) -> Dict[str, Any]:
        """Test Cloudflare Worker streaming endpoint"""
        print("☁️ Testing Cloudflare Worker streaming...")
        
        test_request = {
            "tool_name": "multi_agent_vulnerability_assessment",
            "agent": "bug_hunter",
            "parameters": {
                "target_url": "https://example.com",
                "assessment_depth": "basic"
            },
            "request_id": f"test_worker_{int(time.time())}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_urls['worker']}/execute/stream",
                    json=test_request,
                    headers={"Authorization": "Bearer test_token"}
                ) as response:
                    
                    if response.status != 200:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {await response.text()}"
                        }
                    
                    chunks_received = []
                    start_time = time.time()
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                chunk_data = json.loads(line_str[6:])
                                chunks_received.append(chunk_data)
                                print(f"  📦 Worker chunk: {chunk_data.get('type')} - {chunk_data.get('data', {}).get('message', 'No message')}")
                                
                                # Break on completion
                                if chunk_data.get('type') == 'complete':
                                    break
                                    
                            except json.JSONDecodeError:
                                print(f"  ⚠️ Failed to parse worker chunk: {line_str}")
                    
                    execution_time = time.time() - start_time
                    
                    return {
                        "success": True,
                        "chunks_received": len(chunks_received),
                        "execution_time": execution_time,
                        "final_chunk": chunks_received[-1] if chunks_received else None
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive streaming functionality test"""
        print("🚀 Starting comprehensive streaming functionality test...")
        print(f"📋 Session ID: {self.session_id}")
        print("=" * 60)
        
        test_suite = [
            ("Backend Streaming", self.test_backend_streaming),
            ("Tools Service Streaming", self.test_tools_service_streaming),
            ("WebSocket Communication", self.test_websocket_connection),
            ("Worker Streaming", self.test_worker_streaming)
        ]
        
        results = {}
        overall_success = True
        
        for test_name, test_func in test_suite:
            print(f"\n🧪 Running {test_name}...")
            try:
                result = await test_func()
                results[test_name] = result
                
                if result["success"]:
                    print(f"  ✅ {test_name} PASSED")
                    if "execution_time" in result:
                        print(f"     ⏱️ Execution time: {result['execution_time']:.2f}s")
                    if "chunks_received" in result:
                        print(f"     📊 Chunks received: {result['chunks_received']}")
                else:
                    print(f"  ❌ {test_name} FAILED: {result.get('error', 'Unknown error')}")
                    overall_success = False
                    
            except Exception as e:
                print(f"  💥 {test_name} CRASHED: {str(e)}")
                results[test_name] = {"success": False, "error": str(e)}
                overall_success = False
        
        # Generate summary report
        print("\n" + "=" * 60)
        print("📊 STREAMING FUNCTIONALITY TEST RESULTS")
        print("=" * 60)
        
        passed_tests = sum(1 for result in results.values() if result["success"])
        total_tests = len(results)
        
        print(f"🎯 Overall Result: {'PASSED' if overall_success else 'FAILED'}")
        print(f"📈 Success Rate: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        print(f"🕐 Test Session: {self.session_id}")
        print(f"⏰ Test Time: {datetime.utcnow().isoformat()}")
        
        print("\n📋 Detailed Results:")
        for test_name, result in results.items():
            status_icon = "✅" if result["success"] else "❌"
            print(f"{status_icon} {test_name}")
            
            if result["success"]:
                if "execution_time" in result:
                    print(f"   ⏱️ Time: {result['execution_time']:.2f}s")
                if "chunks_received" in result:
                    print(f"   📊 Chunks: {result['chunks_received']}")
            else:
                print(f"   💥 Error: {result.get('error', 'Unknown')}")
        
        if overall_success:
            print("\n🎉 All streaming functionality tests PASSED!")
            print("✨ The offsec-team infrastructure is ready for real-time streaming!")
        else:
            print("\n⚠️ Some streaming tests FAILED!")
            print("🔧 Review the errors above and fix the issues before deployment.")
        
        return {
            "overall_success": overall_success,
            "results": results,
            "session_id": self.session_id,
            "test_time": datetime.utcnow().isoformat()
        }

async def main():
    """Main test execution"""
    tester = StreamingTester()
    
    print("🌟 OffSec-Team Streaming Functionality Test Suite")
    print("🎯 Testing real-time streaming across the entire infrastructure")
    print(f"📅 {datetime.utcnow().isoformat()}")
    print()
    
    # Run comprehensive test
    results = await tester.run_comprehensive_test()
    
    # Exit with appropriate code
    exit_code = 0 if results["overall_success"] else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {str(e)}")
        sys.exit(1)
