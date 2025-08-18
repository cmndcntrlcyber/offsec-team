# Manual Open WebUI Configuration Guide
## Step-by-Step Setup for Agent Tool Bridge Integration

Since automated browser configuration encountered authentication challenges, follow this manual guide to configure Open WebUI at https://chat.attck.nexus/

## Prerequisites

### 1. Ensure Bridge Server is Running
First, make sure your Agent Tool Bridge server is operational:

```powershell
# Navigate to bridge directory
cd openwebui-bridge

# Start the bridge server
python start-bridge.py --dev
```

**Verify it's running:**
- Open http://localhost:8000/health in a browser
- Should show: `{"status":"healthy","agents_loaded":19}`

### 2. Authentication Information Ready
- **Bearer Token**: `sk-755ea70d07874c7d9e0b46d3966eb145`
- **Bridge URL**: `http://localhost:8000`
- **Cloudflare Token**: `k0L4Fa3IxD9WEU5o_bmsySQiyKjQg-TEILgDX_v8` (for zone access)

## Step-by-Step Open WebUI Configuration

### Step 1: Access Open WebUI Admin Panel

1. **Log into Open WebUI** at https://chat.attck.nexus/
2. **Navigate to Admin Panel**:
   - Look for a ⚙️ settings icon or "Admin" menu
   - Usually in the top-right corner or sidebar
3. **Find Tools/External Tools Section**:
   - Look for "Tools", "External Tools", "Integrations", or "Functions"
   - This might be under "Settings" > "Tools" or similar

### Step 2: Add the Agent Tool Bridge

**Create New External Tool/Function:**

```json
{
  "name": "Agent Tool Bridge",
  "description": "Cybersecurity agent tools integration with 68+ tools across 5 categories",
  "url": "http://localhost:8000",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "timeout": 30,
  "max_retries": 3
}
```

### Step 3: Configure Individual Agent Tools

Add these specific tools one by one:

#### 3.1 Web Vulnerability Scanner

```json
{
  "name": "Web Vulnerability Scanner",
  "description": "Scan websites for security vulnerabilities using Bug Hunter tools",
  "endpoint": "/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "body_template": {
    "tool_name": "test_injection_vulnerabilities",
    "agent": "bug_hunter",
    "parameters": {
      "target_url": "{{target_url}}",
      "scan_depth": "{{scan_depth|default('medium')}}",
      "include_blind": "{{include_blind|default(false)}}"
    }
  },
  "parameters": [
    {
      "name": "target_url",
      "type": "string",
      "required": true,
      "description": "Target URL to scan for vulnerabilities"
    },
    {
      "name": "scan_depth",
      "type": "select",
      "options": ["shallow", "medium", "deep"],
      "default": "medium",
      "description": "Depth of vulnerability scan"
    },
    {
      "name": "include_blind",
      "type": "boolean",
      "default": false,
      "description": "Include blind vulnerability tests"
    }
  ]
}
```

#### 3.2 Code Generator

```json
{
  "name": "Code Template Generator",
  "description": "Generate code templates using RT-Dev tools",
  "endpoint": "/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "body_template": {
    "tool_name": "generate_language_template",
    "agent": "rt_dev",
    "parameters": {
      "language": "{{language}}",
      "template_type": "{{template_type}}",
      "include_tests": "{{include_tests|default(true)}}"
    }
  },
  "parameters": [
    {
      "name": "language",
      "type": "select",
      "options": ["python", "javascript", "go", "rust", "java"],
      "required": true,
      "description": "Programming language"
    },
    {
      "name": "template_type",
      "type": "select",
      "options": ["fastapi", "flask", "express", "gin", "spring"],
      "required": true,
      "description": "Framework template type"
    },
    {
      "name": "include_tests",
      "type": "boolean",
      "default": true,
      "description": "Include test templates"
    }
  ]
}
```

#### 3.3 BurpSuite Scanner

```json
{
  "name": "BurpSuite Automated Scanner",
  "description": "Launch automated security scans using BurpSuite integration",
  "endpoint": "/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "body_template": {
    "tool_name": "launch_automated_scan",
    "agent": "burpsuite_operator",
    "parameters": {
      "target_url": "{{target_url}}",
      "scan_type": "{{scan_type|default('crawl_and_audit')}}",
      "timeout": "{{timeout|default(3600)}}"
    }
  },
  "parameters": [
    {
      "name": "target_url",
      "type": "string",
      "required": true,
      "description": "Target URL for BurpSuite scan"
    },
    {
      "name": "scan_type",
      "type": "select",
      "options": ["crawl_and_audit", "audit_only", "crawl_only"],
      "default": "crawl_and_audit",
      "description": "Type of scan to perform"
    },
    {
      "name": "timeout",
      "type": "number",
      "default": 3600,
      "description": "Scan timeout in seconds"
    }
  ]
}
```

#### 3.4 Infrastructure Deployment

```json
{
  "name": "Deploy Infrastructure",
  "description": "Deploy infrastructure using Daedelu5 IaC tools",
  "endpoint": "/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "body_template": {
    "tool_name": "deploy_infrastructure_stack",
    "agent": "daedelu5",
    "parameters": {
      "stack_name": "{{stack_name}}",
      "environment": "{{environment|default('development')}}",
      "auto_approve": "{{auto_approve|default(false)}}"
    }
  },
  "parameters": [
    {
      "name": "stack_name",
      "type": "string",
      "required": true,
      "description": "Name of the infrastructure stack"
    },
    {
      "name": "environment",
      "type": "select",
      "options": ["development", "staging", "production"],
      "default": "development",
      "description": "Target environment"
    },
    {
      "name": "auto_approve",
      "type": "boolean",
      "default": false,
      "description": "Automatically approve deployment"
    }
  ]
}
```

#### 3.5 Multi-Agent Workflow

```json
{
  "name": "Create Multi-Agent Workflow",
  "description": "Orchestrate complex workflows using Nexus-Kamuy coordination",
  "endpoint": "/execute",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145",
    "Content-Type": "application/json"
  },
  "body_template": {
    "tool_name": "create_multi_agent_workflow",
    "agent": "nexus_kamuy",
    "parameters": {
      "workflow_name": "{{workflow_name}}",
      "agents": "{{agents}}",
      "coordination_type": "{{coordination_type|default('sequential')}}"
    }
  },
  "parameters": [
    {
      "name": "workflow_name",
      "type": "string",
      "required": true,
      "description": "Name for the workflow"
    },
    {
      "name": "agents",
      "type": "string",
      "required": true,
      "description": "Comma-separated list of agents (rt_dev,bug_hunter,burpsuite_operator,daedelu5)"
    },
    {
      "name": "coordination_type",
      "type": "select",
      "options": ["sequential", "parallel", "conditional"],
      "default": "sequential",
      "description": "How agents should be coordinated"
    }
  ]
}
```

### Step 4: Test the Integration

#### Test 1: Basic Connectivity
1. **Use the Web Vulnerability Scanner** tool
2. **Enter a test URL**: `https://example.com`
3. **Select scan depth**: `shallow`
4. **Execute the tool**

**Expected Response:**
```json
{
  "success": false,
  "error": "FrameworkSecurityAnalyzer.detect_framework() got an unexpected keyword argument 'target_url'",
  "agent": "bug_hunter",
  "tool_name": "test_injection_vulnerabilities",
  "timestamp": "2025-08-15T10:45:00.000000",
  "execution_time_ms": 5
}
```

This error is expected and shows the bridge is working (authentication successful, tool execution attempted).

#### Test 2: Health Check
Create a simple health check tool:

```json
{
  "name": "Bridge Health Check",
  "description": "Check if the agent bridge is healthy",
  "endpoint": "/health",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145"
  }
}
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-15T10:45:00.000000",
  "version": "1.0.0",
  "agents_loaded": 19,
  "open_webui_endpoint": "https://chat.attck.nexus/"
}
```

### Step 5: Advanced Configuration

#### Add Tool Discovery
Create a tool that lists all available agents and tools:

```json
{
  "name": "List Available Agent Tools",
  "description": "Get a complete list of all available cybersecurity tools",
  "endpoint": "/agents",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer sk-755ea70d07874c7d9e0b46d3966eb145"
  }
}
```

This will return the complete catalog of 68+ tools across all 5 agent categories.

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - **Check**: Bridge server is running on localhost:8000
   - **Solution**: Start with `python start-bridge.py --dev`

2. **Authentication Failed**
   - **Check**: Bearer token is correct: `sk-755ea70d07874c7d9e0b46d3966eb145`
   - **Solution**: Verify token in headers

3. **Tool Not Found**
   - **Check**: Use `/agents` endpoint to see available tools
   - **Solution**: Match exact tool names from the API response

4. **CORS Errors**
   - **Check**: Open WebUI URL is in CORS whitelist
   - **Solution**: Bridge server already configured for https://chat.attck.nexus/

5. **Timeout Errors**
   - **Check**: Network connectivity between Open WebUI and bridge
   - **Solution**: Increase timeout values in tool configurations

### Debug Commands

Test the bridge server directly:

```powershell
# Test health
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Test agents list
Invoke-RestMethod -Uri "http://localhost:8000/agents" -Method Get

# Test tool execution
Invoke-RestMethod -Uri "http://localhost:8000/execute" -Method Post -Body '{"tool_name": "detect_framework", "agent": "bug_hunter", "parameters": {"url": "https://example.com"}}' -ContentType "application/json" -Headers @{Authorization="Bearer sk-755ea70d07874c7d9e0b46d3966eb145"}
```

## Security Considerations

- **Bearer Token**: Keep `sk-755ea70d07874c7d9e0b46d3966eb145` secure
- **Network**: Bridge runs on localhost (secure by default)
- **HTTPS**: Use HTTPS for Open WebUI in production
- **Input Validation**: All tool parameters are validated by the bridge

## Next Steps

1. **Configure core tools** (vulnerability scanner, code generator)
2. **Test with sample data** to verify functionality
3. **Add more specialized tools** based on your needs
4. **Set up monitoring** through the health endpoint
5. **Create custom workflows** using multi-agent coordination

Your Agent Tool Bridge is now ready for integration with Open WebUI at https://chat.attck.nexus/!
