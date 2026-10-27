"""LLM provider service using Groq API with automatic model discovery, rate-limit protection, and fallback."""

from __future__ import annotations

import logging
import time
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Cache the active working model
_active_model: str | None = None

# Max characters in prompt to stay well under Groq 7,000 input token rate limit
# (Roughly 1 token ~= 3.5 to 4 chars; 10,000 chars ~= 2,500 tokens)
MAX_PROMPT_CHARS = 10000


def _get_client():
    """Create a Groq client. Returns None if API key is not set."""
    key = settings.GROQ_API_KEY.strip("\"' ")
    if not key:
        return None
    from groq import Groq
    return Groq(api_key=key)


def _resolve_working_model(client) -> str:
    """Discover available models on the user's Groq key and pick the best one."""
    global _active_model
    if _active_model:
        return _active_model

    preferred_models = [
        "qwen/qwen3.8-27b",
        "allam-2-7b",
        settings.LLM_MODEL,
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]

    try:
        models_list = client.models.list()
        available_ids = [m.id for m in models_list.data]
        logger.info("Available Groq models on account: %s", available_ids)

        for pm in preferred_models:
            if pm in available_ids:
                _active_model = pm
                logger.info("Selected active Groq model: %s", _active_model)
                return _active_model

        for m_id in available_ids:
            if "whisper" not in m_id and "guard" not in m_id and "gpt-oss" not in m_id:
                _active_model = m_id
                logger.info("Fallback active Groq model: %s", _active_model)
                return _active_model

        if available_ids:
            _active_model = available_ids[0]
            return _active_model
    except Exception as e:
        logger.warning("Could not query Groq models list: %s", e)

    return settings.LLM_MODEL or "qwen/qwen3.8-27b"


def _truncate_messages(messages: list[dict[str, str]], max_total_chars: int = MAX_PROMPT_CHARS) -> list[dict[str, str]]:
    """Ensure total characters across all messages do not exceed max_total_chars."""
    total_len = sum(len(m.get("content", "")) for m in messages)
    if total_len <= max_total_chars:
        return messages

    # Truncate the largest message (typically the document content in the user message)
    new_messages = [dict(m) for m in messages]
    largest_idx = max(range(len(new_messages)), key=lambda i: len(new_messages[i].get("content", "")))
    excess = total_len - max_total_chars
    content = new_messages[largest_idx].get("content", "")
    if len(content) > excess + 500:
        new_messages[largest_idx]["content"] = (
            content[: len(content) - excess - 100] + "\n\n[... content truncated to fit token limits ...]"
        )
    else:
        new_messages[largest_idx]["content"] = content[:max(500, max_total_chars // 2)]

    return new_messages


def call_llm(
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2048,
    model: str | None = None,
) -> str:
    """
    Call the LLM with the given messages, rate-limit protection, and automatic fallback.

    Args:
        messages: List of message dicts with 'role' and 'content'.
        temperature: Sampling temperature.
        max_tokens: Maximum tokens in the response.
        model: Override the default model.

    Returns:
        The assistant's response text.
    """
    client = _get_client()
    if client is None:
        raise ValueError(
            "GROQ_API_KEY is not set. Please configure it in your backend/.env file. "
            "Get a free API key at https://console.groq.com/"
        )

    used_model = model or _resolve_working_model(client)
    safe_messages = _truncate_messages(messages, MAX_PROMPT_CHARS)

    def _execute_call(m_name: str, msgs: list[dict[str, str]], m_tokens: int) -> str:
        resp = client.chat.completions.create(
            model=m_name,
            messages=msgs,
            temperature=temperature,
            max_tokens=m_tokens,
        )
        ch = resp.choices[0]
        txt = ch.message.content
        if not txt and hasattr(ch.message, "reasoning") and ch.message.reasoning:
            txt = ch.message.reasoning
        return (txt or "").strip()

    try:
        return _execute_call(used_model, safe_messages, max_tokens)
    except Exception as e:
        err_str = str(e)
        logger.warning("LLM call with %s failed: %s. Initiating smart recovery...", used_model, err_str)

        # Case 1: 413 Request too large / token limit exceeded
        if "413" in err_str or "too large" in err_str.lower() or "limit" in err_str.lower():
            logger.info("Applying aggressive 50% truncation and retrying...")
            try:
                aggressive_messages = _truncate_messages(messages, max_total_chars=5000)
                return _execute_call(used_model, aggressive_messages, min(max_tokens, 1500))
            except Exception as retry_err:
                logger.warning("Aggressive truncation retry failed: %s", retry_err)

        # Case 2: 429 Rate limit / ITPM exceeded
        if "429" in err_str or "rate_limit" in err_str.lower():
            logger.info("Rate limit hit. Waiting 3 seconds before retry...")
            time.sleep(3)
            try:
                reduced_messages = _truncate_messages(messages, max_total_chars=5000)
                return _execute_call(used_model, reduced_messages, min(max_tokens, 1500))
            except Exception as retry_err:
                logger.warning("Rate-limit retry failed: %s", retry_err)

        # Fallback to secondary model candidate if primary model is failing
        fallback_model = "allam-2-7b" if used_model != "allam-2-7b" else "qwen/qwen3.8-27b"
        try:
            logger.info("Attempting final fallback to model: %s", fallback_model)
            fallback_msgs = _truncate_messages(messages, max_total_chars=5000)
            return _execute_call(fallback_model, fallback_msgs, min(max_tokens, 1500))
        except Exception as fallback_err:
            logger.error("All LLM fallbacks failed: %s", fallback_err)
            raise RuntimeError(f"LLM API call failed: {err_str}") from e


def call_llm_safe(
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2048,
    model: str | None = None,
) -> tuple[str, str | None]:
    """
    Call the LLM, returning (response, error).
    """
    try:
        result = call_llm(messages, temperature, max_tokens, model)
        return result, None
    except (ValueError, RuntimeError) as e:
        return "", str(e)
