"""Domain models for the registration system"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class RegistrationStatus(str, Enum):
    """Status of a registration"""
    ACTIVE = "ACTIVE"
    WAITLISTED = "WAITLISTED"


# User Models
class UserBase(BaseModel):
    """Base user model"""
    name: str = Field(..., min_length=1, max_length=200, description="User name")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or contain only whitespace')
        return v.strip()


class UserCreate(UserBase):
    """Model for creating a user"""
    userId: str = Field(..., min_length=1, max_length=100, description="Unique user identifier")
    
    @field_validator('userId')
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Ensure userId is not just whitespace"""
        if not v or not v.strip():
            raise ValueError('UserId cannot be empty or contain only whitespace')
        return v.strip()


class User(UserBase):
    """Complete user model"""
    userId: str
    createdAt: str
    
    class Config:
        from_attributes = True


# Registration Event Models (extends existing Event model)
class RegistrationEventCreate(BaseModel):
    """Model for creating an event with registration capabilities"""
    eventId: Optional[str] = Field(None, description="Optional custom event ID")
    name: str = Field(..., min_length=1, max_length=200, description="Event name")
    capacity: int = Field(..., gt=0, le=100000, description="Maximum number of attendees")
    hasWaitlist: bool = Field(default=False, description="Whether event has waitlist enabled")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or contain only whitespace')
        return v.strip()


class RegistrationEvent(BaseModel):
    """Complete registration event model"""
    eventId: str
    name: str
    capacity: int
    hasWaitlist: bool
    createdAt: str
    
    class Config:
        from_attributes = True


# Registration Models
class RegistrationCreate(BaseModel):
    """Model for creating a registration"""
    userId: str = Field(..., description="User ID")
    eventId: str = Field(..., description="Event ID")


class Registration(BaseModel):
    """Complete registration model"""
    registrationId: str
    userId: str
    eventId: str
    status: RegistrationStatus
    createdAt: str
    
    class Config:
        from_attributes = True


# Waitlist Models
class WaitlistEntry(BaseModel):
    """Waitlist entry model"""
    entryId: str
    userId: str
    eventId: str
    position: int
    createdAt: str
    
    class Config:
        from_attributes = True


# Response Models
class RegistrationResult(BaseModel):
    """Result of a registration attempt"""
    success: bool
    message: str
    registration: Optional[Registration] = None
    waitlistEntry: Optional[WaitlistEntry] = None


class UnregistrationResult(BaseModel):
    """Result of an unregistration"""
    success: bool
    message: str
    promoted: Optional[Registration] = None
