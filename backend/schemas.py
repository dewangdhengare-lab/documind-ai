"""Pydantic schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


# ── Document ──────────────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    error_message: Optional[str] = None
    page_count: Optional[int] = None
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChunkResponse(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]


# ── Chat ──────────────────────────────────────────────────────────────────────

class CreateConversationRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=1)
    title: Optional[str] = None


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)


class CitationSchema(BaseModel):
    document_id: str
    filename: str
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_text: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    citations: Optional[list[CitationSchema]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    document_ids: list[str]
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConversationListItem(BaseModel):
    id: str
    title: Optional[str] = None
    document_ids: list[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ── Summarization ────────────────────────────────────────────────────────────

class SummarizeRequest(BaseModel):
    document_id: str
    summary_type: str = Field(default="concise")


class SummaryResponse(BaseModel):
    id: str
    document_id: str
    summary_type: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Extraction ───────────────────────────────────────────────────────────────

class ExtractRequest(BaseModel):
    document_id: str
    instruction: str = Field(..., min_length=1, max_length=5000)


class ExtractionResponse(BaseModel):
    id: str
    document_id: str
    instruction: str
    result: Any  # JSON data
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Comparison ───────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=2, max_length=5)


class ComparisonResponse(BaseModel):
    id: str
    document_ids: list[str]
    result: Any
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Quiz ─────────────────────────────────────────────────────────────────────

class QuizGenerateRequest(BaseModel):
    document_id: str
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    question_types: list[str] = Field(
        default=["multiple_choice", "true_false"],
        min_length=1,
    )


class QuizQuestionSchema(BaseModel):
    id: int
    type: str
    question: str
    options: Optional[list[str]] = None
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    id: str
    document_id: str
    config: dict[str, Any]
    questions: list[QuizQuestionSchema]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizSubmitRequest(BaseModel):
    answers: dict[str, str]  # question_id -> answer


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    answers: dict[str, str]
    score: Optional[float] = None
    total: Optional[int] = None
    created_at: datetime
    results: Optional[list[dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)


# ── Reports ──────────────────────────────────────────────────────────────────

class ReportGenerateRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=1)
    report_type: str = Field(default="analysis", pattern="^(analysis|summary|comparison|research)$")
    title: Optional[str] = None
    purpose: Optional[str] = None
    audience: Optional[str] = None
    sections: Optional[list[str]] = None
    detail_level: str = Field(default="medium", pattern="^(brief|medium|detailed)$")


class ReportUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ReportResponse(BaseModel):
    id: str
    document_ids: list[str]
    report_type: str
    config: dict[str, Any]
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ── Generic ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
