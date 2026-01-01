"""
Code Generation Request Model

Represents a user-initiated code generation request with progress tracking.
All data is stored locally with no database requirements, maintaining stateless backend design.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class RequestStatus(str, Enum):
    """Request status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeGenerationRequest(BaseModel):
    """
    Represents a user-initiated code generation request with progress tracking.

    Fields:
    - request_id (UUID): Unique identifier for the request
    - user_input (str): Original natural language request from user
    - status (RequestStatus): Current request status
    - created_at (datetime): Request creation timestamp
    - updated_at (datetime): Last status update timestamp
    - error_message (str, optional): Error details if status is 'failed'
    """

    request_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the request")
    user_input: str = Field(..., min_length=1, max_length=1000, description="Original natural language request from user")
    application_type: Optional[str] = Field(None, description="Detected or selected application type for US3")
    analysis: Optional[Any] = Field(None, description="Technology and application analysis results for US3")
    status: RequestStatus = Field(default=RequestStatus.PENDING, description="Current request status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last status update timestamp")
    error_message: Optional[str] = Field(None, description="Error details if status is 'failed'")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @validator('user_input')
    def validate_user_input(cls, v):
        """Validate user input is not empty and within length limits."""
        if not v or not v.strip():
            raise ValueError('用户输入不能为空')
        if len(v) > 1000:
            raise ValueError('用户输入长度不能超过1000个字符')
        return v.strip()

    def update_status(self, new_status: RequestStatus, error_message: Optional[str] = None):
        """
        Update request status and timestamp.

        Args:
            new_status: New status to set
            error_message: Error message if status is FAILED
        """
        self.status = new_status
        self.updated_at = datetime.utcnow()

        if new_status == RequestStatus.FAILED and error_message:
            self.error_message = error_message
        elif new_status != RequestStatus.FAILED:
            self.error_message = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'CodeGenerationRequest':
        """Create instance from dictionary (for JSON deserialization)."""
        # Handle UUID string conversion
        if 'request_id' in data and isinstance(data['request_id'], str):
            data['request_id'] = UUID(data['request_id'])

        # Handle datetime string conversion
        for field in ['created_at', 'updated_at']:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))

        return cls(**data)
