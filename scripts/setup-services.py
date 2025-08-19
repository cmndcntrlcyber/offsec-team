#!/usr/bin/env python3
"""
Service Configuration Setup Utility
Initializes service configurations and validates setup
"""

import json
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

class ServiceConfigManager:
    """Manages service configuration and setup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.configs_dir = Path(__file__).parent.parent / "configs"
        self.env_file = self.project_root / ".env"
        
    def load_env_vars(self) -> dict:
        """Load environment variables from .env file"""
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        return env_vars
    
    def validate_service_tokens(self, env_vars: dict) -> bool:
        """Validate all required service tokens exist"""
        required_tokens = [
            'CHAT_SERVICE_TOKEN',
            'TOOLS_SERVICE_TOKEN',
            'RESEARCH_SERVICE_TOKEN',
            'MCP_SERVICE_TOKEN',
            'RTPI_PEN_TOKEN'
        ]
        
        missing_tokens = []
        for token in required_tokens:
            if token not in env_vars or not env_vars[token]:
                missing_tokens.append(token)
        
        if missing_tokens:
            print(f"❌ Missing service tokens: {', '.join(missing_tokens)}")
            return False
        
        print("✅ All service tokens validated")
        return True
    
    def validate_cloudflare_config(self, env_vars: dict) -> bool:
        """Validate Cloudflare configuration"""
        required_cf_vars = [
            'CLOUDFLARE_ACCOUNT_ID',
            'CLOUDFLARE_API_TOKEN'
        ]
        
        missing_vars = []
        for var in required_cf_vars:
            if var not in env_vars or not env_vars[var]:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing Cloudflare config: {', '.join(missing_vars)}")
            return False
        
        print("✅ Cloudflare configuration validated")
        return True
    
    def create_service_config_json(self, env_vars: dict) -> bool:
        """Create comprehensive service configuration JSON"""
        config_file = self.configs_dir / "service-config.json"
        
        service_config = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "services": {
                "chat-service": {
                    "name": "OpenWebUI Chat Service",
                    "domain": "chat.attck.nexus",
                    "port": int(env_vars.get('CHAT_PORT', 3001)),
                    "container_port": 8080,
                    "token": env_vars.get('CHAT_SERVICE_TOKEN'),
                    "endpoints": ["/api/chat", "/health", "/openapi.json"],
                    "description": "Main chat interface with OpenWebUI integration"
                },
                "tools-service": {
                    "name": "Tools Agent Gateway",
                    "domain": "tools.attck.nexus",
                    "port": int(env_vars.get('TOOLS_PORT', 8001)),
                    "container_port": 8001,
                    "token": env_vars.get('TOOLS_SERVICE_TOKEN'),
                    "endpoints": ["/api/tools", "/openapi.json", "/agents"],
                    "description": "Agent tools and capabilities gateway"
                },
                "research-service": {
                    "name": "Research Service",
                    "domain": "researcher.c3s.nexus",
                    "port": int(env_vars.get('RESEARCH_PORT', 8002)),
                    "container_port": 8002,
                    "token": env_vars.get('RESEARCH_SERVICE_TOKEN'),
                    "endpoints": ["/api/research", "/search", "/analyze"],
                    "description": "Content analysis and research capabilities"
                },
                "mcp-service": {
                    "name": "Model Context Protocol Service",
                    "domain": "mcp.c3s.nexus",
                    "port": int(env_vars.get('MCP_PORT', 8003)),
                    "container_port": 8003,
                    "token": env_vars.get('MCP_SERVICE_TOKEN'),
                    "endpoints": ["/api/mcp", "/models", "/context"],
                    "description": "Model Context Protocol implementation"
                },
                "rtpi-pen": {
                    "name": "RTPI Penetration Testing Service",
                    "domain": "rtpi.attck.nexus",
                    "port": int(env_vars.get('RTPI_PORT', 8004)),
                    "container_port": 8080,
                    "token": env_vars.get('RTPI_PEN_TOKEN'),
                    "endpoints": ["/api/rtpi", "/health"],
                    "description": "Real-time penetration testing interface"
                },
                "gateway": {
                    "name": "Service Gateway",
                    "domain": "config.attck.nexus",
                    "port": int(env_vars.get('GATEWAY_PORT', 8005)),
                    "container_port": 8005,
                    "endpoints": ["/health", "/api/gateway"],
                    "description": "Central service coordination gateway"
                }
            },
            "cloudflare": {
                "account_id": env_vars.get('CLOUDFLARE_ACCOUNT_ID'),
                "zones": {
                    "attck_nexus": "attck.nexus",
                    "c3s_nexus": "c3s.nexus"
                }
            },
            "security": {
                "cors_enabled": True,
                "rate_limiting": True,
                "service_tokens": True,
                "ssl_required": True
            }
        }
        
        try:
            with open(config_file, 'w') as f:
                json.dump(service_config, f, indent=2)
            print(f"✅ Service configuration created: {config_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating service config: {e}")
            return False
    
    def validate_config_files(self) -> bool:
        """Validate all configuration files exist and are valid"""
        config_files = {
            "cors-config.json": "CORS configuration",
            "gateway-config.yaml": "Gateway configuration", 
            "service-tokens.json": "Service tokens"
        }
        
        all_valid = True
        
        for filename, description in config_files.items():
            filepath = self.configs_dir / filename
            if not filepath.exists():
                print(f"❌ Missing {description}: {filepath}")
                all_valid = False
            else:
                # Validate file format
                try:
                    if filename.endswith('.json'):
                        with open(filepath, 'r') as f:
                            json.load(f)
                    elif filename.endswith('.yaml'):
                        with open(filepath, 'r') as f:
                            yaml.safe_load(f)
                    print(f"✅ Valid {description}")
                except Exception as e:
                    print(f"❌ Invalid {description}: {e}")
                    all_valid = False
        
        return all_valid
    
    def display_service_status(self, env_vars: dict):
        """Display current service configuration status"""
        print("\n🔧 C3S-ATTCK Service Configuration Status")
        print("=" * 50)
        
        services = [
            ("Chat Service", env_vars.get('CHAT_PORT', '3001'), 'chat.attck.nexus'),
            ("Tools Service", env_vars.get('TOOLS_PORT', '8001'), 'tools.attck.nexus'),
            ("Research Service", env_vars.get('RESEARCH_PORT', '8002'), 'researcher.c3s.nexus'),
            ("MCP Service", env_vars.get('MCP_PORT', '8003'), 'mcp.c3s.nexus'),
            ("RTPI-Pen Service", env_vars.get('RTPI_PORT', '8004'), 'rtpi.attck.nexus'),
            ("Gateway", env_vars.get('GATEWAY_PORT', '8005'), 'config.attck.nexus')
        ]
        
        for name, port, domain in services:
            print(f"{name:20} → localhost:{port} → {domain}")
        
        print("\n🔑 Authentication:")
        print(f"Service Tokens: {'✅ Configured' if env_vars.get('CHAT_SERVICE_TOKEN') else '❌ Missing'}")
        print(f"Cloudflare API:  {'✅ Configured' if env_vars.get('CLOUDFLARE_API_TOKEN') else '❌ Missing'}")
        
    def run_setup(self) -> bool:
        """Run complete service setup"""
        print("🚀 Starting C3S-ATTCK service configuration setup...")
        
        # Load environment variables
        env_vars = self.load_env_vars()
        if not env_vars:
            print("❌ No .env file found or empty")
            return False
        
        # Validate tokens
        if not self.validate_service_tokens(env_vars):
            return False
        
        # Validate Cloudflare config
        if not self.validate_cloudflare_config(env_vars):
            return False
        
        # Create service configuration
        if not self.create_service_config_json(env_vars):
            return False
        
        # Validate config files
        if not self.validate_config_files():
            print("⚠️  Some configuration files are missing or invalid")
        
        # Display status
        self.display_service_status(env_vars)
        
        print("\n✅ Service configuration setup completed!")
        print("\n📋 Next steps:")
        print("1. Verify your server's public IP in terraform.tfvars")
        print("2. Deploy Cloudflare infrastructure: cd infrastructure && terraform apply")
        print("3. Test service health: ../scripts/health-check.sh")
        
        return True

def main():
    """Main entry point"""
    manager = ServiceConfigManager()
    
    try:
        success = manager.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
