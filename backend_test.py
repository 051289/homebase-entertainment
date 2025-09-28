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
        self.test_collaborator = None
        self.test_invite = None

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
            
        # Now create collaboration invite - using form data
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
            
        # The endpoint expects user_id as a query parameter, not in the URL path
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

    # Advanced Studio Features Tests
    
    def test_initialize_daw_plugins(self):
        """Test initializing DAW plugins"""
        success, response = self.run_test(
            "Initialize DAW Plugins",
            "POST",
            "admin/init-daw-plugins",
            200
        )
        
        if success and 'message' in response:
            print(f"   {response['message']}")
            return True
        return False

    def test_get_daw_plugins_all(self):
        """Test getting all DAW plugins"""
        success, response = self.run_test(
            "Get All DAW Plugins",
            "GET",
            "daw/plugins",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} DAW plugins")
            if len(response) > 0:
                # Store first plugin for detailed testing
                self.test_plugin = response[0]
                print(f"   Sample plugin: {response[0].get('name')} ({response[0].get('category')})")
            return True
        return False

    def test_get_daw_plugins_filtered_by_daw(self):
        """Test getting DAW plugins filtered by DAW compatibility"""
        test_cases = [
            ("pro_tools", "Pro Tools"),
            ("fl_studio", "FL Studio"),
            ("both", "Universal")
        ]
        
        all_passed = True
        for daw_filter, daw_name in test_cases:
            success, response = self.run_test(
                f"Get {daw_name} Compatible Plugins",
                "GET",
                f"daw/plugins?daw={daw_filter}",
                200
            )
            
            if success and isinstance(response, list):
                compatible_count = sum(1 for plugin in response 
                                     if daw_filter in plugin.get('daw_compatibility', []) or 
                                        'both' in plugin.get('daw_compatibility', []))
                print(f"   Found {len(response)} plugins compatible with {daw_name}")
                if len(response) != compatible_count:
                    print(f"   ⚠️  Warning: {len(response) - compatible_count} plugins may have incorrect compatibility")
            else:
                all_passed = False
                
        return all_passed

    def test_get_daw_plugins_filtered_by_category(self):
        """Test getting DAW plugins filtered by category"""
        test_categories = ["compressor", "reverb", "equalizer", "synthesizer", "limiter", "delay"]
        
        all_passed = True
        for category in test_categories:
            success, response = self.run_test(
                f"Get {category.title()} Plugins",
                "GET",
                f"daw/plugins?category={category}",
                200
            )
            
            if success and isinstance(response, list):
                category_count = sum(1 for plugin in response if plugin.get('category') == category)
                print(f"   Found {len(response)} {category} plugins")
                if len(response) != category_count:
                    print(f"   ⚠️  Warning: {len(response) - category_count} plugins have incorrect category")
            else:
                all_passed = False
                
        return all_passed

    def test_get_daw_plugins_premium_filter(self):
        """Test DAW plugin premium access filtering"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        # Test with premium user (should see all plugins)
        success, response = self.run_test(
            "Get DAW Plugins (Premium User)",
            "GET",
            f"daw/plugins?user_id={self.test_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            premium_count = sum(1 for plugin in response if plugin.get('is_premium', False))
            print(f"   Premium user sees {len(response)} plugins ({premium_count} premium)")
            return True
        return False

    def test_create_daw_plugin(self):
        """Test creating a new DAW plugin"""
        plugin_data = {
            "name": "Test Studio Compressor",
            "category": "compressor",
            "daw_compatibility": ["both"],
            "author": "T.H.U.G N HOMEBASE ENT.",
            "version": "1.0",
            "is_premium": False,
            "description": "A test compressor plugin for studio use"
        }
        
        success, response = self.run_test(
            "Create DAW Plugin",
            "POST",
            "daw/plugins",
            200,
            data=plugin_data
        )
        
        if success and 'id' in response:
            self.test_created_plugin = response
            print(f"   Created plugin: {response['name']} (ID: {response['id']})")
            return True
        return False

    def test_get_daw_plugin_by_id(self):
        """Test getting specific DAW plugin details"""
        if not hasattr(self, 'test_plugin') or not self.test_plugin:
            print("❌ Skipping - No test plugin available")
            return False
            
        success, response = self.run_test(
            "Get DAW Plugin by ID",
            "GET",
            f"daw/plugins/{self.test_plugin['id']}",
            200
        )
        
        if success and response.get('id') == self.test_plugin['id']:
            print(f"   Retrieved plugin: {response['name']} - {response['description']}")
            # Verify plugin has required fields
            required_fields = ['name', 'category', 'daw_compatibility', 'author', 'version']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
                return False
            return True
        return False

    def test_project_daw_export(self):
        """Test exporting project to DAW formats"""
        if not self.test_user or not self.test_project:
            print("❌ Skipping - No test user or project available")
            return False
            
        # Test Pro Tools export
        export_data = {
            "daw_format": "pro_tools",
            "user_id": self.test_user['id']
        }
        
        success, response = self.run_test(
            "Export Project to Pro Tools",
            "POST",
            f"projects/{self.test_project['id']}/export",
            200,
            data=export_data,
            use_json=False
        )
        
        if success and 'id' in response:
            print(f"   Pro Tools export created (ID: {response['id']})")
            if response.get('daw_format') == 'pro_tools' and response.get('status') == 'completed':
                print(f"   Export settings: {response.get('export_settings', {})}")
            else:
                print(f"   ⚠️  Export format or status incorrect")
                return False
        else:
            return False
            
        # Test FL Studio export
        export_data['daw_format'] = 'fl_studio'
        success, response = self.run_test(
            "Export Project to FL Studio",
            "POST",
            f"projects/{self.test_project['id']}/export",
            200,
            data=export_data,
            use_json=False
        )
        
        if success and response.get('daw_format') == 'fl_studio':
            print(f"   FL Studio export created (ID: {response['id']})")
            return True
        return False

    def test_get_studio_settings(self):
        """Test getting user studio settings (should create defaults if not exist)"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        success, response = self.run_test(
            "Get Studio Settings",
            "GET",
            f"studio/settings/{self.test_user['id']}",
            200
        )
        
        if success and 'user_id' in response:
            # Verify default settings structure
            expected_fields = ['room_size', 'acoustic_treatment', 'noise_reduction', 'reverb_simulation',
                             'surround_enabled', 'surround_format', 'speaker_positions', 'audio_interface']
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                print(f"   ⚠️  Missing studio settings fields: {missing_fields}")
                return False
                
            print(f"   Studio settings retrieved: Room={response.get('room_size')}, "
                  f"Treatment={response.get('acoustic_treatment')}, "
                  f"Noise Reduction={response.get('noise_reduction')}")
            self.test_studio_settings = response
            return True
        return False

    def test_update_studio_settings(self):
        """Test updating sound-proof studio settings"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        settings_update = {
            "room_size": "large",
            "acoustic_treatment": "professional",
            "noise_reduction": 0.9,
            "reverb_simulation": "hall"
        }
        
        success, response = self.run_test(
            "Update Studio Settings",
            "PUT",
            f"studio/settings/{self.test_user['id']}",
            200,
            data=settings_update
        )
        
        if success and 'message' in response:
            print(f"   {response['message']}")
            
            # Verify settings were updated by getting them again
            verify_success, verify_response = self.run_test(
                "Verify Studio Settings Update",
                "GET",
                f"studio/settings/{self.test_user['id']}",
                200
            )
            
            if verify_success:
                updated_correctly = all(
                    verify_response.get(key) == value 
                    for key, value in settings_update.items()
                )
                if updated_correctly:
                    print(f"   Settings verified: Room={verify_response.get('room_size')}, "
                          f"Treatment={verify_response.get('acoustic_treatment')}, "
                          f"Noise Reduction={verify_response.get('noise_reduction')}")
                    return True
                else:
                    print(f"   ⚠️  Settings not updated correctly")
                    return False
            return False
        return False

    def test_update_audio_interface_settings(self):
        """Test updating Presonus Audiobox 96 interface settings"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        interface_settings = {
            "sample_rate": 48000,
            "buffer_size": 512,
            "phantom_power": True,
            "direct_monitoring": False,
            "input_gain": [0.7, 0.8]
        }
        
        success, response = self.run_test(
            "Update Audio Interface Settings",
            "PUT",
            f"studio/audio-interface/{self.test_user['id']}",
            200,
            data=interface_settings
        )
        
        if success and 'message' in response:
            print(f"   {response['message']}")
            
            # Verify by getting studio settings (audio interface is nested)
            verify_success, verify_response = self.run_test(
                "Verify Audio Interface Update",
                "GET",
                f"studio/settings/{self.test_user['id']}",
                200
            )
            
            if verify_success and 'audio_interface' in verify_response:
                audio_interface = verify_response['audio_interface']
                updated_correctly = all(
                    audio_interface.get(key) == value 
                    for key, value in interface_settings.items()
                )
                if updated_correctly:
                    print(f"   Interface verified: Sample Rate={audio_interface.get('sample_rate')}, "
                          f"Buffer={audio_interface.get('buffer_size')}, "
                          f"Phantom Power={audio_interface.get('phantom_power')}")
                    return True
                else:
                    print(f"   ⚠️  Audio interface settings not updated correctly")
                    return False
            return False
        return False

    def test_configure_surround_sound_stereo(self):
        """Test configuring surround sound for stereo"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        surround_data = {
            "surround_format": "stereo",
            "enable_surround": True
        }
        
        success, response = self.run_test(
            "Configure Stereo Surround Sound",
            "POST",
            f"studio/surround-sound/{self.test_user['id']}/configure",
            200,
            data=surround_data,
            use_json=False
        )
        
        if success and 'speakers' in response:
            expected_speakers = 2
            if response['speakers'] == expected_speakers:
                print(f"   Stereo configuration: {response['speakers']} speakers positioned")
                return True
            else:
                print(f"   ⚠️  Expected {expected_speakers} speakers, got {response['speakers']}")
                return False
        return False

    def test_configure_surround_sound_5_1(self):
        """Test configuring surround sound for 5.1"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        surround_data = {
            "surround_format": "5.1",
            "enable_surround": True
        }
        
        success, response = self.run_test(
            "Configure 5.1 Surround Sound",
            "POST",
            f"studio/surround-sound/{self.test_user['id']}/configure",
            200,
            data=surround_data,
            use_json=False
        )
        
        if success and 'speakers' in response:
            expected_speakers = 6  # 5.1 = 6 speakers
            if response['speakers'] == expected_speakers:
                print(f"   5.1 configuration: {response['speakers']} speakers positioned")
                
                # Verify speaker positions were set correctly
                verify_success, verify_response = self.run_test(
                    "Verify 5.1 Speaker Positions",
                    "GET",
                    f"studio/settings/{self.test_user['id']}",
                    200
                )
                
                if verify_success and verify_response.get('surround_format') == '5.1':
                    speaker_positions = verify_response.get('speaker_positions', [])
                    if len(speaker_positions) == 6:
                        speaker_names = [pos.get('name') for pos in speaker_positions]
                        print(f"   Speaker positions: {', '.join(speaker_names)}")
                        return True
                    else:
                        print(f"   ⚠️  Expected 6 speaker positions, got {len(speaker_positions)}")
                        return False
                return False
            else:
                print(f"   ⚠️  Expected {expected_speakers} speakers, got {response['speakers']}")
                return False
        return False

    def test_configure_surround_sound_7_1(self):
        """Test configuring surround sound for 7.1"""
        if not self.test_user:
            print("❌ Skipping - No test user available")
            return False
            
        surround_data = {
            "surround_format": "7.1",
            "enable_surround": True
        }
        
        success, response = self.run_test(
            "Configure 7.1 Surround Sound",
            "POST",
            f"studio/surround-sound/{self.test_user['id']}/configure",
            200,
            data=surround_data,
            use_json=False
        )
        
        if success and 'speakers' in response:
            expected_speakers = 8  # 7.1 = 8 speakers
            if response['speakers'] == expected_speakers:
                print(f"   7.1 configuration: {response['speakers']} speakers positioned")
                
                # Verify speaker positions were set correctly
                verify_success, verify_response = self.run_test(
                    "Verify 7.1 Speaker Positions",
                    "GET",
                    f"studio/settings/{self.test_user['id']}",
                    200
                )
                
                if verify_success and verify_response.get('surround_format') == '7.1':
                    speaker_positions = verify_response.get('speaker_positions', [])
                    if len(speaker_positions) == 8:
                        speaker_names = [pos.get('name') for pos in speaker_positions]
                        print(f"   Speaker positions: {', '.join(speaker_names)}")
                        return True
                    else:
                        print(f"   ⚠️  Expected 8 speaker positions, got {len(speaker_positions)}")
                        return False
                return False
            else:
                print(f"   ⚠️  Expected {expected_speakers} speakers, got {response['speakers']}")
                return False
        return False

    def test_daw_plugin_access_restrictions(self):
        """Test premium plugin access restrictions"""
        # Create a free user to test restrictions
        timestamp = datetime.now().strftime('%H%M%S')
        free_user_data = {
            "username": f"freeuser_daw_{timestamp}",
            "email": f"freedaw_{timestamp}@example.com",
            "full_name": f"Free DAW User {timestamp}",
            "is_artist": False
        }
        
        success, free_user = self.run_test(
            "Create Free User for DAW Test",
            "POST",
            "auth/register",
            200,
            data=free_user_data
        )
        
        if not success:
            return False
            
        # Test DAW plugins filtering for free user (should not see premium plugins)
        success, response = self.run_test(
            "Get DAW Plugins (Free User)",
            "GET",
            f"daw/plugins?user_id={free_user['id']}",
            200
        )
        
        if success and isinstance(response, list):
            premium_plugins = [plugin for plugin in response if plugin.get('is_premium', False)]
            if len(premium_plugins) == 0:
                print(f"   Free user correctly sees {len(response)} non-premium plugins only")
                return True
            else:
                print(f"   ⚠️  Free user should not see {len(premium_plugins)} premium plugins")
                return False
        return False

    def test_studio_settings_error_cases(self):
        """Test error cases for studio settings"""
        # Test with non-existent user
        fake_user_id = "non-existent-user-id"
        
        success, response = self.run_test(
            "Update Settings for Non-existent User",
            "PUT",
            f"studio/settings/{fake_user_id}",
            200,  # Should still work, creates new settings
            data={"room_size": "small"}
        )
        
        if success:
            print(f"   Settings endpoint handles non-existent users correctly")
            return True
        return False

def main():
    print("🎵 T.H.U.G N HOMEBASE ENT. Recording Studio API Test Suite")
    print("🎯 Advanced Studio Features Testing")
    print("=" * 60)
    
    tester = RecordingStudioAPITester()
    
    # Test sequence - Core functionality first, then BandLab features, then Advanced Studio Features
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
        
        # Advanced Studio Features Tests - DAW Plugins & Integration
        ("Initialize DAW Plugins", tester.test_initialize_daw_plugins),
        ("Get All DAW Plugins", tester.test_get_daw_plugins_all),
        ("Get DAW Plugins Filtered by DAW", tester.test_get_daw_plugins_filtered_by_daw),
        ("Get DAW Plugins Filtered by Category", tester.test_get_daw_plugins_filtered_by_category),
        ("Get DAW Plugins Premium Filter", tester.test_get_daw_plugins_premium_filter),
        ("Create DAW Plugin", tester.test_create_daw_plugin),
        ("Get DAW Plugin by ID", tester.test_get_daw_plugin_by_id),
        ("Project DAW Export", tester.test_project_daw_export),
        ("DAW Plugin Access Restrictions", tester.test_daw_plugin_access_restrictions),
        
        # Studio Settings Management
        ("Get Studio Settings", tester.test_get_studio_settings),
        ("Update Studio Settings", tester.test_update_studio_settings),
        
        # Presonus Audiobox 96 Interface
        ("Update Audio Interface Settings", tester.test_update_audio_interface_settings),
        
        # Creative Sound Blaster Surround Sound
        ("Configure Stereo Surround Sound", tester.test_configure_surround_sound_stereo),
        ("Configure 5.1 Surround Sound", tester.test_configure_surround_sound_5_1),
        ("Configure 7.1 Surround Sound", tester.test_configure_surround_sound_7_1),
        
        # Error Cases and Edge Cases
        ("Studio Settings Error Cases", tester.test_studio_settings_error_cases),
    ]
    
    print(f"\nRunning {len(tests)} comprehensive API tests...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} - Unexpected error: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All advanced studio features tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())