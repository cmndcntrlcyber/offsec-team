/**
 * Cloudflare Worker for Service Authentication
 * Handles authentication and routing for C3S-ATTCK services
 */

// Service tokens from environment bindings
const SERVICE_TOKENS = {
  'chat': CHAT_SERVICE_TOKEN,
  'tools': TOOLS_SERVICE_TOKEN, 
  'research': RESEARCH_SERVICE_TOKEN,
  'mcp': MCP_SERVICE_TOKEN,
  'rtpi': RTPI_PEN_TOKEN
};

// Service mappings - All services route through gateway at 192.168.1.74:443
const SERVICE_MAPPINGS = {
  'chat.attck.nexus': { service: 'chat', port: 443, protocol: 'https' },
  'tools.attck.nexus': { service: 'tools', port: 443, protocol: 'https' },
  'researcher.c3s.nexus': { service: 'research', port: 443, protocol: 'https' },
  'mcp.c3s.nexus': { service: 'mcp', port: 443, protocol: 'https' },
  'rtpi.attck.nexus': { service: 'rtpi', port: 443, protocol: 'https' }
};

/**
 * Handle incoming requests
 */
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

/**
 * Main request handler
 */
async function handleRequest(request) {
  const url = new URL(request.url);
  const hostname = url.hostname;
  
  // Get service configuration
  const serviceConfig = SERVICE_MAPPINGS[hostname];
  if (!serviceConfig) {
    return new Response('Service not found', { status: 404 });
  }

  try {
    // Check authentication
    const authResult = await checkAuthentication(request, serviceConfig.service);
    if (!authResult.allowed) {
      return new Response(authResult.message, { 
        status: authResult.status,
        headers: { 'Content-Type': 'text/plain' }
      });
    }

    // Forward request to backend service
    const backendResponse = await forwardToService(request, serviceConfig);
    
    // Add security headers
    return addSecurityHeaders(backendResponse, hostname);
    
  } catch (error) {
    console.error('Worker error:', error);
    return new Response('Internal server error', { status: 500 });
  }
}

/**
 * Check request authentication
 */
async function checkAuthentication(request, serviceName) {
  const serviceToken = request.headers.get('X-Service-Token');
  const cfAccessToken = request.headers.get('CF-Access-Jwt-Assertion');
  
  // Allow service tokens for inter-service communication
  if (serviceToken) {
    const validTokens = Object.values(SERVICE_TOKENS);
    if (validTokens.includes(serviceToken)) {
      return { allowed: true, method: 'service-token' };
    }
    return { 
      allowed: false, 
      status: 401, 
      message: 'Invalid service token' 
    };
  }
  
  // Check Cloudflare Access token
  if (cfAccessToken) {
    try {
      // Validate JWT token (simplified - in production use proper JWT validation)
      const isValid = await validateAccessToken(cfAccessToken);
      if (isValid) {
        return { allowed: true, method: 'cloudflare-access' };
      }
    } catch (error) {
      console.error('Token validation error:', error);
    }
  }
  
  // For health checks, allow without authentication
  const url = new URL(request.url);
  if (url.pathname === '/health') {
    return { allowed: true, method: 'health-check' };
  }
  
  return { 
    allowed: false, 
    status: 403, 
    message: 'Authentication required' 
  };
}

/**
 * Validate Cloudflare Access token (simplified)
 */
async function validateAccessToken(token) {
  // In production, implement proper JWT validation
  // For now, just check if token exists and is not empty
  return token && token.length > 0;
}

/**
 * Forward request to backend service
 */
async function forwardToService(request, serviceConfig) {
  // Create new URL with backend - all traffic goes through gateway
  const url = new URL(request.url);
  const targetUrl = `https://192.168.1.74:443${url.pathname}${url.search}`;
  
  // Create new headers
  const headers = new Headers(request.headers);
  headers.set('X-Forwarded-For', request.headers.get('CF-Connecting-IP') || '');
  headers.set('X-Forwarded-Proto', 'https');
  headers.set('X-Original-Host', url.hostname);
  headers.set('Host', url.hostname);
  
  // Forward the request
  const response = await fetch(targetUrl, {
    method: request.method,
    headers: headers,
    body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : undefined,
  });
  
  return response;
}

/**
 * Add security headers to response
 */
function addSecurityHeaders(response, hostname) {
  const newResponse = new Response(response.body, response);
  
  // Security headers
  newResponse.headers.set('X-Frame-Options', 'DENY');
  newResponse.headers.set('X-Content-Type-Options', 'nosniff');
  newResponse.headers.set('X-XSS-Protection', '1; mode=block');
  newResponse.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  newResponse.headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()');
  
  // CORS headers
  newResponse.headers.set('Access-Control-Allow-Origin', `https://${hostname}`);
  newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Service-Token');
  newResponse.headers.set('Access-Control-Allow-Credentials', 'true');
  
  // Service identification
  newResponse.headers.set('X-Service-Worker', 'c3s-attck-auth');
  newResponse.headers.set('X-Service-Version', '1.0.0');
  
  return newResponse;
}
