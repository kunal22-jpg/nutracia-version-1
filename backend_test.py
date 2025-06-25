import requests
import json
import sys
import time
import uuid
from datetime import datetime

class NutraciaAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user = {
            "email": f"test_user_{uuid.uuid4()}@test.com",
            "password": "Test123!",
            "name": "Test User",
            "age": 30,
            "health_goals": ["Weight Management", "Better Sleep", "Stress Reduction"]
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        self.tests_run += 1
        
        if not headers and self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
        
        if not headers:
            headers = {}
            
        headers['Content-Type'] = 'application/json'
        
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, None

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, None
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.json()}")
                except:
                    print(f"Response: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_signup(self):
        """Test user signup"""
        success, response = self.run_test(
            "User Signup",
            "POST",
            "api/signup",
            200,
            data=self.test_user
        )
        
        if success and response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            print(f"📝 Created test user with ID: {self.user_id}")
        
        return success, response

    def test_login(self):
        """Test user login"""
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "api/login",
            200,
            data=login_data
        )
        
        if success and response and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user_id']
            print(f"🔑 Logged in as user with ID: {self.user_id}")
        
        return success, response

    def test_get_profile(self):
        """Test getting user profile"""
        if not self.user_id:
            print("❌ Cannot test profile - No user ID")
            return False, None
            
        return self.run_test(
            "Get User Profile",
            "GET",
            f"api/profile/{self.user_id}",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_update_profile(self):
        """Test updating user profile"""
        if not self.user_id:
            print("❌ Cannot test profile update - No user ID")
            return False, None
            
        profile_data = {
            "name": "Updated Test User",
            "fitness_level": "Intermediate",
            "dietary_preferences": ["Vegetarian", "Low Carb"]
        }
            
        return self.run_test(
            "Update User Profile",
            "PUT",
            f"api/profile/{self.user_id}",
            200,
            data=profile_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_get_dashboard(self):
        """Test getting user dashboard"""
        if not self.user_id:
            print("❌ Cannot test dashboard - No user ID")
            return False, None
            
        return self.run_test(
            "Get User Dashboard",
            "GET",
            f"api/dashboard/{self.user_id}",
            200,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_chat_with_ai(self, message="What should I eat for breakfast to boost energy?"):
        """Test the AI chat functionality"""
        if not self.user_id:
            print("❌ Cannot test AI chat - No user ID")
            return False, None
            
        chat_data = {
            "message": message,
            "user_id": self.user_id
        }
            
        return self.run_test(
            f"Chat with AI: '{message}'",
            "POST",
            "api/chat/ai",
            200,
            data=chat_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def test_cart_sync(self):
        """Test cart synchronization"""
        if not self.user_id:
            print("❌ Cannot test cart sync - No user ID")
            return False, None
            
        cart_data = {
            "user_id": self.user_id,
            "items": [
                {
                    "product_name": "Organic Protein Powder",
                    "category": "Supplements",
                    "price": 29.99,
                    "quantity": 1
                },
                {
                    "product_name": "Vitamin D3 Supplements",
                    "category": "Vitamins",
                    "price": 15.99,
                    "quantity": 2
                }
            ]
        }
            
        return self.run_test(
            "Sync Cart",
            "POST",
            "api/cart/sync",
            200,
            data=cart_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Nutracía API Tests")
        print("=" * 50)
        
        # Test root endpoint
        self.test_root_endpoint()
        
        # Test user signup
        signup_success, _ = self.test_signup()
        
        # If signup fails, try login (in case user already exists)
        if not signup_success:
            self.test_login()
        
        # Test profile endpoints
        self.test_get_profile()
        self.test_update_profile()
        
        # Test dashboard
        self.test_get_dashboard()
        
        # Test cart sync
        self.test_cart_sync()
        
        # Test AI chat with multiple wellness questions
        print("\n🤖 Testing AI Chat with Multiple Wellness Questions:")
        print("-" * 50)
        
        wellness_questions = [
            "What should I eat for breakfast to boost energy?",
            "Can you recommend a 5-minute morning skincare routine?",
            "What exercises can I do at home for stress relief?"
        ]
        
        for question in wellness_questions:
            chat_success, chat_response = self.test_chat_with_ai(question)
            
            if chat_success and chat_response:
                print(f"\n🤖 AI Response to: '{question}'")
                print("-" * 50)
                response_text = chat_response.get('response', '')
                preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
                print(preview)
                print("-" * 50)
        
        # Print results
        print("\n📊 Test Results:")
        print(f"Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Get the backend URL from environment or use default
    import os
    backend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
    
    print(f"Using backend URL: {backend_url}")
    
    tester = NutraciaAPITester(backend_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)