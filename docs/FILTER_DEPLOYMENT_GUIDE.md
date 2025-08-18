# Offsec Team Tools Auto-Router Filter Deployment Guide

This guide explains how to deploy and configure the intelligent routing filter for Open WebUI at https://chat.attck.nexus/

## Overview

The `intelligent_routing_filter.py` automatically detects user intent and routes requests to the appropriate offsec-team tools without requiring manual specification. It connects to `https://tools.attck.nexus` and provides seamless access to 115+ cybersecurity tools across 5 agent categories.

## Installation Steps

### Step 1: Upload Filter to Open WebUI

1. **Access Admin Panel**
   - Navigate to https://chat.attck.nexus/
   - Login as administrator
   - Go to **Admin Settings** → **Functions** → **Filters**

2. **Add New Filter**
   - Click **"+ Add Filter"**
   - Copy the entire contents of `intelligent_routing_filter.py`
   - Paste into the code editor
   - Click **"Save"**

### Step 2: Configure Filter Settings

The filter includes configurable settings (Valves):

**Global Settings (Admin Only):**
```python
api_base_url = "https://tools.attck.nexus"  # Tools API endpoint
bearer_token = "sk-755ea70d07874c7d9e0b46d3966eb145"  # API authentication
enable_auto_routing = True  # Enable automatic tool routing
debug_mode = False  # Enable for troubleshooting
max_turns = 50  # Maximum conversation turns
priority = 10  # Filter priority level
```

**User Settings (Per User):**
```python
enable_tools = True  # Allow user to access offsec tools
max_turns = 25  # Maximum conversation turns for user
```

### Step 3: Activate Filter

1. **Enable Filter**
   - Toggle the filter to **"Active"** status
   - Ensure priority is set appropriately (10 is recommended)
   - Save changes

2. **Test Basic Functionality**
   - Start a new conversation
   - Send a test message: `"scan https://example.com for vulnerabilities"`
   - The filter should automatically detect this as a Bug Hunter request

## Usage Examples

The filter automatically routes requests based on detected intent:

### Bug Hunter Tools
**User Input:** "Scan this website for SQL injection: https://example.com"
**Auto-Route:** `bug_hunter.test_injection_vulnerabilities`

**User Input:** "Find XSS vulnerabilities on my site"
**Auto-Route:** `bug_hunter.analyze_cross_site_vulnerabilities`

### RT-Dev Tools  
**User Input:** "Generate a Python FastAPI template with tests"
**Auto-Route:** `rt_dev.generate_language_template`

**User Input:** "Deploy this with Docker Compose"
**Auto-Route:** `rt_dev.deploy_docker_compose_stack`

### BurpSuite Operator Tools
**User Input:** "Launch a Burp scan on https://target.com"
**Auto-Route:** `burpsuite_operator.launch_automated_scan`

**User Input:** "Connect to Burp Suite proxy"
**Auto-Route:** `burpsuite_operator.establish_burp_connection`

### Daedelu5 Tools
**User Input:** "Audit our infrastructure for SOC2 compliance"
**Auto-Route:** `daedelu5.audit_infrastructure_compliance`

**User Input:** "Check regulatory requirements for PCI DSS"
**Auto-Route:** `daedelu5.check_regulatory_requirements`

### Nexus-Kamuy Tools
**User Input:** "Create a multi-agent workflow for testing"
**Auto-Route:** `nexus_kamuy.create_multi_agent_workflow`

**User Input:** "Coordinate agents for vulnerability assessment"
**Auto-Route:** `nexus_kamuy.coordinate_multi_agent_task`

## Intent Detection Logic

The filter uses multiple detection methods:

### 1. Keyword Patterns
- **Security Keywords:** vulnerability, exploit, pentest, security audit, xss, sql injection
- **Development Keywords:** generate code, fastapi, docker, terraform, deployment, ci/cd
- **Testing Keywords:** burp scan, proxy, automated scan, payload testing
- **Compliance Keywords:** audit, policy, soc2, iso27001, pci dss, gdpr
- **Workflow Keywords:** orchestration, coordination, multi-agent, pipeline

### 2. URL Detection
Automatically extracts URLs from messages and passes as `target_url` parameter

### 3. Parameter Extraction
- **Languages:** python, javascript, go, rust, java, typescript
- **Frameworks:** fastapi, flask, express, gin
- **Scan Depths:** shallow, medium, deep
- **Compliance Frameworks:** SOC2, ISO27001, PCI_DSS

### 4. Context Analysis
Analyzes conversation history and current message for better intent detection

## Response Format

Tool responses are formatted for natural conversation:

```
✅ **Bug-Hunter Tool Executed Successfully**

**Tool:** `test_injection_vulnerabilities`
**Execution Time:** 1250ms

**Results:**
- **Vulnerabilities Found:** 3
- **Critical Issues:** 1
- **Recommendations:** ["Fix SQL injection in login form", "Update input validation"]
```

## Troubleshooting

### Common Issues

1. **Filter Not Activating**
   - Check filter is set to "Active" status
   - Verify priority setting (should be 10 or higher)
   - Ensure no other filters are conflicting

2. **API Connection Errors**
   - Verify `https://tools.attck.nexus` is accessible
   - Check bearer token is correct
   - Enable debug mode to see detailed logs

3. **Intent Not Detected**
   - Use more specific keywords (scan, test, generate, deploy, audit)
   - Include URLs when relevant
   - Try explicit agent names (bug hunter, rt-dev, burp, compliance, workflow)

4. **Tool Execution Failures**
   - Check if bridge server is running on port 8001
   - Verify tool parameters are correctly extracted
   - Review execution logs in debug mode

### Debug Mode

Enable debug mode for troubleshooting:

```python
debug_mode = True
```

This will log:
- Intent detection results
- Tool selection decisions
- API requests and responses
- Parameter extraction details

### Testing Filter Status

Use these test phrases to verify filter functionality:

```
"Test security scan on https://example.com"          # Should trigger Bug Hunter
"Generate Python FastAPI code"                       # Should trigger RT-Dev  
"Launch Burp Suite scan"                            # Should trigger BurpSuite
"Check SOC2 compliance"                             # Should trigger Daedelu5
"Create workflow automation"                         # Should trigger Nexus-Kamuy
```

## Security Considerations

1. **Authentication**
   - Bearer token is required for all API calls
   - Token is configured in filter settings (not exposed to users)

2. **User Permissions**
   - Users can disable tool access via UserValves
   - Administrators can disable auto-routing globally
   - Turn limits prevent excessive API usage

3. **Input Validation**
   - All parameters are validated before API calls
   - URL extraction uses secure regex patterns
   - API responses are sanitized before display

## Maintenance

### Regular Checks
- Monitor filter performance and response times
- Review API usage patterns
- Update bearer token as needed
- Check for new tool additions in the bridge

### Updates
- Filter automatically discovers new tools via `/agents` endpoint
- No manual configuration needed for new tool additions
- Update filter code for new intent patterns or improvements

## Support

For issues or questions:
1. Check debug logs with debug mode enabled
2. Verify API endpoint accessibility at https://tools.attck.nexus/health
3. Test individual tools via direct API calls
4. Review conversation patterns that aren't being detected
