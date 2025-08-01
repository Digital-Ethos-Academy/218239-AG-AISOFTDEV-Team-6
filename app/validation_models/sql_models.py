# sql_models.py
"""
SQLAlchemy ORM models for the application database, based on the provided schema.

This module defines the data model using SQLAlchemy's Declarative Mapping,
which will be used by the application's data access layer to interact with
the SQLite database. Each class corresponds to a table in the database.
"""

from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional


# Define a base class for declarative models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class Organization(Base):
    """Represents an organization or a company."""
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    meetings: Mapped[list["Meeting"]] = relationship(
        back_populates="organization", cascade="all, delete"
    )


class User(Base):
    """Represents a user account."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL")
    )
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    timezone: Mapped[str | None] = mapped_column(Text, server_default="UTC")
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship(back_populates="users")
    meeting_participations: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    presented_agenda_items: Mapped[list["AgendaItem"]] = relationship(
        back_populates="presenter"
    )
    integrations: Mapped[list["UserIntegration"]] = relationship(
        back_populates="user", cascade="all, delete"
    )


class Meeting(Base):
    """Represents a single meeting event."""
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    scheduled_start_time: Mapped[str] = mapped_column(Text, nullable=False)
    actual_start_time: Mapped[Optional[str]] = mapped_column(Text)
    actual_end_time: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint(
            status.in_(["scheduled", "in_progress", "completed", "cancelled"]),
            name="ck_meeting_status",
        ),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="meetings")
    participants: Mapped[list["MeetingParticipant"]] = relationship(
        back_populates="meeting", cascade="all, delete"
    )
    agenda: Mapped["MeetingAgenda"] = relationship(
        back_populates="meeting", uselist=False, cascade="all, delete"
    )
    transcript: Mapped["Transcript"] = relationship(
        back_populates="meeting", uselist=False, cascade="all, delete"
    )
    action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="meeting", cascade="all, delete"
    )
    decisions: Mapped[list["Decision"]] = relationship(
        back_populates="meeting", cascade="all, delete"
    )
    summary: Mapped["MeetingSummary"] = relationship(
        back_populates="meeting", uselist=False, cascade="all, delete"
    )
    analytics: Mapped["MeetingAnalytics"] = relationship(
        back_populates="meeting", uselist=False, cascade="all, delete"
    )


class MeetingParticipant(Base):
    """Association object linking users to meetings with a specific role."""
    __tablename__ = "meeting_participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    joined_at: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("meeting_id", "user_id", name="uq_meeting_user"),
        CheckConstraint(
            role.in_(["host", "attendee", "note_taker_agent", "facilitator_agent"]),
            name="ck_participant_role",
        ),
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="meeting_participations")
    transcript_entries: Mapped[list["TranscriptEntry"]] = relationship(
        back_populates="participant", cascade="all, delete"
    )
    assigned_action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="assignee"
    )
    analytics: Mapped[Optional["ParticipantAnalytics"]] = relationship(
        back_populates="participant", uselist=False, cascade="all, delete"
    )


class MeetingAgenda(Base):
    """Represents the agenda for a single meeting."""
    __tablename__ = "meeting_agendas"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="agenda")
    items: Mapped[list["AgendaItem"]] = relationship(
        back_populates="agenda", cascade="all, delete"
    )


class AgendaItem(Base):
    """Represents a single item within a meeting agenda."""
    __tablename__ = "agenda_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    agenda_id: Mapped[int] = mapped_column(
        ForeignKey("meeting_agendas.id", ondelete="CASCADE"), nullable=False
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    presenter_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    agenda: Mapped["MeetingAgenda"] = relationship(back_populates="items")
    presenter: Mapped[Optional["User"]] = relationship(
        back_populates="presented_agenda_items"
    )


class Transcript(Base):
    """Stores the full transcript and metadata for a meeting."""
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    word_error_rate: Mapped[Optional[float]] = mapped_column(Float)
    processing_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="processing"
    )
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint(
            processing_status.in_(["processing", "completed", "failed"]),
            name="ck_transcript_status",
        ),
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="transcript")
    entries: Mapped[list["TranscriptEntry"]] = relationship(
        back_populates="transcript", cascade="all, delete"
    )


class TranscriptEntry(Base):
    """Represents a single utterance or block of text in a transcript."""
    __tablename__ = "transcript_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[int] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("meeting_participants.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time_offset_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    end_time_offset_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    transcript: Mapped["Transcript"] = relationship(back_populates="entries")
    participant: Mapped["MeetingParticipant"] = relationship(
        back_populates="transcript_entries"
    )
    source_for_action_items: Mapped[list["ActionItem"]] = relationship(
        back_populates="source_transcript_entry"
    )
    source_for_decisions: Mapped[list["Decision"]] = relationship(
        back_populates="source_transcript_entry"
    )


class ActionItem(Base):
    """Represents a single actionable task derived from a meeting."""
    __tablename__ = "action_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assignee_participant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("meeting_participants.id", ondelete="SET NULL")
    )
    due_date: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="open")
    source_transcript_entry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transcript_entries.id", ondelete="SET NULL")
    )
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        CheckConstraint(
            status.in_(["open", "in_progress", "completed"]),
            name="ck_action_item_status",
        ),
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="action_items")
    assignee: Mapped[Optional["MeetingParticipant"]] = relationship(
        back_populates="assigned_action_items"
    )
    source_transcript_entry: Mapped[Optional["TranscriptEntry"]] = relationship(
        back_populates="source_for_action_items"
    )


class Decision(Base):
    """Represents a key decision made during a meeting."""
    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_transcript_entry_id: Mapped[int | None] = mapped_column(
        ForeignKey("transcript_entries.id", ondelete="SET NULL")
    )
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="decisions")
    source_transcript_entry: Mapped[Optional["TranscriptEntry"]] = relationship(
        back_populates="source_for_decisions"
    )


class MeetingSummary(Base):
    """Stores the AI-generated summary of a meeting."""
    __tablename__ = "meeting_summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="summary")


class UserIntegration(Base):
    """Stores authentication information for third-party user integrations."""
    __tablename__ = "user_integrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service_name: Mapped[str] = mapped_column(Text, nullable=False)
    auth_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="active")
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    __table_args__ = (
        UniqueConstraint("user_id", "service_name", name="uq_user_service"),
        CheckConstraint(
            service_name.in_(["Google Workspace", "Microsoft 365", "Slack", "Jira"]),
            name="ck_integration_service",
        ),
        CheckConstraint(
            status.in_(["active", "revoked", "expired"]), name="ck_integration_status"
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="integrations")


class MeetingAnalytics(Base):
    """Stores high-level analytics for a meeting."""
    __tablename__ = "meeting_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    participation_equity_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    meeting: Mapped["Meeting"] = relationship(back_populates="analytics")
    participant_analytics: Mapped[list["ParticipantAnalytics"]] = relationship(
        back_populates="meeting_analytics", cascade="all, delete"
    )


class ParticipantAnalytics(Base):
    """Stores analytics specific to a single participant in a meeting."""
    __tablename__ = "participant_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_analytics_id: Mapped[int] = mapped_column(
        ForeignKey("meeting_analytics.id", ondelete="CASCADE"), nullable=False
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("meeting_participants.id", ondelete="CASCADE"), nullable=False
    )
    speaking_time_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    prompt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    __table_args__ = (
        UniqueConstraint(
            "meeting_analytics_id", "participant_id", name="uq_meeting_analytics_participant"
        ),
    )

    # Relationships
    meeting_analytics: Mapped["MeetingAnalytics"] = relationship(
        back_populates="participant_analytics"
    )
    participant: Mapped["MeetingParticipant"] = relationship(back_populates="analytics")