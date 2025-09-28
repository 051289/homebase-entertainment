from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import shutil
import aiofiles
from fastapi.staticfiles import StaticFiles

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="T.H.U.G N HOMEBASE ENT. Recording Studio API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Create directories for audio files
audio_dir = Path("audio_files")
audio_dir.mkdir(exist_ok=True)
sound_packs_dir = Path("sound_packs")
sound_packs_dir.mkdir(exist_ok=True)

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    is_artist: bool = False
    membership_tier: str = "free"  # free, bandlab_basic, bandlab_pro, bandlab_premium
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    contract_signed: bool = False
    profile_image: Optional[str] = None
    # BandLab membership features
    bandlab_connected: bool = False
    bandlab_username: Optional[str] = None
    collaboration_enabled: bool = False
    premium_sound_packs: bool = False
    cloud_storage_gb: int = 1  # 1GB free, more with upgrades
    max_collaborators: int = 2  # 2 free, more with upgrades
    monthly_downloads: int = 0  # Track monthly downloads
    last_download_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    is_artist: bool = False

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    user_id: str
    tracks: List[str] = []  # Track file names
    bpm: Optional[int] = 120
    key_signature: Optional[str] = "C"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_public: bool = False
    collaborators: List[str] = []  # User IDs

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    bpm: Optional[int] = 120
    key_signature: Optional[str] = "C"

class SoundPack(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    genre: str
    author: str
    files: List[str] = []  # Audio file names
    tags: List[str] = []
    is_premium: bool = False
    download_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SoundPackCreate(BaseModel):
    name: str
    description: Optional[str] = None
    genre: str
    tags: List[str] = []
    is_premium: bool = False

class Contract(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    artist_name: str
    contract_type: str = "artist_agreement"  # artist_agreement, collaboration, licensing
    terms: str
    signed_at: Optional[datetime] = None
    signature_data: Optional[str] = None  # Base64 signature image
    status: str = "pending"  # pending, signed, cancelled
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContractCreate(BaseModel):
    artist_name: str
    contract_type: str = "artist_agreement"

class ContractSign(BaseModel):
    signature_data: str  # Base64 signature image

# BandLab Membership Models
class MembershipPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tier: str  # free, bandlab_basic, bandlab_pro, bandlab_premium
    price_monthly: float
    price_yearly: float
    features: List[str]
    cloud_storage_gb: int
    max_collaborators: int
    premium_sound_packs: bool
    monthly_download_limit: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CollaborationInvite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    from_user_id: str
    to_user_id: str
    from_username: str
    to_username: str
    status: str = "pending"  # pending, accepted, rejected
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    responded_at: Optional[datetime] = None

class UserUpgrade(BaseModel):
    user_id: str
    new_tier: str

class CollaborationInviteCreate(BaseModel):
    project_id: str
    to_username: str
    
class CollaborationResponse(BaseModel):
    invite_id: str
    action: str  # accept, reject

# Authentication endpoints
@api_router.post("/auth/register", response_model=User)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user = User(**user_data.dict())
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/auth/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/auth/user/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    user_id: str = Form(...),
    bpm: Optional[int] = Form(120),
    key_signature: Optional[str] = Form("C")
):
    project = Project(
        title=title,
        description=description,
        user_id=user_id,
        bpm=bpm,
        key_signature=key_signature
    )
    await db.projects.insert_one(project.dict())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects(user_id: Optional[str] = None):
    filter_query = {"user_id": user_id} if user_id else {}
    projects = await db.projects.find(filter_query).to_list(1000)
    return [Project(**project) for project in projects]

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**project)

# Audio upload endpoints
@api_router.post("/audio/upload")
async def upload_audio(file: UploadFile = File(...), project_id: str = Form(...)):
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.aac')):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = audio_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update project with new track
    project = await db.projects.find_one({"id": project_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_tracks = project.get("tracks", []) + [unique_filename]
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {"tracks": updated_tracks, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"filename": unique_filename, "message": "Audio uploaded successfully"}

@api_router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = audio_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(file_path)

# Sound pack endpoints
@api_router.post("/soundpacks", response_model=SoundPack)
async def create_sound_pack(
    name: str = Form(...),
    author: str = Form(...),
    description: Optional[str] = Form(None),
    genre: str = Form(...),
    tags: str = Form(""),  # Comma-separated tags
    is_premium: bool = Form(False)
):
    # Parse tags from comma-separated string
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
    
    sound_pack = SoundPack(
        name=name,
        description=description,
        genre=genre,
        author=author,
        tags=tag_list,
        is_premium=is_premium
    )
    await db.sound_packs.insert_one(sound_pack.dict())
    return sound_pack

@api_router.post("/soundpacks/{pack_id}/upload")
async def upload_to_sound_pack(pack_id: str, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.aac')):
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # Check if sound pack exists
    pack = await db.sound_packs.find_one({"id": pack_id})
    if not pack:
        raise HTTPException(status_code=404, detail="Sound pack not found")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = sound_packs_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Update sound pack
    updated_files = pack.get("files", []) + [unique_filename]
    await db.sound_packs.update_one(
        {"id": pack_id},
        {"$set": {"files": updated_files}}
    )
    
    return {"filename": unique_filename, "message": "Audio added to sound pack"}

@api_router.get("/soundpacks", response_model=List[SoundPack])
async def get_sound_packs(genre: Optional[str] = None, user_id: Optional[str] = None):
    filter_query = {"genre": genre} if genre else {}
    
    # If user_id provided, filter based on membership
    if user_id:
        user = await db.users.find_one({"id": user_id})
        if user and not user.get("premium_sound_packs", False):
            # Only show non-premium packs for free users
            filter_query["is_premium"] = False
    
    packs = await db.sound_packs.find(filter_query).to_list(1000)
    return [SoundPack(**pack) for pack in packs]

# Premium sound packs endpoint - must come before {filename} route
@api_router.get("/soundpacks/premium", response_model=List[SoundPack])
async def get_premium_sound_packs(user_id: str):
    """Get premium sound packs (requires membership)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.get("premium_sound_packs", False):
        raise HTTPException(status_code=403, detail="Premium membership required for premium sound packs")
    
    packs = await db.sound_packs.find({"is_premium": True}).to_list(1000)
    return [SoundPack(**pack) for pack in packs]

@api_router.get("/soundpacks/{filename}")
async def get_sound_pack_audio(filename: str, user_id: Optional[str] = None):
    file_path = sound_packs_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sound pack file not found")
    
    # If user_id provided, track download and check limits
    if user_id:
        user = await db.users.find_one({"id": user_id})
        if user:
            # Check if month has passed, reset download count
            last_reset = datetime.fromisoformat(user.get("last_download_reset", datetime.now(timezone.utc).isoformat()))
            if (datetime.now(timezone.utc) - last_reset).days >= 30:
                await db.users.update_one(
                    {"id": user_id},
                    {
                        "$set": {
                            "monthly_downloads": 0,
                            "last_download_reset": datetime.now(timezone.utc)
                        }
                    }
                )
                user["monthly_downloads"] = 0
            
            # Check download limit
            monthly_limit = user.get("monthly_download_limit", 5)
            current_downloads = user.get("monthly_downloads", 0)
            
            if current_downloads >= monthly_limit:
                raise HTTPException(status_code=429, detail="Monthly download limit reached. Upgrade membership for more downloads.")
            
            # Increment download count
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"monthly_downloads": 1}}
            )
    
    return FileResponse(file_path)

# Contract endpoints
@api_router.post("/contracts", response_model=Contract)
async def create_contract(
    artist_name: str = Form(...),
    user_id: str = Form(...),
    contract_type: str = Form("artist_agreement")
):
    # Default T.H.U.G N HOMEBASE ENT. artist agreement terms
    default_terms = """
T.H.U.G N HOMEBASE ENT. ARTIST AGREEMENT

1. EXCLUSIVE RECORDING AGREEMENT
The Artist agrees to record exclusively for T.H.U.G N HOMEBASE ENT. during the term of this agreement.

2. REVENUE SHARING
- Streaming Revenue: 70% Artist / 30% Label
- Performance Revenue: 80% Artist / 20% Label
- Merchandise: 60% Artist / 40% Label

3. PROMOTIONAL SUPPORT
T.H.U.G N HOMEBASE ENT. will provide marketing, distribution, and promotional support for all releases.

4. CREATIVE CONTROL
Artist maintains creative control over their music with label consultation on commercial releases.

5. TERM
This agreement is valid for 2 years from the date of signing, with option to renew.

By signing below, both parties agree to the terms and conditions outlined above.
"""
    
    contract = Contract(
        artist_name=artist_name,
        user_id=user_id,
        contract_type=contract_type,
        terms=default_terms
    )
    await db.contracts.insert_one(contract.dict())
    return contract

@api_router.post("/contracts/{contract_id}/sign")
async def sign_contract(contract_id: str, signature: ContractSign):
    contract = await db.contracts.find_one({"id": contract_id})
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    await db.contracts.update_one(
        {"id": contract_id},
        {
            "$set": {
                "signature_data": signature.signature_data,
                "signed_at": datetime.now(timezone.utc),
                "status": "signed"
            }
        }
    )
    
    # Update user contract status
    await db.users.update_one(
        {"id": contract["user_id"]},
        {"$set": {"contract_signed": True}}
    )
    
    return {"message": "Contract signed successfully"}

@api_router.get("/contracts", response_model=List[Contract])
async def get_contracts(user_id: Optional[str] = None):
    filter_query = {"user_id": user_id} if user_id else {}
    contracts = await db.contracts.find(filter_query).to_list(1000)
    return [Contract(**contract) for contract in contracts]

# BandLab Membership Endpoints
@api_router.get("/membership/plans", response_model=List[MembershipPlan])
async def get_membership_plans():
    # Check if plans exist, if not create default plans
    plans = await db.membership_plans.find().to_list(1000)
    if not plans:
        default_plans = [
            MembershipPlan(
                name="Free",
                tier="free",
                price_monthly=0.0,
                price_yearly=0.0,
                features=[
                    "1GB Cloud Storage",
                    "2 Collaborators per project",
                    "Basic sound packs",
                    "5 downloads per month"
                ],
                cloud_storage_gb=1,
                max_collaborators=2,
                premium_sound_packs=False,
                monthly_download_limit=5
            ),
            MembershipPlan(
                name="BandLab Basic",
                tier="bandlab_basic",
                price_monthly=9.99,
                price_yearly=99.99,
                features=[
                    "10GB Cloud Storage",
                    "5 Collaborators per project",
                    "Premium sound packs access",
                    "50 downloads per month",
                    "BandLab integration"
                ],
                cloud_storage_gb=10,
                max_collaborators=5,
                premium_sound_packs=True,
                monthly_download_limit=50
            ),
            MembershipPlan(
                name="BandLab Pro",
                tier="bandlab_pro",
                price_monthly=19.99,
                price_yearly=199.99,
                features=[
                    "50GB Cloud Storage",
                    "15 Collaborators per project",
                    "All premium sound packs",
                    "200 downloads per month",
                    "Advanced collaboration tools",
                    "Pro Tools integration",
                    "FL Studio integration"
                ],
                cloud_storage_gb=50,
                max_collaborators=15,
                premium_sound_packs=True,
                monthly_download_limit=200
            ),
            MembershipPlan(
                name="BandLab Premium",
                tier="bandlab_premium",
                price_monthly=39.99,
                price_yearly=399.99,
                features=[
                    "200GB Cloud Storage",
                    "Unlimited Collaborators",
                    "Exclusive sound packs",
                    "Unlimited downloads",
                    "Priority support",
                    "Advanced mixing tools",
                    "Professional distribution"
                ],
                cloud_storage_gb=200,
                max_collaborators=999,
                premium_sound_packs=True,
                monthly_download_limit=999999
            )
        ]
        
        for plan in default_plans:
            await db.membership_plans.insert_one(plan.dict())
        
        plans = [plan.dict() for plan in default_plans]
    
    return [MembershipPlan(**plan) for plan in plans]

@api_router.post("/membership/upgrade")
async def upgrade_membership(upgrade: UserUpgrade):
    # Get the plan details
    plan = await db.membership_plans.find_one({"tier": upgrade.new_tier})
    if not plan:
        raise HTTPException(status_code=404, detail="Membership plan not found")
    
    # Update user membership
    await db.users.update_one(
        {"id": upgrade.user_id},
        {
            "$set": {
                "membership_tier": upgrade.new_tier,
                "cloud_storage_gb": plan["cloud_storage_gb"],
                "max_collaborators": plan["max_collaborators"],
                "premium_sound_packs": plan["premium_sound_packs"],
                "collaboration_enabled": True if upgrade.new_tier != "free" else False,
                "monthly_downloads": 0,  # Reset download count
                "last_download_reset": datetime.now(timezone.utc)
            }
        }
    )
    
    # Get updated user
    updated_user = await db.users.find_one({"id": upgrade.user_id})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"Successfully upgraded to {plan['name']}", "user": User(**updated_user)}

@api_router.post("/membership/connect-bandlab")
async def connect_bandlab_account(user_id: str = Form(...), bandlab_username: str = Form(...)):
    """Simulate connecting to BandLab account"""
    await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "bandlab_connected": True,
                "bandlab_username": bandlab_username,
                "collaboration_enabled": True
            }
        }
    )
    
    return {"message": "BandLab account connected successfully"}

# Collaboration Endpoints
@api_router.post("/collaboration/invite", response_model=CollaborationInvite)
async def invite_collaborator(
    project_id: str = Form(...),
    to_username: str = Form(...),
    from_user_id: str = Form(...)
):
    # Get the inviting user
    from_user = await db.users.find_one({"id": from_user_id})
    if not from_user:
        raise HTTPException(status_code=404, detail="Inviting user not found")
    
    # Get the invited user by username
    to_user = await db.users.find_one({"username": to_username})
    if not to_user:
        raise HTTPException(status_code=404, detail="User to invite not found")
    
    # Check if project exists and belongs to the inviting user
    project = await db.projects.find_one({"id": project_id, "user_id": from_user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    
    # Check collaboration limits
    current_collaborators = len(project.get("collaborators", []))
    if current_collaborators >= from_user.get("max_collaborators", 2):
        raise HTTPException(status_code=400, detail="Collaboration limit reached for your membership tier")
    
    collaboration_invite = CollaborationInvite(
        project_id=invite.project_id,
        from_user_id=from_user_id,
        to_user_id=to_user["id"],
        from_username=from_user["username"],
        to_username=invite.to_username
    )
    
    await db.collaboration_invites.insert_one(collaboration_invite.dict())
    return collaboration_invite

@api_router.get("/collaboration/invites/{user_id}", response_model=List[CollaborationInvite])
async def get_collaboration_invites(user_id: str):
    """Get pending collaboration invites for a user"""
    invites = await db.collaboration_invites.find({
        "to_user_id": user_id,
        "status": "pending"
    }).to_list(1000)
    return [CollaborationInvite(**invite) for invite in invites]

@api_router.post("/collaboration/respond")
async def respond_to_collaboration(response: CollaborationResponse):
    # Get the invite
    invite = await db.collaboration_invites.find_one({"id": response.invite_id})
    if not invite:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Update invite status
    await db.collaboration_invites.update_one(
        {"id": response.invite_id},
        {
            "$set": {
                "status": "accepted" if response.action == "accept" else "rejected",
                "responded_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # If accepted, add user to project collaborators
    if response.action == "accept":
        await db.projects.update_one(
            {"id": invite["project_id"]},
            {"$addToSet": {"collaborators": invite["to_user_id"]}}
        )
    
    return {"message": f"Invitation {response.action}ed successfully"}

@api_router.post("/admin/init-premium-packs")
async def initialize_premium_sound_packs():
    """Initialize premium sound packs for demo purposes"""
    premium_packs = [
        SoundPack(
            name="BandLab Exclusive Trap Beats",
            description="Premium trap beats exclusively for BandLab members",
            genre="Trap",
            author="BandLab Studios",
            tags=["trap", "exclusive", "professional", "bandlab"],
            is_premium=True
        ),
        SoundPack(
            name="Pro Studio Vocals",
            description="Professional vocal samples recorded in premium studios",
            genre="Pop",
            author="T.H.U.G N HOMEBASE ENT.",
            tags=["vocals", "professional", "studio", "premium"],
            is_premium=True
        ),
        SoundPack(
            name="Orchestral Elements Premium",
            description="High-quality orchestral samples for premium members",
            genre="Classical",
            author="Symphony Studios",
            tags=["orchestral", "strings", "premium", "cinematic"],
            is_premium=True
        ),
        SoundPack(
            name="Future Bass Collection",
            description="Modern future bass sounds and synths",
            genre="Electronic",
            author="Electronic Dreams",
            tags=["future bass", "synths", "modern", "premium"],
            is_premium=True
        )
    ]
    
    for pack in premium_packs:
        await db.sound_packs.insert_one(pack.dict())
    
    return {"message": f"Initialized {len(premium_packs)} premium sound packs"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()