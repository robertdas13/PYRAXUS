# API Contracts - PYRAXUS Portfolio Backend

## Overview
This document outlines the backend implementation for the PYRAXUS portfolio website, specifically for the contact form functionality.

## Current State (Frontend Mock)
- Contact form in `/app/frontend/src/components/Contact.jsx`
- Mock form submission shows success toast
- Form data: { name, email, message }
- No actual data persistence

## Backend Implementation Plan

### 1. MongoDB Model
**Collection**: `contacts`

**Schema**:
```json
{
  "_id": ObjectId,
  "name": String (required),
  "email": String (required, validated),
  "message": String (required),
  "createdAt": DateTime (auto-generated),
  "status": String (default: "new", enum: ["new", "read", "replied"])
}
```

### 2. API Endpoints

#### POST /api/contact
**Purpose**: Submit a new contact form message

**Request Body**:
```json
{
  "name": "string (required, min 2 chars)",
  "email": "string (required, valid email)",
  "message": "string (required, min 10 chars)"
}
```

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "id": "contact_id",
    "createdAt": "timestamp"
  }
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "error": "Validation error message"
}
```

#### GET /api/contacts
**Purpose**: Retrieve all contact messages (admin view - optional for now)

**Success Response (200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "contact_id",
      "name": "string",
      "email": "string",
      "message": "string",
      "createdAt": "timestamp",
      "status": "new"
    }
  ]
}
```

### 3. Frontend Integration

**File**: `/app/frontend/src/components/Contact.jsx`

**Changes Required**:
- Remove mock setTimeout
- Replace with actual axios POST request to `/api/contact`
- Handle loading state during submission
- Handle success response (show toast)
- Handle error response (show error toast)
- Clear form on success

**API Call**:
```javascript
const response = await axios.post(`${API}/contact`, formData);
```

### 4. Validation Rules

**Backend Validation**:
- Name: Required, min 2 characters, max 100 characters
- Email: Required, valid email format
- Message: Required, min 10 characters, max 1000 characters

**Frontend Validation**:
- HTML5 required attributes (already present)
- Additional validation can be added for better UX

### 5. Error Handling
- Database connection errors
- Validation errors
- Server errors (500)
- Proper error messages returned to frontend

## Implementation Steps
1. ✅ Create contracts.md
2. Create MongoDB model for contacts
3. Create POST /api/contact endpoint
4. Create GET /api/contacts endpoint (optional)
5. Update frontend Contact.jsx to use real API
6. Test with backend testing agent
7. Verify form submission works end-to-end
