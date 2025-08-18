#!/usr/bin/env python3
"""
Mock API server for testing the Offsec Team Tools Auto-Router Filter
Provides fallback endpoints when the real API is unavailable
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from typing import Dict, Any

class MockAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/agents':
            self.send_agents_response()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/execute':
            self.send_execute_response()
        else:
            self.send_error(404, "Not Found")
    
    def send_health_response(self):
        """Send mock health response"""
        response_data = {
            "status": "healthy",
            "version": "1.0.0-mock",
            "agents_loaded": 5,
            "uptime": "mock-server",
            "message": "Mock API server running for testing"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def send_agents_response(self):
        """Send mock agents list response"""
        response_data = {
            "agents": {
                "bug_hunter": {
                    "loaded": 1,
                    "status": "active",
                    "available_tools": [
                        "bug_hunter.detect_framework",
                        "bug_hunter.test_injection_vulnerabilities", 
                        "bug_hunter.analyze_cross_site_vulnerabilities",
                        "bug_hunter.evaluate_authentication_security"
                    ]
                },
                "rt_dev": {
                    "loaded": 1,
                    "status": "active",
                    "available_tools": [
                        "rt_dev.generate_language_template",
                        "rt_dev.deploy_docker_compose_stack",
                        "rt_dev.generate_terraform_configuration"
                    ]
                },
                "burpsuite_operator": {
                    "loaded": 1,
                    "status": "active", 
                    "available_tools": [
                        "burpsuite_operator.launch_automated_scan",
                        "burpsuite_operator.establish_burp_connection",
                        "burpsuite_operator.extract_scan_findings"
                    ]
                },
                "daedelu5": {
                    "loaded": 1,
                    "status": "active",
                    "available_tools": [
                        "daedelu5.audit_infrastructure_compliance",
                        "daedelu5.check_regulatory_requirements",
                        "daedelu5.enforce_security_baseline"
                    ]
                },
                "nexus_kamuy": {
                    "loaded": 1,
                    "status": "active",
                    "available_tools": [
                        "nexus_kamuy.create_multi_agent_workflow",
                        "nexus_kamuy.coordinate_multi_agent_task",
                        "nexus_kamuy.establish_collaboration_session"
                    ]
                }
            },
            "total_agents": 5,
            "total_tools": 16,
            "server_type": "mock"
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def send_execute_response(self):
        """Send mock tool execution response"""
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(post_data.decode())
        except:
            request_data = {}
        
        # Generate mock response based on tool
        agent = request_data.get('agent', 'unknown')
        tool = request_data.get('tool_name', 'unknown')
        parameters = request_data.get('parameters', {})
        
        response_data = {
            "success": True,
            "request_id": request_data.get('request_id', 'mock-request'),
            "agent": agent,
            "tool": tool,
            "execution_time_ms": 125,
            "result": {
                "status": "Mock execution successful",
                "agent": agent,
                "tool": tool,
                "parameters": parameters,
                "mock_data": True,
                "note": "This is a simulated response from mock API server"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class MockAPIServer:
    def __init__(self, host='localhost', port=8899):
        self.host = host
        self.port = port
        self.httpd = None
        self.thread = None
        
    def start(self):
        """Start the mock API server"""
        self.httpd = HTTPServer((self.host, self.port), MockAPIHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"🚀 Mock API server started on http://{self.host}:{self.port}")
        time.sleep(0.1)  # Give server time to start
        
    def stop(self):
        """Stop the mock API server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            if self.thread:
                self.thread.join(timeout=1)
            print("🛑 Mock API server stopped")

if __name__ == "__main__":
    # Run mock server standalone
    server = MockAPIServer()
    try:
        server.start()
        print("Press Ctrl+C to stop the server")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
