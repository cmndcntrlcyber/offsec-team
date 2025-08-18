# Open WebUI Bridge for Offsec Team Tools

Complete integration package for connecting Open WebUI at https://chat.attck.nexus/ to the offsec-team cybersecurity tools ecosystem via https://tools.attck.nexus.

## 🎯 Overview

This bridge provides seamless integration between Open WebUI and 115+ cybersecurity tools across 5 agent categories:

- **Bug Hunter** (18 tools) - Web vulnerability testing and security analysis
- **RT-Dev** (24 tools) - Code generation, infrastructure deployment, DevSecOps
- **BurpSuite Operator** (35 tools) - Automated scanning and payload intelligence  
- **Daedelu5** (31 tools) - Infrastructure as Code and compliance management
- **Nexus-Kamuy** (37 tools) - Multi-agent orchestration and workflow management

## 🚀 Quick Start

### 1. Deploy the Filter

1. **Copy Filter Code**
   ```bash
   cat intelligent_routing_filter.py
   ```

2. **Upload to Open WebUI**
   - Navigate to https://chat.attck.nexus/
   - Go to **Admin Settings** → **Functions** → **Filters**
   - Click **"+ Add Filter"**
   - Paste the filter code and save

3. **Activate Filter**
   - Enable the filter (set to Active)
   - Set priority to 10
   - Verify configuration

### 2. Test Integration

```bash
cd /home/cmndcntrl/code/offsec-team/openwebui-bridge
python test_filter_integration.py
```

### 3. Start Using Tools

Simply chat naturally with tool-related requests:

- **"Scan https://example.com for vulnerabilities"** → Bug Hunter tools
- **"Generate a Python FastAPI template"** → RT-Dev tools  
- **"Launch a Burp Suite scan"** → BurpSuite Operator tools
- **"Audit our infrastructure for compliance"** → Daedelu5 tools
- **"Create a workflow for testing"** → Nexus-Kamuy tools

## 📁 File Structure

```
openwebui-bridge/
├── README.md                           # This file
├── intelligent_routing_filter.py       # Main filter implementation
├── FILTER_DEPLOYMENT_GUIDE.md         # Detailed deployment instructions
├── test_filter_integration.py         # Integration test suite
├── main.py                            # FastAPI bridge server
├── .env                               # Environment configuration
├── OPEN_WEBUI_INTEGRATION_GUIDE.md    # Complete integration guide
└── routers/                           # Agent-specific API routes
    ├── bug_hunter_router.py
    ├── rt_dev_router.py
    ├── burpsuite_router.py
    ├── daedelu5_router.py
    └── nexus_kamuy_router.py
```

## 🔧 Architecture

```
┌─────────────────┐    HTTPS    ┌─────────────────┐    HTTP    ┌─────────────────┐
│ Open WebUI      │   ──────>   │ tools.attck.    │  ──────>   │ Bridge Server   │
│ chat.attck.nexus│   Filter    │ nexus (Proxy)   │   8001     │ localhost:8001  │
└─────────────────┘             └─────────────────┘            └─────────────────┘
                                                                        │
                                                               ┌─────────────────┐
                                                               │ Offsec Tools    │
                                                               │ • Bug Hunter    │
                                                               │ • RT-Dev        │
                                                               │ • BurpSuite     │
                                                               │ • Daedelu5      │
                                                               │ • Nexus-Kamuy   │
                                                               └─────────────────┘
```

## 🤖 Intelligent Routing

The filter automatically detects user intent using:

### Intent Detection Patterns
- **Security Keywords**: vulnerability, exploit, pentest, xss, sql injection
- **Development Keywords**: generate code, fastapi, docker, terraform, ci/cd
- **Testing Keywords**: burp scan, automated scan, payload testing  
- **Compliance Keywords**: audit, policy, soc2, iso27001, pci dss
- **Workflow Keywords**: orchestration, multi-agent, coordination

### Parameter Extraction
- **URLs**: Automatically extracted and passed as `target_url`
- **Languages**: python, javascript, go, rust, java, typescript
- **Frameworks**: fastapi, flask, express, gin
- **Scan Types**: shallow, medium, deep
- **Compliance Standards**: SOC2, ISO27001, PCI_DSS

### Smart Tool Selection
```python
"Find XSS vulnerabilities" → bug_hunter.analyze_cross_site_vulnerabilities
"Generate Python API code" → rt_dev.generate_language_template  
"Launch automated scan" → burpsuite_operator.launch_automated_scan
"Check SOC2 compliance" → daedelu5.audit_infrastructure_compliance
"Create workflow pipeline" → nexus_kamuy.create_multi_agent_workflow
```

## 🔒 Security Features

- **Bearer Token Authentication**: All API calls use secure token authentication
- **Input Validation**: Parameters validated before execution
- **User Permissions**: Per-user tool access controls
- **Rate Limiting**: Conversation turn limits prevent abuse
- **HTTPS Communication**: Secure communication throughout the chain

## 🧪 Testing

### Automated Test Suite

```bash
# Run all integration tests
python test_filter_integration.py

# Tests include:
# ✅ API Connectivity
# ✅ Agents Endpoint  
# ✅ Intent Detection
# ✅ Parameter Extraction
# ✅ Tool Selection
# ✅ Live API Calls
# ✅ Filter Processing
```

### Manual Testing

Use these phrases to test functionality:

```
"Test security scan on https://example.com"          # Bug Hunter
"Generate Python FastAPI code"                       # RT-Dev
"Launch Burp Suite scan"                            # BurpSuite  
"Check SOC2 compliance"                             # Daedelu5
"Create workflow automation"                         # Nexus-Kamuy
```

## 📊 Available Tools

### Bug Hunter Tools (18 total)
- `analyze_cross_site_vulnerabilities` - XSS detection
- `test_injection_vulnerabilities` - SQL injection testing
- `evaluate_authentication_security` - Auth security analysis
- `detect_framework` - Technology detection
- `research_threat_intelligence` - Threat intelligence gathering
- And 13 more specialized security tools...

### RT-Dev Tools (24 total)  
- `generate_language_template` - Code template generation
- `deploy_docker_compose_stack` - Docker deployment
- `generate_terraform_configuration` - Infrastructure as Code
- `research_devsecops_practices` - DevSecOps methodologies
- `analyze_security_patterns` - Security pattern analysis
- And 19 more development and security tools...

### BurpSuite Operator Tools (35 total)
- `launch_automated_scan` - Automated vulnerability scanning
- `establish_burp_connection` - Proxy connection management
- `extract_scan_findings` - Results processing
- `research_payload_intelligence` - Payload effectiveness research
- `analyze_evasion_techniques` - WAF bypass research
- And 30 more scanning and testing tools...

### Daedelu5 Tools (31 total)
- `audit_infrastructure_compliance` - Compliance auditing
- `check_regulatory_requirements` - Regulatory compliance
- `enforce_security_baseline` - Security hardening
- `research_compliance_frameworks` - Compliance research
- `analyze_threat_landscape` - Risk intelligence
- And 26 more governance and compliance tools...

### Nexus-Kamuy Tools (37 total)
- `create_multi_agent_workflow` - Workflow orchestration
- `coordinate_multi_agent_task` - Task coordination
- `establish_collaboration_session` - Team collaboration
- `research_workflow_patterns` - Process optimization
- `analyze_task_performance` - Performance analysis
- And 32 more orchestration and collaboration tools...

## ⚙️ Configuration

### Environment Variables
```bash
BRIDGE_HOST=0.0.0.0
BRIDGE_PORT=8001  
OPEN_WEBUI_ENDPOINT=https://chat.attck.nexus/
CHAT_NEXUS_BEARER=sk-755ea70d07874c7d9e0b46d3966eb145
API_BASE_URL=https://tools.attck.nexus
```

### Filter Settings (Valves)
```python
api_base_url = "https://tools.attck.nexus"
bearer_token = "sk-755ea70d07874c7d9e0b46d3966eb145"  
enable_auto_routing = True
debug_mode = False
max_turns = 50
priority = 10
```

## 🛠️ Maintenance

### Regular Checks
- Monitor filter performance and response times
- Review API usage patterns and rate limits
- Update bearer tokens as needed
- Check for new tool additions

### Troubleshooting
- Enable `debug_mode = True` for detailed logging
- Check API connectivity: `curl https://tools.attck.nexus/health`
- Verify bearer token authentication
- Review conversation patterns not being detected

## 📚 Documentation

- **[FILTER_DEPLOYMENT_GUIDE.md](FILTER_DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[OPEN_WEBUI_INTEGRATION_GUIDE.md](OPEN_WEBUI_INTEGRATION_GUIDE.md)** - Full integration guide
- **[test_filter_integration.py](test_filter_integration.py)** - Test suite with examples

## 🎉 Usage Examples

### Security Testing
```
User: "Scan https://myapp.com for SQL injection vulnerabilities"

Filter: Detects bug_hunter intent → test_injection_vulnerabilities
API Call: POST https://tools.attck.nexus/execute
Response: ✅ Bug-Hunter Tool Executed Successfully
         Found 2 potential SQL injection points...
```

### Code Generation
```
User: "Create a Python FastAPI service with authentication"

Filter: Detects rt_dev intent → generate_language_template  
API Call: POST https://tools.attck.nexus/execute
Response: ✅ RT-Dev Tool Executed Successfully
         Generated FastAPI template with JWT auth...
```

### Compliance Auditing
```
User: "Audit our AWS infrastructure for SOC2 Type II compliance"

Filter: Detects daedelu5 intent → audit_infrastructure_compliance
API Call: POST https://tools.attck.nexus/execute  
Response: ✅ Daedelu5 Tool Executed Successfully
         Found 3 compliance gaps requiring attention...
```

## 🤝 Support

For issues or questions:
1. Check debug logs with `debug_mode = True`
2. Verify API health: https://tools.attck.nexus/health
3. Test individual components with the test suite
4. Review intent detection patterns and keywords

---

**Ready to deploy!** 🚀 The intelligent routing filter provides seamless access to the full offsec-team tools ecosystem through natural conversation in Open WebUI.
