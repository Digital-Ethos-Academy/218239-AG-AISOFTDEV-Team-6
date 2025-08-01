# pd_models.py

"""
Pydantic models for request and response validation, based on the application's
SQL schema. These models are used by FastAPI to validate incoming data,
serialize outgoing data, and auto-generate API documentation.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Enums for CHECK constraints ---

class MeetingStatus(str, Enum):
    """Enumeration for the status of a meeting."""
    SCHEDULED = 'scheduled'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class MeetingParticipantRole(str, Enum):
    """Enumeration for the role of a participant in a meeting."""
    HOST = 'host'
    ATTENDEE = 'attendee'
    NOTE_TAKER_AGENT = 'note_taker_agent'
    FACILITATOR_AGENT = 'facilitator_agent'


class TranscriptProcessingStatus(str, Enum):
    """Enumeration for the status of a transcript generation process."""
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


class ActionItemStatus(str, Enum):
    """Enumeration for the status of an action item."""
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'


class UserIntegrationService(str, Enum):
    """Enumeration for supported third-party integration services."""
    GOOGLE_WORKSPACE = 'Google Workspace'
    MICROSOFT_365 = 'Microsoft 365'
    SLACK = 'Slack'
    JIRA = 'Jira'


class UserIntegrationStatus(str, Enum):
    """Enumeration for the status of a user's integration."""
    ACTIVE = 'active'
    REVOKED = 'revoked'
    EXPIRED = 'expired'


# --- Model Configuration ---
# Enables models to be created from ORM objects (e.g., SQLAlchemy instances)
orm_config = ConfigDict(from_attributes=True)


# --- Organization Models ---

class OrganizationBase(BaseModel):
    name: str = Field(..., description="The name of the organization.")


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The new name of the organization.")


class Organization(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = orm_config


# --- User Models ---

class UserBase(BaseModel):
    full_name: str = Field(..., description="The user's full name.")
    email: EmailStr = Field(..., description="The user's unique email address.")
    timezone: str = Field(default='UTC', description="The user's preferred timezone.")
    organization_id: Optional[int] = Field(None, description="The ID of the organization the user belongs to.")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="The user's plaintext password. Will be hashed before storage.")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="The user's new full name.")
    email: Optional[EmailStr] = Field(None, description="The user's new email address.")
    password: Optional[str] = Field(None, min_length=8, description="A new password for the user.")
    timezone: Optional[str] = Field(None, description="The user's new timezone.")


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = orm_config


# --- Meeting Participant Models ---

class MeetingParticipantBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting.")
    user_id: int = Field(..., description="The ID of the user participating in the meeting.")
    role: MeetingParticipantRole = Field(..., description="The role of the participant in the meeting.")


class MeetingParticipantCreate(MeetingParticipantBase):
    pass


class MeetingParticipantUpdate(BaseModel):
    role: Optional[MeetingParticipantRole] = Field(None, description="The participant's new role.")


class MeetingParticipant(MeetingParticipantBase):
    id: int
    joined_at: Optional[datetime] = None
    model_config = orm_config


class MeetingParticipantWithUser(MeetingParticipant):
    user: User


# --- Agenda Models ---

class AgendaItemBase(BaseModel):
    topic: str = Field(..., description="The main topic of the agenda item.")
    description: Optional[str] = Field(None, description="A detailed description of the agenda item.")
    presenter_user_id: Optional[int] = Field(None, description="The ID of the user presenting this item.")
    display_order: int = Field(..., description="The order in which this item appears in the agenda.")
    estimated_duration_minutes: Optional[int] = Field(None, description="The estimated time for this item in minutes.")


class AgendaItemCreate(AgendaItemBase):
    # The agenda_id will be provided when creating the item.
    agenda_id: int


class AgendaItemUpdate(BaseModel):
    topic: Optional[str] = Field(None, description="The new topic of the agenda item.")
    description: Optional[str] = Field(None, description="The new description of the agenda item.")
    presenter_user_id: Optional[int] = Field(None, description="The new presenter for this item.")
    display_order: Optional[int] = Field(None, description="The new display order for this item.")
    estimated_duration_minutes: Optional[int] = Field(None, description="The new estimated duration.")


class AgendaItem(AgendaItemBase):
    id: int
    agenda_id: int
    model_config = orm_config


class AgendaItemWithPresenter(AgendaItem):
    presenter: Optional[User] = None


class MeetingAgendaBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting this agenda belongs to.")


class MeetingAgendaCreate(MeetingAgendaBase):
    pass


class MeetingAgenda(MeetingAgendaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[AgendaItemWithPresenter] = []
    model_config = orm_config

class MeetingAgendaUpdate(BaseModel):
    items: Optional[List[AgendaItemUpdate]] = Field(None, description="List of updated agenda items.")



# --- Transcript Models ---

class TranscriptEntryBase(BaseModel):
    participant_id: int = Field(..., description="The ID of the participant who spoke.")
    text: str = Field(..., description="The transcribed text of the utterance.")
    start_time_offset_seconds: int = Field(..., description="Start time in seconds from the beginning of the meeting.")
    end_time_offset_seconds: int = Field(..., description="End time in seconds from the beginning of the meeting.")


class TranscriptEntryCreate(TranscriptEntryBase):
    transcript_id: int


class TranscriptEntry(TranscriptEntryBase):
    id: int
    transcript_id: int
    model_config = orm_config


class TranscriptEntryWithParticipant(TranscriptEntry):
    participant: MeetingParticipantWithUser


class TranscriptBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting for the transcript.")
    processing_status: TranscriptProcessingStatus = Field(default='processing', description="The processing status.")


class TranscriptCreate(TranscriptBase):
    pass


class TranscriptUpdate(BaseModel):
    word_error_rate: Optional[float] = Field(None, description="The Word Error Rate (WER) of the transcription.")
    processing_status: Optional[TranscriptProcessingStatus] = Field(None, description="The new processing status.")


class Transcript(TranscriptBase):
    id: int
    word_error_rate: Optional[float] = None
    created_at: datetime
    entries: List[TranscriptEntryWithParticipant] = []
    model_config = orm_config


# --- Action Item Models ---

class ActionItemBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting where the action item was created.")
    description: str = Field(..., description="The description of the action to be taken.")
    assignee_participant_id: Optional[int] = Field(None, description="The participant assigned to this action item.")
    due_date: Optional[date] = Field(None, description="The due date for the action item.")
    status: ActionItemStatus = Field(default='open', description="The current status of the action item.")
    source_transcript_entry_id: Optional[int] = Field(None, description="The transcript entry that originated this item.")


class ActionItemCreate(ActionItemBase):
    pass


class ActionItemUpdate(BaseModel):
    description: Optional[str] = Field(None, description="The new description of the action.")
    assignee_participant_id: Optional[int] = Field(None, description="The new assignee for the action.")
    due_date: Optional[date] = Field(None, description="The new due date.")
    status: Optional[ActionItemStatus] = Field(None, description="The new status.")


class ActionItem(ActionItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = orm_config


class ActionItemWithDetails(ActionItem):
    assignee: Optional[MeetingParticipantWithUser] = None
    source_transcript_entry: Optional[TranscriptEntry] = None


# --- Decision Models ---

class DecisionBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting where the decision was made.")
    description: str = Field(..., description="The description of the decision.")
    source_transcript_entry_id: Optional[int] = Field(None, description="The transcript entry that originated this decision.")


class DecisionCreate(DecisionBase):
    pass


class DecisionUpdate(BaseModel):
    description: Optional[str] = Field(None, description="The updated description of the decision.")


class Decision(DecisionBase):
    id: int
    created_at: datetime
    model_config = orm_config


class DecisionWithSource(Decision):
    source_transcript_entry: Optional[TranscriptEntry] = None


# --- Meeting Summary Models ---

class MeetingSummaryBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting being summarized.")
    summary_text: str = Field(..., description="The generated summary of the meeting.")


class MeetingSummaryCreate(MeetingSummaryBase):
    pass


class MeetingSummaryUpdate(BaseModel):
    summary_text: Optional[str] = Field(None, description="The updated summary text.")


class MeetingSummary(MeetingSummaryBase):
    id: int
    generated_at: datetime
    model_config = orm_config


# --- User Integration Models ---

class UserIntegrationBase(BaseModel):
    user_id: int = Field(..., description="The ID of the user who owns this integration.")
    service_name: UserIntegrationService = Field(..., description="The name of the integrated third-party service.")


class UserIntegrationCreate(UserIntegrationBase):
    # Raw tokens would be handled in the endpoint; these fields map to the DB schema
    auth_token_encrypted: str
    refresh_token_encrypted: Optional[str] = None


class UserIntegrationUpdate(BaseModel):
    auth_token_encrypted: Optional[str] = None
    refresh_token_encrypted: Optional[str] = None
    status: Optional[UserIntegrationStatus] = None


class UserIntegration(UserIntegrationBase):
    """Response model for a user integration, omitting sensitive tokens."""
    id: int
    status: UserIntegrationStatus
    created_at: datetime
    updated_at: datetime
    model_config = orm_config


# --- Analytics Models ---

class ParticipantAnalyticsBase(BaseModel):
    participant_id: int = Field(..., description="The ID of the participant being analyzed.")
    speaking_time_seconds: int = Field(default=0, description="Total speaking time for the participant in seconds.")
    prompt_count: int = Field(default=0, description="The number of times the participant was prompted by an agent.")


class ParticipantAnalyticsCreate(ParticipantAnalyticsBase):
    meeting_analytics_id: int


class ParticipantAnalytics(ParticipantAnalyticsBase):
    id: int
    meeting_analytics_id: int
    model_config = orm_config


class ParticipantAnalyticsWithDetails(ParticipantAnalytics):
    participant: MeetingParticipantWithUser


class MeetingAnalyticsBase(BaseModel):
    meeting_id: int = Field(..., description="The ID of the meeting being analyzed.")
    participation_equity_score: Optional[float] = Field(None, description="A score representing participation equity.")


class MeetingAnalyticsCreate(MeetingAnalyticsBase):
    pass


class MeetingAnalytics(MeetingAnalyticsBase):
    id: int
    created_at: datetime
    participants_analytics: List[ParticipantAnalyticsWithDetails] = []
    model_config = orm_config


# --- Meeting Models (including comprehensive response model) ---

class MeetingBase(BaseModel):
    organization_id: int = Field(..., description="The ID of the organization hosting the meeting.")
    title: str = Field(..., description="The title or purpose of the meeting.")
    scheduled_start_time: datetime = Field(..., description="The planned start time of the meeting.")


class MeetingCreate(MeetingBase):
    # Status is set on creation, often defaults to 'scheduled' in business logic
    status: MeetingStatus = Field(default=MeetingStatus.SCHEDULED)


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The new title for the meeting.")
    status: Optional[MeetingStatus] = Field(None, description="The new status of the meeting.")
    scheduled_start_time: Optional[datetime] = Field(None, description="The rescheduled start time.")
    actual_start_time: Optional[datetime] = Field(None, description="The actual time the meeting started.")
    actual_end_time: Optional[datetime] = Field(None, description="The actual time the meeting ended.")


class Meeting(MeetingBase):
    id: int
    status: MeetingStatus
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    model_config = orm_config


class MeetingDetails(Meeting):
    """A comprehensive model representing a meeting and all its related data."""
    organization: Organization
    participants: List[MeetingParticipantWithUser] = []
    agenda: Optional[MeetingAgenda] = None
    transcript: Optional[Transcript] = None
    action_items: List[ActionItemWithDetails] = []
    decisions: List[DecisionWithSource] = []
    summary: Optional[MeetingSummary] = None
    analytics: Optional[MeetingAnalytics] = None