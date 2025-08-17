"""
Bug Hunter Agent Router

FastAPI router for Bug Hunter agent tools, including web vulnerability testing,
framework security analysis, and vulnerability reporting.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import Bug Hunter tools
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from tools.bug_hunter.WebVulnerabilityTester import WebVulnerabilityTester
from tools.bug_hunter.FrameworkSecurityAnalyzer import FrameworkSecurityAnalyzer
from tools.bug_hunter.VulnerabilityReportGenerator import VulnerabilityReportGenerator

logger = logging.getLogger("BugHunterRouter")

# Create router
router = APIRouter()

# Initialize Bug Hunter tool instances
web_vuln_tester = WebVulnerabilityTester()
framework_analyzer = FrameworkSecurityAnalyzer()
report_generator = VulnerabilityReportGenerator()

# Pydantic models for Bug Hunter specific requests
class VulnerabilityTestRequest(BaseModel):
    """Request model for vulnerability testing"""
    target_url: str = Field(..., description="URL of the target to test")
    parameters: List[str] = Field(default_factory=list, description="List of parameters to test")

class CrossSiteTestRequest(BaseModel):
    """Request model for cross-site vulnerability testing"""
    target_url: str = Field(..., description="URL of the target to test")

class AuthSecurityRequest(BaseModel):
    """Request model for authentication security testing"""
    login_url: str = Field(..., description="URL of the login page")
    auth_flow: Dict[str, Any] = Field(..., description="Authentication flow details")

class FrameworkAnalysisRequest(BaseModel):
    """Request model for framework security analysis"""
    target_url: str = Field(..., description="URL of the target application")
    framework_hints: List[str] = Field(default_factory=list, description="Hints about the framework used")

class ReportGenerationRequest(BaseModel):
    """Request model for vulnerability report generation"""
    scan_results: Dict[str, Any] = Field(..., description="Scan results to include in report")
    report_type: str = Field(default="comprehensive", description="Type of report to generate")

# Bug Hunter Endpoints
@router.post("/vulnerability/test-injection")
async def test_injection_vulnerabilities(request: VulnerabilityTestRequest):
    """Test for SQL, NoSQL, and command injection vulnerabilities"""
    try:
        result = web_vuln_tester.test_injection_vulnerabilities(
            target_url=request.target_url,
            parameters=request.parameters
        )
        
        return {
            "success": result.get("success", False),
            "vulnerability_results": result,
            "target_url": request.target_url,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Injection vulnerability testing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Injection vulnerability testing failed: {str(e)}")

@router.post("/vulnerability/test-cross-site")
async def test_cross_site_vulnerabilities(request: CrossSiteTestRequest):
    """Test for XSS and CSRF vulnerabilities"""
    try:
        result = web_vuln_tester.analyze_cross_site_vulnerabilities(
            target_url=request.target_url
        )
        
        return {
            "success": result.get("success", False),
            "cross_site_results": result,
            "target_url": request.target_url,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Cross-site vulnerability testing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cross-site vulnerability testing failed: {str(e)}")

@router.post("/security/test-authentication")
async def test_authentication_security(request: AuthSecurityRequest):
    """Assess authentication implementation security"""
    try:
        result = web_vuln_tester.evaluate_authentication_security(
            login_url=request.login_url,
            auth_flow=request.auth_flow
        )
        
        return {
            "success": result.get("success", False),
            "auth_security_results": result,
            "login_url": request.login_url,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Authentication security testing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication security testing failed: {str(e)}")

@router.post("/framework/analyze")
async def analyze_framework_security(request: FrameworkAnalysisRequest):
    """Analyze web application framework security"""
    try:
        result = framework_analyzer.analyze_framework_security_posture(
            target_url=request.target_url,
            framework_hints=request.framework_hints
        )
        
        return {
            "success": result.get("success", False),
            "framework_analysis": result,
            "target_url": request.target_url,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Framework security analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Framework security analysis failed: {str(e)}")

@router.post("/report/generate")
async def generate_vulnerability_report(request: ReportGenerationRequest):
    """Generate comprehensive vulnerability reports"""
    try:
        result = report_generator.generate_executive_summary_report(
            scan_results=request.scan_results,
            report_type=request.report_type
        )
        
        return {
            "success": result.get("success", False),
            "report_result": result,
            "report_type": request.report_type,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Vulnerability report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vulnerability report generation failed: {str(e)}")

@router.get("/status")
async def get_bug_hunter_status():
    """Get Bug Hunter agent status and capabilities"""
    return {
        "agent": "Bug Hunter",
        "status": "active",
        "capabilities": {
            "vulnerability_testing": {
                "injection_testing": True,
                "cross_site_testing": True,
                "authentication_testing": True
            },
            "framework_analysis": {
                "security_posture": True,
                "configuration_analysis": True
            },
            "reporting": {
                "vulnerability_reports": True,
                "executive_summaries": True,
                "technical_details": True
            }
        },
        "tools_loaded": [
            "WebVulnerabilityTester",
            "FrameworkSecurityAnalyzer",
            "VulnerabilityReportGenerator"
        ],
        "timestamp": datetime.utcnow()
    }

@router.get("/tools")
async def list_bug_hunter_tools():
    """List all available Bug Hunter tools and endpoints"""
    return {
        "agent": "Bug Hunter",
        "tools": {
            "vulnerability_testing": {
                "test_injection_vulnerabilities": "POST /vulnerability/test-injection",
                "test_cross_site_vulnerabilities": "POST /vulnerability/test-cross-site",
                "test_authentication_security": "POST /security/test-authentication"
            },
            "framework_analysis": {
                "analyze_framework_security": "POST /framework/analyze"
            },
            "reporting": {
                "generate_vulnerability_report": "POST /report/generate"
            },
            "status": {
                "get_bug_hunter_status": "GET /status",
                "list_bug_hunter_tools": "GET /tools"
            }
        },
        "total_endpoints": 7,
        "timestamp": datetime.utcnow()
    }
