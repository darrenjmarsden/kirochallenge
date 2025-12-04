from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, max_length=2000, description="Event description")
    date: str = Field(..., description="Event date in ISO format (YYYY-MM-DDTHH:MM:SS)")
    location: str = Field(..., min_length=1, max_length=500, description="Event location")
    capacity: int = Field(..., gt=0, le=100000, description="Maximum number of attendees")
    organizer: str = Field(..., min_length=1, max_length=200, description="Event organizer name")
    status: EventStatus = Field(default=EventStatus.DRAFT, description="Event status")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format - accepts ISO format or simple date (YYYY-MM-DD)"""
        try:
            # Try parsing as ISO format first
            event_date = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            # Try simple date format YYYY-MM-DD
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in ISO format (YYYY-MM-DDTHH:MM:SS) or simple date format (YYYY-MM-DD)')
    
    @field_validator('title', 'description', 'location', 'organizer')
    @classmethod
    def validate_no_empty_strings(cls, v: str) -> str:
        """Ensure strings are not just whitespace"""
        if not v or not v.strip():
            raise ValueError('Field cannot be empty or contain only whitespace')
        return v.strip()


class EventCreate(EventBase):
    eventId: Optional[str] = Field(None, description="Optional custom event ID (auto-generated if not provided)")


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[EventStatus] = None


class Event(EventBase):
    eventId: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True
