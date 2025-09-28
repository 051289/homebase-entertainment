import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import shadcn components
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Landing Page Component
const LandingPage = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="absolute top-0 w-full z-50 p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="text-2xl font-bold text-white">
            T.H.U.G N HOMEBASE ENT.
          </div>
          <Button 
            onClick={onGetStarted}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-2"
            data-testid="nav-get-started-btn"
          >
            Get Started
          </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1598488035139-bdbb2231ce04" 
            alt="Professional Recording Studio" 
            className="w-full h-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent"></div>
        </div>
        
        <div className="relative z-10 text-center max-w-4xl mx-auto px-6">
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Mega Recording
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent"> Studio</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            Professional recording studio with sound packs, collaboration tools, and exclusive artist contracts for T.H.U.G N HOMEBASE ENT.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              onClick={onGetStarted}
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 text-lg font-semibold transform hover:scale-105 transition-all duration-200"
              data-testid="hero-get-started-btn"
            >
              Start Recording Now
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              className="border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white px-8 py-4 text-lg font-semibold"
              data-testid="hero-learn-more-btn"
            >
              Learn More
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-6">Studio Features</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need to create, collaborate, and distribute your music professionally
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-all duration-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">🎵</span>
                </div>
                <CardTitle className="text-white text-xl">Multi-Track Recording</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Professional multi-track recording with real-time collaboration and mixing capabilities.</p>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-all duration-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">📦</span>
                </div>
                <CardTitle className="text-white text-xl">Sound Pack Library</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Access thousands of professional sound packs and samples from top producers worldwide.</p>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-all duration-200">
              <CardHeader>
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-500 rounded-lg flex items-center justify-center mb-4">
                  <span className="text-2xl">📝</span>
                </div>
                <CardTitle className="text-white text-xl">Artist Contracts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300">Digital contract signing system for exclusive partnerships with T.H.U.G N HOMEBASE ENT.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

// Auth Component
const AuthModal = ({ isOpen, onClose, onUserCreated }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    is_artist: false
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/auth/register`, formData);
      toast.success('Account created successfully!');
      onUserCreated(response.data);
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center">Join T.H.U.G N HOMEBASE ENT.</DialogTitle>
          <DialogDescription className="text-gray-300 text-center">
            Create your account to start recording and collaborating
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4 mt-6">
          <div>
            <Label htmlFor="username" className="text-white">Username</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({...formData, username: e.target.value})}
              className="bg-slate-700 border-slate-600 text-white"
              required
              data-testid="auth-username-input"
            />
          </div>
          
          <div>
            <Label htmlFor="email" className="text-white">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="bg-slate-700 border-slate-600 text-white"
              required
              data-testid="auth-email-input"
            />
          </div>
          
          <div>
            <Label htmlFor="full_name" className="text-white">Full Name</Label>
            <Input
              id="full_name"
              value={formData.full_name}
              onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              className="bg-slate-700 border-slate-600 text-white"
              required
              data-testid="auth-fullname-input"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_artist"
              checked={formData.is_artist}
              onChange={(e) => setFormData({...formData, is_artist: e.target.checked})}
              className="rounded"
              data-testid="auth-artist-checkbox"
            />
            <Label htmlFor="is_artist" className="text-white">I'm an artist looking for a record deal</Label>
          </div>
          
          <Button 
            type="submit" 
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
            data-testid="auth-register-btn"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Studio Dashboard Component
const StudioDashboard = ({ user, onUserUpdate }) => {
  const [projects, setProjects] = useState([]);
  const [soundPacks, setSoundPacks] = useState([]);
  const [activeTab, setActiveTab] = useState('studio');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      // Initialize premium packs if needed
      try {
        await axios.post(`${API}/admin/init-premium-packs`);
      } catch (error) {
        // Ignore if already initialized
      }
      
      const [projectsRes, soundPacksRes] = await Promise.all([
        axios.get(`${API}/projects?user_id=${user.id}`),
        axios.get(`${API}/soundpacks?user_id=${user.id}`)
      ]);
      setProjects(projectsRes.data);
      setSoundPacks(soundPacksRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    try {
      const formData = new FormData();
      formData.append('title', `New Project ${projects.length + 1}`);
      formData.append('description', 'A new recording project');
      formData.append('user_id', user.id);
      
      const response = await axios.post(`${API}/projects`, formData);
      setProjects([...projects, response.data]);
      toast.success('New project created!');
    } catch (error) {
      toast.error('Failed to create project');
    }
  };

  const downloadSoundPack = async (pack) => {
    try {
      // For now, just simulate a download and track it
      // In a real app, this would download the actual files
      
      if (pack.files.length === 0) {
        toast.error('This sound pack has no files available');
        return;
      }

      // Track the download by making a request to one of the files
      // This will increment the download counter
      await axios.get(`${API}/soundpacks/${pack.files[0] || 'dummy.wav'}?user_id=${user.id}`);
      
      toast.success(`Downloaded sound pack: ${pack.name}`);
      
      // Update user's download count locally
      if (onUserUpdate) {
        const updatedUser = { 
          ...user, 
          monthly_downloads: (user.monthly_downloads || 0) + 1 
        };
        onUserUpdate(updatedUser);
      }
      
    } catch (error) {
      if (error.response?.status === 429) {
        toast.error('Monthly download limit reached. Upgrade your membership for more downloads.');
      } else {
        toast.error('Failed to download sound pack');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading studio...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white" data-testid="studio-dashboard">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700 p-6">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">T.H.U.G N HOMEBASE ENT. Studio</h1>
            <p className="text-gray-300 mt-1">Welcome back, {user.full_name}!</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant={user.contract_signed ? "default" : "destructive"} data-testid="contract-status-badge">
              {user.contract_signed ? 'Contract Signed' : 'No Contract'}
            </Badge>
            <Badge variant="outline" className="text-purple-400 border-purple-400" data-testid="membership-badge">
              {user.membership_tier.toUpperCase()}
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-slate-800 border border-slate-700 overflow-x-auto">
            <TabsTrigger value="studio" className="data-[state=active]:bg-purple-600" data-testid="studio-tab">Recording Studio</TabsTrigger>
            <TabsTrigger value="packs" className="data-[state=active]:bg-purple-600" data-testid="soundpacks-tab">Sound Packs</TabsTrigger>
            <TabsTrigger value="daw" className="data-[state=active]:bg-purple-600" data-testid="daw-tab">DAW Plugins</TabsTrigger>
            <TabsTrigger value="studio-settings" className="data-[state=active]:bg-purple-600" data-testid="studio-settings-tab">Studio Settings</TabsTrigger>
            <TabsTrigger value="membership" className="data-[state=active]:bg-purple-600" data-testid="membership-tab">BandLab Membership</TabsTrigger>
            <TabsTrigger value="collaboration" className="data-[state=active]:bg-purple-600" data-testid="collaboration-tab">Collaboration</TabsTrigger>
            <TabsTrigger value="contracts" className="data-[state=active]:bg-purple-600" data-testid="contracts-tab">Contracts</TabsTrigger>
            <TabsTrigger value="profile" className="data-[state=active]:bg-purple-600" data-testid="profile-tab">Profile</TabsTrigger>
          </TabsList>

          {/* Recording Studio Tab */}
          <TabsContent value="studio" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Your Projects</h2>
              <Button 
                onClick={createProject}
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                data-testid="create-project-btn"
              >
                Create New Project
              </Button>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <Card key={project.id} className="bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors" data-testid={`project-card-${project.id}`}>
                  <CardHeader>
                    <CardTitle className="text-white">{project.title}</CardTitle>
                    <CardDescription className="text-gray-300">{project.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-gray-400">
                        <span>Tracks: {project.tracks.length}</span>
                        <span>BPM: {project.bpm}</span>
                      </div>
                      <div className="flex justify-between text-sm text-gray-400">
                        <span>Key: {project.key_signature}</span>
                        <span>{project.is_public ? 'Public' : 'Private'}</span>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="w-full mt-4 border-purple-400 text-purple-400 hover:bg-purple-400 hover:text-white"
                        data-testid={`open-project-${project.id}`}
                      >
                        Open Project
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {projects.length === 0 && (
                <div className="col-span-full text-center py-12" data-testid="no-projects-message">
                  <div className="text-gray-400 text-lg mb-4">No projects yet</div>
                  <p className="text-gray-500">Create your first recording project to get started</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Sound Packs Tab */}
          <TabsContent value="packs" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Available Sound Packs</h2>
              <div className="text-sm text-gray-400">
                Downloads: {user.monthly_downloads || 0}/{user.monthly_download_limit || 5} this month
              </div>
            </div>
            
            {/* Download limit warning */}
            {(user.monthly_downloads || 0) >= (user.monthly_download_limit || 5) && (
              <Card className="bg-slate-800 border-yellow-500">
                <CardHeader>
                  <CardTitle className="text-yellow-400">Download Limit Reached</CardTitle>
                  <CardDescription className="text-gray-300">
                    You've reached your monthly download limit. Upgrade your membership for more downloads.
                  </CardDescription>
                </CardHeader>
              </Card>
            )}
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {soundPacks.map((pack) => (
                <Card key={pack.id} className="bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors" data-testid={`soundpack-card-${pack.id}`}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-white">{pack.name}</CardTitle>
                        <CardDescription className="text-gray-300">{pack.description}</CardDescription>
                      </div>
                      <div className="flex flex-col gap-1">
                        {pack.is_premium && (
                          <Badge className="bg-gradient-to-r from-yellow-400 to-orange-400" data-testid={`premium-badge-${pack.id}`}>
                            PREMIUM
                          </Badge>
                        )}
                        {!pack.is_premium && (
                          <Badge variant="outline" className="text-green-400 border-green-400">
                            FREE
                          </Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-gray-400">
                        <span>Genre: {pack.genre}</span>
                        <span>Files: {pack.files.length}</span>
                      </div>
                      <div className="text-sm text-gray-400">By: {pack.author}</div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {pack.tags.map((tag, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      
                      {/* Download restrictions */}
                      {pack.is_premium && !user.premium_sound_packs ? (
                        <Button 
                          disabled
                          variant="outline" 
                          size="sm" 
                          className="w-full mt-4 opacity-50 cursor-not-allowed"
                          data-testid={`download-pack-${pack.id}`}
                        >
                          Premium Required
                        </Button>
                      ) : (user.monthly_downloads || 0) >= (user.monthly_download_limit || 5) ? (
                        <Button 
                          disabled
                          variant="outline" 
                          size="sm" 
                          className="w-full mt-4 opacity-50 cursor-not-allowed"
                          data-testid={`download-pack-${pack.id}`}
                        >
                          Download Limit Reached
                        </Button>
                      ) : (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="w-full mt-4 border-blue-400 text-blue-400 hover:bg-blue-400 hover:text-white"
                          onClick={() => downloadSoundPack(pack)}
                          data-testid={`download-pack-${pack.id}`}
                        >
                          Download Pack
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
              
              {soundPacks.length === 0 && (
                <div className="col-span-full text-center py-12" data-testid="no-soundpacks-message">
                  <div className="text-gray-400 text-lg mb-4">No sound packs available</div>
                  <p className="text-gray-500">Check back later for new sound packs</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* DAW Plugins Tab */}
          <TabsContent value="daw" className="space-y-6">
            <DAWPluginsSection user={user} />
          </TabsContent>

          {/* Studio Settings Tab */}
          <TabsContent value="studio-settings" className="space-y-6">
            <StudioSettingsSection user={user} />
          </TabsContent>

          {/* BandLab Membership Tab */}
          <TabsContent value="membership" className="space-y-6">
            <MembershipSection user={user} onUserUpdate={onUserUpdate} />
          </TabsContent>

          {/* Collaboration Tab */}
          <TabsContent value="collaboration" className="space-y-6">
            <CollaborationSection user={user} />
          </TabsContent>

          {/* Contracts Tab */}
          <TabsContent value="contracts" className="space-y-6">
            <ContractSection user={user} onUserUpdate={onUserUpdate} />
          </TabsContent>

          {/* Profile Tab */}
          <TabsContent value="profile" className="space-y-6">
            <ProfileSection user={user} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

// BandLab Membership Section Component
const MembershipSection = ({ user, onUserUpdate }) => {
  const [membershipPlans, setMembershipPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [bandlabConnecting, setBandlabConnecting] = useState(false);
  const [bandlabUsername, setBandlabUsername] = useState('');

  useEffect(() => {
    fetchMembershipPlans();
  }, []);

  const fetchMembershipPlans = async () => {
    try {
      const response = await axios.get(`${API}/membership/plans`);
      setMembershipPlans(response.data);
    } catch (error) {
      toast.error('Failed to load membership plans');
    } finally {
      setLoading(false);
    }
  };

  const upgradeMembership = async (tier) => {
    setUpgrading(true);
    try {
      const response = await axios.post(`${API}/membership/upgrade`, {
        user_id: user.id,
        new_tier: tier
      });
      toast.success(response.data.message);
      if (onUserUpdate) {
        onUserUpdate(response.data.user);
      }
    } catch (error) {
      toast.error('Failed to upgrade membership');
    } finally {
      setUpgrading(false);
    }
  };

  const connectBandLab = async () => {
    if (!bandlabUsername.trim()) {
      toast.error('Please enter your BandLab username');
      return;
    }
    
    setBandlabConnecting(true);
    try {
      const formData = new FormData();
      formData.append('user_id', user.id);
      formData.append('bandlab_username', bandlabUsername);
      
      await axios.post(`${API}/membership/connect-bandlab`, formData);
      toast.success('BandLab account connected successfully!');
      
      // Update user state
      if (onUserUpdate) {
        const updatedUser = { 
          ...user, 
          bandlab_connected: true, 
          bandlab_username: bandlabUsername,
          collaboration_enabled: true
        };
        onUserUpdate(updatedUser);
      }
    } catch (error) {
      toast.error('Failed to connect BandLab account');
    } finally {
      setBandlabConnecting(false);
    }
  };

  const getMembershipBadgeColor = (tier) => {
    switch (tier) {
      case 'free': return 'bg-gray-500';
      case 'bandlab_basic': return 'bg-blue-500';
      case 'bandlab_pro': return 'bg-purple-500';
      case 'bandlab_premium': return 'bg-gradient-to-r from-yellow-400 to-orange-400';
      default: return 'bg-gray-500';
    }
  };

  if (loading) return <div className="text-center">Loading membership plans...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">BandLab Membership</h2>
        <div className="flex items-center gap-4">
          {user.bandlab_connected ? (
            <Badge className="bg-green-500" data-testid="bandlab-connected-badge">
              Connected: @{user.bandlab_username}
            </Badge>
          ) : (
            <Badge variant="outline" className="text-orange-400 border-orange-400">
              Not Connected
            </Badge>
          )}
        </div>
      </div>

      {/* BandLab Connection */}
      {!user.bandlab_connected && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              🎵 Connect Your BandLab Account
            </CardTitle>
            <CardDescription className="text-gray-300">
              Connect your BandLab account to unlock collaboration features and sync your projects
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <Label htmlFor="bandlab-username" className="text-white">BandLab Username</Label>
                <Input
                  id="bandlab-username"
                  value={bandlabUsername}
                  onChange={(e) => setBandlabUsername(e.target.value)}
                  placeholder="Enter your BandLab username"
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="bandlab-username-input"
                />
              </div>
              <Button 
                onClick={connectBandLab}
                disabled={bandlabConnecting}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                data-testid="connect-bandlab-btn"
              >
                {bandlabConnecting ? 'Connecting...' : 'Connect BandLab'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Membership Status */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Current Membership</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center mb-4">
            <div>
              <div className="flex items-center gap-2">
                <Badge className={getMembershipBadgeColor(user.membership_tier)} data-testid="current-membership-badge">
                  {membershipPlans.find(p => p.tier === user.membership_tier)?.name || user.membership_tier.toUpperCase()}
                </Badge>
              </div>
              <div className="text-sm text-gray-400 mt-2">
                Cloud Storage: {user.cloud_storage_gb || 1}GB • 
                Max Collaborators: {user.max_collaborators || 2} • 
                Monthly Downloads: {user.monthly_downloads || 0}/{user.monthly_download_limit || 5}
              </div>
            </div>
          </div>
          
          {/* Feature list for current plan */}
          <div className="space-y-2">
            {membershipPlans.find(p => p.tier === user.membership_tier)?.features.map((feature, index) => (
              <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
                <span className="text-green-400">✓</span>
                {feature}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Membership Plans */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {membershipPlans.map((plan) => (
          <Card 
            key={plan.id} 
            className={`bg-slate-800 border-slate-700 hover:bg-slate-750 transition-colors ${
              user.membership_tier === plan.tier ? 'ring-2 ring-purple-500' : ''
            }`}
            data-testid={`membership-plan-${plan.tier}`}
          >
            <CardHeader>
              <div className="text-center">
                <Badge className={getMembershipBadgeColor(plan.tier)} data-testid={`plan-badge-${plan.tier}`}>
                  {plan.name}
                </Badge>
                <div className="mt-4">
                  <div className="text-3xl font-bold text-white">
                    ${plan.price_monthly}
                    <span className="text-lg text-gray-400">/mo</span>
                  </div>
                  {plan.price_yearly > 0 && (
                    <div className="text-sm text-gray-400">
                      ${plan.price_yearly}/year (save 17%)
                    </div>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 mb-4">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
                    <span className="text-green-400">✓</span>
                    {feature}
                  </div>
                ))}
              </div>
              
              <Button 
                onClick={() => upgradeMembership(plan.tier)}
                disabled={upgrading || user.membership_tier === plan.tier}
                className={`w-full ${
                  user.membership_tier === plan.tier 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                }`}
                data-testid={`upgrade-to-${plan.tier}`}
              >
                {user.membership_tier === plan.tier 
                  ? 'Current Plan' 
                  : upgrading 
                    ? 'Upgrading...' 
                    : plan.price_monthly === 0 
                      ? 'Downgrade' 
                      : 'Upgrade'
                }
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

// Collaboration Section Component
const CollaborationSection = ({ user }) => {
  const [collaborationInvites, setCollaborationInvites] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [inviteUsername, setInviteUsername] = useState('');
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [invitesRes, projectsRes] = await Promise.all([
        axios.get(`${API}/collaboration/invites/${user.id}`),
        axios.get(`${API}/projects?user_id=${user.id}`)
      ]);
      setCollaborationInvites(invitesRes.data);
      setProjects(projectsRes.data);
    } catch (error) {
      toast.error('Failed to load collaboration data');
    } finally {
      setLoading(false);
    }
  };

  const sendInvite = async () => {
    if (!inviteUsername.trim() || !selectedProjectId) {
      toast.error('Please select a project and enter a username');
      return;
    }

    setInviting(true);
    try {
      const formData = new FormData();
      formData.append('project_id', selectedProjectId);
      formData.append('to_username', inviteUsername);
      formData.append('from_user_id', user.id);

      await axios.post(`${API}/collaboration/invite`, formData);
      toast.success('Collaboration invite sent!');
      setInviteUsername('');
      setSelectedProjectId('');
      await fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send invite');
    } finally {
      setInviting(false);
    }
  };

  const respondToInvite = async (inviteId, action) => {
    try {
      await axios.post(`${API}/collaboration/respond`, {
        invite_id: inviteId,
        action: action
      });
      toast.success(`Invitation ${action}ed successfully!`);
      await fetchData();
    } catch (error) {
      toast.error('Failed to respond to invitation');
    }
  };

  if (loading) return <div className="text-center">Loading collaboration data...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Collaboration</h2>
        <div className="flex items-center gap-2">
          {user.collaboration_enabled ? (
            <Badge className="bg-green-500" data-testid="collaboration-enabled-badge">
              Collaboration Enabled
            </Badge>
          ) : (
            <Badge variant="destructive">
              Collaboration Disabled
            </Badge>
          )}
        </div>
      </div>

      {!user.collaboration_enabled && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">🚀 Enable Collaboration</CardTitle>
            <CardDescription className="text-gray-300">
              Connect your BandLab account or upgrade your membership to collaborate with other artists
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-400">
              To enable collaboration features, please connect your BandLab account in the membership section or upgrade to a paid plan.
            </p>
          </CardContent>
        </Card>
      )}

      {user.collaboration_enabled && (
        <>
          {/* Send Invite */}
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Invite Collaborators</CardTitle>
              <CardDescription className="text-gray-300">
                Invite other artists to collaborate on your projects
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="project-select" className="text-white">Select Project</Label>
                  <select
                    id="project-select"
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full p-2 bg-slate-700 border border-slate-600 text-white rounded"
                    data-testid="project-select"
                  >
                    <option value="">Choose a project...</option>
                    {projects.map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.title}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="invite-username" className="text-white">Username to Invite</Label>
                  <Input
                    id="invite-username"
                    value={inviteUsername}
                    onChange={(e) => setInviteUsername(e.target.value)}
                    placeholder="Enter username"
                    className="bg-slate-700 border-slate-600 text-white"
                    data-testid="invite-username-input"
                  />
                </div>
                <div className="flex items-end">
                  <Button 
                    onClick={sendInvite}
                    disabled={inviting}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    data-testid="send-invite-btn"
                  >
                    {inviting ? 'Sending...' : 'Send Invite'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pending Invites */}
          {collaborationInvites.length > 0 && (
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Pending Invitations</CardTitle>
                <CardDescription className="text-gray-300">
                  You have {collaborationInvites.length} pending collaboration invitations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {collaborationInvites.map((invite) => (
                    <div key={invite.id} className="flex justify-between items-center p-4 bg-slate-700 rounded-lg" data-testid={`invite-${invite.id}`}>
                      <div>
                        <div className="text-white font-medium">
                          Collaboration invite from @{invite.from_username}
                        </div>
                        <div className="text-gray-400 text-sm">
                          Project ID: {invite.project_id}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm"
                          onClick={() => respondToInvite(invite.id, 'accept')}
                          className="bg-green-600 hover:bg-green-700"
                          data-testid={`accept-invite-${invite.id}`}
                        >
                          Accept
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => respondToInvite(invite.id, 'reject')}
                          data-testid={`reject-invite-${invite.id}`}
                        >
                          Reject
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

// Contract Section Component
const ContractSection = ({ user, onUserUpdate }) => {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateContract, setShowCreateContract] = useState(false);

  useEffect(() => {
    fetchContracts();
  }, [user]);

  const fetchContracts = async () => {
    try {
      const response = await axios.get(`${API}/contracts?user_id=${user.id}`);
      setContracts(response.data);
    } catch (error) {
      toast.error('Failed to load contracts');
    } finally {
      setLoading(false);
    }
  };

  const createContract = async () => {
    try {
      const formData = new FormData();
      formData.append('artist_name', user.full_name);
      formData.append('contract_type', 'artist_agreement');
      formData.append('user_id', user.id);
      
      const response = await axios.post(`${API}/contracts`, formData);
      setContracts([...contracts, response.data]);
      setShowCreateContract(false);
      toast.success('Contract created! Please review and sign.');
    } catch (error) {
      toast.error('Failed to create contract');
    }
  };

  const signContract = async (contractId) => {
    try {
      // Create a simple signature data (in a real app, this would be from a signature pad)
      const signatureData = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";
      
      await axios.post(`${API}/contracts/${contractId}/sign`, {
        signature_data: signatureData
      });
      
      // Refresh contracts to get updated status
      await fetchContracts();
      
      // Update user state to reflect contract signed status
      if (onUserUpdate) {
        const updatedUser = { ...user, contract_signed: true };
        onUserUpdate(updatedUser);
      }
      
      toast.success('Contract signed successfully!');
    } catch (error) {
      toast.error('Failed to sign contract');
    }
  };

  if (loading) return <div className="text-center">Loading contracts...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Artist Contracts</h2>
        {user.is_artist && !user.contract_signed && (
          <Button 
            onClick={() => setShowCreateContract(true)}
            className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            data-testid="create-contract-btn"
          >
            Request Artist Contract
          </Button>
        )}
      </div>

      {showCreateContract && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Request Artist Agreement</CardTitle>
            <CardDescription className="text-gray-300">
              Submit a request for an exclusive artist agreement with T.H.U.G N HOMEBASE ENT.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Button onClick={createContract} data-testid="confirm-create-contract-btn">
                Create Contract Request
              </Button>
              <Button variant="outline" onClick={() => setShowCreateContract(false)} data-testid="cancel-create-contract-btn">
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-4">
        {contracts.map((contract) => (
          <Card key={contract.id} className="bg-slate-800 border-slate-700" data-testid={`contract-card-${contract.id}`}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-white">{contract.contract_type.replace('_', ' ').toUpperCase()}</CardTitle>
                  <CardDescription className="text-gray-300">Artist: {contract.artist_name}</CardDescription>
                </div>
                <Badge 
                  variant={contract.status === 'signed' ? 'default' : contract.status === 'pending' ? 'secondary' : 'destructive'}
                  data-testid={`contract-status-${contract.id}`}
                >
                  {contract.status.toUpperCase()}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-slate-700 p-4 rounded-lg max-h-64 overflow-y-auto">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap">{contract.terms}</pre>
                </div>
                
                {contract.status === 'pending' && (
                  <div className="flex gap-4">
                    <Button 
                      onClick={() => signContract(contract.id)}
                      className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                      data-testid={`sign-contract-${contract.id}`}
                    >
                      Sign Contract
                    </Button>
                    <Button variant="outline" data-testid={`review-contract-${contract.id}`}>
                      Download for Review
                    </Button>
                  </div>
                )}
                
                {contract.signed_at && (
                  <div className="text-sm text-gray-400" data-testid={`signed-date-${contract.id}`}>
                    Signed on: {new Date(contract.signed_at).toLocaleDateString()}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
        
        {contracts.length === 0 && (
          <div className="text-center py-12" data-testid="no-contracts-message">
            <div className="text-gray-400 text-lg mb-4">No contracts yet</div>
            {user.is_artist ? (
              <p className="text-gray-500">Request an artist agreement to get started with T.H.U.G N HOMEBASE ENT.</p>
            ) : (
              <p className="text-gray-500">Mark yourself as an artist in your profile to request contracts</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Profile Section Component
const ProfileSection = ({ user }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Profile</h2>
      
      <div className="grid md:grid-cols-2 gap-6">
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-300">Username</Label>
              <div className="text-white font-medium" data-testid="profile-username">{user.username}</div>
            </div>
            <div>
              <Label className="text-gray-300">Email</Label>
              <div className="text-white font-medium" data-testid="profile-email">{user.email}</div>
            </div>
            <div>
              <Label className="text-gray-300">Full Name</Label>
              <div className="text-white font-medium" data-testid="profile-fullname">{user.full_name}</div>
            </div>
            <div>
              <Label className="text-gray-300">Account Type</Label>
              <div className="text-white font-medium" data-testid="profile-account-type">
                {user.is_artist ? 'Artist Account' : 'Standard Account'}
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Membership & Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-300">Membership Tier</Label>
              <Badge className="ml-2" data-testid="profile-membership-tier">
                {user.membership_tier.toUpperCase()}
              </Badge>
            </div>
            <div>
              <Label className="text-gray-300">Contract Status</Label>
              <Badge 
                variant={user.contract_signed ? "default" : "destructive"} 
                className="ml-2"
                data-testid="profile-contract-status"
              >
                {user.contract_signed ? 'Signed' : 'No Contract'}
              </Badge>
            </div>
            <div>
              <Label className="text-gray-300">Member Since</Label>
              <div className="text-white font-medium" data-testid="profile-member-since">
                {new Date(user.created_at).toLocaleDateString()}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);

  const handleGetStarted = () => {
    setShowAuth(true);
  };

  const handleUserCreated = (userData) => {
    setUser(userData);
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={
              user ? (
                <Navigate to="/studio" replace />
              ) : (
                <LandingPage onGetStarted={handleGetStarted} />
              )
            } 
          />
          <Route 
            path="/studio" 
            element={
              user ? (
                <StudioDashboard user={user} onUserUpdate={setUser} />
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
        </Routes>
      </BrowserRouter>
      
      <AuthModal 
        isOpen={showAuth} 
        onClose={() => setShowAuth(false)} 
        onUserCreated={handleUserCreated} 
      />
      
      <Toaster position="top-right" />
    </div>
  );
}

export default App;