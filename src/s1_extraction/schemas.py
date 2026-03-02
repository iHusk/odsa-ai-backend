"""
schemas.py -- Pydantic models for structured extraction from the Northbrook Partners corpus.

Each model defines the expected output shape for a specific document type.
Claude will be asked to return JSON matching these schemas, and Pydantic
will validate the result.

Usage:
    from src.s1_extraction.schemas import DocumentMeta, MemoExtraction, MeetingExtraction, PolicyExtraction

    # Get the JSON schema to pass to Claude
    schema = MemoExtraction.model_json_schema()
"""

from typing import Literal

from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    """Basic metadata extracted from any Northbrook document."""

    title: str = Field(description="Document title or subject line")
    doc_type: Literal["memo", "meeting_notes", "policy", "financial_report", "other"] = Field(
        description="Type of document"
    )
    date: str = Field(description="Document date in YYYY-MM-DD format")
    author: str | None = Field(default=None, description="Author or sender")
    page_count: int = Field(description="Estimated number of pages")
    confidential: bool = Field(
        default=False, description="Whether the document contains sensitive information"
    )
    summary: str = Field(description="One-sentence summary of the document's purpose")
    departments: list[str] = Field(
        default_factory=list, description="Departments referenced in the document"
    )


class MemoExtraction(BaseModel):
    """Structured extraction for internal memos."""

    author: str = Field(description="Who wrote the memo")
    date: str = Field(description="Date in YYYY-MM-DD format")
    subject: str = Field(description="Main topic")
    key_points: list[str] = Field(description="Important points from the memo")
    action_items: list[str] = Field(
        default_factory=list, description="Follow-up tasks if any"
    )
    priority: str | None = Field(
        default=None, description="Priority level if mentioned"
    )


class MeetingExtraction(BaseModel):
    """Structured extraction for meeting notes."""

    meeting_date: str = Field(description="Date in YYYY-MM-DD format")
    attendees: list[str] = Field(description="List of attendee names")
    agenda_topics: list[str] = Field(description="Topics discussed")
    decisions: list[str] = Field(
        default_factory=list, description="Decisions made"
    )
    action_items: list[str] = Field(
        default_factory=list, description="Action items with assignees"
    )
    next_meeting: str | None = Field(
        default=None, description="Next meeting date if mentioned"
    )


class PolicyExtraction(BaseModel):
    """Structured extraction for policy documents."""

    title: str = Field(description="Policy title")
    effective_date: str = Field(
        description="When the policy takes effect, YYYY-MM-DD"
    )
    department: str = Field(description="Department this policy applies to")
    summary: str = Field(description="Brief summary of the policy")
    key_provisions: list[str] = Field(description="Main policy provisions")
    exceptions: list[str] = Field(
        default_factory=list, description="Exceptions or special cases"
    )
