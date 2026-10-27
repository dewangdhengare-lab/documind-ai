"""RAG chat service with citations."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from config import settings
from models import Conversation, Message, Document
from services.retrieval_service import retrieve_relevant_chunks, format_context_for_llm
from services.llm_service import call_llm
from services.csv_service import run_csv_query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are DocuMind AI, an intelligent document analysis assistant. You answer questions based on the provided document context.

RULES:
1. Answer ONLY based on the provided context. Do not use outside knowledge.
2. If the context does not contain enough information to answer, say so clearly.
3. Always cite your sources using [Source N] notation, where N is the source number from the context.
4. Be precise and factual. Do not hallucinate or make up information.
5. If asked about numerical data from a CSV, refer to the computed statistics provided.
6. Provide clear, well-structured answers."""


def create_conversation(
    document_ids: list[str],
    title: str | None,
    db: Session,
) -> Conversation:
    """Create a new chat conversation."""
    # Validate that all documents exist and are ready
    for doc_id in document_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        if doc.status != "ready":
            raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")

    conv = Conversation(
        id=str(uuid.uuid4()),
        title=title or "New Conversation",
        document_ids=json.dumps(document_ids),
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def send_message(
    conversation_id: str,
    user_content: str,
    db: Session,
) -> Message:
    """
    Process a user message: retrieve context, call LLM, store response with citations.
    Returns the assistant's Message.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise ValueError(f"Conversation {conversation_id} not found")

    document_ids = json.loads(conv.document_ids)

    # Save user message
    user_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=user_content,
    )
    db.add(user_msg)
    db.commit()

    # Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(
        query=user_content,
        document_ids=document_ids,
        top_k=settings.TOP_K,
    )

    # Check if any document is CSV and add computed analytics
    csv_context = ""
    for doc_id in document_ids:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc and doc.file_type == ".csv":
            file_path = settings.UPLOAD_DIR / doc.filename
            if file_path.exists():
                csv_result = run_csv_query(file_path, user_content)
                csv_context += f"\n\n[CSV Analytics for {doc.original_filename}]\n{csv_result}"

    # Format context
    context = format_context_for_llm(chunks)
    if csv_context:
        context += csv_context

    if len(context) > 6000:
        context = context[:6000] + "\n...[truncated for length]..."

    # Build conversation history for context
    history_messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    llm_messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Add last few messages for context (keep it manageable)
    recent_messages = history_messages[-6:]  # Last 6 messages
    for msg in recent_messages:
        if msg.id == user_msg.id:
            continue  # We'll add the current message with context
        llm_messages.append({"role": msg.role, "content": msg.content})

    # Add user message with context
    llm_messages.append({
        "role": "user",
        "content": f"Context from documents:\n{context}\n\nUser question: {user_content}",
    })

    # Call LLM
    try:
        response_text = call_llm(llm_messages)
    except (ValueError, RuntimeError) as e:
        response_text = f"I apologize, but I encountered an error: {str(e)}"

    # Build citations from retrieved chunks
    citations: list[dict[str, Any]] = []
    for chunk in chunks:
        meta = chunk.get("metadata", {})
        citation: dict[str, Any] = {
            "document_id": meta.get("document_id", ""),
            "filename": meta.get("filename", ""),
            "chunk_text": chunk.get("text", "")[:200],  # Truncate for brevity
        }
        if meta.get("page_number"):
            citation["page"] = meta["page_number"]
        if meta.get("heading"):
            citation["section"] = meta["heading"]
        citations.append(citation)

    # Save assistant message
    assistant_msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
        citations=json.dumps(citations),
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg


def get_conversation(conversation_id: str, db: Session) -> Conversation | None:
    """Get a conversation with all its messages."""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def list_conversations(db: Session) -> list[dict[str, Any]]:
    """List all conversations with message counts."""
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    result = []
    for conv in conversations:
        msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
        result.append({
            "id": conv.id,
            "title": conv.title,
            "document_ids": json.loads(conv.document_ids),
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": msg_count,
        })
    return result


def delete_conversation(conversation_id: str, db: Session) -> bool:
    """Delete a conversation and all its messages."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True
