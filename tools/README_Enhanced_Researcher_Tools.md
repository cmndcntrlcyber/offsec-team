# Enhanced Researcher Tools Documentation

## Overview

The Enhanced Researcher Tools represent a comprehensive optimization of the original research capabilities, transforming a basic research interface into a powerful multi-agent research orchestration platform that leverages the entire offsec-team infrastructure.

## Key Features

### 🚀 Multi-Endpoint Integration
- **Parallel Processing**: Simultaneous requests across `tools.attck.nexus`, `researcher.attck.nexus`, and `research-agent-mcp.attck-community.workers.dev`
- **Intelligent Routing**: Context-aware routing based on query complexity and requirements
- **Fallback Mechanisms**: Graceful degradation with sequential processing when parallel requests fail

### 🤖 Multi-Agent Coordination
- **Bug Hunter**: Advanced vulnerability scanning, framework detection, exploit database access
- **RT-Dev**: Infrastructure-as-code generation, CI/CD pipeline management, secure code templates
- **BurpSuite Operator**: Automated web application scanning, payload intelligence
- **Daedelu5**: Compliance auditing, policy enforcement, risk assessment
- **Nexus Kamuy**: Multi-agent workflow orchestration, task coordination

### 🧠 Intelligent Analysis
- **Complexity Assessment**: Automatic query complexity analysis (Simple → Moderate → Complex → Orchestrated)
- **Agent Selection**: Context-aware agent selection based on query content
- **Threat Intelligence**: Real-time correlation with multiple threat feeds
- **Cross-Endpoint Synthesis**: Intelligent aggregation of insights from multiple sources

### 🔄 Workflow Orchestration
- **Multi-Step Workflows**: Complex security assessment workflows
- **Real-Time Coordination**: Agent collaboration for comprehensive analysis
- **Automated Escalation**: Complexity-based workflow escalation

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Researcher Tools                    │
├─────────────────────────────────────────────────────────────────┤
│  Query Analysis & Context Creation                              │
│  ├── Complexity Assessment (Simple/Moderate/Complex/Orchestrated)│
│  ├── Agent Selection (Bug Hunter, RT-Dev, BurpSuite, etc.)     │
│  └── Thread Context Management                                 │
├─────────────────────────────────────────────────────────────────┤
│  Multi-Endpoint Parallel Processing                            │
│  ├── tools.attck.nexus        (Direct Tool Execution)         │
│  ├── researcher.attck.nexus   (Advanced Analysis)             │
│  └── research-agent-mcp       (MCP Research Capabilities)     │
├─────────────────────────────────────────────────────────────────┤
│  Response Aggregation & Synthesis                              │
│  ├── Cross-Endpoint Correlation                               │
│  ├── Threat Intelligence Extraction                           │
│  ├── Security Recommendations                                 │
│  └── Workflow Suggestions                                     │
├─────────────────────────────────────────────────────────────────┤
│  Specialized Agent Capabilities                                │
│  ├── 🔍 Bug Hunter: Vulnerability Assessment                  │
│  ├── 🛠️  RT-Dev: Infrastructure & Code Generation             │
│  ├── 🌐 BurpSuite: Web Application Testing                    │
│  ├── 📋 Daedelu5: Compliance & Risk Management                │
│  └── 🎯 Nexus Kamuy: Workflow Orchestration                   │
└─────────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Prerequisites
```bash
pip install requests pydantic asyncio websockets
```

### Configuration
```python
from tools.enhanced_researcher_tools import EnhancedResearcherTools, EndpointConfig

# Custom configuration
config = EndpointConfig(
    tools_api="https://tools.attck.nexus",
    researcher_api="https://researcher.attck.nexus", 
    mcp_research_agent="https://research-agent-mcp.attck-community.workers.dev",
    timeout=45,
    parallel_enabled=True
)

# Initialize enhanced tools
enhanced_tools = EnhancedResearcherTools(config=config)
```

## Usage Examples

### 1. Enhanced Web Search with Threat Intelligence

```python
result = enhanced_tools.enhanced_web_search(
    query="APT29 attack techniques 2024",
    max_results=15,
    include_threat_intel=True,
    analysis_depth="comprehensive",
    __user__={"id": "analyst_001", "name": "Security Analyst"}
)
```

**Output Features:**
- Multi-endpoint search across all research platforms
- Threat intelligence correlation
- Security recommendations
- Confidence scoring
- Cross-platform insight synthesis

### 2. Multi-Agent Vulnerability Assessment

```python
result = enhanced_tools.multi_agent_vulnerability_assessment(
    target_url="https://target-application.com",
    assessment_depth="comprehensive", 
    include_compliance_check=True,
    __user__={"id": "pentester_001"}
)
```

**Capabilities:**
- Parallel vulnerability scanning across multiple agents
- Framework detection and technology profiling
- Compliance gap analysis
- Risk scoring and prioritization
- Automated remediation recommendations

### 3. Orchestrated Security Workflow

```python
result = enhanced_tools.orchestrated_security_workflow(
    workflow_type="security_audit",
    target_scope="web_application_infrastructure",
    coordination_level="full",
    __user__={"id": "security_manager"}
)
```

**Workflow Features:**
- Multi-phase security assessment
- Agent coordination and task distribution
- Real-time collaboration between specialized agents
- Comprehensive reporting with executive summaries

### 4. Advanced Threat Intelligence Research

```python
result = enhanced_tools.advanced_threat_intelligence_research(
    indicators=["malicious-domain.com", "suspicious-hash-value"],
    threat_types=["malware", "apt", "vulnerability"],
    include_attribution=True,
    correlation_depth="deep",
    __user__={"id": "threat_analyst"}
)
```

**Intelligence Features:**
- Multi-source threat feed correlation
- Attribution analysis
- Attack pattern identification
- IOC enrichment and validation
- Risk assessment and scoring

### 5. Infrastructure Security Assessment

```python
result = enhanced_tools.infrastructure_security_assessment(
    infrastructure_config={
        "cloud_provider": "AWS",
        "services": ["EC2", "RDS", "S3"],
        "compliance_requirements": ["SOC2", "ISO27001"]
    },
    compliance_frameworks=["SOC2", "ISO27001", "PCI_DSS"],
    include_iac_analysis=True,
    __user__={"id": "compliance_officer"}
)
```

**Assessment Capabilities:**
- Infrastructure-as-Code security analysis
- Multi-framework compliance checking
- Security baseline enforcement
- Risk intelligence assessment
- Policy optimization recommendations

## Agent Capabilities

### 🔍 Bug Hunter Agent
**Specializations:**
- Framework and technology detection
- Injection vulnerability testing (SQL, NoSQL, LDAP, etc.)
- Cross-site scripting (XSS) analysis
- Authentication security evaluation
- Threat intelligence correlation
- Exploit database integration

**Tools:**
- `detect_framework`: Advanced framework fingerprinting
- `test_injection_vulnerabilities`: Comprehensive injection testing
- `analyze_cross_site_vulnerabilities`: XSS and CSRF analysis
- `evaluate_authentication_security`: Auth mechanism assessment
- `threat_intelligence_lookup`: Real-time threat correlation
- `exploit_database_search`: CVE and exploit research

### 🛠️ RT-Dev Agent
**Specializations:**
- Secure code template generation
- Infrastructure-as-Code (IaC) development
- CI/CD pipeline security integration
- Container and orchestration security
- Development workflow optimization

**Tools:**
- `generate_language_template`: Secure code scaffolding
- `deploy_docker_compose_stack`: Container deployment
- `generate_terraform_configuration`: IaC generation
- `ci_cd_pipeline_analysis`: Pipeline security assessment
- `security_integration_assessment`: DevSecOps evaluation

### 🌐 BurpSuite Operator Agent
**Specializations:**
- Automated web application scanning
- Advanced payload analysis
- Proxy configuration and management
- Web application intelligence gathering
- Scan result analysis and correlation

**Tools:**
- `launch_automated_scan`: Comprehensive web app scanning
- `establish_burp_connection`: Proxy setup and configuration
- `extract_scan_findings`: Result analysis and reporting
- `payload_intelligence_analysis`: Advanced payload optimization
- `web_app_intelligence_gathering`: Reconnaissance and profiling

### 📋 Daedelu5 Agent
**Specializations:**
- Multi-framework compliance auditing
- Regulatory requirement assessment
- Security baseline enforcement
- Risk intelligence and assessment
- Policy analysis and optimization

**Tools:**
- `audit_infrastructure_compliance`: Comprehensive compliance auditing
- `check_regulatory_requirements`: Regulatory assessment
- `enforce_security_baseline`: Baseline configuration enforcement
- `risk_intelligence_assessment`: Advanced risk analysis
- `policy_analysis_engine`: Policy optimization

### 🎯 Nexus Kamuy Agent
**Specializations:**
- Multi-agent workflow orchestration
- Task coordination and distribution
- Real-time agent collaboration
- Workflow optimization and intelligence
- Complex process automation

**Tools:**
- `create_multi_agent_workflow`: Workflow design and creation
- `coordinate_multi_agent_task`: Task distribution and coordination
- `establish_collaboration_session`: Real-time agent collaboration
- `workflow_optimization_engine`: Process optimization
- `task_intelligence_coordinator`: Intelligent task management

## Research Complexity Levels

### Simple (Basic Operations)
- Single-agent tasks
- Direct tool execution
- Basic information retrieval
- Standard vulnerability scans

**Example:** "Scan website for basic vulnerabilities"

### Moderate (Standard Analysis)
- Multi-tool coordination
- Cross-reference analysis
- Moderate complexity assessments
- Standard compliance checks

**Example:** "Analyze web application security posture"

### Complex (Advanced Assessment)
- Multi-agent coordination
- Deep analysis requirements
- Comprehensive assessments
- Advanced threat modeling

**Example:** "Comprehensive security audit with compliance assessment"

### Orchestrated (Multi-Phase Workflows)
- Full workflow orchestration
- Multi-agent collaboration
- End-to-end process automation
- Complex coordination requirements

**Example:** "Multi-step security assessment workflow with real-time agent coordination"

## Response Format

### Standard Response Structure
```
🚀 **[Operation Name] Complete**

**Thread ID:** `research_1234567890_abcd1234`
**Execution Time:** 2500ms
**Research Complexity:** complex
**Agents Involved:** bug_hunter, daedelu5, nexus_kamuy
**User:** security_analyst_001

**Executive Summary:**
Multi-endpoint research analysis completed across 3 platforms. 
Generated 15 findings with complex complexity analysis. 
Involved 3 specialized agents.

**Key Findings:**
• Critical SQL injection vulnerability identified
• Framework detected: React 18.2.0 with Express backend
• Compliance gaps found in authentication mechanisms
• Infrastructure hardening recommendations available

**Confidence Score:** 0.89/1.0

**Threat Intelligence:**
• Risk Score: 7.5/10.0
• Vulnerabilities Found: 3
• IOCs Identified: 2

**Security Recommendations:**
• Implement immediate patches for critical vulnerabilities
• Deploy web application firewall (WAF)
• Establish security testing in CI/CD pipeline
• Update security policies and procedures

**Workflow Suggestions:**
• Schedule regular security assessments
• Implement automated vulnerability scanning
• Establish incident response procedures

**Multi-Endpoint Analysis:** 3/3 endpoints successful
**Endpoints:** tools_api, researcher_api, mcp_agent

*Routed via: chat.attck.nexus → tools.attck.nexus → researcher.attck.nexus → research-agent-mcp.attck-community.workers.dev → chat.attck.nexus*
```

## Configuration Options

### EndpointConfig Parameters
```python
@dataclass
class EndpointConfig:
    tools_api: str = "https://tools.attck.nexus"
    researcher_api: str = "https://researcher.attck.nexus" 
    mcp_research_agent: str = "https://research-agent-mcp.attck-community.workers.dev"
    chat_return: str = "https://chat.attck.nexus"
    timeout: int = 45                    # Request timeout in seconds
    max_retries: int = 3                 # Maximum retry attempts
    parallel_enabled: bool = True        # Enable parallel processing
```

### Environment Variables
```bash
# Optional API keys and tokens
export RESEARCH_AGENT_TOKEN="your_token_here"
export OPENWEATHER_API_KEY="your_weather_api_key"

# Custom endpoint URLs
export TOOLS_API_URL="https://custom-tools.domain.com"
export RESEARCHER_API_URL="https://custom-researcher.domain.com"
```

## Error Handling & Resilience

### Automatic Fallbacks
1. **Parallel → Sequential**: Falls back to sequential processing if parallel requests fail
2. **Researcher → Tools**: Falls back to direct tool execution if researcher API unavailable
3. **Multi-Endpoint → Single**: Graceful degradation to single endpoint if others fail

### Error Response Format
```
❌ **[Operation Name] Failed**

Error: Connection timeout after 45 seconds
Thread: research_1234567890_abcd1234

**Failed Endpoints (2):**
- **researcher_api**: HTTP 503: Service Unavailable
- **mcp_agent**: Connection timeout

**Successful Endpoints (1):**
- **tools_api**: 1250ms execution time
```

### Retry Logic
- Exponential backoff for failed requests
- Configurable retry attempts (default: 3)
- Circuit breaker pattern for persistent failures

## Performance Optimization

### Parallel Processing
- Concurrent execution across all endpoints
- ThreadPoolExecutor for optimal resource utilization
- Configurable timeout and retry parameters

### Caching Strategy
- Session context caching for thread continuity
- Automatic cleanup of expired contexts
- Intelligent result caching for repeated queries

### Resource Management
- Connection pooling for HTTP requests
- Memory-efficient response aggregation
- Automatic garbage collection of old sessions

## Monitoring & Health Checks

### Infrastructure Status
```python
status = enhanced_tools.get_research_infrastructure_status()
```

**Provides:**
- Endpoint health status
- Response time metrics
- Agent capability status
- MCP connection status
- Configuration validation

### Performance Metrics
- Request execution times
- Success/failure rates
- Agent utilization statistics
- Endpoint performance comparison

## Integration Examples

### OpenWebUI Integration
```python
# tools.py - OpenWebUI Tools Integration
from tools.enhanced_researcher_tools import EnhancedResearcherTools

class Tools:
    def __init__(self):
        self.enhanced_researcher = EnhancedResearcherTools()
    
    def comprehensive_security_research(
        self, 
        query: str,
        research_type: str = "comprehensive",
        __user__: dict = {}
    ) -> str:
        """Enhanced security research with multi-agent coordination"""
        return self.enhanced_researcher.enhanced_web_search(
            query=query,
            analysis_depth=research_type,
            include_threat_intel=True,
            __user__=__user__
        )
```

### API Integration
```python
# FastAPI endpoint integration
from fastapi import FastAPI
from tools.enhanced_researcher_tools import EnhancedResearcherTools

app = FastAPI()
enhanced_tools = EnhancedResearcherTools()

@app.post("/research/vulnerability-assessment")
async def vulnerability_assessment(request: VulnAssessmentRequest):
    return enhanced_tools.multi_agent_vulnerability_assessment(
        target_url=request.target_url,
        assessment_depth=request.depth,
        include_compliance_check=request.compliance,
        __user__=request.user_context
    )
```

## Testing

### Running Tests
```bash
# Run comprehensive test suite
cd tools/
python test_enhanced_researcher_tools.py

# Run specific test categories
python -m unittest test_enhanced_researcher_tools.TestEnhancedResearcherTools
python -m unittest test_enhanced_researcher_tools.TestIntegrationScenarios
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-agent workflow testing
- **Performance Tests**: Load and response time testing
- **Error Handling Tests**: Failure scenario validation

### Mock Testing
All tests use comprehensive mocking to avoid external API dependencies:
- HTTP request mocking
- Response simulation
- Error condition testing
- Performance benchmarking

## Migration from Original Tools

### Backward Compatibility
The Enhanced Researcher Tools maintain full backward compatibility with the original Tools class:

```python
# Original methods still work
enhanced_tools.get_user_name_and_email_and_id(__user__)
enhanced_tools.get_current_time()
enhanced_tools.calculator("2 + 2")
enhanced_tools.get_current_weather("New York")
```

### Migration Steps
1. **Replace Import**: Update import statements
2. **Update Configuration**: Add endpoint configuration
3. **Enhance Calls**: Upgrade to enhanced methods for better capabilities
4. **Test Integration**: Validate functionality with existing workflows

### Feature Comparison

| Feature | Original Tools | Enhanced Tools |
|---------|---------------|----------------|
| Web Search | Basic single-endpoint | Multi-endpoint parallel processing |
| Vulnerability Assessment | Simple scanning | Multi-agent comprehensive assessment |
| Threat Intelligence | Limited correlation | Real-time multi-source correlation |
| Workflow Support | Manual coordination | Automated orchestration |
| Error Handling | Basic try/catch | Advanced resilience patterns |
| Performance | Sequential processing | Parallel multi-endpoint |
| Agent Integration | None | 5 specialized agents |
| Compliance Support | None | Multi-framework auditing |

## Troubleshooting

### Common Issues

#### 1. Connection Timeouts
**Symptoms:** Requests timing out after 45 seconds
**Solutions:**
- Increase timeout in configuration
- Check network connectivity to endpoints
- Verify endpoint URLs are correct

#### 2. Authentication Errors
**Symptoms:** HTTP 401/403 responses
**Solutions:**
- Verify API tokens are set correctly
- Check token permissions and expiration
- Validate endpoint authentication requirements

#### 3. Parallel Processing Failures
**Symptoms:** All parallel requests failing
**Solutions:**
- Disable parallel processing temporarily
- Check individual endpoint health
- Review network firewall settings

#### 4. Agent Selection Issues
**Symptoms:** Wrong agents selected for queries
**Solutions:**
- Review query keywords and phrasing
- Check agent determination logic
- Use explicit agent specification if needed

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

enhanced_tools = EnhancedResearcherTools()
```

### Health Check Commands
```python
# Check infrastructure status
status = enhanced_tools.get_research_infrastructure_status()
print(status)

# Validate configuration
config = enhanced_tools.config
print(f"Parallel enabled: {config.parallel_enabled}")
print(f"Timeout: {config.timeout}s")
```

## Contributing

### Development Setup
```bash
git clone https://github.com/cmndcntrlcyber/offsec-team.git
cd offsec-team/tools/
pip install -r requirements.txt
```

### Adding New Agents
1. Define agent capability in `AgentCapability` enum
2. Add agent tools in `_initialize_agent_capabilities()`
3. Update agent determination logic in `_determine_required_agents()`
4. Add agent-specific recommendations in `_generate_security_recommendations()`
5. Create comprehensive tests for new agent

### Adding New Endpoints
1. Update `EndpointConfig` with new endpoint URL
2. Add request preparation method (`_prepare_[endpoint]_request()`)
3. Update parallel request configuration
4. Add endpoint-specific response handling
5. Update health check monitoring

## License

This enhanced research infrastructure is part of the offsec-team project and follows the same licensing terms as the parent project.

## Support

For issues, feature requests, or contributions:
- GitHub Issues: [offsec-team/issues](https://github.com/cmndcntrlcyber/offsec-team/issues)
- Documentation: [offsec-team/docs](https://github.com/cmndcntrlcyber/offsec-team/tree/main/docs)
- Community: [attck.nexus](https://attck.nexus)

---

**Enhanced Researcher Tools v2.0** - Transforming research capabilities through multi-agent orchestration and intelligent workflow automation.
