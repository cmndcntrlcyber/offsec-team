#!/usr/bin/env python3
"""
Integration Test for Research Agent MCP Tools

This script tests the integration between the offsec-team agents and the
research-agent MCP server. It verifies that all research tools are properly
configured and can communicate with the research agent.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List

# Add tools directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

# Import shared researcher tool
from tools.shared.ResearcherTool import ResearcherTool

# Import agent-specific tools
from tools.bug_hunter.ResearcherThreatIntelligence import ResearcherThreatIntelligence
from tools.bug_hunter.ResearcherExploitDatabase import ResearcherExploitDatabase
from tools.bug_hunter.ResearcherVulnContext import ResearcherVulnContext


class ResearchIntegrationTester:
    """Test suite for research agent MCP integration"""
    
    def __init__(self):
        self.logger = logging.getLogger("ResearchIntegrationTester")
        self.test_results = []
        self.failed_tests = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        self.logger.info("Starting research agent MCP integration tests...")
        
        start_time = time.time()
        
        # Test shared researcher tool
        self._test_shared_researcher_tool()
        
        # Test Bug Hunter agent tools
        self._test_bug_hunter_tools()
        
        # Calculate results
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = total_tests - len(self.failed_tests)
        
        results = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": len(self.failed_tests),
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": round(end_time - start_time, 2),
            "test_results": self.test_results,
            "failed_test_details": self.failed_tests
        }
        
        self.logger.info(f"Integration tests completed: {passed_tests}/{total_tests} passed ({results['success_rate']:.1f}%)")
        
        return results
    
    def _test_shared_researcher_tool(self):
        """Test the shared researcher tool"""
        self.logger.info("Testing shared researcher tool...")
        
        try:
            researcher = ResearcherTool()
            
            # Test 1: Check available tools
            self._run_test(
                "Shared Tool - Get Available Tools",
                lambda: researcher.get_available_tools(),
                lambda result: result.get("success", False) and len(result.get("tools", {})) > 0
            )
            
            # Test 2: Test basic research functionality (simulated)
            self._run_test(
                "Shared Tool - Basic Research",
                lambda: researcher.perform_research(
                    tool_name="web_search",
                    query="cybersecurity vulnerability research",
                    agent_id="test_agent"
                ),
                lambda result: result.get("success", False)
            )
            
            # Test 3: Test research history
            self._run_test(
                "Shared Tool - Research History",
                lambda: researcher.get_research_history(limit=5),
                lambda result: result.get("success", False)
            )
            
        except Exception as e:
            self._record_test_failure("Shared Tool - Initialization", str(e))
    
    def _test_bug_hunter_tools(self):
        """Test Bug Hunter agent research tools"""
        self.logger.info("Testing Bug Hunter agent research tools...")
        
        # Test Threat Intelligence Tool
        try:
            threat_intel = ResearcherThreatIntelligence()
            
            self._run_test(
                "Bug Hunter - Threat Intelligence Initialization",
                lambda: {"success": True, "agent_id": threat_intel.agent_id},
                lambda result: result.get("success", False) and result.get("agent_id") == "bug_hunter"
            )
            
            self._run_test(
                "Bug Hunter - Gather Threat Intelligence",
                lambda: threat_intel.gather_threat_intelligence(
                    threat_query="SQL injection vulnerability",
                    research_scope="basic",
                    focus_areas=["general", "mitigations"]
                ),
                lambda result: result.get("success", False)
            )
            
            self._run_test(
                "Bug Hunter - Research Vulnerability Context",
                lambda: threat_intel.research_vulnerability_context(
                    cve_id="CVE-2024-1234",
                    include_exploits=True,
                    include_patches=True
                ),
                lambda result: result.get("success", False)
            )
            
        except Exception as e:
            self._record_test_failure("Bug Hunter - Threat Intelligence Tool", str(e))
        
        # Test Exploit Database Tool
        try:
            exploit_db = ResearcherExploitDatabase()
            
            self._run_test(
                "Bug Hunter - Exploit Database Initialization",
                lambda: {"success": True, "agent_id": exploit_db.agent_id},
                lambda result: result.get("success", False) and result.get("agent_id") == "bug_hunter"
            )
            
            self._run_test(
                "Bug Hunter - Search Exploit Database",
                lambda: exploit_db.search_exploit_database(
                    search_query="buffer overflow",
                    exploit_category="system_exploits",
                    max_results=5
                ),
                lambda result: result.get("success", False)
            )
            
            self._run_test(
                "Bug Hunter - Research Exploit Techniques",
                lambda: exploit_db.research_exploit_techniques(
                    technique_name="SQL injection",
                    target_platform="web_application",
                    include_countermeasures=True
                ),
                lambda result: result.get("success", False)
            )
            
        except Exception as e:
            self._record_test_failure("Bug Hunter - Exploit Database Tool", str(e))
        
        # Test Vulnerability Context Tool
        try:
            vuln_context = ResearcherVulnContext()
            
            self._run_test(
                "Bug Hunter - Vulnerability Context Initialization",
                lambda: {"success": True, "agent_id": vuln_context.agent_id},
                lambda result: result.get("success", False) and result.get("agent_id") == "bug_hunter"
            )
            
            self._run_test(
                "Bug Hunter - Analyze Vulnerability Context",
                lambda: vuln_context.analyze_vulnerability_context(
                    vulnerability_id="CVE-2024-5678",
                    analysis_scope="standard",
                    target_environment="enterprise"
                ),
                lambda result: result.get("success", False)
            )
            
            self._run_test(
                "Bug Hunter - Research Attack Scenarios",
                lambda: vuln_context.research_attack_scenarios(
                    vulnerability_id="CVE-2024-5678",
                    scenario_types=["realistic", "advanced"],
                    environment_context="enterprise"
                ),
                lambda result: result.get("success", False)
            )
            
        except Exception as e:
            self._record_test_failure("Bug Hunter - Vulnerability Context Tool", str(e))
    
    def _run_test(self, test_name: str, test_function, validation_function):
        """Run a single test and record results"""
        try:
            self.logger.info(f"Running test: {test_name}")
            
            start_time = time.time()
            result = test_function()
            end_time = time.time()
            
            execution_time = round(end_time - start_time, 3)
            
            if validation_function(result):
                self.test_results.append({
                    "test_name": test_name,
                    "status": "PASSED",
                    "execution_time": execution_time,
                    "result_summary": self._summarize_result(result)
                })
                self.logger.info(f"✅ {test_name} - PASSED ({execution_time}s)")
            else:
                self._record_test_failure(test_name, f"Validation failed: {result}")
                
        except Exception as e:
            self._record_test_failure(test_name, str(e))
    
    def _record_test_failure(self, test_name: str, error_message: str):
        """Record a test failure"""
        failure_info = {
            "test_name": test_name,
            "status": "FAILED",
            "error": error_message
        }
        
        self.test_results.append(failure_info)
        self.failed_tests.append(failure_info)
        
        self.logger.error(f"❌ {test_name} - FAILED: {error_message}")
    
    def _summarize_result(self, result: Any) -> str:
        """Create a summary of test result"""
        if isinstance(result, dict):
            if result.get("success"):
                return "Operation completed successfully"
            else:
                return f"Operation failed: {result.get('error', 'Unknown error')}"
        else:
            return str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted test report"""
        report = f"""
# Research Agent MCP Integration Test Report

**Test Execution Summary:**
- Total Tests: {results['total_tests']}
- Passed: {results['passed_tests']}
- Failed: {results['failed_tests']}
- Success Rate: {results['success_rate']:.1f}%
- Execution Time: {results['execution_time']}s

## Test Results

"""
        
        for test in results['test_results']:
            status_icon = "✅" if test['status'] == "PASSED" else "❌"
            report += f"{status_icon} **{test['test_name']}** - {test['status']}"
            
            if test['status'] == "PASSED":
                report += f" ({test.get('execution_time', 'N/A')}s)\n"
                if 'result_summary' in test:
                    report += f"   - {test['result_summary']}\n"
            else:
                report += f"\n   - Error: {test.get('error', 'Unknown error')}\n"
            
            report += "\n"
        
        if results['failed_tests']:
            report += "\n## Failed Test Details\n\n"
            for failure in results['failed_tests']:
                report += f"### {failure['test_name']}\n"
                report += f"**Error:** {failure['error']}\n\n"
        
        report += "\n## Recommendations\n\n"
        
        if results['success_rate'] >= 80:
            report += "✅ Integration is working well. Minor issues may need attention.\n"
        elif results['success_rate'] >= 60:
            report += "⚠️ Integration has some issues that should be addressed.\n"
        else:
            report += "❌ Integration has significant issues requiring immediate attention.\n"
        
        report += "\n### Next Steps\n"
        report += "1. Review failed tests and address underlying issues\n"
        report += "2. Verify MCP server connectivity and configuration\n"
        report += "3. Check environment variables and authentication\n"
        report += "4. Test individual components in isolation if needed\n"
        
        return report


def main():
    """Main test execution function"""
    print("🔬 Research Agent MCP Integration Test Suite")
    print("=" * 50)
    
    tester = ResearchIntegrationTester()
    results = tester.run_all_tests()
    
    # Generate and display report
    report = tester.generate_test_report(results)
    print("\n" + report)
    
    # Save report to file
    report_file = "research_integration_test_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    if results['success_rate'] >= 80:
        print("\n🎉 Integration tests completed successfully!")
        return 0
    else:
        print(f"\n⚠️ Integration tests completed with issues ({results['success_rate']:.1f}% success rate)")
        return 1


if __name__ == "__main__":
    exit(main())
