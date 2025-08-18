# 1. Create new directory structure
# cd /path/to/C3S-ATTCK-WORKSPACE/offsec-team
mkdir -p {gateway,infrastructure,workers,scripts,configs}

# 2. Create core infrastructure files
touch gateway/{main.go,go.mod,Dockerfile,README.md}
touch infrastructure/{main.tf,variables.tf,outputs.tf,terraform.tfvars.example}
touch workers/{service-auth.js,config-manager.js,wrangler.toml}
touch scripts/{deploy.sh,health-check.sh,setup-services.py,generate-tokens.py,monitoring.Dockerfile}

# 3. Create shared configuration
touch configs/{service-tokens.json,gateway-config.yaml,cors-config.json,README.md}

# 4. Add service containers
touch openwebui-bridge/{service_manager.py,config.py,Dockerfile}
touch tools/Dockerfile
touch ../researcher-main/Dockerfile
touch ../researcher-main/research-agent-mcp/Dockerfile

# 5. Root level configuration
cd ..
touch docker-compose.yml .env.example .dockerignore

# 6. Update requirements
echo "requests\ncloudflare\npyaml" >> offsec-team/openwebui-bridge/requirements.txt