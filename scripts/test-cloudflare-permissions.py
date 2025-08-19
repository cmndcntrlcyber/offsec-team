#!/usr/bin/env python3
"""
Test Cloudflare API Token Permissions
Verifies what resources the current API token can access
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/cmndcntrl/code/.env')

CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')

if not CLOUDFLARE_API_TOKEN:
    print("ERROR: CLOUDFLARE_API_TOKEN not found in .env file")
    exit(1)

if not CLOUDFLARE_ACCOUNT_ID:
    print("ERROR: CLOUDFLARE_ACCOUNT_ID not found in .env file")
    exit(1)

# Cloudflare API base URL
CF_API_BASE = "https://api.cloudflare.com/client/v4"

# Headers for API requests
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

def test_api_endpoint(endpoint, description):
    """Test a Cloudflare API endpoint"""
    try:
        url = f"{CF_API_BASE}{endpoint}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ {description}: SUCCESS")
            return True
        elif response.status_code == 403:
            print(f"❌ {description}: FORBIDDEN (insufficient permissions)")
            return False
        elif response.status_code == 401:
            print(f"❌ {description}: UNAUTHORIZED (invalid token)")
            return False
        else:
            print(f"⚠️  {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {str(e)}")
        return False

def main():
    print("=" * 60)
    print("CLOUDFLARE API TOKEN PERMISSION TEST")
    print("=" * 60)
    print(f"Account ID: {CLOUDFLARE_ACCOUNT_ID}")
    print(f"Token: {CLOUDFLARE_API_TOKEN[:8]}...")
    print()
    
    # Test basic token validation
    print("Testing API Token Validation:")
    test_api_endpoint("/user/tokens/verify", "Token Verification")
    print()
    
    # Test zone access
    print("Testing Zone Access:")
    test_api_endpoint("/zones", "List Zones")
    print()
    
    # Test account access
    print("Testing Account Access:")
    test_api_endpoint(f"/accounts/{CLOUDFLARE_ACCOUNT_ID}", "Account Details")
    test_api_endpoint(f"/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/scripts", "Workers Scripts")
    print()
    
    # Test specific resource permissions
    print("Testing Resource Permissions:")
    
    # Get zones first to test zone-specific resources
    try:
        zones_response = requests.get(f"{CF_API_BASE}/zones", headers=headers)
        if zones_response.status_code == 200:
            zones = zones_response.json().get('result', [])
            if zones:
                zone_id = zones[0]['id']
                zone_name = zones[0]['name']
                print(f"Using zone: {zone_name} ({zone_id})")
                
                # Test zone-specific permissions
                test_api_endpoint(f"/zones/{zone_id}/dns_records", "DNS Records")
                test_api_endpoint(f"/zones/{zone_id}/access/apps", "Access Applications")
                test_api_endpoint(f"/zones/{zone_id}/access/policies", "Access Policies")
                test_api_endpoint(f"/zones/{zone_id}/pagerules", "Page Rules")
                test_api_endpoint(f"/zones/{zone_id}/filters", "Filters")
                test_api_endpoint(f"/zones/{zone_id}/firewall/rules", "Firewall Rules")
                test_api_endpoint(f"/zones/{zone_id}/rate_limits", "Rate Limits")
                test_api_endpoint(f"/zones/{zone_id}/rulesets", "Rulesets (WAF)")
            else:
                print("❌ No zones found")
        else:
            print("❌ Cannot access zones")
    except Exception as e:
        print(f"❌ Error testing zone permissions: {e}")
    
    print()
    
    # Test account-level resources
    print("Testing Account-Level Resources:")
    test_api_endpoint(f"/accounts/{CLOUDFLARE_ACCOUNT_ID}/load_balancers/monitors", "Load Balancer Monitors")
    test_api_endpoint(f"/accounts/{CLOUDFLARE_ACCOUNT_ID}/load_balancers/pools", "Load Balancer Pools")
    
    print()
    print("=" * 60)
    print("PERMISSION TEST COMPLETE")
    print("=" * 60)
    print()
    print("If you see FORBIDDEN errors above, you need to:")
    print("1. Go to Cloudflare Dashboard > My Profile > API Tokens")
    print("2. Create a new token with these permissions:")
    print("   - Zone:Zone:Edit")
    print("   - Zone:DNS:Edit")
    print("   - Zone:Zone Settings:Edit")
    print("   - Zone:Page Rules:Edit")
    print("   - Zone:Zone WAF:Edit")
    print("   - Zone:Access: Service Tokens:Edit")
    print("   - Account:Cloudflare Workers:Edit")
    print("   - Account:Account Load Balancers:Edit")
    print("   - Account:Access: Apps and Policies:Edit")
    print("3. Replace the CLOUDFLARE_API_TOKEN in your .env file")

if __name__ == "__main__":
    main()
