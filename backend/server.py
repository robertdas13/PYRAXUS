from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks


# Contact Form Models
class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=1000)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('message')
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class Contact(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    message: str
    status: str = Field(default="new")
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Contact Form Endpoints
@api_router.post("/contact")
async def submit_contact(contact_data: ContactCreate):
    try:
        # Create contact object
        contact = Contact(**contact_data.model_dump())
        
        # Convert to dict for MongoDB
        doc = contact.model_dump()
        doc['createdAt'] = doc['createdAt'].isoformat()
        
        # Insert into database
        result = await db.contacts.insert_one(doc)
        
        # Mock Email Notification (logged to backend)
        logger.info("=" * 80)
        logger.info("📧 NEW CONTACT FORM SUBMISSION - EMAIL NOTIFICATION")
        logger.info("=" * 80)
        logger.info(f"To: pyraxus13@gmail.com")
        logger.info(f"Subject: New Contact Form Message from {contact.name}")
        logger.info(f"")
        logger.info(f"You have received a new message through your PYRAXUS portfolio:")
        logger.info(f"")
        logger.info(f"Name: {contact.name}")
        logger.info(f"Email: {contact.email}")
        logger.info(f"Message:")
        logger.info(f"{contact.message}")
        logger.info(f"")
        logger.info(f"Submitted at: {contact.createdAt.isoformat()}")
        logger.info(f"Contact ID: {contact.id}")
        logger.info("=" * 80)
        
        logger.info(f"Contact form submitted: {contact.name} ({contact.email})")
        
        return {
            "success": True,
            "message": "Message sent successfully! I'll get back to you soon.",
            "data": {
                "id": contact.id,
                "createdAt": contact.createdAt.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message. Please try again later.")


@api_router.get("/contacts")
async def get_contacts():
    try:
        # Exclude MongoDB's _id field
        contacts = await db.contacts.find({}, {"_id": 0}).to_list(1000)
        
        # Convert ISO string timestamps back to datetime objects
        for contact in contacts:
            if isinstance(contact.get('createdAt'), str):
                contact['createdAt'] = datetime.fromisoformat(contact['createdAt'])
        
        # Sort by creation date (newest first)
        contacts.sort(key=lambda x: x.get('createdAt', datetime.min), reverse=True)
        
        return {
            "success": True,
            "data": contacts
        }
    except Exception as e:
        logger.error(f"Error fetching contacts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch contacts")


# Admin Authentication
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'default_password')

def verify_admin_password(password: str = Header(..., alias="X-Admin-Password")):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return True


# Admin Login Endpoint
@api_router.post("/admin/login")
async def admin_login(password: str = Header(..., alias="X-Admin-Password")):
    if password == ADMIN_PASSWORD:
        return {
            "success": True,
            "message": "Admin authenticated successfully"
        }
    raise HTTPException(status_code=401, detail="Invalid admin password")


# Admin: Update Contact Status
class ContactStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(new|read|replied)$")


@api_router.patch("/admin/contacts/{contact_id}/status")
async def update_contact_status(
    contact_id: str,
    status_update: ContactStatusUpdate,
    _: bool = Depends(verify_admin_password)
):
    try:
        result = await db.contacts.update_one(
            {"id": contact_id},
            {"$set": {"status": status_update.status}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Admin updated contact {contact_id} status to {status_update.status}")
        
        return {
            "success": True,
            "message": f"Contact status updated to {status_update.status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update contact status")


# Admin: Delete Contact
@api_router.delete("/admin/contacts/{contact_id}")
async def delete_contact(
    contact_id: str,
    _: bool = Depends(verify_admin_password)
):
    try:
        result = await db.contacts.delete_one({"id": contact_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Admin deleted contact {contact_id}")
        
        return {
            "success": True,
            "message": "Contact deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete contact")


# Admin: Get Contacts with Filters
@api_router.get("/admin/contacts")
async def get_admin_contacts(
    status: Optional[str] = None,
    _: bool = Depends(verify_admin_password)
):
    try:
        # Build query filter
        query = {}
        if status:
            query["status"] = status
        
        # Fetch contacts
        contacts = await db.contacts.find(query, {"_id": 0}).to_list(1000)
        
        # Convert ISO string timestamps back to datetime objects
        for contact in contacts:
            if isinstance(contact.get('createdAt'), str):
                contact['createdAt'] = datetime.fromisoformat(contact['createdAt'])
        
        # Sort by creation date (newest first)
        contacts.sort(key=lambda x: x.get('createdAt', datetime.min), reverse=True)
        
        return {
            "success": True,
            "data": contacts,
            "total": len(contacts)
        }
    except Exception as e:
        logger.error(f"Error fetching admin contacts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch contacts")

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