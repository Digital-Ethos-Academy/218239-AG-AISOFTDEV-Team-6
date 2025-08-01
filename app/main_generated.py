# main.py

import datetime
import enum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, APIRouter, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Float,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship, Session, sessionmaker

# --- 1. DATABASE SETUP ---

# For this example, we'll use an in-memory SQLite database.
# The file will be created in the current directory.
SQLALCHEMY_DATABASE_URL = "sqlite:///./app_database.db"

# The `check_same_thread` argument is needed only for SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is the base class for our SQLAlchemy models.
Base = declarative_base()


# --- Dependency for getting a DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- ENUMS for CHECK constraints ---
# Using Python enums provides validation at the application level.

class MeetingStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class ParticipantRole(str, enum.Enum):
    host = "host"
    attendee = "attendee"
    note_taker_agent = "note_taker_agent"
    facilitator_agent = "facilitator_agent"

class TranscriptStatus(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ActionItemStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"

class IntegrationService(str, enum.Enum):
    google_workspace = "Google Workspace"
    microsoft_365 = "Microsoft 365"
    slack = "Slack"
    jira = "Jira"

class IntegrationStatus(str, enum.Enum):
    active = "active"
    revoked = "revoked"
    expired = "expired"


# --- 2. SQLAlchemy MODELS ---
# These classes define the database table structure.


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="organization")
    meetings = relationship("Meeting", back_populates="organization")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="SET NULL"))
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    timezone = Column(String, default="UTC")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="users")
    meeting_participations = relationship("MeetingParticipant", back_populates="user")
    agenda_items_presented = relationship("AgendaItem", back_populates="presenter")
    integrations = relationship("UserIntegration", back_populates="user")


class Meeting(Base):
    __tablename__ = "meetings"
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, CheckConstraint(f"status IN {tuple(e.value for e in MeetingStatus)}"), nullable=False)
    scheduled_start_time = Column(DateTime, nullable=False)
    actual_start_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    agenda = relationship("MeetingAgenda", uselist=False, back_populates="meeting", cascade="all, delete-orphan")
    transcript = relationship("Transcript", uselist=False, back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("MeetingSummary", uselist=False, back_populates="meeting", cascade="all, delete-orphan")
    analytics = relationship("MeetingAnalytics", uselist=False, back_populates="meeting", cascade="all, delete-orphan")


class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, CheckConstraint(f"role IN {tuple(e.value for e in ParticipantRole)}"), nullable=False)
    joined_at = Column(DateTime)
    __table_args__ = (UniqueConstraint("meeting_id", "user_id", name="uq_meeting_user"),)

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participations")
    transcript_entries = relationship("TranscriptEntry", back_populates="participant")
    action_items_assigned = relationship("ActionItem", back_populates="assignee")
    participant_analytics = relationship("ParticipantAnalytics", back_populates="participant", cascade="all, delete-orphan")


class MeetingAgenda(Base):
    __tablename__ = "meeting_agendas"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="agenda")
    items = relationship("AgendaItem", back_populates="agenda", cascade="all, delete-orphan")


class AgendaItem(Base):
    __tablename__ = "agenda_items"
    id = Column(Integer, primary_key=True, index=True)
    agenda_id = Column(Integer, ForeignKey("meeting_agendas.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String, nullable=False)
    description = Column(String)
    presenter_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    display_order = Column(Integer, nullable=False)
    estimated_duration_minutes = Column(Integer)

    agenda = relationship("MeetingAgenda", back_populates="items")
    presenter = relationship("User", back_populates="agenda_items_presented")


class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True)
    word_error_rate = Column(Float)
    processing_status = Column(String, default="processing", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    __table_args__ = (CheckConstraint(f"processing_status IN {tuple(e.value for e in TranscriptStatus)}"),)

    meeting = relationship("Meeting", back_populates="transcript")
    entries = relationship("TranscriptEntry", back_populates="transcript", cascade="all, delete-orphan")


class TranscriptEntry(Base):
    __tablename__ = "transcript_entries"
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Integer, ForeignKey("meeting_participants.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    start_time_offset_seconds = Column(Integer, nullable=False)
    end_time_offset_seconds = Column(Integer, nullable=False)

    transcript = relationship("Transcript", back_populates="entries")
    participant = relationship("MeetingParticipant", back_populates="transcript_entries")
    action_items = relationship("ActionItem", back_populates="source_transcript_entry")
    decisions = relationship("Decision", back_populates="source_transcript_entry")


class ActionItem(Base):
    __tablename__ = "action_items"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    assignee_participant_id = Column(Integer, ForeignKey("meeting_participants.id", ondelete="SET NULL"))
    due_date = Column(DateTime)
    status = Column(String, default="open", nullable=False)
    source_transcript_entry_id = Column(Integer, ForeignKey("transcript_entries.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    __table_args__ = (CheckConstraint(f"status IN {tuple(e.value for e in ActionItemStatus)}"),)

    meeting = relationship("Meeting", back_populates="action_items")
    assignee = relationship("MeetingParticipant", back_populates="action_items_assigned")
    source_transcript_entry = relationship("TranscriptEntry", back_populates="action_items")


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    source_transcript_entry_id = Column(Integer, ForeignKey("transcript_entries.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="decisions")
    source_transcript_entry = relationship("TranscriptEntry", back_populates="decisions")


class MeetingSummary(Base):
    __tablename__ = "meeting_summaries"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary_text = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="summary")


class UserIntegration(Base):
    __tablename__ = "user_integrations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    service_name = Column(String, nullable=False)
    auth_token_encrypted = Column(String, nullable=False)
    refresh_token_encrypted = Column(String)
    status = Column(String, default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    __table_args__ = (
        UniqueConstraint("user_id", "service_name", name="uq_user_service"),
        CheckConstraint(f"service_name IN {tuple(e.value for e in IntegrationService)}"),
        CheckConstraint(f"status IN {tuple(e.value for e in IntegrationStatus)}"),
    )

    user = relationship("User", back_populates="integrations")


class MeetingAnalytics(Base):
    __tablename__ = "meeting_analytics"
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True)
    participation_equity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    meeting = relationship("Meeting", back_populates="analytics")
    participant_stats = relationship("ParticipantAnalytics", back_populates="meeting_analytics_entry", cascade="all, delete-orphan")


class ParticipantAnalytics(Base):
    __tablename__ = "participant_analytics"
    id = Column(Integer, primary_key=True, index=True)
    meeting_analytics_id = Column(Integer, ForeignKey("meeting_analytics.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(Integer, ForeignKey("meeting_participants.id", ondelete="CASCADE"), nullable=False)
    speaking_time_seconds = Column(Integer, default=0, nullable=False)
    prompt_count = Column(Integer, default=0, nullable=False)
    __table_args__ = (UniqueConstraint("meeting_analytics_id", "participant_id", name="uq_analytics_participant"),)

    meeting_analytics_entry = relationship("MeetingAnalytics", back_populates="participant_stats")
    participant = relationship("MeetingParticipant", back_populates="participant_analytics")


# --- 3. Pydantic SCHEMAS ---
# These models define the data shapes for API requests and responses.
# `model_config` with `from_attributes = True` allows creating schemas from ORM objects.

# --- Base, Create, Update, and Read Schemas for Each Model ---

# Organization
class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None

class OrganizationRead(OrganizationBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# User
class UserBase(BaseModel):
    full_name: str
    email: str
    timezone: Optional[str] = 'UTC'
    organization_id: Optional[int] = None

class UserCreate(UserBase):
    password_hash: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    timezone: Optional[str] = None
    organization_id: Optional[int] = None
    password_hash: Optional[str] = None

class UserRead(UserBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# Meeting
class MeetingBase(BaseModel):
    organization_id: int
    title: str
    status: MeetingStatus
    scheduled_start_time: datetime.datetime
    actual_start_time: Optional[datetime.datetime] = None
    actual_end_time: Optional[datetime.datetime] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[MeetingStatus] = None
    scheduled_start_time: Optional[datetime.datetime] = None
    actual_start_time: Optional[datetime.datetime] = None
    actual_end_time: Optional[datetime.datetime] = None

class MeetingRead(MeetingBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# MeetingParticipant
class MeetingParticipantBase(BaseModel):
    meeting_id: int
    user_id: int
    role: ParticipantRole
    joined_at: Optional[datetime.datetime] = None

class MeetingParticipantCreate(MeetingParticipantBase):
    pass

class MeetingParticipantUpdate(BaseModel):
    role: Optional[ParticipantRole] = None
    joined_at: Optional[datetime.datetime] = None

class MeetingParticipantRead(MeetingParticipantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# MeetingAgenda
class MeetingAgendaBase(BaseModel):
    meeting_id: int

class MeetingAgendaCreate(MeetingAgendaBase):
    pass

class MeetingAgendaUpdate(BaseModel):
    pass # No updatable fields except through its items

class MeetingAgendaRead(MeetingAgendaBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# AgendaItem
class AgendaItemBase(BaseModel):
    agenda_id: int
    topic: str
    description: Optional[str] = None
    presenter_user_id: Optional[int] = None
    display_order: int
    estimated_duration_minutes: Optional[int] = None

class AgendaItemCreate(AgendaItemBase):
    pass

class AgendaItemUpdate(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    presenter_user_id: Optional[int] = None
    display_order: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None

class AgendaItemRead(AgendaItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Transcript
class TranscriptBase(BaseModel):
    meeting_id: int
    word_error_rate: Optional[float] = None
    processing_status: TranscriptStatus = Field(default=TranscriptStatus.processing)

class TranscriptCreate(TranscriptBase):
    pass

class TranscriptUpdate(BaseModel):
    word_error_rate: Optional[float] = None
    processing_status: Optional[TranscriptStatus] = None

class TranscriptRead(TranscriptBase):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# TranscriptEntry
class TranscriptEntryBase(BaseModel):
    transcript_id: int
    participant_id: int
    text: str
    start_time_offset_seconds: int
    end_time_offset_seconds: int

class TranscriptEntryCreate(TranscriptEntryBase):
    pass

class TranscriptEntryUpdate(BaseModel):
    text: Optional[str] = None
    start_time_offset_seconds: Optional[int] = None
    end_time_offset_seconds: Optional[int] = None

class TranscriptEntryRead(TranscriptEntryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ActionItem
class ActionItemBase(BaseModel):
    meeting_id: int
    description: str
    assignee_participant_id: Optional[int] = None
    due_date: Optional[datetime.datetime] = None
    status: ActionItemStatus = Field(default=ActionItemStatus.open)
    source_transcript_entry_id: Optional[int] = None

class ActionItemCreate(ActionItemBase):
    pass

class ActionItemUpdate(BaseModel):
    description: Optional[str] = None
    assignee_participant_id: Optional[int] = None
    due_date: Optional[datetime.datetime] = None
    status: Optional[ActionItemStatus] = None

class ActionItemRead(ActionItemBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# Decision
class DecisionBase(BaseModel):
    meeting_id: int
    description: str
    source_transcript_entry_id: Optional[int] = None

class DecisionCreate(DecisionBase):
    pass

class DecisionUpdate(BaseModel):
    description: Optional[str] = None
    source_transcript_entry_id: Optional[int] = None

class DecisionRead(DecisionBase):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# MeetingSummary
class MeetingSummaryBase(BaseModel):
    meeting_id: int
    summary_text: str

class MeetingSummaryCreate(MeetingSummaryBase):
    pass

class MeetingSummaryUpdate(BaseModel):
    summary_text: Optional[str] = None

class MeetingSummaryRead(MeetingSummaryBase):
    id: int
    generated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# UserIntegration
class UserIntegrationBase(BaseModel):
    user_id: int
    service_name: IntegrationService
    auth_token_encrypted: str
    refresh_token_encrypted: Optional[str] = None
    status: IntegrationStatus = Field(default=IntegrationStatus.active)

class UserIntegrationCreate(UserIntegrationBase):
    pass

class UserIntegrationUpdate(BaseModel):
    auth_token_encrypted: Optional[str] = None
    refresh_token_encrypted: Optional[str] = None
    status: Optional[IntegrationStatus] = None

class UserIntegrationRead(UserIntegrationBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# MeetingAnalytics
class MeetingAnalyticsBase(BaseModel):
    meeting_id: int
    participation_equity_score: Optional[float] = None

class MeetingAnalyticsCreate(MeetingAnalyticsBase):
    pass

class MeetingAnalyticsUpdate(BaseModel):
    participation_equity_score: Optional[float] = None

class MeetingAnalyticsRead(MeetingAnalyticsBase):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# ParticipantAnalytics
class ParticipantAnalyticsBase(BaseModel):
    meeting_analytics_id: int
    participant_id: int
    speaking_time_seconds: int = 0
    prompt_count: int = 0

class ParticipantAnalyticsCreate(ParticipantAnalyticsBase):
    pass

class ParticipantAnalyticsUpdate(BaseModel):
    speaking_time_seconds: Optional[int] = None
    prompt_count: Optional[int] = None

class ParticipantAnalyticsRead(ParticipantAnalyticsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# --- 4. CRUD Helper Functions ---
# Functions to interact with the database.

def create_db_item(db: Session, model, schema):
    db_item = model(**schema.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_db_item(db: Session, model, item_id: int):
    return db.query(model).filter(model.id == item_id).first()

def get_all_db_items(db: Session, model, skip: int = 0, limit: int = 100):
    return db.query(model).offset(skip).limit(limit).all()

def update_db_item(db: Session, db_item, schema):
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_db_item(db: Session, db_item):
    db.delete(db_item)
    db.commit()


# --- 5. API Routers ---
# Grouping endpoints by entity for better organization.

# --- Generic CRUD Router Factory ---
def create_crud_router(
    *,
    router_name: str,
    prefix: str,
    db_model,
    create_schema,
    read_schema,
    update_schema,
    tags: list[str]
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags)

    @router.post("/", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_item(item_in: create_schema, db: Session = Depends(get_db)):
        return create_db_item(db, model=db_model, schema=item_in)

    @router.get("/", response_model=List[read_schema])
    def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return get_all_db_items(db, model=db_model, skip=skip, limit=limit)

    @router.get("/{item_id}", response_model=read_schema)
    def read_item(item_id: int, db: Session = Depends(get_db)):
        db_item = get_db_item(db, model=db_model, item_id=item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{router_name} not found")
        return db_item

    @router.put("/{item_id}", response_model=read_schema)
    def update_item(item_id: int, item_in: update_schema, db: Session = Depends(get_db)):
        db_item = get_db_item(db, model=db_model, item_id=item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{router_name} not found")
        return update_db_item(db, db_item=db_item, schema=item_in)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        db_item = get_db_item(db, model=db_model, item_id=item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail=f"{router_name} not found")
        delete_db_item(db, db_item=db_item)
        return None

    return router

# Create routers for each entity
router_orgs = create_crud_router(router_name="Organization", prefix="/organizations", db_model=Organization, create_schema=OrganizationCreate, read_schema=OrganizationRead, update_schema=OrganizationUpdate, tags=["Organizations"])
router_users = create_crud_router(router_name="User", prefix="/users", db_model=User, create_schema=UserCreate, read_schema=UserRead, update_schema=UserUpdate, tags=["Users"])
router_meetings = create_crud_router(router_name="Meeting", prefix="/meetings", db_model=Meeting, create_schema=MeetingCreate, read_schema=MeetingRead, update_schema=MeetingUpdate, tags=["Meetings"])
router_participants = create_crud_router(router_name="Meeting Participant", prefix="/meeting_participants", db_model=MeetingParticipant, create_schema=MeetingParticipantCreate, read_schema=MeetingParticipantRead, update_schema=MeetingParticipantUpdate, tags=["Meeting Participants"])
router_agendas = create_crud_router(router_name="Meeting Agenda", prefix="/meeting_agendas", db_model=MeetingAgenda, create_schema=MeetingAgendaCreate, read_schema=MeetingAgendaRead, update_schema=MeetingAgendaUpdate, tags=["Meeting Agendas"])
router_agenda_items = create_crud_router(router_name="Agenda Item", prefix="/agenda_items", db_model=AgendaItem, create_schema=AgendaItemCreate, read_schema=AgendaItemRead, update_schema=AgendaItemUpdate, tags=["Agenda Items"])
router_transcripts = create_crud_router(router_name="Transcript", prefix="/transcripts", db_model=Transcript, create_schema=TranscriptCreate, read_schema=TranscriptRead, update_schema=TranscriptUpdate, tags=["Transcripts"])
router_transcript_entries = create_crud_router(router_name="Transcript Entry", prefix="/transcript_entries", db_model=TranscriptEntry, create_schema=TranscriptEntryCreate, read_schema=TranscriptEntryRead, update_schema=TranscriptEntryUpdate, tags=["Transcript Entries"])
router_action_items = create_crud_router(router_name="Action Item", prefix="/action_items", db_model=ActionItem, create_schema=ActionItemCreate, read_schema=ActionItemRead, update_schema=ActionItemUpdate, tags=["Action Items"])
router_decisions = create_crud_router(router_name="Decision", prefix="/decisions", db_model=Decision, create_schema=DecisionCreate, read_schema=DecisionRead, update_schema=DecisionUpdate, tags=["Decisions"])
router_summaries = create_crud_router(router_name="Meeting Summary", prefix="/meeting_summaries", db_model=MeetingSummary, create_schema=MeetingSummaryCreate, read_schema=MeetingSummaryRead, update_schema=MeetingSummaryUpdate, tags=["Meeting Summaries"])
router_integrations = create_crud_router(router_name="User Integration", prefix="/user_integrations", db_model=UserIntegration, create_schema=UserIntegrationCreate, read_schema=UserIntegrationRead, update_schema=UserIntegrationUpdate, tags=["User Integrations"])
router_meeting_analytics = create_crud_router(router_name="Meeting Analytics", prefix="/meeting_analytics", db_model=MeetingAnalytics, create_schema=MeetingAnalyticsCreate, read_schema=MeetingAnalyticsRead, update_schema=MeetingAnalyticsUpdate, tags=["Meeting Analytics"])
router_participant_analytics = create_crud_router(router_name="Participant Analytics", prefix="/participant_analytics", db_model=ParticipantAnalytics, create_schema=ParticipantAnalyticsCreate, read_schema=ParticipantAnalyticsRead, update_schema=ParticipantAnalyticsUpdate, tags=["Participant Analytics"])

# --- 6. MAIN APP ---

app = FastAPI(
    title="Meeting Intelligence Platform API",
    description="API for managing organizations, users, meetings, and related data.",
    version="1.0.0",
)

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)

# Include all the routers in the main FastAPI app
app.include_router(router_orgs)
app.include_router(router_users)
app.include_router(router_meetings)
app.include_router(router_participants)
app.include_router(router_agendas)
app.include_router(router_agenda_items)
app.include_router(router_transcripts)
app.include_router(router_transcript_entries)
app.include_router(router_action_items)
app.include_router(router_decisions)
app.include_router(router_summaries)
app.include_router(router_integrations)
app.include_router(router_meeting_analytics)
app.include_router(router_participant_analytics)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Meeting Intelligence Platform API. See /docs for documentation."}

# To run this application:
# 1. Install necessary packages: pip install "fastapi[all]" sqlalchemy
# 2. Save the code as main.py
# 3. Run from your terminal: uvicorn main:app --reload
# 4. Open your browser to http://127.0.0.1:8000/docs