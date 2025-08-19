variable "cloudflare_api_token" {
  description = "Cloudflare API token with necessary permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_c3s_edit" {
  description = "Cloudflare API token for c3s.nexus zone with edit permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_attck_edit" {
  description = "Cloudflare API token for attck.nexus zone with edit permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
  default     = "27e1b1a898bcee51303504e20ac5d743"
}

variable "server_ip" {
  description = "Primary server IP address for DNS records"
  type        = string
  validation {
    condition     = can(regex("^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$", var.server_ip))
    error_message = "Server IP must be a valid IPv4 address."
  }
}

variable "backup_servers" {
  description = "List of backup server IPs for load balancing"
  type        = list(string)
  default     = []
}

variable "enable_load_balancer" {
  description = "Enable Cloudflare Load Balancer for high availability"
  type        = bool
  default     = false
}

# Service Authentication Tokens
variable "chat_service_token" {
  description = "Authentication token for chat service"
  type        = string
  sensitive   = true
}

variable "tools_service_token" {
  description = "Authentication token for tools service"
  type        = string
  sensitive   = true
}

variable "research_service_token" {
  description = "Authentication token for research service"
  type        = string
  sensitive   = true
}

variable "mcp_service_token" {
  description = "Authentication token for MCP service"
  type        = string
  sensitive   = true
}

variable "rtpi_pen_token" {
  description = "Authentication token for RTPI-Pen service"
  type        = string
  sensitive   = true
}

# Access Control
variable "allowed_email_domains" {
  description = "List of email domains allowed for Cloudflare Access"
  type        = list(string)
  default     = ["attck.nexus", "c3s.nexus"]
}

variable "allowed_emails" {
  description = "List of specific email addresses allowed for Cloudflare Access"
  type        = list(string)
  default     = []
}

variable "github_organization" {
  description = "GitHub organization for authentication (optional)"
  type        = string
  default     = ""
}

# Service Configuration
variable "session_duration" {
  description = "Session duration for Cloudflare Access"
  type        = string
  default     = "24h"
}

variable "gateway_url" {
  description = "Gateway service URL"
  type        = string
  default     = "http://localhost:8005"
}

# Rate Limiting
variable "api_rate_limit_threshold" {
  description = "API rate limit threshold (requests per period)"
  type        = number
  default     = 100
}

variable "api_rate_limit_period" {
  description = "API rate limit period in seconds"
  type        = number
  default     = 60
}

# Security Settings
variable "threat_score_threshold" {
  description = "Cloudflare threat score threshold for blocking requests"
  type        = number
  default     = 14
  validation {
    condition     = var.threat_score_threshold >= 0 && var.threat_score_threshold <= 100
    error_message = "Threat score threshold must be between 0 and 100."
  }
}

variable "enable_waf" {
  description = "Enable Web Application Firewall rules"
  type        = bool
  default     = true
}

variable "enable_ddos_protection" {
  description = "Enable DDoS protection features"
  type        = bool
  default     = true
}

# SSL/TLS Configuration
variable "ssl_mode" {
  description = "SSL/TLS mode for Cloudflare"
  type        = string
  default     = "full"
  validation {
    condition     = contains(["off", "flexible", "full", "strict"], var.ssl_mode)
    error_message = "SSL mode must be one of: off, flexible, full, strict."
  }
}

variable "min_tls_version" {
  description = "Minimum TLS version"
  type        = string
  default     = "1.2"
  validation {
    condition     = contains(["1.0", "1.1", "1.2", "1.3"], var.min_tls_version)
    error_message = "TLS version must be one of: 1.0, 1.1, 1.2, 1.3."
  }
}

# Caching Settings
variable "cache_level" {
  description = "Default cache level for static assets"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["aggressive", "basic", "simplified", "standard"], var.cache_level)
    error_message = "Cache level must be one of: aggressive, basic, simplified, standard."
  }
}

variable "browser_cache_ttl" {
  description = "Browser cache TTL in seconds"
  type        = number
  default     = 14400
}

# Monitoring and Logging
variable "enable_analytics" {
  description = "Enable Cloudflare Analytics"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "Log retention period in days"
  type        = number
  default     = 30
}

# Worker Configuration
variable "worker_cpu_limit" {
  description = "CPU limit for Workers (in milliseconds per request)"
  type        = number
  default     = 50
}

variable "worker_memory_limit" {
  description = "Memory limit for Workers (in MB)"
  type        = number
  default     = 128
}

# Development/Testing
variable "development_mode" {
  description = "Enable development mode (disables caching, enables detailed logging)"
  type        = bool
  default     = false
}

variable "debug_logging" {
  description = "Enable debug logging in Workers"
  type        = bool
  default     = false
}

# Geographic Restrictions
variable "allowed_countries" {
  description = "List of country codes allowed to access services (empty = all countries)"
  type        = list(string)
  default     = []
}

variable "blocked_countries" {
  description = "List of country codes blocked from accessing services"
  type        = list(string)
  default     = []
}

# Bot Management
variable "bot_fight_mode" {
  description = "Bot Fight Mode setting"
  type        = string
  default     = "on"
  validation {
    condition     = contains(["on", "off"], var.bot_fight_mode)
    error_message = "Bot Fight Mode must be either 'on' or 'off'."
  }
}

variable "super_bot_fight_mode" {
  description = "Super Bot Fight Mode (Enterprise feature)"
  type        = bool
  default     = false
}

# Performance Optimization
variable "auto_minify" {
  description = "Auto minify settings"
  type = object({
    css  = bool
    html = bool
    js   = bool
  })
  default = {
    css  = true
    html = true
    js   = true
  }
}

variable "brotli_compression" {
  description = "Enable Brotli compression"
  type        = bool
  default     = true
}

variable "early_hints" {
  description = "Enable Early Hints for performance"
  type        = bool
  default     = true
}

# Mobile Optimization
variable "mobile_redirect" {
  description = "Mobile redirect settings"
  type = object({
    enabled     = bool
    mobile_subdomain = string
  })
  default = {
    enabled          = false
    mobile_subdomain = ""
  }
}

# Image Optimization
variable "polish" {
  description = "Image optimization level"
  type        = string
  default     = "basic"
  validation {
    condition     = contains(["off", "basic", "lossless"], var.polish)
    error_message = "Polish setting must be one of: off, basic, lossless."
  }
}

variable "webp" {
  description = "Enable WebP image format"
  type        = bool
  default     = true
}

# Custom Domains
variable "custom_domains" {
  description = "Additional custom domains to configure"
  type = map(object({
    zone_name = string
    ssl_mode  = string
    proxied   = bool
  }))
  default = {}
}

# Service Ports (for reference)
variable "service_ports" {
  description = "Service port mappings"
  type = map(number)
  default = {
    gateway  = 8005
    chat     = 3001
    tools    = 8001
    research = 8002
    mcp      = 8003
    rtpi     = 8004
  }
}

# Tags for organization
variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "C3S-ATTCK"
    Environment = "production"
    ManagedBy   = "terraform"
    Owner       = "security-team"
  }
}
