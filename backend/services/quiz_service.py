"""Interactive quiz generation and scoring service."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from sqlalchemy.orm import Session

from models import Document, Quiz, QuizAttempt
from services.vector_store import get_chunks_by_document
from services.llm_service import call_llm

logger = logging.getLogger(__name__)


def _get_document_full_text(document_id: str) -> str:
    """Retrieve full text from stored chunks of the document."""
    chunks = get_chunks_by_document(document_id)
    if not chunks:
        return ""
    return "\n\n".join(c["text"] for c in chunks)


def generate_quiz(
    document_id: str,
    num_questions: int,
    difficulty: str,
    question_types: list[str],
    db: Session,
) -> Quiz:
    """Generate a quiz grounded in document content."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise ValueError(f"Document {document_id} not found")
    if doc.status != "ready":
        raise ValueError(f"Document '{doc.original_filename}' is not ready (status: {doc.status})")

    full_text = _get_document_full_text(document_id)
    if not full_text.strip():
        raise ValueError(f"No text content found for document '{doc.original_filename}'")

    max_chars = 8000
    if len(full_text) > max_chars:
        truncated_text = (
            full_text[:5000]
            + "\n\n[... content truncated to fit token limits ...]\n\n"
            + full_text[-3000:]
        )
    else:
        truncated_text = full_text

    types_desc = ", ".join(question_types)
    system_prompt = (
        "You are an educational assessment expert. "
        "Create an interactive quiz strictly grounded in the facts and concepts of the provided document.\n"
        f"Generate exactly {num_questions} questions.\n"
        f"Difficulty Level: {difficulty.upper()}.\n"
        f"Allowed Question Types: {types_desc}.\n\n"
        "RULES:\n"
        "1. Every question MUST be answerable from the text. Never ask outside questions.\n"
        "2. For multiple_choice: include 'options' (array of 4 distinct choices, e.g. ['A) ...', 'B) ...', ...]). "
        "The 'correct_answer' must match one of the options.\n"
        "3. For true_false: options must be ['True', 'False']. 'correct_answer' must be 'True' or 'False'.\n"
        "4. For short_answer: 'options' can be null or empty list. 'correct_answer' is the concise expected answer phrase.\n"
        "5. Include a thorough 'explanation' referencing the source facts.\n\n"
        "Output MUST be a valid JSON array of question objects:\n"
        "[\n"
        "  {\n"
        '    "id": 1,\n'
        '    "type": "multiple_choice",\n'
        '    "question": "Question text?",\n'
        '    "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        '    "correct_answer": "Option A",\n'
        '    "explanation": "Explanation grounded in source text..."\n'
        "  }\n"
        "]\n"
        "Output ONLY raw JSON. No markdown code blocks."
    )

    user_prompt = f"Document ({doc.original_filename}):\n{truncated_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_text = call_llm(messages, temperature=0.3)

    cleaned_json = response_text.strip()
    if cleaned_json.startswith("```json"):
        cleaned_json = cleaned_json[7:]
    if cleaned_json.startswith("```"):
        cleaned_json = cleaned_json[3:]
    if cleaned_json.endswith("```"):
        cleaned_json = cleaned_json[:-3]
    cleaned_json = cleaned_json.strip()

    try:
        questions_data = json.loads(cleaned_json)
        if not isinstance(questions_data, list):
            if isinstance(questions_data, dict) and "questions" in questions_data:
                questions_data = questions_data["questions"]
            else:
                raise ValueError("Expected a list of questions")
    except Exception as e:
        logger.error("Failed to parse quiz questions JSON: %s. Response was: %s", e, response_text[:500])
        raise RuntimeError("Failed to generate valid quiz questions from document.")

    config_data = {
        "num_questions": num_questions,
        "difficulty": difficulty,
        "question_types": question_types,
    }

    quiz = Quiz(
        id=str(uuid.uuid4()),
        document_id=document_id,
        config=json.dumps(config_data),
        questions=json.dumps(questions_data),
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


def get_quiz(quiz_id: str, db: Session) -> Quiz | None:
    """Get a quiz by ID."""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()


def list_quizzes(document_id: str | None, db: Session) -> list[Quiz]:
    """List quizzes."""
    query = db.query(Quiz)
    if document_id:
        query = query.filter(Quiz.document_id == document_id)
    return query.order_by(Quiz.created_at.desc()).all()


def delete_quiz(quiz_id: str, db: Session) -> bool:
    """Delete a quiz by ID."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return False
    db.delete(quiz)
    db.commit()
    return True


def submit_quiz_attempt(
    quiz_id: str,
    answers: dict[str, str],
    db: Session,
) -> QuizAttempt:
    """
    Score a quiz attempt and persist results.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise ValueError(f"Quiz {quiz_id} not found")

    questions: list[dict[str, Any]] = json.loads(quiz.questions)
    correct_count = 0
    total = len(questions)

    detailed_results = []
    for q in questions:
        q_id = str(q.get("id"))
        user_ans = str(answers.get(q_id, "")).strip()
        correct_ans = str(q.get("correct_answer", "")).strip()

        # Compare answers (case-insensitive for short answers / robust matching)
        is_correct = False
        if user_ans.lower() == correct_ans.lower():
            is_correct = True
        elif user_ans and (user_ans in correct_ans or correct_ans in user_ans):
            # For multiple choice with letter prefixes or matching strings
            is_correct = True

        if is_correct:
            correct_count += 1

        detailed_results.append({
            "question_id": q.get("id"),
            "question": q.get("question"),
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score = round((correct_count / total * 100), 1) if total > 0 else 0.0

    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        quiz_id=quiz_id,
        answers=json.dumps(answers),
        score=score,
        total=total,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Attach transient results attribute for response
    setattr(attempt, "results", detailed_results)
    return attempt


def get_quiz_attempts(quiz_id: str, db: Session) -> list[QuizAttempt]:
    """Get all attempts for a quiz."""
    return db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).order_by(QuizAttempt.created_at.desc()).all()
