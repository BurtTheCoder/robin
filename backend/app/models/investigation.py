"""Investigation-related Pydantic models."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InvestigationStatus(str, Enum):
    """Investigation status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationCreate(BaseModel):
    """Request to create a new investigation."""
    query: str = Field(..., min_length=1, description="Investigation query")
    model: Optional[str] = Field(None, description="Model override")


class FollowUpRequest(BaseModel):
    """Request to send a follow-up query."""
    query: str = Field(..., min_length=1, description="Follow-up query")


class ToolExecution(BaseModel):
    """Record of a tool execution."""
    id: str
    tool: str
    input: dict[str, Any]
    output: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: str = "running"


class SubAgentResultModel(BaseModel):
    """Result from a sub-agent."""
    agent_type: str
    analysis: str
    success: bool
    error: Optional[str] = None


class InvestigationResponse(BaseModel):
    """Response after creating an investigation."""
    id: UUID
    stream_url: str
    status: InvestigationStatus = InvestigationStatus.PENDING


class InvestigationSummary(BaseModel):
    """Summary for investigation list."""
    id: UUID
    initial_query: str
    status: InvestigationStatus
    model: str
    num_turns: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class InvestigationDetail(BaseModel):
    """Full investigation details."""
    id: UUID
    session_id: Optional[str] = None
    initial_query: str
    status: InvestigationStatus
    full_response: Optional[str] = None
    tools_used: list[ToolExecution] = []
    subagent_results: list[SubAgentResultModel] = []
    model: str
    num_turns: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageModel(BaseModel):
    """Chat message model."""
    id: UUID
    role: str
    content: str
    tool_calls: Optional[list[dict]] = None
    created_at: datetime


# SSE Event Models

class SSEEventData(BaseModel):
    """Base class for SSE event data."""
    pass


class TextEventData(SSEEventData):
    """Text chunk event data."""
    content: str


class ToolStartEventData(SSEEventData):
    """Tool start event data."""
    id: str
    tool: str
    input: dict[str, Any]


class ToolEndEventData(SSEEventData):
    """Tool end event data."""
    id: str
    tool: str
    duration_ms: int
    output: Optional[str] = None


class SubAgentStartEventData(SSEEventData):
    """Sub-agent start event data."""
    agent_type: str


class SubAgentEndEventData(SSEEventData):
    """Sub-agent end event data."""
    agent_type: str
    analysis: str
    success: bool
    error: Optional[str] = None


class CompleteEventData(SSEEventData):
    """Investigation complete event data."""
    text: str
    session_id: Optional[str] = None
    duration_ms: Optional[int] = None
    num_turns: Optional[int] = None


class ErrorEventData(SSEEventData):
    """Error event data."""
    message: str
    code: str = "INVESTIGATION_ERROR"


class SSEEvent(BaseModel):
    """Server-Sent Event wrapper."""
    type: str
    data: dict[str, Any]
