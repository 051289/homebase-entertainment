import requests
import sys
import json
from datetime import datetime

class RecordingStudioAPITester:
    def __init__(self, base_url="https://studio-master-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_user = None
        self.test_project = None
        self.test_contract = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, use_json=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers=headers)
                elif use_json:
                    # JSON data
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers)
                else:
                    # Form data
                    response = requests.post(url, data=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and 'id' in response_data:
                        print(f"   Response ID: {response_data['id']}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "full_name": f"Test User {timestamp}",
            "is_artist": True
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=user_data
        )
        
        if success and 'id' in response:
            self.test_user = response
            print(f"   Created user: {response['username']} (ID: {response['id']})")
            return True
        return False

    def test_get_users(self):
        """Test getting all users"""
        success, response = self.run_test(
            "Get All Users",
            "GET",
            "auth/users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} users")
            return True
        return False

    def test_get_user_by_id(self):
        """Test getting user by ID"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get User by ID",
            "GET",
            f"auth/user/{self.test_user['id']}",
            200
        )
        
        if success and response.get('id') == self.test_user['id']:
            print(f"   Retrieved user: {response['username']}")
            return True
        return False

    def test_create_project(self):
        """Test project creation"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        project_data = {
            "title": "Test Recording Project",
            "description": "A test project for the recording studio",
            "user_id": self.test_user['id'],
            "bpm": 120,
            "key_signature": "C"
        }
        
        success, response = self.run_test(
            "Create Project",
            "POST",
            "projects",
            200,
            data=project_data,
            use_json=False
        )
        
        if success and 'id' in response:
            self.test_project = response
            print(f"   Created project: {response['title']} (ID: {response['id']})")
            return True
        return False

    def test_get_projects(self):
        """Test getting projects"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get User Projects",
            "GET",
            f"projects?user_id={self.test_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} projects for user")
            return True
        return False

    def test_get_project_by_id(self):
        """Test getting project by ID"""
        if not self.test_project:
            print("❌ Skipping - No test project available")
            return False
            
        success, response = self.run_test(
            "Get Project by ID",
            "GET",
            f"projects/{self.test_project['id']}",
            200
        )
        
        if success and response.get('id') == self.test_project['id']:
            print(f"   Retrieved project: {response['title']}")
            return True
        return False

    def test_create_sound_pack(self):
        """Test sound pack creation"""
        pack_data = {
            "name": "Test Hip-Hop Pack",
            "description": "A collection of hip-hop beats and samples",
            "genre": "Hip-Hop",
            "author": "Test Producer",
            "tags": ["hip-hop", "beats", "samples"],
            "is_premium": False
        }
        
        success, response = self.run_test(
            "Create Sound Pack",
            "POST",
            "soundpacks",
            200,
            data=pack_data,
            use_json=False
        )
        
        if success and 'id' in response:
            print(f"   Created sound pack: {response['name']} (ID: {response['id']})")
            return True
        return False

    def test_get_sound_packs(self):
        """Test getting sound packs"""
        success, response = self.run_test(
            "Get Sound Packs",
            "GET",
            "soundpacks",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} sound packs")
            return True
        return False

    def test_create_contract(self):
        """Test contract creation"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        contract_data = {
            "artist_name": self.test_user['full_name'],
            "contract_type": "artist_agreement",
            "user_id": self.test_user['id']
        }
        
        success, response = self.run_test(
            "Create Contract",
            "POST",
            "contracts",
            200,
            data=contract_data
        )
        
        if success and 'id' in response:
            self.test_contract = response
            print(f"   Created contract: {response['contract_type']} (ID: {response['id']})")
            return True
        return False

    def test_get_contracts(self):
        """Test getting contracts"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get User Contracts",
            "GET",
            f"contracts?user_id={self.test_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} contracts for user")
            return True
        return False

    def test_sign_contract(self):
        """Test contract signing"""
        if not self.test_contract:
            print("❌ Skipping - No test contract available")
            return False
            
        signature_data = {
            "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
        
        success, response = self.run_test(
            "Sign Contract",
            "POST",
            f"contracts/{self.test_contract['id']}/sign",
            200,
            data=signature_data
        )
        
        if success:
            print(f"   Contract signed successfully")
            return True
        return False

def main():
    print("🎵 T.H.U.G N HOMEBASE ENT. Recording Studio API Test Suite")
    print("=" * 60)
    
    tester = RecordingStudioAPITester()
    
    # Test sequence
    tests = [
        ("User Registration", tester.test_user_registration),
        ("Get All Users", tester.test_get_users),
        ("Get User by ID", tester.test_get_user_by_id),
        ("Create Project", tester.test_create_project),
        ("Get Projects", tester.test_get_projects),
        ("Get Project by ID", tester.test_get_project_by_id),
        ("Create Sound Pack", tester.test_create_sound_pack),
        ("Get Sound Packs", tester.test_get_sound_packs),
        ("Create Contract", tester.test_create_contract),
        ("Get Contracts", tester.test_get_contracts),
        ("Sign Contract", tester.test_sign_contract),
    ]
    
    print(f"\nRunning {len(tests)} API tests...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} - Unexpected error: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend API tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())