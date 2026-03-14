#!/usr/bin/env python3
"""
PYRAXUS Portfolio Backend Contact Form API Testing Script
Tests the contact form submission and retrieval APIs
"""

import requests
import json
import sys
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://cyberpunk-dev-11.preview.emergentagent.com/api"

def print_test_result(test_name, success, details=None):
    """Print formatted test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} {test_name}")
    if details:
        print(f"   Details: {details}")

def test_valid_contact_submission():
    """Test Case 1: Valid contact form submission"""
    print("\n" + "="*60)
    print("TEST 1: Valid Contact Form Submission")
    print("="*60)
    
    url = f"{BACKEND_URL}/contact"
    payload = {
        "name": "John Doe",
        "email": "john@example.com", 
        "message": "This is a test message for the PYRAXUS contact form."
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "id" in data.get("data", {}):
                print_test_result("Valid Contact Submission", True, "Contact form submitted successfully")
                return data.get("data", {}).get("id")
            else:
                print_test_result("Valid Contact Submission", False, "Response missing success flag or contact ID")
                return None
        else:
            print_test_result("Valid Contact Submission", False, f"Expected 200, got {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("Valid Contact Submission", False, f"Request failed: {str(e)}")
        return None

def test_invalid_email():
    """Test Case 2: Invalid email format"""
    print("\n" + "="*60)
    print("TEST 2: Invalid Email Format")
    print("="*60)
    
    url = f"{BACKEND_URL}/contact"
    payload = {
        "name": "Jane Doe",
        "email": "invalid-email",
        "message": "Testing with invalid email"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print_test_result("Invalid Email Validation", True, "Correctly rejected invalid email")
            return True
        else:
            print_test_result("Invalid Email Validation", False, f"Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Invalid Email Validation", False, f"Request failed: {str(e)}")
        return False

def test_missing_fields():
    """Test Case 3: Missing required fields"""
    print("\n" + "="*60)
    print("TEST 3: Missing Required Fields")
    print("="*60)
    
    url = f"{BACKEND_URL}/contact"
    payload = {
        "name": "Test User"
        # Missing email and message
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print_test_result("Missing Fields Validation", True, "Correctly rejected missing fields")
            return True
        else:
            print_test_result("Missing Fields Validation", False, f"Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Missing Fields Validation", False, f"Request failed: {str(e)}")
        return False

def test_short_message():
    """Test Case 4: Message too short"""
    print("\n" + "="*60)
    print("TEST 4: Message Too Short")
    print("="*60)
    
    url = f"{BACKEND_URL}/contact"
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "message": "Short"  # Only 5 characters, minimum is 10
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 422:
            print_test_result("Short Message Validation", True, "Correctly rejected short message")
            return True
        else:
            print_test_result("Short Message Validation", False, f"Expected 422, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Short Message Validation", False, f"Request failed: {str(e)}")
        return False

def test_get_contacts(created_contact_id=None):
    """Test Case 5: Get all contacts"""
    print("\n" + "="*60)
    print("TEST 5: Get All Contacts")
    print("="*60)
    
    url = f"{BACKEND_URL}/contacts"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and isinstance(data.get("data"), list):
                contacts = data.get("data", [])
                print(f"Found {len(contacts)} contacts")
                
                # If we created a contact, check if it's in the list
                if created_contact_id:
                    found_contact = any(contact.get("id") == created_contact_id for contact in contacts)
                    if found_contact:
                        print_test_result("Get Contacts", True, f"Successfully retrieved contacts including newly created one")
                        return True
                    else:
                        print_test_result("Get Contacts", False, "Created contact not found in contacts list")
                        return False
                else:
                    print_test_result("Get Contacts", True, "Successfully retrieved contacts list")
                    return True
            else:
                print_test_result("Get Contacts", False, "Response missing success flag or data array")
                return False
        else:
            print_test_result("Get Contacts", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Get Contacts", False, f"Request failed: {str(e)}")
        return False

def test_server_connectivity():
    """Test basic server connectivity"""
    print("\n" + "="*60)
    print("CONNECTIVITY TEST: Backend Server")
    print("="*60)
    
    url = f"{BACKEND_URL}/"
    
    try:
        response = requests.get(url, timeout=10)
        
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print_test_result("Server Connectivity", True, "Backend server is accessible")
            return True
        else:
            print_test_result("Server Connectivity", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("Server Connectivity", False, f"Cannot reach backend server: {str(e)}")
        return False

def main():
    """Main testing function"""
    print("PYRAXUS PORTFOLIO BACKEND CONTACT API TESTING")
    print("=" * 60)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Test server connectivity first
    connectivity = test_server_connectivity()
    results.append(("Server Connectivity", connectivity))
    
    if not connectivity:
        print("\n❌ CRITICAL: Cannot reach backend server. Stopping tests.")
        return False
    
    # Run all test cases
    created_contact_id = test_valid_contact_submission()
    results.append(("Valid Contact Submission", created_contact_id is not None))
    
    invalid_email_result = test_invalid_email()
    results.append(("Invalid Email Validation", invalid_email_result))
    
    missing_fields_result = test_missing_fields()
    results.append(("Missing Fields Validation", missing_fields_result))
    
    short_message_result = test_short_message()
    results.append(("Short Message Validation", short_message_result))
    
    get_contacts_result = test_get_contacts(created_contact_id)
    results.append(("Get Contacts", get_contacts_result))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Contact form API is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the details above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)