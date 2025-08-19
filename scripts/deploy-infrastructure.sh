#!/bin/bash

set -e

echo "🚀 Starting Infrastructure Deployment"
echo "======================================"

# Change to infrastructure directory
cd "$(dirname "$0")/../infrastructure"

echo "📋 Terraform Plan - Reviewing Changes..."
terraform plan

echo ""
read -p "🤔 Do you want to apply these changes? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🔧 Applying Terraform Changes..."
terraform apply -auto-approve

echo ""
echo "📦 Installing offsec-team worker dependencies..."
cd ../
npm install

echo ""
echo "🏗️  Building TypeScript worker..."
npm run build

echo ""
echo "🚀 Deploying offsec-team Cloudflare Worker..."
npx wrangler deploy

echo ""
echo "🔍 Deploying research-agent-mcp worker..."
cd ../researcher-main/research-agent-mcp
npx wrangler deploy

echo ""
echo "✅ Infrastructure Deployment Complete!"
echo ""
echo "🌐 Available Endpoints:"
echo "   • https://chat.attck.nexus (OpenWebUI)"
echo "   • https://tools.attck.nexus (Legacy Tools)"
echo "   • https://offsec-team.attck.nexus (OffSec Team Tools)"
echo "   • https://research.attck.nexus (Research Agent)"
echo ""
echo "🔗 Worker Endpoints:"
echo "   • https://offsec-team.attck.community.workers.dev"
echo "   • https://research-agent-mcp.attck-community.workers.dev"
echo ""
echo "📄 OpenAPI Specifications:"
echo "   • https://offsec-team.attck.community.workers.dev/openapi.json"
echo "   • https://research-agent-mcp.attck-community.workers.dev/openapi.json"
echo ""
echo "🔒 Security: Only c3s-nexus-login-method policy (ff667ee6-91c3-4596-98d2-e688e9e335a4) is applied"
echo ""
