"""Router for AI chat conversations and RAG messaging."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    CreateConversationRequest,
    SendMessageRequest,
    ConversationResponse,
    ConversationListItem,
    MessageResponse,
    CitationSchema,
)
import services.chat_service as chat_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


def _format_message(msg) -> MessageResponse:
    """Helper to convert Message ORM model to MessageResponse schema."""
    citations_list = None
    if msg.citations:
        try:
            raw_citations = json.loads(msg.citations)
            if isinstance(raw_citations, list):
                citations_list = [
                    CitationSchema(
                        document_id=c.get("document_id", ""),
                        filename=c.get("filename", ""),
                        page=c.get("page"),
                        section=c.get("section"),
                        chunk_text=c.get("chunk_text", ""),
                    )
                    for c in raw_citations
                ]
        except Exception:
            citations_list = None

    return MessageResponse(
        id=msg.id,
        conversation_id=msg.conversation_id,
        role=msg.role,
        content=msg.content,
        citations=citations_list,
        created_at=msg.created_at,
    )


def _format_conversation(conv) -> ConversationResponse:
    """Helper to format Conversation with parsed messages."""
    doc_ids = []
    try:
        doc_ids = json.loads(conv.document_ids)
    except Exception:
        doc_ids = []

    formatted_messages = [_format_message(m) for m in conv.messages]

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        document_ids=doc_ids,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=formatted_messages,
    )


@router.post("/api/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
@router.post("/api/chat/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    req: CreateConversationRequest,
    db: Session = Depends(get_db),
):
    """Create a new chat conversation for one or multiple ready documents."""
    try:
        conv = chat_service.create_conversation(
            document_ids=req.document_ids,
            title=req.title,
            db=db,
        )
        return _format_conversation(conv)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/conversations", response_model=list[ConversationListItem])
@router.get("/api/chat/conversations", response_model=list[ConversationListItem])
def list_conversations(db: Session = Depends(get_db)):
    """List all user conversations."""
    return chat_service.list_conversations(db)


@router.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
@router.get("/api/chat/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation details and full message history."""
    conv = chat_service.get_conversation(conversation_id, db)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return _format_conversation(conv)


@router.post("/api/conversations/{conversation_id}/messages", response_model=MessageResponse)
@router.post("/api/chat/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: str,
    req: SendMessageRequest,
    db: Session = Depends(get_db),
):
    """Send a query to the conversation and receive a RAG-grounded response with citations."""
    try:
        assistant_msg = chat_service.send_message(
            conversation_id=conversation_id,
            user_content=req.content,
            db=db,
        )
        return _format_message(assistant_msg)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Chat processing failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.delete("/api/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/api/chat/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Delete conversation and its message history."""
    success = chat_service.delete_conversation(conversation_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return None
