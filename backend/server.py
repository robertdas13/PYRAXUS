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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


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
    phone: str = Field(..., min_length=10, max_length=15)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=1000)

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('phone')
    @classmethod
    def phone_must_be_valid(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Phone number cannot be empty')
        # Remove spaces and check if it's a valid number
        phone_clean = v.strip().replace(' ', '').replace('-', '')
        if not phone_clean.replace('+', '').isdigit():
            raise ValueError('Phone number must contain only digits')
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
    phone: str
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
        
        # Send real email notification via Gmail
        email_sent = send_email_notification(contact)
        
        if email_sent:
            logger.info(f"📧 Email notification sent to {GMAIL_USER}")
        else:
            logger.warning(f"⚠️ Email notification failed, but contact saved to database")
        
        logger.info(f"Contact form submitted: {contact.name} ({contact.email})")
        
        return {
            "success": True,
            "message": "Message sent successfully! I'll get back to you soon.",
            "data": {
                "id": contact.id,
                "createdAt": contact.createdAt.isoformat(),
                "email_sent": email_sent
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

# Gmail Configuration
GMAIL_USER = os.environ.get('GMAIL_USER', '')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', '')


def send_email_notification(contact: Contact):
    """Send email notification via Gmail SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Contact Form Message from {contact.name}"
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER
        
        # Create HTML email body
        html_body = f"""
        <html>
          <head>
            <style>
              body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
              .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
              .header {{ background: linear-gradient(135deg, #ff003c 0%, #ff4d6d 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
              .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; border-radius: 0 0 8px 8px; }}
              .field {{ margin-bottom: 20px; }}
              .label {{ font-weight: bold; color: #ff003c; margin-bottom: 5px; }}
              .value {{ background: white; padding: 10px; border-left: 3px solid #ff003c; margin-top: 5px; }}
              .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
          </head>
          <body>
            <div class="container">
              <div class="header">
                <h1>🎯 PYRAXUS Portfolio</h1>
                <p>New Contact Form Submission</p>
              </div>
              <div class="content">
                <div class="field">
                  <div class="label">👤 Name:</div>
                  <div class="value">{contact.name}</div>
                </div>
                <div class="field">
                  <div class="label">📞 Phone Number:</div>
                  <div class="value"><a href="tel:{contact.phone}">{contact.phone}</a></div>
                </div>
                <div class="field">
                  <div class="label">📧 Email:</div>
                  <div class="value"><a href="mailto:{contact.email}">{contact.email}</a></div>
                </div>
                <div class="field">
                  <div class="label">💬 Message:</div>
                  <div class="value">{contact.message}</div>
                </div>
                <div class="field">
                  <div class="label">🕒 Submitted at:</div>
                  <div class="value">{contact.createdAt.strftime('%B %d, %Y at %I:%M %p')}</div>
                </div>
                <div class="field">
                  <div class="label">🆔 Contact ID:</div>
                  <div class="value">{contact.id}</div>
                </div>
              </div>
              <div class="footer">
                <p>This email was sent from your PYRAXUS portfolio contact form</p>
                <p>Visit your <a href="http://localhost:3000/admin">Admin Dashboard</a> to manage messages</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Create plain text version
        text_body = f"""
        New Contact Form Submission - PYRAXUS Portfolio
        
        Name: {contact.name}
        Phone: {contact.phone}
        Email: {contact.email}
        
        Message:
        {contact.message}
        
        Submitted at: {contact.createdAt.strftime('%B %d, %Y at %I:%M %p')}
        Contact ID: {contact.id}
        
        ---
        This email was sent from your PYRAXUS portfolio contact form
        """
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent successfully to {GMAIL_USER}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email: {str(e)}")
        return False

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