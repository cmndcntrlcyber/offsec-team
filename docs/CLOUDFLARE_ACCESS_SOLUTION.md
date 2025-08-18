# Cloudflare Access Solution for OpenWebUI Integration

## Problem Identified

OpenWebUI cannot connect to `https://tools.attck.nexus/openapi.json` because:
- The production server is behind Cloudflare Access authentication
- All JSON endpoints (`/openapi.json`, `/health`, `/agents`) return HTML sign-in pages
- OpenWebUI cannot authenticate through Cloudflare Access

## Test Results

✅ **Local server is running** at `http://localhost:8001/openapi.json`  
❌ **Production server blocked** by Cloudflare Access  
✅ **Documentation endpoints** (`/docs`, `/redoc`) work but return HTML  
❌ **No header bypasses** work for Cloudflare Access  

## Immediate Solution

### Option 1: Use Local Development Server (Recommended)

1. **Start the local server** (if not already running):
   ```bash
   cd ../offsec-team/openwebui-bridge
   python main.py
   ```

2. **Configure OpenWebUI to use local endpoint**:
   - In OpenWebUI settings, change the tool server URL from:
     `https://tools.attck.nexus/openapi.json`
   - To:
     `http://localhost:8001/openapi.json`

3. **Verify connection**:
   - OpenWebUI should now successfully connect
   - All agent tools will be available through local server
   - Local server will proxy requests to production agents

### Option 2: Cloudflare Access Bypass (Production Fix)

**For Production Deployment**, you need to configure Cloudflare Access:

1. **Create Bypass Rule**:
   - Go to Cloudflare Dashboard → Access → Applications
   - Find the `tools.attck.nexus` application
   - Add a bypass rule for `/openapi.json` endpoint

2. **Service Token Method**:
   - Create a Cloudflare Access service token
   - Configure OpenWebUI to send the token in headers

3. **IP Whitelist**:
   - Add OpenWebUI's IP address to Cloudflare Access bypass rules

### Option 3: Alternative Endpoint (Quick Fix)

Create a public endpoint specifically for the OpenAPI spec:

1. **Host on different subdomain**:
   - `api.tools.attck.nexus/openapi.json` (without Cloudflare Access)
   - `public.tools.attck.nexus/openapi.json` (public access)

2. **Static hosting**:
   - Upload `openapi.json` to CDN or static hosting
   - Point OpenWebUI to the static file

## Current Status

- ✅ Local development server is operational
- ✅ OpenAPI specification is correctly formatted
- ✅ All agent tools are loaded and ready
- ❌ Production access blocked by authentication

## Next Steps

1. **Immediate**: Use local server (`http://localhost:8001/openapi.json`)
2. **Short-term**: Configure Cloudflare Access bypass for `/openapi.json`
3. **Long-term**: Set up dedicated public API endpoint for OpenWebUI integration

## Testing Commands

```bash
# Test local server
curl http://localhost:8001/openapi.json

# Test production server (will fail)
curl https://tools.attck.nexus/openapi.json

# Start local server if needed
cd ../offsec-team/openwebui-bridge && python main.py
```

## Configuration Change Needed

In OpenWebUI Settings → Tool Servers:
- **Remove**: `https://tools.attck.nexus/openapi.json`
- **Add**: `http://localhost:8001/openapi.json`

This will immediately resolve the connection issue and allow OpenWebUI to access all agent tools.
