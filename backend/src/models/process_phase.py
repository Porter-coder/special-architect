"""
Process Phase Model

Tracks the three-phase progress of the software engineering process.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class PhaseName(str, Enum):
    """Development phase enumeration."""
    SPECIFY = "specify"
    PLAN = "plan"
    IMPLEMENT = "implement"


class ProcessPhase(BaseModel):
    """
    Tracks the three-phase progress of the software engineering process.

    Fields:
    - phase_id (UUID): Unique identifier for phase record
    - request_id (UUID): Reference to parent request
    - phase_name (PhaseName): Current development phase
    - educational_message (str): Chinese message explaining current phase
    - timestamp (datetime): When this phase was entered
    - thinking_trace (str, optional): AI thinking content for current phase
    """

    phase_id: UUID = Field(default_factory=uuid4, description="Unique identifier for phase record")
    request_id: UUID = Field(..., description="Reference to parent request")
    phase_name: PhaseName = Field(..., description="Current development phase")
    educational_message: str = Field(..., description="Chinese message explaining current phase")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this phase was entered")
    thinking_trace: Optional[str] = Field(None, description="AI thinking content for current phase")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @validator('educational_message')
    def validate_educational_message(cls, v):
        """Validate educational message is in Chinese and not empty."""
        if not v or not v.strip():
            raise ValueError('教育性消息不能为空')
        # Basic check for Chinese characters (contains CJK unicode range)
        if not any('\u4e00' <= char <= '\u9fff' for char in v):
            raise ValueError('教育性消息必须包含中文字符')
        return v.strip()

    @validator('phase_name')
    def validate_phase_name(cls, v):
        """Validate phase name is one of the allowed phases."""
        if v not in [PhaseName.SPECIFY, PhaseName.PLAN, PhaseName.IMPLEMENT]:
            raise ValueError(f'无效的阶段名称: {v}')
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: dict) -> 'ProcessPhase':
        """Create instance from dictionary (for JSON deserialization)."""
        # Handle UUID string conversion
        for field in ['phase_id', 'request_id']:
            if field in data and isinstance(data[field], str):
                data[field] = UUID(data[field])

        # Handle datetime string conversion
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

        return cls(**data)


# Phase progression utilities
PHASE_ORDER = [PhaseName.SPECIFY, PhaseName.PLAN, PhaseName.IMPLEMENT]

PHASE_MESSAGES = {
    PhaseName.SPECIFY: "正在分析需求，定义功能边界...",
    PhaseName.PLAN: "正在设计技术方案，确定使用技术栈...",
    PhaseName.IMPLEMENT: "正在编写代码..."
}


def get_phase_message(phase: PhaseName) -> str:
    """Get the default educational message for a phase."""
    return PHASE_MESSAGES.get(phase, "正在处理中...")


def is_valid_phase_transition(from_phase: Optional[PhaseName], to_phase: PhaseName) -> bool:
    """
    Check if a phase transition is valid.

    Args:
        from_phase: Previous phase (None for initial phase)
        to_phase: Target phase

    Returns:
        True if transition is valid, False otherwise
    """
    if from_phase is None:
        return to_phase == PhaseName.SPECIFY

    from_index = PHASE_ORDER.index(from_phase)
    to_index = PHASE_ORDER.index(to_phase)

    # Can only move forward in phase order
    return to_index > from_index
