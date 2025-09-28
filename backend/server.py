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
    membership_tier: str = "free"  # free, pro, premium
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    contract_signed: bool = False
    profile_image: Optional[str] = None

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
async def create_project(project_data: ProjectCreate, user_id: str = Form(...)):
    project = Project(**project_data.dict(), user_id=user_id)
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
async def create_sound_pack(pack_data: SoundPackCreate, author: str = Form(...)):
    sound_pack = SoundPack(**pack_data.dict(), author=author)
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
async def get_sound_packs(genre: Optional[str] = None):
    filter_query = {"genre": genre} if genre else {}
    packs = await db.sound_packs.find(filter_query).to_list(1000)
    return [SoundPack(**pack) for pack in packs]

@api_router.get("/soundpacks/{filename}")
async def get_sound_pack_audio(filename: str):
    file_path = sound_packs_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sound pack file not found")
    return FileResponse(file_path)

# Contract endpoints
@api_router.post("/contracts", response_model=Contract)
async def create_contract(contract_data: ContractCreate, user_id: str = Form(...)):
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
        **contract_data.dict(),
        user_id=user_id,
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