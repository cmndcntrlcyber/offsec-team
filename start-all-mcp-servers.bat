@echo off
echo Starting Cybersecurity AI Workflow Integration - MCP Servers
echo ==============================================================

echo.
echo Setting up environment...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo Please edit .env file to configure your API keys and credentials before running the servers.
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo Creating logs directory...
if not exist logs mkdir logs

echo.
echo Starting RTPI-Pen MCP Server (Port 3002)...
start "RTPI-Pen MCP Server" cmd /k "cd rtpi-pen\mcp && python src\server.py"

echo.
echo Waiting 5 seconds for RTPI-Pen server to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting Attack-Node MCP Server (Port 3001)...
echo Note: Node.js must be installed for this server to work
start "Attack-Node MCP Server" cmd /k "cd attack-node\mcp && node src\index.ts"

echo.
echo Waiting 5 seconds for Attack-Node server to initialize...
timeout /t 5 /nobreak >nul

echo.
echo Starting MCP-Nexus Orchestrator Server (Port 3000)...
echo Note: Node.js must be installed for this server to work
start "MCP-Nexus Orchestrator" cmd /k "cd MCP-Nexus\server\mcp && node nexus-server.ts"

echo.
echo ==============================================================
echo All MCP servers are starting up...
echo.
echo Server Status:
echo - RTPI-Pen MCP Server: http://localhost:3002
echo - Attack-Node MCP Server: http://localhost:3001  
echo - MCP-Nexus Orchestrator: http://localhost:3000
echo.
echo Check the individual terminal windows for server logs.
echo.
echo To test the integration, you can run:
echo   python integration_test.py
echo.
echo To configure Cline to use these servers, add the mcp-config.json
echo file to your Cline MCP server configuration.
echo ==============================================================

pause
