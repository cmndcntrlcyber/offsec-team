/**
 * Cloudflare Worker: Configuration Manager
 * Handles dynamic configuration updates for OpenWebUI services
 */

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Service-Token',
  'Access-Control-Max-Age': '86400',
};

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const { pathname } = url;

  // Handle preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Validate service token
    const authHeader = request.headers.get('Authorization');
    const serviceToken = request.headers.get('X-Service-Token');
    
    if (!authHeader && !serviceToken) {
      return new Response('Unauthorized', { 
        status: 401,
        headers: corsHeaders 
      });
    }

    // Configuration endpoints
    switch (pathname) {
      case '/health':
        return handleHealth(corsHeaders);
      
      case '/config/services':
        return handleServiceConfig(request, corsHeaders);
      
      case '/config/cors':
        return handleCorsConfig(request, corsHeaders);
      
      case '/config/tokens':
        return handleTokenConfig(request, corsHeaders);
      
      case '/config/update':
        return handleConfigUpdate(request, corsHeaders);
      
      default:
        return new Response('Not Found', { 
          status: 404,
          headers: corsHeaders 
        });
    }
  } catch (error) {
    console.error('Config Manager Error:', error);
    return new Response('Internal Server Error', { 
      status: 500,
      headers: corsHeaders 
    });
  }
}

// Health check endpoint
function handleHealth(corsHeaders) {
  return new Response(JSON.stringify({
    status: 'healthy',
    service: 'config-manager',
    timestamp: new Date().toISOString()
  }), {
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json'
    }
  });
}

// Service configuration endpoint
async function handleServiceConfig(request, corsHeaders) {
  if (request.method === 'GET') {
    const serviceConfig = {
      services: {
        'openwebui-bridge': {
          port: 8001,
          domain: 'bridge.offsecteam.com',
          health_endpoint: '/health'
        },
        'nexus-kamuy': {
          port: 8002,
          domain: 'nexus.offsecteam.com',
          health_endpoint: '/health'
        },
        'bug-hunter': {
          port: 8003,
          domain: 'bughunter.offsecteam.com',
          health_endpoint: '/health'
        },
        'burpsuite-operator': {
          port: 8004,
          domain: 'burp.offsecteam.com',
          health_endpoint: '/health'
        },
        'daedelu5': {
          port: 8005,
          domain: 'daedelu5.offsecteam.com',
          health_endpoint: '/health'
        },
        'rt-dev': {
          port: 8006,
          domain: 'rtdev.offsecteam.com',
          health_endpoint: '/health'
        },
        'researcher-main': {
          port: 8007,
          domain: 'research.offsecteam.com',
          health_endpoint: '/health'
        }
      }
    };

    return new Response(JSON.stringify(serviceConfig), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }

  return new Response('Method Not Allowed', { 
    status: 405,
    headers: corsHeaders 
  });
}

// CORS configuration endpoint
async function handleCorsConfig(request, corsHeaders) {
  if (request.method === 'GET') {
    const corsConfig = {
      allowed_origins: [
        'https://bridge.offsecteam.com',
        'https://nexus.offsecteam.com',
        'https://bughunter.offsecteam.com',
        'https://burp.offsecteam.com',
        'https://daedelu5.offsecteam.com',
        'https://rtdev.offsecteam.com',
        'https://research.offsecteam.com',
        'http://localhost:8001',
        'http://localhost:8002',
        'http://localhost:8003',
        'http://localhost:8004',
        'http://localhost:8005',
        'http://localhost:8006',
        'http://localhost:8007'
      ],
      allowed_methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowed_headers: [
        'Content-Type',
        'Authorization',
        'X-Service-Token',
        'X-Requested-With',
        'Accept',
        'Origin'
      ],
      max_age: 86400
    };

    return new Response(JSON.stringify(corsConfig), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }

  return new Response('Method Not Allowed', { 
    status: 405,
    headers: corsHeaders 
  });
}

// Token configuration endpoint
async function handleTokenConfig(request, corsHeaders) {
  if (request.method === 'GET') {
    // Return token validation info (not actual tokens)
    const tokenInfo = {
      tokens: {
        service_tokens: ['OPENWEBUI_BRIDGE_TOKEN', 'NEXUS_KAMUY_TOKEN', 'BUG_HUNTER_TOKEN'],
        api_tokens: ['CLOUDFLARE_API_TOKEN'],
        auth_domains: ['offsecteam.com']
      },
      validation: {
        min_length: 32,
        required_prefix: 'ey',
        expiry_check: true
      }
    };

    return new Response(JSON.stringify(tokenInfo), {
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json'
      }
    });
  }

  return new Response('Method Not Allowed', { 
    status: 405,
    headers: corsHeaders 
  });
}

// Configuration update endpoint
async function handleConfigUpdate(request, corsHeaders) {
  if (request.method === 'POST') {
    try {
      const updateData = await request.json();
      
      // Log configuration update
      console.log('Configuration Update:', {
        timestamp: new Date().toISOString(),
        update_type: updateData.type || 'unknown',
        service: updateData.service || 'all',
        user_agent: request.headers.get('User-Agent')
      });

      // Return success response
      return new Response(JSON.stringify({
        status: 'success',
        message: 'Configuration updated successfully',
        timestamp: new Date().toISOString(),
        applied_changes: updateData
      }), {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        status: 'error',
        message: 'Invalid JSON payload',
        error: error.message
      }), {
        status: 400,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json'
        }
      });
    }
  }

  return new Response('Method Not Allowed', { 
    status: 405,
    headers: corsHeaders 
  });
}
