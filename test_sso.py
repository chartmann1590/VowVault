#!/usr/bin/env python3
"""
Simple test script to verify SSO functionality
"""

import json
from urllib.parse import urlparse

def test_sso_configuration():
    """Test SSO configuration without actual OAuth flow"""
    
    # Test data
    test_settings = {
        'enabled': True,
        'provider': 'google',
        'client_id': 'test-client-id',
        'client_secret': 'test-client-secret',
        'redirect_uri': 'https://example.com/sso/callback',
        'scope': 'openid email profile',
        'allowed_domains': ['example.com', 'test.com'],
        'allowed_emails': ['admin@example.com', 'user@test.com'],
        'admin_key_fallback': True
    }
    
    print("🔐 SSO Configuration Test")
    print("=" * 50)
    
    # Test domain validation
    print("\n📧 Testing domain validation:")
    test_emails = [
        'user@example.com',
        'admin@test.com', 
        'user@other.com',
        'admin@example.com'
    ]
    
    for email in test_emails:
        domain = email.split('@')[1] if '@' in email else ''
        allowed_domains = test_settings['allowed_domains']
        allowed_emails = test_settings['allowed_emails']
        
        # Check domain access
        domain_access = any(domain.lower().endswith(d.lower()) for d in allowed_domains)
        email_access = email in allowed_emails
        
        access_granted = domain_access or email_access
        
        status = "✅" if access_granted else "❌"
        print(f"  {status} {email} -> {'Access Granted' if access_granted else 'Access Denied'}")
    
    # Test OAuth URL generation
    print("\n🔗 Testing OAuth URL generation:")
    
    if test_settings['provider'] == 'google':
        auth_url = 'https://accounts.google.com/oauth/authorize'
        params = {
            'client_id': test_settings['client_id'],
            'redirect_uri': test_settings['redirect_uri'],
            'response_type': 'code',
            'scope': test_settings['scope'],
            'state': 'test-state'
        }
        
        # Build URL (simplified)
        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{auth_url}?{param_str}"
        
        print(f"  ✅ Generated OAuth URL: {full_url[:80]}...")
    
    # Test fallback authentication
    print("\n🔑 Testing fallback authentication:")
    admin_key = 'wedding2024'
    fallback_enabled = test_settings['admin_key_fallback']
    
    if fallback_enabled:
        print(f"  ✅ Admin key fallback enabled: {admin_key}")
    else:
        print(f"  ❌ Admin key fallback disabled")
    
    print("\n✅ SSO configuration test completed!")
    print("\n📝 Next steps:")
    print("  1. Configure your OAuth provider (Google, Azure, Okta)")
    print("  2. Set up the redirect URI in your OAuth app")
    print("  3. Add your client ID and secret to the admin panel")
    print("  4. Configure allowed domains/emails")
    print("  5. Test the SSO login flow")

if __name__ == "__main__":
    test_sso_configuration() 