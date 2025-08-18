# Open WebUI Integration Guide

This guide explains how to integrate the Agent Tool Bridge API with Open WebUI at https://chat.attck.nexus/

## Overview

The Agent Tool Bridge API provides a FastAPI server that exposes cybersecurity agent tools through standardized REST endpoints for Open WebUI integration. The bridge serves as a middleware layer between Open WebUI and the existing agent ecosystem.

## Server Configuration

### Bridge Server Details
- **URL**: http://localhost:8000 (configurable)
- **Status**: ✅ Operational with 19 agent instances loaded
- **CORS**: Configured for https://chat.attck.nexus/
- **Authentication**: Bearer token required
- **API Documentation**: http://localhost:8000/docs (FastAPI Swagger UI)

### Starting the Bridge Server

```powershell
# Navigate to bridge directory
cd openwebui-bridge

# Install dependencies (first time only)
pip install -r requirements.txt

# Start in development mode (with auto-reload)
python start-bridge.py --dev

# Start in production mode
python start-bridge.py --host 0.0.0.0 --port 8000

# Validate setup only
python start-bridge.py --validate-only
```

## Available Agent Tools

### 1. RT-Dev Tools (7 instances, 24 tools)
**Purpose**: Rapid development, deployment capabilities, and DevSecOps research intelligence

**Core Development Instances**:
- `code_forge_generator`: Code generation and validation
- `infrastructure_orchestrator`: Infrastructure deployment 
- `platform_connector`: Platform integration
- `ci_pipeline_manager`: CI/CD pipeline management

**Research Intelligence Instances**:
- `researcher_security_integration`: DevSecOps practices and CI/CD security integration
- `researcher_code_analysis`: Static/dynamic analysis and security pattern detection
- `researcher_automation_intelligence`: Automation frameworks and testing intelligence

**Available Tools**:
- `generate_language_template` - Generate code templates
- `inject_custom_code_blocks` - Inject custom code
- `validate_code_syntax` - Validate code syntax
- `deploy_docker_compose_stack` - Deploy Docker environments
- `generate_terraform_configuration` - Generate Terraform configs
- `validate_infrastructure_deployment` - Validate deployments
- `deploy_to_rtpi_pen` - Deploy to RTPI-Pen platform
- `push_code_to_attack_node` - Push to Attack Node
- `register_service_with_mcp_nexus` - Register with MCP Nexus
- `create_pipeline_configuration` - Create CI pipelines
- `execute_test_suite` - Run test suites
- `manage_deployment_workflow` - Manage deployments
- `research_devsecops_practices` - DevSecOps methodologies research
- `integrate_cicd_security` - CI/CD security integration research
- `research_security_testing_automation` - Automated security testing research
- `research_static_analysis_techniques` - Static code analysis research
- `analyze_security_patterns` - Security patterns and anti-patterns analysis
- `research_code_quality_metrics` - Code quality assessment research
- `research_testing_automation_intelligence` - Intelligent testing automation research
- `optimize_deployment_automation` - Deployment automation optimization
- `research_infrastructure_automation_intelligence` - Infrastructure automation research
- And 3 more specialized tools...

### 2. Bug Hunter Tools (6 instances, 18 tools)
**Purpose**: Web vulnerability testing, security analysis, and threat intelligence research

**Core Testing Instances**:
- `web_vulnerability_tester`: Web security testing
- `framework_security_analyzer`: Framework security analysis
- `vulnerability_report_generator`: Report generation

**Research Intelligence Instances**:
- `researcher_threat_intelligence`: Threat intelligence gathering and analysis
- `researcher_exploit_database`: Exploit research and analysis
- `researcher_vuln_context`: Vulnerability context and impact analysis

**Available Tools**:
- `analyze_cross_site_vulnerabilities` - XSS testing
- `evaluate_authentication_security` - Auth security testing
- `test_injection_vulnerabilities` - Injection testing
- `analyze_security_settings` - Security configuration analysis
- `detect_framework` - Framework detection
- `generate_security_recommendations` - Security recommendations
- `create_executive_summary` - Executive summaries
- `export_report_data` - Export reports
- `generate_comprehensive_report` - Full security reports
- `gather_threat_intelligence` - Threat intelligence research
- `research_vulnerability_context` - CVE context analysis
- `analyze_attack_patterns` - Attack technique analysis
- `search_exploit_database` - Exploit database research
- `analyze_exploit_code` - Exploit code analysis
- `research_exploit_techniques` - Exploitation method research
- `analyze_vulnerability_context` - Vulnerability impact analysis
- `research_attack_scenarios` - Attack scenario research
- `assess_business_impact` - Business impact evaluation

### 3. BurpSuite Operator Tools (7 instances, 35 tools)
**Purpose**: BurpSuite integration, automated scanning, and payload intelligence research

**Core Testing Instances**:
- `burp_suite_client`: BurpSuite API client
- `burp_scan_orchestrator`: Scan management
- `burp_result_processor`: Result processing
- `burp_vulnerability_assessor`: Risk assessment

**Research Intelligence Instances**:
- `researcher_payload_intelligence`: Payload research and evasion techniques
- `researcher_scan_enhancer`: Scan optimization and methodology enhancement
- `researcher_webapp_intelligence`: Web application intelligence and attack surface analysis

**Available Tools**:
- `establish_burp_connection` - Connect to BurpSuite
- `execute_burp_function` - Execute BurpSuite functions
- `export_burp_project` - Export projects
- `get_burp_configuration` - Get configurations
- `manage_burp_extensions` - Manage extensions
- `launch_automated_scan` - Start scans
- `track_scan_status` - Monitor scan progress
- `extract_scan_findings` - Extract results
- `classify_vulnerability_findings` - Classify vulnerabilities
- `calculate_vulnerability_risk` - Risk assessment
- `generate_executive_summary` - Executive summaries
- `research_payload_intelligence` - Payload effectiveness research
- `analyze_evasion_techniques` - WAF bypass research
- `optimize_payload_selection` - Target-specific payload optimization
- `research_scan_optimization` - Scan configuration research
- `analyze_coverage_gaps` - Scan coverage analysis
- `enhance_scan_methodology` - Methodology improvement research
- `research_web_app_intelligence` - Web application intelligence gathering
- `analyze_attack_surface` - Attack surface mapping
- `research_technology_vulnerabilities` - Technology stack vulnerability research
- And 14 more specialized tools...

### 4. Daedelu5 Tools (7 instances, 31 tools)
**Purpose**: Infrastructure as Code, compliance management, and governance intelligence research

**Core Management Instances**:
- `infrastructure_iac_manager`: IaC management
- `compliance_auditor`: Compliance auditing
- `security_policy_enforcer`: Policy enforcement
- `self_healing_integrator`: Self-healing systems

**Research Intelligence Instances**:
- `researcher_compliance_intelligence`: Compliance frameworks and regulatory research
- `researcher_policy_analyzer`: Security policy and governance analysis
- `researcher_risk_intelligence`: Risk intelligence and threat landscape analysis

**Available Tools**:
- `build_docker_compose_environment` - Build Docker environments
- `deploy_infrastructure_stack` - Deploy infrastructure
- `generate_terraform_modules` - Generate Terraform modules
- `audit_infrastructure_compliance` - Compliance auditing
- `check_regulatory_requirements` - Regulatory compliance
- `generate_compliance_report` - Compliance reports
- `enforce_security_baseline` - Security baselines
- `apply_hardening_configurations` - Security hardening
- `manage_access_controls` - Access control management
- `define_healing_rules` - Self-healing rules
- `research_compliance_frameworks` - Compliance framework research
- `analyze_regulatory_changes` - Regulatory updates analysis
- `assess_compliance_gaps` - Compliance gap identification
- `analyze_security_policies` - Security policy analysis
- `research_policy_effectiveness` - Policy effectiveness research
- `optimize_policy_framework` - Policy framework optimization
- `research_risk_intelligence` - Risk intelligence gathering
- `analyze_threat_landscape` - Threat landscape analysis
- `assess_business_risk_impact` - Business risk impact assessment
- And 12 more specialized tools...

### 5. Nexus-Kamuy Tools (7 instances, 37 tools)
**Purpose**: Multi-agent orchestration, collaboration, and workflow intelligence research

**Core Orchestration Instances**:
- `workflow_orchestrator`: Workflow management
- `agent_coordinator`: Agent coordination
- `task_scheduler`: Task scheduling
- `collaboration_manager`: Agent collaboration

**Research Intelligence Instances**:
- `researcher_workflow_optimization`: Workflow optimization and automation pattern research
- `researcher_task_intelligence`: Task analysis and resource optimization research
- `researcher_collaboration_enhancement`: Team collaboration and communication optimization research

**Available Tools**:
- `create_multi_agent_workflow` - Multi-agent workflows
- `execute_workflow_pipeline` - Execute workflows
- `coordinate_agent_handoffs` - Agent handoffs
- `delegate_task_to_agent` - Task delegation
- `coordinate_multi_agent_task` - Multi-agent coordination
- `schedule_task_execution` - Task scheduling
- `manage_task_priorities` - Priority management
- `establish_collaboration_session` - Collaboration sessions
- `facilitate_knowledge_sharing` - Knowledge sharing
- `synchronize_session_data` - Data synchronization
- `research_workflow_patterns` - Workflow patterns research
- `analyze_process_bottlenecks` - Process bottleneck analysis
- `optimize_automation_workflows` - Automation workflow optimization
- `analyze_task_performance` - Task performance analysis
- `research_resource_optimization` - Resource optimization research
- `analyze_task_prioritization` - Task prioritization analysis
- `research_team_dynamics` - Team dynamics research
- `optimize_communication_patterns` - Communication pattern optimization
- `enhance_knowledge_sharing` - Knowledge sharing enhancement
- And 18 more specialized tools...

## API Endpoints

### Core Endpoints

#### Health Check
```http
GET /health
```
**Response**:
```json
{
    "status": "healthy",
    "timestamp": "2025-08-15T10:00:53.339242",
    "version": "1.0.0",
    "agents_loaded": 19,
    "open_webui_endpoint": "https://chat.attck.nexus/"
}
```

#### List Available Agents and Tools
```http
GET /agents
```
**Response**: Complete agent catalog with instances and available tools

#### Execute Tool
```http
POST /execute
Content-Type: application/json
Authorization: Bearer <token>
```
**Request Body**:
```json
{
    "tool_name": "generate_language_template",
    "parameters": {
        "language": "python",
        "template_type": "fastapi",
        "include_tests": true
    },
    "agent": "rt_dev",
    "request_id": "optional-request-id"
}
```

**Response**:
```json
{
    "success": true,
    "result": "Generated template content...",
    "error": null,
    "agent": "rt_dev",
    "tool_name": "generate_language_template",
    "request_id": "optional-request-id",
    "timestamp": "2025-08-15T10:00:53.339242",
    "execution_time_ms": 150
}
```

### Agent-Specific Endpoints
- `/agents/rt_dev/*` - RT-Dev specific endpoints
- `/agents/bug_hunter/*` - Bug Hunter specific endpoints  
- `/agents/burpsuite_operator/*` - BurpSuite Operator specific endpoints
- `/agents/daedelu5/*` - Daedelu5 specific endpoints
- `/agents/nexus_kamuy/*` - Nexus-Kamuy specific endpoints

## Open WebUI Integration Steps

### 1. Configure External Tools in Open WebUI

Navigate to **Admin Settings > Tools > External Tools** in Open WebUI and add:

**Base Configuration**:
```json
{
    "name": "Agent Tool Bridge",
    "description": "Cybersecurity agent tools integration",
    "url": "http://localhost:8000",
    "headers": {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
}
```

### 2. Configure Individual Tools

For each agent category, create tool configurations:

**Example: RT-Dev Code Generator**:
```json
{
    "name": "Generate Code Template",
    "endpoint": "/execute",
    "method": "POST",
    "body": {
        "tool_name": "generate_language_template",
        "agent": "rt_dev",
        "parameters": {
            "language": "{language}",
            "template_type": "{template_type}",
            "include_tests": "{include_tests}"
        }
    },
    "parameters": [
        {
            "name": "language",
            "type": "select",
            "options": ["python", "javascript", "go", "rust"],
            "required": true
        },
        {
            "name": "template_type",
            "type": "select", 
            "options": ["fastapi", "flask", "express", "gin"],
            "required": true
        },
        {
            "name": "include_tests",
            "type": "boolean",
            "default": true
        }
    ]
}
```

**Example: Bug Hunter Vulnerability Scanner**:
```json
{
    "name": "Scan for Web Vulnerabilities",
    "endpoint": "/execute",
    "method": "POST",
    "body": {
        "tool_name": "test_injection_vulnerabilities",
        "agent": "bug_hunter",
        "parameters": {
            "target_url": "{target_url}",
            "scan_depth": "{scan_depth}",
            "include_blind": "{include_blind}"
        }
    },
    "parameters": [
        {
            "name": "target_url",
            "type": "string",
            "required": true,
            "description": "Target URL to scan"
        },
        {
            "name": "scan_depth",
            "type": "select",
            "options": ["shallow", "medium", "deep"],
            "default": "medium"
        },
        {
            "name": "include_blind",
            "type": "boolean",
            "default": false
        }
    ]
}
```

### 3. Authentication Configuration

The API requires bearer token authentication. Configure your token in the Open WebUI tool settings:

**Production Configuration (chat.attck.nexus)**:
```json
{
    "headers": {
        "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
        "Content-Type": "application/json"
    }
}
```

**Environment Variables**:
```bash
CHAT_NEXUS_BEARER=sk-755ea70d07874c7d9e0b46d3966eb145
AGENT_MCP_TOKEN=k0L4Fa3IxD9WEU5o_bmsySQiyKjQg-TEILgDX_v8
```

**Note**: The CHAT_NEXUS_BEARER token is for Agent Tool Bridge authentication, while AGENT_MCP_TOKEN provides Cloudflare zone access for c3s.nexus and attck.nexus domains.

### 4. Testing Integration

Use these test commands to verify integration:

```bash
# Test health endpoint
curl -X GET "http://localhost:8000/health"

# Test agent listing
curl -X GET "http://localhost:8000/agents"

# Test tool execution
curl -X POST "http://localhost:8000/execute" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "detect_framework",
    "agent": "bug_hunter", 
    "parameters": {"target_url": "https://example.com"}
  }'
```

## Environment Variables

Configure these environment variables for customization:

```bash
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=8000
OPEN_WEBUI_ENDPOINT=https://chat.attck.nexus/
LOG_LEVEL=INFO
CDB_PATH=  # Auto-detect Windows Debugging Tools
WINDBG_SYMBOLS_PATH=SRV*C:\Symbols*https://msdl.microsoft.com/download/symbols
```

## Troubleshooting

### Common Issues

1. **PowerShell Syntax Errors**: Use `;` instead of `&&` for command chaining
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Port Conflicts**: Change port with `--port` parameter
4. **CORS Issues**: Verify Open WebUI URL in CORS configuration
5. **Authentication Errors**: Check bearer token format

### Logs and Monitoring

- Server logs display in console during development mode
- Access API documentation at http://localhost:8000/docs
- Monitor health at http://localhost:8000/health
- Check agent status at http://localhost:8000/agents

## Security Considerations

- **Authentication**: Implement proper token validation for production
- **HTTPS**: Use HTTPS in production environments
- **Rate Limiting**: Consider implementing rate limiting
- **Input Validation**: All tool parameters are validated
- **Network Security**: Ensure secure communication between Open WebUI and bridge

## Support

For issues or questions:
1. Check the FastAPI documentation at `/docs`
2. Review agent logs for error details
3. Validate configuration with `--validate-only` flag
4. Test individual endpoints with curl or PowerShell
