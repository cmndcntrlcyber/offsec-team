# Security Setup Guide

## Overview

This repository contains offensive security tools and integrations that require careful configuration to protect sensitive information. Before publishing or sharing this repository, ensure all sensitive data is properly secured.

## Critical Security Files

### Environment Configuration
- **`.env` files**: Never commit these to version control
- **Copy from examples**: Use `.env.example` files as templates
- **Unique secrets**: Generate unique tokens and passwords for each deployment

### Required Environment Files

1. **`openwebui-bridge/.env`**: Copy from `openwebui-bridge/.env.example`
2. **`mcp-config.json`**: Copy from `mcp-config.example.json`
3. **Root `.env`**: Copy from `.env.example` if needed for your setup

## API Keys and Tokens

### Generate Secure Tokens

```bash
# Generate secure random tokens (PowerShell)
[System.Web.Security.Membership]::GeneratePassword(32, 0)

# Or use OpenSSL (if available)
openssl rand -hex 32
```

### Required API Keys

- **CHAT_NEXUS_BEARER**: Your Open WebUI bearer token
- **AGENT_MCP_TOKEN**: MCP agent authentication token
- **EMPIRE_API_TOKEN**: Empire C2 framework API token
- **BURP_API_KEY**: Burp Suite Professional API key
- **POSTGRES_PASSWORD**: Database password

## Network Security

### CORS Configuration
Update `CORS_ORIGINS` in your `.env` to only include trusted domains:

```env
CORS_ORIGINS=https://your-trusted-domain.com,https://your-other-domain.com
```

### Domain Configuration
Replace example domains with your actual domains:

```env
CF_ZONE_ATTCK_NEXUS=your-actual-domain.com
CF_ZONE_C3S_NEXUS=your-secondary-domain.com
OPEN_WEBUI_ENDPOINT=https://your-webui-instance.com/
```

## Database Security

### PostgreSQL Configuration
- Use strong passwords (minimum 16 characters)
- Restrict network access to trusted IPs
- Enable SSL/TLS encryption
- Regular security updates

### Redis Configuration
- Configure authentication if exposed to network
- Use separate Redis instances for different environments
- Enable SSL/TLS if transmitting sensitive data

## File Permissions

### Unix/Linux Systems
```bash
chmod 600 .env
chmod 600 */env
chmod 600 mcp-config.json
```

### Windows Systems
- Right-click file → Properties → Security
- Remove permissions for "Users" and "Everyone"
- Keep only necessary admin accounts

## Deployment Considerations

### Production Deployment
1. Use separate configuration files for each environment
2. Store secrets in secure secret management systems (Azure Key Vault, AWS Secrets Manager, etc.)
3. Enable audit logging for all API access
4. Implement rate limiting and IP whitelisting
5. Use HTTPS everywhere with valid certificates

### Development Environment
1. Never use production credentials in development
2. Use localhost/127.0.0.1 for local services
3. Regularly rotate development tokens
4. Keep development and production environments completely separate

## Monitoring and Logging

### Security Monitoring
- Monitor for unauthorized API access attempts
- Log all authentication attempts
- Alert on configuration changes
- Track unusual network activity

### Log Security
- Ensure logs don't contain sensitive data
- Secure log storage with appropriate access controls
- Regular log rotation and secure archival

## Incident Response

### If Secrets Are Compromised
1. **Immediately revoke** all exposed tokens/keys
2. **Generate new credentials** for all services
3. **Audit logs** for unauthorized access
4. **Update all deployment configurations**
5. **Notify relevant stakeholders**

### Git History Cleanup
If sensitive data was accidentally committed:

```bash
# Remove file from git history (USE WITH CAUTION)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push to update remote (THIS WILL REWRITE HISTORY)
git push origin --force --all
```

## Additional Security Measures

### Network Isolation
- Use VPNs or private networks for sensitive operations
- Implement network segmentation
- Restrict outbound connections where possible

### Access Control
- Implement role-based access control (RBAC)
- Use multi-factor authentication (MFA) where possible
- Regular access reviews and deprovisioning

### Regular Security Maintenance
- Update all dependencies regularly
- Perform security scans of the codebase
- Review and update security configurations
- Conduct periodic security assessments

---

**Remember**: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures as the threat landscape evolves.
