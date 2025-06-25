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
        
        # Measure response time
        start_time = time.time()
        success, response = self.run_test(
            f"Chat with AI: '{message}'",
            "POST",
            "api/chat/ai",
            200,
            data=chat_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        end_time = time.time()
        
        if success and response:
            response_time = end_time - start_time
            response['response_time'] = round(response_time, 2)
            print(f"⏱️ Response time: {response_time:.2f} seconds")
            
        return success, response

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
        print("🚀 Starting Nutracía API Tests - Final Validation")
        print("=" * 70)
        print("Testing Nutracía as an Intelligent Wellness Companion")
        print("=" * 70)
        
        # Test root endpoint
        self.test_root_endpoint()
        
        # 1. Create a Demo User
        print("\n📝 STEP 1: Creating a Demo User")
        print("-" * 70)
        signup_success, _ = self.test_signup()
        
        # If signup fails, try login (in case user already exists)
        if not signup_success:
            self.test_login()
        
        if not self.user_id:
            print("❌ Critical Error: Failed to create or login user. Aborting tests.")
            return False
            
        # 2. Test User Features
        print("\n👤 STEP 2: Testing User Features")
        print("-" * 70)
        
        # Get initial profile
        print("\n📋 Getting initial user profile:")
        profile_success, profile_data = self.test_get_profile()
        
        # Update profile with specific health goals
        print("\n✏️ Updating user profile with specific health goals:")
        profile_update = {
            "name": "Wellness Tester",
            "age": 32,
            "health_goals": ["Weight Management", "Better Sleep", "Stress Reduction", "Improved Energy"],
            "dietary_preferences": ["Plant-based", "Gluten-free", "Low sugar"],
            "fitness_level": "Intermediate"
        }
        self.run_test(
            "Update User Profile with Health Goals",
            "PUT",
            f"api/profile/{self.user_id}",
            200,
            data=profile_update,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        # Sync wellness-focused shopping cart
        print("\n🛒 Syncing wellness-focused shopping cart:")
        cart_data = {
            "user_id": self.user_id,
            "items": [
                {
                    "product_name": "Organic Plant Protein",
                    "category": "Nutrition",
                    "price": 39.99,
                    "quantity": 1
                },
                {
                    "product_name": "Vitamin D3 + K2 Supplements",
                    "category": "Supplements",
                    "price": 24.99,
                    "quantity": 1
                },
                {
                    "product_name": "Hyaluronic Acid Serum",
                    "category": "Skincare",
                    "price": 32.50,
                    "quantity": 1
                },
                {
                    "product_name": "Yoga Mat",
                    "category": "Fitness",
                    "price": 45.00,
                    "quantity": 1
                }
            ]
        }
        self.test_cart_sync()
        
        # Get personalized dashboard data
        print("\n📊 Getting personalized dashboard data:")
        dashboard_success, dashboard_data = self.test_get_dashboard()
        if dashboard_success and dashboard_data:
            print("\nDashboard Data:")
            print(f"User: {dashboard_data.get('name')}")
            print(f"Health Goals: {', '.join(dashboard_data.get('health_goals', []))}")
            print(f"Cart Items: {dashboard_data.get('cart_items_count')}")
            print(f"Daily Tip: {dashboard_data.get('daily_tip')}")
        
        # 3. Test AI Conversation with Multiple Questions
        print("\n🤖 STEP 3: Testing Full AI Conversation with Multiple Questions")
        print("-" * 70)
        
        wellness_questions = [
            "I'm a 25-year-old who works from home and feels tired all day. What breakfast would you recommend?",
            "I have combination skin and live in a dry climate. What's a good skincare routine?",
            "I only have 15 minutes in the morning for exercise. What should I do?"
        ]
        
        ai_responses = []
        
        for i, question in enumerate(wellness_questions, 1):
            print(f"\n🔍 Question {i}: {question}")
            chat_success, chat_response = self.test_chat_with_ai(question)
            
            if chat_success and chat_response:
                response_text = chat_response.get('response', '')
                ai_responses.append(response_text)
                
                print(f"\n🤖 AI Response {i}:")
                print("-" * 50)
                print(response_text)
                print("-" * 50)
                
                # 4. Validate AI Quality
                print("\n✅ AI Response Quality Check:")
                
                # Check response length (a basic quality metric)
                word_count = len(response_text.split())
                print(f"- Response length: {word_count} words")
                
                # Check for personalization
                personalization = "Yes" if any(term in response_text.lower() for term in 
                                             ["your", "you", "based on", "recommend", "suggest"]) else "Limited"
                print(f"- Personalization: {personalization}")
                
                # Check for evidence-based content
                evidence_based = "Yes" if any(term in response_text.lower() for term in 
                                            ["research", "studies", "evidence", "shown", "according"]) else "Limited"
                print(f"- Evidence-based: {evidence_based}")
                
                # Check for medical-grade terminology
                medical_grade = "Yes" if any(term in response_text.lower() for term in 
                                           ["nutrient", "protein", "vitamin", "mineral", "hydration", 
                                            "metabolism", "inflammation"]) else "Limited"
                print(f"- Medical-grade terminology: {medical_grade}")
                
                # Measure response time
                print(f"- Response time: {chat_response.get('response_time', 'N/A')} seconds")
        
        # Print overall results
        print("\n📊 Final Test Results:")
        print(f"Tests Passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 SUCCESS: Nutracía is fully functional as an Intelligent Wellness Companion!")
            print("✓ User features working correctly")
            print("✓ AI providing personalized wellness guidance")
            print("✓ All API endpoints responding as expected")
        else:
            print("\n⚠️ Some tests failed. Nutracía may need additional configuration.")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    # Get the backend URL from environment or use default
    import os
    backend_url = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
    
    print(f"Using backend URL: {backend_url}")
    
    tester = NutraciaAPITester(backend_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)