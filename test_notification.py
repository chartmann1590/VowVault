#!/usr/bin/env python3
import requests
import json

# Test the notification system
base_url = "http://localhost:5000"
user_id = "test_user_123"

# Set up session with user identifier
session = requests.Session()
session.cookies.set('user_identifier', user_id)

# Test 1: Check if we can access the main page
print("Testing main page access...")
response = session.get(f"{base_url}/")
print(f"Main page status: {response.status_code}")

# Test 2: Create a test notification
print("\nCreating test notification...")
response = session.get(f"{base_url}/test-notification")
print(f"Test notification status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {response.text}")

# Test 3: Check notifications
print("\nChecking notifications...")
response = session.get(f"{base_url}/api/notifications/check")
print(f"Check notifications status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Notifications: {json.dumps(data, indent=2)}")

# Test 4: Check if FAB elements exist in the page
print("\nChecking page for FAB elements...")
response = session.get(f"{base_url}/")
if response.status_code == 200:
    content = response.text
    if 'notificationFab' in content:
        print("✓ notificationFab found in page")
    else:
        print("✗ notificationFab NOT found in page")
    
    if 'notificationBadge' in content:
        print("✓ notificationBadge found in page")
    else:
        print("✗ notificationBadge NOT found in page")
    
    if 'checkForNotifications' in content:
        print("✓ checkForNotifications function found in page")
    else:
        print("✗ checkForNotifications function NOT found in page")
else:
    print(f"Failed to get main page: {response.status_code}") 