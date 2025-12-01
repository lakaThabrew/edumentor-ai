"""
Simple error utilities for sanitizing exceptions before showing to users.
"""
import re
from typing import Optional


def _extract_retry_seconds(text: str) -> Optional[int]:
    try:
        m = re.search(r'retry in (\d+(?:\.\d+)?)s', text)
        if m:
            return int(float(m.group(1)))
    except Exception:
        return None
    return None


def format_error(exc: Exception) -> str:
    """
    Turn exceptions into concise, user-friendly messages.

    - For API quota (RESOURCE_EXHAUSTED / 429) errors return a short retry message.
    - For other exceptions return a short generic message without stack traces.
    """
    text = str(exc)

    # Handle Google API quota errors (RESOURCE_EXHAUSTED / 429)
    if 'RESOURCE_EXHAUSTED' in text or '429' in text or 'quota' in text.lower():
        retry = _extract_retry_seconds(text)
        if retry:
            return f"The language API quota was exceeded. Please try again in ~{retry} seconds."
        return "The language API quota was exceeded. Please check your API key / billing or try again later."

    # Fallback: show a short generic error message
    # Avoid including full exception text which may contain sensitive or verbose info
    return "An internal error occurred while processing your request. Please try again or rephrase your question." + text[:100]  # Include first 100 chars for context
