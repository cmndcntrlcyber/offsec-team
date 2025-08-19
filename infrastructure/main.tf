terraform {
  required_version = ">= 1.0"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Data sources for existing zones
data "cloudflare_zone" "attck_nexus" {
  name = "attck.nexus"
}

data "cloudflare_zone" "c3s_nexus" {
  name = "c3s.nexus"
}

# Cloudflare Workers for service authentication and routing
resource "cloudflare_workers_script" "service_auth" {
  account_id = var.cloudflare_account_id
  name       = "service-auth"
  content    = file("${path.module}/../workers/service-auth.js")

  secret_text_binding {
    name = "CHAT_SERVICE_TOKEN"
    text = var.chat_service_token
  }

  secret_text_binding {
    name = "TOOLS_SERVICE_TOKEN"
    text = var.tools_service_token
  }

  secret_text_binding {
    name = "RESEARCH_SERVICE_TOKEN"
    text = var.research_service_token
  }

  secret_text_binding {
    name = "MCP_SERVICE_TOKEN"
    text = var.mcp_service_token
  }

  secret_text_binding {
    name = "RTPI_PEN_TOKEN"
    text = var.rtpi_pen_token
  }

  plain_text_binding {
    name = "GATEWAY_URL"
    text = "http://localhost:8005"
  }
}

resource "cloudflare_workers_script" "config_manager" {
  account_id = var.cloudflare_account_id
  name       = "config-manager"
  content    = file("${path.module}/../workers/config-manager.js")

  secret_text_binding {
    name = "CLOUDFLARE_API_TOKEN"
    text = var.cloudflare_api_token
  }

  plain_text_binding {
    name = "GATEWAY_URL"
    text = "http://localhost:8005"
  }
}

# DNS Records for service domains (using content instead of value)
resource "cloudflare_record" "chat_attck_nexus" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  name    = "chat"
  content = var.server_ip
  type    = "A"
  proxied = true
  comment = "Chat service - OpenWebUI Bridge"

  lifecycle {
    ignore_changes = [content]
  }
}

resource "cloudflare_record" "tools_attck_nexus" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  name    = "tools"
  content = var.server_ip
  type    = "A"
  proxied = true
  comment = "Tools service - Agent Gateway"

  lifecycle {
    ignore_changes = [content]
  }
}

resource "cloudflare_record" "offsec_team_attck_nexus" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  name    = "offsec-team"
  content = var.server_ip
  type    = "A"
  proxied = true
  comment = "OffSec Team - Cybersecurity Tool Bridge"

  lifecycle {
    ignore_changes = [content]
  }
}

resource "cloudflare_record" "research_attck_nexus" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  name    = "research"
  content = var.server_ip
  type    = "A"
  proxied = true
  comment = "Research Agent - MCP Service"

  lifecycle {
    ignore_changes = [content]
  }
}

# Worker Routes for service domains (excluding chat.attck.nexus for direct IP access)
resource "cloudflare_workers_route" "service_auth_tools" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  pattern = "tools.attck.nexus/*"
  script_name = cloudflare_workers_script.service_auth.name
}

resource "cloudflare_workers_route" "service_auth_offsec" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  pattern = "offsec-team.attck.nexus/*"
  script_name = cloudflare_workers_script.service_auth.name
}

resource "cloudflare_workers_route" "service_auth_research" {
  zone_id = data.cloudflare_zone.attck_nexus.id
  pattern = "research.attck.nexus/*"
  script_name = cloudflare_workers_script.service_auth.name
}

# Unified Zero Trust Access Application for all services
resource "cloudflare_zero_trust_access_application" "unified_services" {
  zone_id          = data.cloudflare_zone.attck_nexus.id
  name             = "ATTCK Nexus Unified Services"
  domain           = "*.attck.nexus"
  type             = "self_hosted"
  session_duration = "24h"
  
  # Reference the existing policy by direct ID
  policies = ["ff667ee6-91c3-4596-98d2-e688e9e335a4"]
  
  cors_headers {
    allow_all_headers   = true
    allow_all_methods   = true
    allow_all_origins   = false
    allowed_origins     = [
      "https://chat.attck.nexus",
      "https://tools.attck.nexus",
      "https://offsec-team.attck.nexus",
      "https://research.attck.nexus"
    ]
    allow_credentials   = true
    max_age            = 300
  }
}
