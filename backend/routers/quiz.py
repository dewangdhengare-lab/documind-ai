"""Router for quiz generation and assessment endpoints."""

from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    QuizGenerateRequest,
    QuizResponse,
    QuizQuestionSchema,
    QuizSubmitRequest,
    QuizAttemptResponse,
)
import services.quiz_service as quiz_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])


def _format_quiz(quiz) -> QuizResponse:
    """Format Quiz ORM model into QuizResponse schema."""
    config_data = {}
    try:
        config_data = json.loads(quiz.config)
    except Exception:
        pass

    questions_list = []
    try:
        raw_questions = json.loads(quiz.questions)
        for q in raw_questions:
            questions_list.append(
                QuizQuestionSchema(
                    id=q.get("id", 1),
                    type=q.get("type", "multiple_choice"),
                    question=q.get("question", ""),
                    options=q.get("options"),
                    correct_answer=q.get("correct_answer", ""),
                    explanation=q.get("explanation", ""),
                )
            )
    except Exception as e:
        logger.warning("Failed to deserialize quiz questions: %s", e)

    return QuizResponse(
        id=quiz.id,
        document_id=quiz.document_id,
        config=config_data,
        questions=questions_list,
        created_at=quiz.created_at,
    )


def _format_attempt(attempt) -> QuizAttemptResponse:
    """Format QuizAttempt model into QuizAttemptResponse."""
    answers_data = {}
    try:
        answers_data = json.loads(attempt.answers)
    except Exception:
        pass

    results_data = getattr(attempt, "results", None)

    return QuizAttemptResponse(
        id=attempt.id,
        quiz_id=attempt.quiz_id,
        answers=answers_data,
        score=attempt.score,
        total=attempt.total,
        created_at=attempt.created_at,
        results=results_data,
    )


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def generate_quiz(
    req: QuizGenerateRequest,
    db: Session = Depends(get_db),
):
    """Generate an interactive assessment based on document content."""
    try:
        quiz = quiz_service.generate_quiz(
            document_id=req.document_id,
            num_questions=req.num_questions,
            difficulty=req.difficulty,
            question_types=req.question_types,
            db=db,
        )
        return _format_quiz(quiz)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Quiz generation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.get("", response_model=list[QuizResponse])
def list_quizzes(
    document_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List quizzes, optionally filtered by document_id."""
    quizzes = quiz_service.list_quizzes(document_id=document_id, db=db)
    return [_format_quiz(q) for q in quizzes]


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    """Get single quiz with its questions."""
    quiz = quiz_service.get_quiz(quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return _format_quiz(quiz)


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(quiz_id: str, db: Session = Depends(get_db)):
    """Delete a quiz by ID."""
    success = quiz_service.delete_quiz(quiz_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return None


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResponse)
@router.post("/{quiz_id}/attempts", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    quiz_id: str,
    req: QuizSubmitRequest,
    db: Session = Depends(get_db),
):
    """Submit quiz answers, compute final score, and return detailed answer explanations."""
    try:
        attempt = quiz_service.submit_quiz_attempt(
            quiz_id=quiz_id,
            answers=req.answers,
            db=db,
        )
        return _format_attempt(attempt)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Quiz submission failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Quiz submission failed: {str(e)}")


@router.get("/{quiz_id}/attempts", response_model=list[QuizAttemptResponse])
def get_quiz_attempts(quiz_id: str, db: Session = Depends(get_db)):
    """Get all past submission attempts for this quiz."""
    quiz = quiz_service.get_quiz(quiz_id, db)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    attempts = quiz_service.get_quiz_attempts(quiz_id, db)
    return [_format_attempt(a) for a in attempts]
