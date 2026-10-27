"""SQLAlchemy ORM models for DocuMind AI."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=_generate_uuid)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String, default="uploading")
    error_message = Column(Text, nullable=True)
    page_count = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    # Relationships
    summaries = relationship("Summary", back_populates="document", cascade="all, delete-orphan")
    extractions = relationship("Extraction", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="document", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=_generate_uuid)
    title = Column(String, nullable=True)
    document_ids = Column(Text, nullable=False)  # JSON array
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=_generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    citations = Column(Text, nullable=True)  # JSON array of citation objects
    created_at = Column(DateTime, default=_utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String, primary_key=True, default=_generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    summary_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="summaries")


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(String, primary_key=True, default=_generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    instruction = Column(Text, nullable=False)
    result = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="extractions")


class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(String, primary_key=True, default=_generate_uuid)
    document_ids = Column(Text, nullable=False)  # JSON array
    result = Column(Text, nullable=False)  # JSON
    created_at = Column(DateTime, default=_utcnow)


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=_generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    config = Column(Text, nullable=False)  # JSON
    questions = Column(Text, nullable=False)  # JSON array
    created_at = Column(DateTime, default=_utcnow)

    document = relationship("Document", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String, primary_key=True, default=_generate_uuid)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    answers = Column(Text, nullable=False)  # JSON
    score = Column(Float, nullable=True)
    total = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    quiz = relationship("Quiz", back_populates="attempts")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True, default=_generate_uuid)
    document_ids = Column(Text, nullable=False)  # JSON array
    report_type = Column(String, nullable=False)
    config = Column(Text, nullable=False)  # JSON
    content = Column(Text, nullable=False)  # Markdown content
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
