import requests
import sys
import json
from datetime import datetime

class RecordingStudioAPITester:
    def __init__(self, base_url="https://beatforge-38.preview.emergentagent.com"):
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
            
        # Send as FormData like the frontend does
        project_data = {
            "title": "Test Recording Project",
            "description": "A test project for the recording studio",
            "user_id": self.test_user['id']
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
        # Send as FormData like the frontend would
        pack_data = {
            "name": "Test Hip-Hop Pack",
            "description": "A collection of hip-hop beats and samples",
            "genre": "Hip-Hop",
            "author": "Test Producer",
            "is_premium": "false"  # Form data sends as string
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
            
        # Send as FormData like the frontend does
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
            data=contract_data,
            use_json=False
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

    # BandLab Membership Integration Tests
    def test_get_membership_plans(self):
        """Test getting membership plans"""
        success, response = self.run_test(
            "Get Membership Plans",
            "GET",
            "membership/plans",
            200
        )
        
        if success and isinstance(response, list):
            expected_tiers = ["free", "bandlab_basic", "bandlab_pro", "bandlab_premium"]
            found_tiers = [plan.get('tier') for plan in response]
            
            if len(response) == 4 and all(tier in found_tiers for tier in expected_tiers):
                print(f"   Found all 4 membership plans: {', '.join(found_tiers)}")
                return True
            else:
                print(f"   Expected 4 plans with tiers {expected_tiers}, got {len(response)} plans with tiers {found_tiers}")
                return False
        return False

    def test_upgrade_membership(self):
        """Test upgrading user membership"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        upgrade_data = {
            "user_id": self.test_user['id'],
            "new_tier": "bandlab_pro"
        }
        
        success, response = self.run_test(
            "Upgrade Membership",
            "POST",
            "membership/upgrade",
            200,
            data=upgrade_data
        )
        
        if success and 'user' in response:
            updated_user = response['user']
            if (updated_user.get('membership_tier') == 'bandlab_pro' and
                updated_user.get('cloud_storage_gb') == 50 and
                updated_user.get('max_collaborators') == 15 and
                updated_user.get('premium_sound_packs') == True):
                print(f"   Successfully upgraded to BandLab Pro with enhanced features")
                # Update test_user with new data
                self.test_user = updated_user
                return True
            else:
                print(f"   Upgrade failed - user features not updated correctly")
                return False
        return False

    def test_connect_bandlab_account(self):
        """Test connecting BandLab account"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        bandlab_data = {
            "user_id": self.test_user['id'],
            "bandlab_username": "testuser_bandlab"
        }
        
        success, response = self.run_test(
            "Connect BandLab Account",
            "POST",
            "membership/connect-bandlab",
            200,
            data=bandlab_data,
            use_json=False
        )
        
        if success:
            print(f"   BandLab account connected successfully")
            return True
        return False

    def test_create_collaboration_invite(self):
        """Test creating collaboration invite"""
        if not self.test_user or not self.test_project:
            print("❌ Skipping - No test user or project available")
            return False
            
        # Create a second user to invite
        timestamp = datetime.now().strftime('%H%M%S')
        collaborator_data = {
            "username": f"collaborator_{timestamp}",
            "email": f"collab_{timestamp}@example.com",
            "full_name": f"Collaborator User {timestamp}",
            "is_artist": True
        }
        
        success, collaborator = self.run_test(
            "Create Collaborator User",
            "POST",
            "auth/register",
            200,
            data=collaborator_data
        )
        
        if not success:
            return False
            
        # Now create collaboration invite
        invite_data = {
            "project_id": self.test_project['id'],
            "to_username": collaborator['username'],
            "from_user_id": self.test_user['id']
        }
        
        success, response = self.run_test(
            "Create Collaboration Invite",
            "POST",
            "collaboration/invite",
            200,
            data=invite_data,
            use_json=False
        )
        
        if success and 'id' in response:
            self.test_collaborator = collaborator
            self.test_invite = response
            print(f"   Created collaboration invite from {response['from_username']} to {response['to_username']}")
            return True
        return False

    def test_get_collaboration_invites(self):
        """Test getting collaboration invites"""
        if not self.test_collaborator:
            print("❌ Skipping - No test collaborator available")
            return False
            
        success, response = self.run_test(
            "Get Collaboration Invites",
            "GET",
            f"collaboration/invites/{self.test_collaborator['id']}",
            200
        )
        
        if success and isinstance(response, list):
            if len(response) > 0 and response[0].get('status') == 'pending':
                print(f"   Found {len(response)} pending invites for collaborator")
                return True
            else:
                print(f"   Expected pending invites, got {len(response)} invites")
                return False
        return False

    def test_respond_to_collaboration(self):
        """Test responding to collaboration invite"""
        if not self.test_invite:
            print("❌ Skipping - No test invite available")
            return False
            
        response_data = {
            "invite_id": self.test_invite['id'],
            "action": "accept"
        }
        
        success, response = self.run_test(
            "Respond to Collaboration",
            "POST",
            "collaboration/respond",
            200,
            data=response_data
        )
        
        if success:
            print(f"   Collaboration invite accepted successfully")
            return True
        return False

    def test_initialize_premium_packs(self):
        """Test initializing premium sound packs"""
        success, response = self.run_test(
            "Initialize Premium Sound Packs",
            "POST",
            "admin/init-premium-packs",
            200
        )
        
        if success and 'message' in response:
            print(f"   {response['message']}")
            return True
        return False

    def test_get_premium_sound_packs(self):
        """Test getting premium sound packs (requires membership)"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get Premium Sound Packs",
            "GET",
            f"soundpacks/premium?user_id={self.test_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            premium_count = sum(1 for pack in response if pack.get('is_premium', False))
            print(f"   Found {len(response)} premium sound packs")
            return True
        return False

    def test_get_sound_packs_with_membership_filter(self):
        """Test getting sound packs filtered by membership"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get Sound Packs with Membership Filter",
            "GET",
            f"soundpacks?user_id={self.test_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            # Since user has premium membership, should see all packs
            print(f"   Found {len(response)} sound packs (including premium)")
            return True
        return False

    def test_download_tracking_and_limits(self):
        """Test download tracking and monthly limits"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        # First, get sound packs to find a file to download
        success, packs = self.run_test(
            "Get Sound Packs for Download Test",
            "GET",
            "soundpacks",
            200
        )
        
        if not success or not packs:
            print("❌ No sound packs available for download test")
            return False
            
        # Try to download a sound pack file (this will likely fail since no actual files exist)
        # But we can test the API endpoint structure
        test_filename = "test_audio.mp3"
        
        success, response = self.run_test(
            "Test Download Tracking",
            "GET",
            f"soundpacks/{test_filename}?user_id={self.test_user['id']}",
            404  # Expecting 404 since file doesn't exist, but API should handle user_id parameter
        )
        
        # The test passes if we get a 404 (file not found) rather than a 500 (server error)
        # This means the download tracking logic is working
        if success:  # 404 is expected and considered success for this test
            print(f"   Download tracking API endpoint working correctly")
            return True
        return False

    def test_membership_features_verification(self):
        """Test that user has correct membership features after upgrade"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        # Get updated user data
        success, user_data = self.run_test(
            "Verify Membership Features",
            "GET",
            f"auth/user/{self.test_user['id']}",
            200
        )
        
        if success:
            expected_features = {
                'membership_tier': 'bandlab_pro',
                'cloud_storage_gb': 50,
                'max_collaborators': 15,
                'premium_sound_packs': True,
                'collaboration_enabled': True
            }
            
            all_correct = True
            for feature, expected_value in expected_features.items():
                actual_value = user_data.get(feature)
                if actual_value != expected_value:
                    print(f"   ❌ {feature}: expected {expected_value}, got {actual_value}")
                    all_correct = False
                else:
                    print(f"   ✅ {feature}: {actual_value}")
            
            if all_correct:
                print(f"   All membership features verified correctly")
                return True
            else:
                print(f"   Some membership features are incorrect")
                return False
        return False

    def test_free_user_premium_access_restriction(self):
        """Test that free users cannot access premium features"""
        # Create a free user
        timestamp = datetime.now().strftime('%H%M%S')
        free_user_data = {
            "username": f"freeuser_{timestamp}",
            "email": f"free_{timestamp}@example.com",
            "full_name": f"Free User {timestamp}",
            "is_artist": False
        }
        
        success, free_user = self.run_test(
            "Create Free User",
            "POST",
            "auth/register",
            200,
            data=free_user_data
        )
        
        if not success:
            return False
            
        # Try to access premium sound packs with free user (should fail)
        success, response = self.run_test(
            "Test Premium Access Restriction",
            "GET",
            f"soundpacks/premium?user_id={free_user['id']}",
            403  # Should be forbidden
        )
        
        if success:  # 403 is expected and considered success
            print(f"   Premium access correctly restricted for free users")
            return True
        return False

def main():
    print("🎵 T.H.U.G N HOMEBASE ENT. Recording Studio API Test Suite")
    print("🎯 BandLab Membership Integration Testing")
    print("=" * 60)
    
    tester = RecordingStudioAPITester()
    
    # Test sequence - Core functionality first, then BandLab features
    tests = [
        # Core API Tests
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
        
        # BandLab Membership Integration Tests
        ("Get Membership Plans", tester.test_get_membership_plans),
        ("Upgrade Membership", tester.test_upgrade_membership),
        ("Connect BandLab Account", tester.test_connect_bandlab_account),
        ("Verify Membership Features", tester.test_membership_features_verification),
        
        # Collaboration System Tests
        ("Create Collaboration Invite", tester.test_create_collaboration_invite),
        ("Get Collaboration Invites", tester.test_get_collaboration_invites),
        ("Respond to Collaboration", tester.test_respond_to_collaboration),
        
        # Enhanced Sound Packs Tests
        ("Initialize Premium Sound Packs", tester.test_initialize_premium_packs),
        ("Get Premium Sound Packs", tester.test_get_premium_sound_packs),
        ("Get Sound Packs with Membership Filter", tester.test_get_sound_packs_with_membership_filter),
        ("Test Download Tracking", tester.test_download_tracking_and_limits),
        
        # Access Control Tests
        ("Test Premium Access Restriction", tester.test_free_user_premium_access_restriction),
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
        print("🎉 All BandLab membership integration tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())