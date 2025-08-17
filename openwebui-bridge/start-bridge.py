#!/usr/bin/env python3
"""
Agent Tool Bridge API Startup Script

Launches the FastAPI bridge server that integrates cybersecurity agent tools
with Open WebUI at https://chat.attck.nexus/
"""

import os
import sys
import logging
import argparse
import signal
import asyncio
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from main import app, logger

def setup_signal_handlers():
    """Setup graceful shutdown signal handlers"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def setup_environment():
    """Setup environment variables and configuration"""
    # Set default environment variables if not present
    env_defaults = {
        "PYTHONPATH": str(Path(__file__).parent.parent),
        "LOG_LEVEL": "INFO",
        "BRIDGE_HOST": "0.0.0.0",
        "BRIDGE_PORT": "8000",
        "OPEN_WEBUI_ENDPOINT": "https://chat.attck.nexus/",
        "CDB_PATH": "",  # Auto-detect
        "WINDBG_SYMBOLS_PATH": "SRV*C:\\Symbols*https://msdl.microsoft.com/download/symbols"
    }
    
    for key, default_value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = default_value
    
    # Log environment setup
    logger.info("Environment configuration:")
    for key in env_defaults:
        logger.info(f"  {key}: {os.environ.get(key, 'Not set')}")

def validate_dependencies():
    """Validate that required dependencies are available"""
    logger.info("Validating dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    # Check if agent tools are accessible
    try:
        from tools.rt_dev.CodeForgeGenerator import CodeForgeGenerator
        from tools.bug_hunter.WebVulnerabilityTester import WebVulnerabilityTester
        logger.info("✓ Agent tools are accessible")
    except ImportError as e:
        logger.warning(f"Some agent tools may not be accessible: {e}")
    
    # Check for Windows Debugging Tools (optional)
    windbg_paths = [
        r"C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe",
        r"C:\Program Files\Windows Kits\10\Debuggers\x64\cdb.exe",
    ]
    
    cdb_found = False
    for path in windbg_paths:
        if os.path.exists(path):
            logger.info(f"✓ Windows Debugging Tools found: {path}")
            cdb_found = True
            break
    
    if not cdb_found:
        logger.warning("⚠ Windows Debugging Tools not found - mcp-windbg features will be limited")
    
    return True

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(
        description="Agent Tool Bridge API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start-bridge.py                    # Start with default settings
  python start-bridge.py --port 9000       # Start on port 9000
  python start-bridge.py --dev             # Start in development mode
  python start-bridge.py --log-level DEBUG # Enable debug logging
        """
    )
    
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--dev", 
        action="store_true",
        help="Enable development mode with auto-reload"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate setup without starting server"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Setup environment
    setup_environment()
    
    # Validate dependencies
    if not validate_dependencies():
        logger.error("Dependency validation failed")
        sys.exit(1)
    
    if args.validate_only:
        logger.info("✓ Validation completed successfully")
        sys.exit(0)
    
    # Update environment from args
    os.environ["BRIDGE_HOST"] = args.host
    os.environ["BRIDGE_PORT"] = str(args.port)
    
    logger.info("=" * 60)
    logger.info("🚀 Agent Tool Bridge API Server Starting")
    logger.info("=" * 60)
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Mode: {'Development' if args.dev else 'Production'}")
    logger.info(f"Log Level: {args.log_level}")
    logger.info(f"Open WebUI: {os.environ.get('OPEN_WEBUI_ENDPOINT')}")
    logger.info("=" * 60)
    
    # Configure uvicorn
    uvicorn_config = {
        "app": "main:app",
        "host": args.host,
        "port": args.port,
        "log_level": args.log_level.lower(),
        "access_log": True,
    }
    
    if args.dev:
        uvicorn_config.update({
            "reload": True,
            "reload_dirs": [str(Path(__file__).parent)]
        })
        logger.info("🔧 Development mode enabled - auto-reload active")
    else:
        uvicorn_config.update({
            "workers": args.workers
        })
    
    try:
        # Start the server
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
