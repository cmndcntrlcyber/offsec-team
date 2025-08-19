import { Hono } from 'hono';
import { cors } from 'hono/cors';

interface Env {
  TOOL_CACHE: KVNamespace;
  API_KEYS: KVNamespace;
  USER_SESSIONS: KVNamespace;
  RATE_LIMITS: KVNamespace;
  ANALYTICS: KVNamespace;
  TOOL_LOGS: R2Bucket;
  TOOL_DATA: R2Bucket;
  TEMP_STORAGE: R2Bucket;
  TOOL_SESSION: DurableObjectNamespace;
  AI: Ai;
  BACKEND_URL: string;
  ENVIRONMENT: string;
}

export { ToolSession } from './durable-objects/ToolSession';

const app = new Hono<{ Bindings: Env }>();

// CORS configuration - Allow all origins
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));

// Health check endpoint
app.get('/health', async (c) => {
  return c.json({
    status: 'healthy',
    service: 'offsec-team-worker',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: c.env.ENVIRONMENT
  });
});

// OpenAPI specification endpoint
app.get('/openapi.json', async (c) => {
  // Static OpenAPI spec with updated server URLs
  const openApiSpec = {
    "openapi": "3.0.2",
    "info": {
      "title": "Cybersecurity Agent Tool Bridge",
      "description": "Complete cybersecurity agent ecosystem with 68+ tools across 5 categories for Open WebUI integration",
      "version": "1.0.0",
      "contact": {
        "name": "ATTCK Nexus",
        "url": "https://attck.nexus"
      }
    },
    "servers": [
      {
        "url": "https://offsec-team.attck.community.workers.dev",
        "description": "Cloudflare Worker endpoint"
      },
      {
        "url": c.env.BACKEND_URL,
        "description": "Backend service"
      }
    ],
    "security": [
      {
        "HTTPBearer": []
      }
    ],
    "components": {
      "securitySchemes": {
        "HTTPBearer": {
          "type": "http",
          "scheme": "bearer"
        }
      },
      "schemas": {
        "ToolRequest": {
          "type": "object",
          "required": ["tool_name", "agent"],
          "properties": {
            "tool_name": {
              "type": "string",
              "description": "Name of the tool to execute",
              "examples": ["test_injection_vulnerabilities", "generate_language_template", "launch_automated_scan"]
            },
            "parameters": {
              "type": "object",
              "additionalProperties": true,
              "description": "Tool parameters"
            },
            "agent": {
              "type": "string",
              "enum": ["rt_dev", "bug_hunter", "burpsuite_operator", "daedelu5", "nexus_kamuy"],
              "description": "Target agent"
            },
            "request_id": {
              "type": "string",
              "description": "Optional request ID for tracking"
            }
          }
        },
        "ToolResponse": {
          "type": "object",
          "required": ["success", "agent", "tool_name", "timestamp"],
          "properties": {
            "success": {
              "type": "boolean"
            },
            "result": {
              "description": "Tool execution result"
            },
            "error": {
              "type": "string",
              "nullable": true
            },
            "agent": {
              "type": "string"
            },
            "tool_name": {
              "type": "string"
            },
            "request_id": {
              "type": "string",
              "nullable": true
            },
            "timestamp": {
              "type": "string",
              "format": "date-time"
            },
            "execution_time_ms": {
              "type": "integer",
              "nullable": true
            }
          }
        }
      }
    },
    "paths": {
      "/": {
        "get": {
          "tags": ["Core"],
          "summary": "Health Check",
          "description": "Check the health status and basic information about the cybersecurity agent tool bridge",
          "operationId": "root__get",
          "responses": {
            "200": {
              "description": "Successful Response",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "object",
                    "properties": {
                      "status": {"type": "string"},
                      "timestamp": {"type": "string", "format": "date-time"},
                      "version": {"type": "string"},
                      "agents_loaded": {"type": "integer"},
                      "open_webui_endpoint": {"type": "string"}
                    }
                  }
                }
              }
            }
          }
        }
      },
      "/health": {
        "get": {
          "tags": ["Core"],
          "summary": "Detailed Health Check",
          "description": "Get detailed health information including agent status and system metrics",
          "operationId": "health_check_health_get",
          "responses": {
            "200": {
              "description": "Successful Response"
            }
          }
        }
      },
      "/agents": {
        "get": {
          "tags": ["Core"],
          "summary": "List Available Agents",
          "description": "Get comprehensive list of all cybersecurity agents and their available tools",
          "operationId": "list_agents_agents_get",
          "responses": {
            "200": {
              "description": "Successfully retrieved agents and tools"
            }
          }
        }
      },
      "/execute": {
        "post": {
          "tags": ["Core"],
          "summary": "Execute Cybersecurity Tool",
          "description": "Execute any cybersecurity tool from the available agent ecosystem. Available agents: rt_dev (code generation), bug_hunter (vulnerability scanning), burpsuite_operator (automated penetration testing), daedelu5 (compliance auditing), nexus_kamuy (workflow orchestration).",
          "operationId": "execute_tool_execute_post",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {"$ref": "#/components/schemas/ToolRequest"}
              }
            },
            "required": true
          },
          "responses": {
            "200": {
              "description": "Tool executed successfully",
              "content": {
                "application/json": {
                  "schema": {"$ref": "#/components/schemas/ToolResponse"}
                }
              }
            },
            "400": {"description": "Invalid tool request or parameters"},
            "401": {"description": "Authentication required - provide Bearer token"},
            "422": {"description": "Validation Error"},
            "500": {"description": "Tool execution failed"}
          },
          "security": [
            {"HTTPBearer": []}
          ]
        }
      }
    },
    "tags": [
      {
        "name": "Core",
        "description": "Core API endpoints for health checks and tool execution"
      }
    ]
  };
  
  return c.json(openApiSpec);
});

// Proxy all tool execution requests to backend
app.all('/execute', async (c) => {
  try {
    const requestBody = await c.req.text();
    
    // Forward request to backend service
    const backendResponse = await fetch(`${c.env.BACKEND_URL}/execute`, {
      method: c.req.method,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'offsec-team-worker/1.0.0',
        ...Object.fromEntries(c.req.raw.headers.entries())
      },
      body: requestBody
    });
    
    const responseBody = await backendResponse.text();
    
    // Log the request for analytics
    if (c.env.TOOL_LOGS) {
      const logKey = `${Date.now()}-${crypto.randomUUID()}`;
      await c.env.TOOL_LOGS.put(logKey, JSON.stringify({
        timestamp: new Date().toISOString(),
        method: c.req.method,
        url: c.req.url,
        status: backendResponse.status,
        body: requestBody.substring(0, 1000) // Truncate for storage
      }));
    }
    
    return new Response(responseBody, {
      status: backendResponse.status,
      headers: backendResponse.headers
    });
  } catch (error) {
    console.error('Error proxying request:', error);
    return c.json({ error: 'Internal server error' }, 500);
  }
});

// Proxy all other requests to backend
app.all('*', async (c) => {
  try {
    const url = new URL(c.req.url);
    const backendUrl = `${c.env.BACKEND_URL}${url.pathname}${url.search}`;
    
    const backendResponse = await fetch(backendUrl, {
      method: c.req.method,
      headers: Object.fromEntries(c.req.raw.headers.entries()),
      body: c.req.method !== 'GET' && c.req.method !== 'HEAD' ? c.req.raw.body : undefined
    });
    
    return new Response(backendResponse.body, {
      status: backendResponse.status,
      headers: backendResponse.headers
    });
  } catch (error) {
    console.error('Error proxying request:', error);
    return c.json({ error: 'Service unavailable' }, 503);
  }
});

export default app;
