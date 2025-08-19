#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced Researcher Tools

This test suite validates the functionality of the enhanced research infrastructure
including multi-endpoint integration, agent coordination, and workflow orchestration.
"""

import unittest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the enhanced tools
from enhanced_researcher_tools import (
    EnhancedResearcherTools,
    ResearchComplexity,
    AgentCapability,
    ResearchContext,
    EndpointConfig
)


class TestEnhancedResearcherTools(unittest.TestCase):
    """Test cases for Enhanced Researcher Tools"""
    
    def setUp(self):
        """Set up test environment"""
        # Create test configuration
        self.test_config = EndpointConfig(
            tools_api="https://test-tools.attck.nexus",
            researcher_api="https://test-researcher.attck.nexus",
            mcp_research_agent="https://test-mcp.attck-community.workers.dev",
            chat_return="https://test-chat.attck.nexus",
            timeout=10,
            max_retries=2,
            parallel_enabled=True
        )
        
        # Initialize enhanced tools with test config
        self.enhanced_tools = EnhancedResearcherTools(config=self.test_config)
        
        # Test user context
        self.test_user = {
            "id": "test_user_123",
            "name": "Test User",
            "email": "test@example.com"
        }

    def test_initialization(self):
        """Test proper initialization of enhanced tools"""
        self.assertIsNotNone(self.enhanced_tools)
        self.assertEqual(len(self.enhanced_tools.agent_tools), 5)  # 5 agent types
        self.assertTrue(self.enhanced_tools.mcp_connected)
        self.assertIsNotNone(self.enhanced_tools.threat_feeds)

    def test_query_complexity_analysis(self):
        """Test query complexity analysis"""
        # Simple query
        simple_query = "scan website for vulnerabilities"
        complexity = self.enhanced_tools._analyze_query_complexity(simple_query)
        self.assertEqual(complexity, ResearchComplexity.MODERATE)
        
        # Complex query
        complex_query = "comprehensive security audit with deep analysis"
        complexity = self.enhanced_tools._analyze_query_complexity(complex_query)
        self.assertEqual(complexity, ResearchComplexity.COMPLEX)
        
        # Orchestrated query
        orchestrated_query = "multi-step workflow orchestration for end-to-end assessment"
        complexity = self.enhanced_tools._analyze_query_complexity(orchestrated_query)
        self.assertEqual(complexity, ResearchComplexity.ORCHESTRATED)

    def test_agent_determination(self):
        """Test agent determination based on query content"""
        # Bug hunter query
        bug_query = "test for SQL injection vulnerabilities"
        agents = self.enhanced_tools._determine_required_agents(bug_query)
        self.assertIn(AgentCapability.BUG_HUNTER, agents)
        
        # RT-Dev query
        dev_query = "generate terraform infrastructure configuration"
        agents = self.enhanced_tools._determine_required_agents(dev_query)
        self.assertIn(AgentCapability.RT_DEV, agents)
        
        # Compliance query
        compliance_query = "audit infrastructure for SOC2 compliance"
        agents = self.enhanced_tools._determine_required_agents(compliance_query)
        self.assertIn(AgentCapability.DAEDELU5, agents)
        
        # Multi-agent query
        multi_query = "comprehensive security assessment with compliance check and code generation"
        agents = self.enhanced_tools._determine_required_agents(multi_query)
        self.assertGreaterEqual(len(agents), 3)

    def test_research_context_creation(self):
        """Test research context creation"""
        query = "test vulnerability assessment"
        context = self.enhanced_tools._create_research_context(query, self.test_user)
        
        self.assertIsNotNone(context.thread_id)
        self.assertEqual(context.user_id, "test_user_123")
        self.assertIsInstance(context.complexity, ResearchComplexity)
        self.assertIsInstance(context.agents_involved, list)
        self.assertGreater(context.timestamp, 0)

    @patch('requests.request')
    def test_endpoint_request_execution(self, mock_request):
        """Test endpoint request execution"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {"test": "data"}
        }
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_request.return_value = mock_response
        
        # Test request config
        request_config = {
            "method": "POST",
            "url": "https://test-api.com/endpoint",
            "headers": {"Content-Type": "application/json"},
            "data": {"test": "request"}
        }
        
        result = self.enhanced_tools._execute_endpoint_request("test_endpoint", request_config)
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("endpoint_source"), "test_endpoint")
        self.assertIsNotNone(result.get("response_time_ms"))

    @patch('requests.request')
    def test_parallel_requests(self, mock_request):
        """Test parallel request execution"""
        # Mock successful responses from all endpoints
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "vulnerabilities": ["XSS", "SQL Injection"],
                "framework_detected": "React",
                "insights": "Security analysis completed",
                "recommendations": ["Implement WAF", "Update dependencies"]
            }
        }
        mock_response.elapsed.total_seconds.return_value = 1.0
        mock_request.return_value = mock_response
        
        # Create test context
        context = self.enhanced_tools._create_research_context("test parallel requests", self.test_user)
        
        # Execute parallel requests
        result = self.enhanced_tools._make_parallel_requests(
            context, 
            "test vulnerability scan", 
            {"target_url": "https://example.com"}
        )
        
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("research_type"), "parallel_multi_endpoint")
        self.assertGreater(result.get("total_execution_time_ms", 0), 0)
        self.assertIn("result", result)

    def test_threat_intelligence_extraction(self):
        """Test threat intelligence extraction from responses"""
        test_responses = [
            {
                "endpoint_source": "tools_api",
                "result": {
                    "vulnerabilities": ["CVE-2023-1234", "CVE-2023-5678"],
                    "iocs": ["malicious-domain.com", "192.168.1.100"]
                }
            },
            {
                "endpoint_source": "researcher_api",
                "result": {
                    "attack_patterns": ["T1190", "T1059"],
                    "vulnerabilities": ["CVE-2023-9999"]
                }
            }
        ]
        
        threat_intel = self.enhanced_tools._extract_threat_intelligence(test_responses)
        
        self.assertIn("indicators_of_compromise", threat_intel)
        self.assertIn("vulnerabilities", threat_intel)
        self.assertIn("attack_patterns", threat_intel)
        self.assertGreater(threat_intel.get("risk_score", 0), 0)

    def test_security_recommendations_generation(self):
        """Test security recommendations generation"""
        test_responses = [
            {
                "result": {
                    "recommendations": ["Implement HTTPS", "Update software"]
                }
            }
        ]
        
        context = self.enhanced_tools._create_research_context("test recommendations", self.test_user)
        context.agents_involved = [AgentCapability.BUG_HUNTER, AgentCapability.DAEDELU5]
        
        recommendations = self.enhanced_tools._generate_security_recommendations(test_responses, context)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        # Should include agent-specific recommendations
        self.assertTrue(any("vulnerability scanning" in rec for rec in recommendations))
        self.assertTrue(any("compliance" in rec for rec in recommendations))

    @patch('requests.request')
    def test_enhanced_web_search(self, mock_request):
        """Test enhanced web search functionality"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "combined_insights": {
                    "executive_summary": "Web search completed successfully",
                    "key_findings": ["Finding 1", "Finding 2"],
                    "confidence_score": 0.85
                },
                "threat_intelligence": {
                    "risk_score": 3.5,
                    "vulnerabilities": ["CVE-2023-1234"]
                },
                "security_recommendations": ["Implement security headers"],
                "workflow_suggestions": ["Schedule follow-up analysis"]
            }
        }
        mock_response.elapsed.total_seconds.return_value = 2.0
        mock_request.return_value = mock_response
        
        result = self.enhanced_tools.enhanced_web_search(
            query="cybersecurity threat landscape 2024",
            max_results=10,
            include_threat_intel=True,
            __user__=self.test_user
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("Web Search Complete", result)
        self.assertIn("Executive Summary", result)
        self.assertIn("Thread ID", result)

    @patch('requests.request')
    def test_multi_agent_vulnerability_assessment(self, mock_request):
        """Test multi-agent vulnerability assessment"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "combined_insights": {
                    "executive_summary": "Vulnerability assessment completed",
                    "key_findings": ["SQL Injection found", "XSS vulnerability detected"],
                    "confidence_score": 0.92
                },
                "threat_intelligence": {
                    "risk_score": 7.5,
                    "vulnerabilities": ["High severity SQL injection", "Medium severity XSS"]
                },
                "security_recommendations": [
                    "Implement input validation",
                    "Deploy WAF",
                    "Update security policies"
                ]
            }
        }
        mock_response.elapsed.total_seconds.return_value = 5.0
        mock_request.return_value = mock_response
        
        result = self.enhanced_tools.multi_agent_vulnerability_assessment(
            target_url="https://example.com",
            assessment_depth="comprehensive",
            include_compliance_check=True,
            __user__=self.test_user
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("Multi-Agent Vulnerability Assessment Complete", result)
        self.assertIn("Risk Score", result)
        self.assertIn("Security Recommendations", result)

    @patch('requests.request')
    def test_orchestrated_security_workflow(self, mock_request):
        """Test orchestrated security workflow"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "combined_insights": {
                    "executive_summary": "Orchestrated workflow completed successfully",
                    "key_findings": ["Workflow phase 1 completed", "Multi-agent coordination successful"],
                    "confidence_score": 0.88
                },
                "workflow_suggestions": [
                    "Implement automated workflow for similar tasks",
                    "Set up continuous monitoring"
                ]
            }
        }
        mock_response.elapsed.total_seconds.return_value = 10.0
        mock_request.return_value = mock_response
        
        result = self.enhanced_tools.orchestrated_security_workflow(
            workflow_type="security_audit",
            target_scope="web_application",
            coordination_level="full",
            __user__=self.test_user
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("Orchestrated Security Workflow Complete", result)
        self.assertIn("nexus_kamuy", result.lower())
        self.assertIn("Workflow Suggestions", result)

    @patch('requests.request')
    def test_advanced_threat_intelligence_research(self, mock_request):
        """Test advanced threat intelligence research"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "combined_insights": {
                    "executive_summary": "Threat intelligence research completed",
                    "key_findings": ["APT group identified", "Malware family analyzed"],
                    "confidence_score": 0.91
                },
                "threat_intelligence": {
                    "risk_score": 8.5,
                    "threat_actors": ["APT29", "Lazarus Group"],
                    "indicators_of_compromise": ["malicious-domain.com", "bad-ip.com"]
                }
            }
        }
        mock_response.elapsed.total_seconds.return_value = 3.0
        mock_request.return_value = mock_response
        
        result = self.enhanced_tools.advanced_threat_intelligence_research(
            indicators=["malicious-domain.com", "suspicious-hash"],
            threat_types=["malware", "apt"],
            include_attribution=True,
            __user__=self.test_user
        )
        
        self.assertIsInstance(result, str)
        self.assertIn("Advanced Threat Intelligence Research Complete", result)
        self.assertIn("Risk Score", result)

    @patch('requests.get')
    def test_infrastructure_status_check(self, mock_get):
        """Test infrastructure status checking"""
        # Mock healthy responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response
        
        result = self.enhanced_tools.get_research_infrastructure_status(__user__=self.test_user)
        
        self.assertIsInstance(result, str)
        self.assertIn("Research Infrastructure Status", result)
        self.assertIn("endpoints healthy", result)
        self.assertIn("Agent Capabilities", result)
        self.assertIn("MCP Connection", result)

    def test_backward_compatibility_methods(self):
        """Test backward compatibility with original Tools class"""
        # Test user info method
        user_info = self.enhanced_tools.get_user_name_and_email_and_id(self.test_user)
        self.assertIn("Test User", user_info)
        self.assertIn("test_user_123", user_info)
        
        # Test time method
        current_time = self.enhanced_tools.get_current_time()
        self.assertIn("Current Date and Time", current_time)
        
        # Test calculator
        calc_result = self.enhanced_tools.calculator("2 + 2")
        self.assertEqual(calc_result, "2 + 2 = 4")
        
        # Test invalid calculation
        invalid_calc = self.enhanced_tools.calculator("import os")
        self.assertIn("Invalid equation", invalid_calc)

    def test_sequential_research_fallback(self):
        """Test sequential research fallback when parallel is disabled"""
        # Disable parallel processing
        self.enhanced_tools.config.parallel_enabled = False
        
        with patch('requests.request') as mock_request:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "result": {"test": "sequential_data"}
            }
            mock_response.elapsed.total_seconds.return_value = 1.0
            mock_request.return_value = mock_response
            
            context = self.enhanced_tools._create_research_context("test sequential", self.test_user)
            result = self.enhanced_tools._sequential_research(context, "test query", {})
            
            self.assertTrue(result.get("success"))
            self.assertIn("sequential", result.get("research_type", ""))

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test with invalid endpoint responses
        with patch('requests.request') as mock_request:
            # Mock failed response
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_request.return_value = mock_response
            
            request_config = {
                "method": "POST",
                "url": "https://test-api.com/endpoint",
                "headers": {"Content-Type": "application/json"},
                "data": {"test": "request"}
            }
            
            result = self.enhanced_tools._execute_endpoint_request("test_endpoint", request_config)
            
            self.assertFalse(result.get("success"))
            self.assertIn("HTTP 500", result.get("error", ""))

    def test_response_formatting(self):
        """Test response formatting functionality"""
        # Create test result
        test_result = {
            "success": True,
            "research_type": "parallel_multi_endpoint",
            "total_execution_time_ms": 2500,
            "successful_endpoints": 3,
            "endpoints_queried": ["tools_api", "researcher_api", "mcp_agent"],
            "result": {
                "combined_insights": {
                    "executive_summary": "Test analysis completed",
                    "key_findings": ["Finding 1", "Finding 2"],
                    "confidence_score": 0.85
                },
                "threat_intelligence": {
                    "risk_score": 5.5,
                    "vulnerabilities": ["CVE-2023-1234"]
                },
                "security_recommendations": ["Recommendation 1", "Recommendation 2"],
                "workflow_suggestions": ["Suggestion 1"]
            }
        }
        
        context = self.enhanced_tools._create_research_context("test formatting", self.test_user)
        formatted = self.enhanced_tools._format_enhanced_response("Test Operation", test_result, context)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("Test Operation Complete", formatted)
        self.assertIn("2500ms", formatted)
        self.assertIn("Executive Summary", formatted)
        self.assertIn("Threat Intelligence", formatted)
        self.assertIn("Security Recommendations", formatted)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for real-world usage"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.enhanced_tools = EnhancedResearcherTools()
        self.test_user = {
            "id": "integration_user",
            "name": "Integration Tester",
            "email": "integration@test.com"
        }

    @patch('requests.request')
    def test_comprehensive_security_assessment_workflow(self, mock_request):
        """Test comprehensive security assessment workflow"""
        # Mock responses for different phases
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "result": {
                "combined_insights": {
                    "executive_summary": "Comprehensive assessment completed",
                    "key_findings": [
                        "Multiple vulnerabilities identified",
                        "Compliance gaps found",
                        "Infrastructure hardening needed"
                    ],
                    "confidence_score": 0.89
                },
                "threat_intelligence": {
                    "risk_score": 7.8,
                    "vulnerabilities": ["Critical SQL injection", "High XSS", "Medium CSRF"],
                    "indicators_of_compromise": ["suspicious-domain.com"]
                },
                "security_recommendations": [
                    "Implement immediate patches for critical vulnerabilities",
                    "Deploy web application firewall",
                    "Conduct compliance remediation",
                    "Establish continuous monitoring"
                ],
                "workflow_suggestions": [
                    "Schedule regular security assessments",
                    "Implement automated vulnerability scanning",
                    "Establish incident response procedures"
                ]
            }
        }
        mock_response.elapsed.total_seconds.return_value = 15.0
        mock_request.return_value = mock_response
        
        # Execute comprehensive assessment
        result = self.enhanced_tools.multi_agent_vulnerability_assessment(
            target_url="https://target-application.com",
            assessment_depth="comprehensive",
            include_compliance_check=True,
            __user__=self.test_user
        )
        
        # Validate comprehensive results
        self.assertIn("Multi-Agent Vulnerability Assessment Complete", result)
        self.assertIn("Risk Score: 7.8", result)
        self.assertIn("Critical SQL injection", result)
        self.assertIn("Deploy web application firewall", result)
        self.assertIn("Schedule regular security assessments", result)

    def test_agent_capability_coverage(self):
        """Test that all agent capabilities are properly covered"""
        # Test each agent type
        agent_test_queries = {
            AgentCapability.BUG_HUNTER: "scan for SQL injection vulnerabilities",
            AgentCapability.RT_DEV: "generate secure Python FastAPI template",
            AgentCapability.BURPSUITE_OPERATOR: "launch automated Burp Suite scan",
            AgentCapability.DAEDELU5: "audit infrastructure for SOC2 compliance",
            AgentCapability.NEXUS_KAMUY: "orchestrate multi-agent security workflow"
        }
        
        for agent, query in agent_test_queries.items():
            determined_agents = self.enhanced_tools._determine_required_agents(query)
            self.assertIn(agent, determined_agents, 
                         f"Agent {agent.value} not detected for query: {query}")

    def test_complexity_escalation(self):
        """Test complexity escalation scenarios"""
        complexity_queries = [
            ("scan website", ResearchComplexity.MODERATE),
            ("comprehensive security audit", ResearchComplexity.COMPLEX),
            ("orchestrated multi-step workflow analysis", ResearchComplexity.ORCHESTRATED)
        ]
        
        for query, expected_complexity in complexity_queries:
            detected_complexity = self.enhanced_tools._analyze_query_complexity(query)
            self.assertEqual(detected_complexity, expected_complexity,
                           f"Wrong complexity for query '{query}': expected {expected_complexity}, got {detected_complexity}")


def run_performance_tests():
    """Run performance tests for the enhanced tools"""
    print("Running performance tests...")
    
    enhanced_tools = EnhancedResearcherTools()
    test_user = {"id": "perf_test", "name": "Performance Tester"}
    
    # Test context creation performance
    start_time = time.time()
    for i in range(100):
        context = enhanced_tools._create_research_context(f"test query {i}", test_user)
    context_creation_time = time.time() - start_time
    print(f"Context creation (100 iterations): {context_creation_time:.3f}s")
    
    # Test query analysis performance
    start_time = time.time()
    test_queries = [
        "scan for vulnerabilities",
        "comprehensive security audit with compliance check",
        "orchestrated multi-agent workflow for threat assessment",
        "generate secure infrastructure configuration",
        "analyze web application security posture"
    ]
    
    for _ in range(20):
        for query in test_queries:
            complexity = enhanced_tools._analyze_query_complexity(query)
            agents = enhanced_tools._determine_required_agents(query)
    
    analysis_time = time.time() - start_time
    print(f"Query analysis (100 queries): {analysis_time:.3f}s")
    
    print("Performance tests completed.")


if __name__ == "__main__":
    # Run unit tests
    print("Running Enhanced Researcher Tools Test Suite...")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestEnhancedResearcherTools))
    test_suite.addTest(unittest.makeSuite(TestIntegrationScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    print("\n" + "=" * 60)
    run_performance_tests()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
