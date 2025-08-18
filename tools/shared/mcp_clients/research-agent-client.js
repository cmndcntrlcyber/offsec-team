#!/usr/bin/env node

/**
 * Research Agent MCP Client
 * 
 * This client acts as a bridge between the local MCP ecosystem and the remote
 * research-agent MCP server at https://research-agent-mcp.attck-community.workers.dev
 * 
 * It implements the MCP protocol to expose research agent capabilities as local tools.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

// Environment configuration
const RESEARCH_AGENT_ENDPOINT = process.env.RESEARCH_AGENT_ENDPOINT || 'https://research-agent-mcp.attck-community.workers.dev';
const RESEARCH_AGENT_TOKEN = process.env.RESEARCH_AGENT_TOKEN || '';
const RESEARCH_AGENT_TIMEOUT = parseInt(process.env.RESEARCH_AGENT_TIMEOUT || '30000');
const RESEARCH_AGENT_RETRY_ATTEMPTS = parseInt(process.env.RESEARCH_AGENT_RETRY_ATTEMPTS || '3');

class ResearchAgentMCPClient {
  constructor() {
    this.server = new Server(
      {
        name: 'research-agent-client',
        version: '1.0.0',
        description: 'MCP client for research-agent server integration'
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.availableTools = [];
    this.setupToolHandlers();
    this.initializeRemoteCapabilities();
  }

  async initializeRemoteCapabilities() {
    try {
      console.error('Initializing research agent capabilities...');
      const capabilities = await this.fetchRemoteCapabilities();
      
      if (capabilities && capabilities.tools) {
        this.availableTools = capabilities.tools.map(tool => ({
          name: `research_${tool.name}`,
          description: `${tool.description} (via research agent)`,
          category: tool.category || 'research',
          originalName: tool.name,
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Query or input for the research tool'
              },
              options: {
                type: 'object',
                description: 'Additional options for the tool',
                properties: {}
              }
            },
            required: ['query']
          }
        }));
        
        console.error(`Loaded ${this.availableTools.length} research tools`);
      }
    } catch (error) {
      console.error('Failed to initialize research agent capabilities:', error.message);
      // Continue with empty tools list - graceful degradation
    }
  }

  async fetchRemoteCapabilities() {
    const maxRetries = RESEARCH_AGENT_RETRY_ATTEMPTS;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.error(`Fetching capabilities (attempt ${attempt}/${maxRetries})...`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), RESEARCH_AGENT_TIMEOUT);

        const response = await fetch(`${RESEARCH_AGENT_ENDPOINT}/capabilities`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(RESEARCH_AGENT_TOKEN && { 'Authorization': `Bearer ${RESEARCH_AGENT_TOKEN}` })
          },
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.error('Successfully fetched capabilities');
        return data;

      } catch (error) {
        lastError = error;
        console.error(`Attempt ${attempt} failed:`, error.message);
        
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          console.error(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw new Error(`Failed to fetch capabilities after ${maxRetries} attempts: ${lastError.message}`);
  }

  async callRemoteTool(toolName, parameters) {
    const maxRetries = RESEARCH_AGENT_RETRY_ATTEMPTS;
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        console.error(`Calling remote tool ${toolName} (attempt ${attempt}/${maxRetries})...`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), RESEARCH_AGENT_TIMEOUT);

        const response = await fetch(`${RESEARCH_AGENT_ENDPOINT}/call-tool`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(RESEARCH_AGENT_TOKEN && { 'Authorization': `Bearer ${RESEARCH_AGENT_TOKEN}` })
          },
          body: JSON.stringify({
            method: 'tools/call',
            params: {
              name: toolName,
              arguments: parameters
            }
          }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.error(`Successfully called ${toolName}`);
        return data;

      } catch (error) {
        lastError = error;
        console.error(`Attempt ${attempt} failed:`, error.message);
        
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          console.error(`Retrying in ${delay}ms...`);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw new Error(`Failed to call tool ${toolName} after ${maxRetries} attempts: ${lastError.message}`);
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: this.availableTools
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      // Find the tool
      const tool = this.availableTools.find(t => t.name === name);
      if (!tool) {
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Tool ${name} not found`
        );
      }

      try {
        // Extract parameters
        const query = args.query || '';
        const options = args.options || {};

        // Call the remote tool using its original name
        const result = await this.callRemoteTool(tool.originalName, {
          query,
          ...options
        });

        // Return the result in MCP format
        return {
          content: [
            {
              type: 'text',
              text: typeof result === 'string' ? result : JSON.stringify(result, null, 2)
            }
          ]
        };

      } catch (error) {
        console.error(`Error calling tool ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to execute tool ${name}: ${error.message}`
        );
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Research Agent MCP Client running on stdio');
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.error('Shutting down Research Agent MCP Client...');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.error('Shutting down Research Agent MCP Client...');
  process.exit(0);
});

// Start the client
if (require.main === module) {
  const client = new ResearchAgentMCPClient();
  client.run().catch(error => {
    console.error('Failed to start Research Agent MCP Client:', error);
    process.exit(1);
  });
}

module.exports = ResearchAgentMCPClient;
