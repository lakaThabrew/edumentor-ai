import asyncio
from typing import Any
from google.genai import types


async def async_chat(client: Any, model: str, system_prompt: str, user_prompt: str,
                     temperature: float = 0.7, max_output_tokens: int = 800) -> str:
    """Call GenAI chat.create in a thread and return a best-effort text result.

    This helper wraps the synchronous client.chat.create in asyncio.to_thread and
    attempts several common response shapes to extract a sensible text string.
    """
    # Build a combined prompt for clients that accept a single string input
    full_prompt = "".join([p for p in [system_prompt, "\n\n", user_prompt] if p])

    # Try multiple client APIs in a best-effort order
    # 1) Preferred: client.chats.create(...) (some versions expose `chats`)
    if hasattr(client, "chats") and hasattr(client.chats, "create"):
        try:
            response = await asyncio.to_thread(
                client.chats.create,
                model=model,
                messages=[
                    {"author": "system", "content": system_prompt or ""},
                    {"author": "user", "content": user_prompt or ""},
                ],
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            return _extract_response_text(response)
        except Exception as e:
            # If the client supports chats.create but it failed at runtime,
            # surface the real error instead of silently falling back.
            raise

    # Also try singular chat.create if present
    if hasattr(client, "chat") and hasattr(client.chat, "create"):
        try:
            response = await asyncio.to_thread(
                client.chat.create,
                model=model,
                messages=[
                    {"author": "system", "content": system_prompt or ""},
                    {"author": "user", "content": user_prompt or ""},
                ],
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            return _extract_response_text(response)
        except Exception as e:
            # Surface runtime errors from a supported API
            raise

    # 2) Older simpler APIs that accept a single prompt string
    # try client.generate_text
    if hasattr(client, "generate_text"):
        try:
            response = await asyncio.to_thread(
                client.generate_text,
                model=model,
                prompt=full_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            return _extract_response_text(response)
        except Exception as e:
            raise

    # 3) generic client.generate
    if hasattr(client, "generate"):
        try:
            response = await asyncio.to_thread(
                client.generate,
                model=model,
                prompt=full_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            return _extract_response_text(response)
        except Exception as e:
            raise

    # 4) client.models.generate_text or client.models.generate_content
    models_ns = getattr(client, "models", None)
    if models_ns is not None:
        # try generate_text
        if hasattr(models_ns, "generate_text"):
            try:
                response = await asyncio.to_thread(
                    models_ns.generate_text,
                    model=model,
                    prompt=full_prompt,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
                return _extract_response_text(response)
            except Exception as e:
                raise

        # try generate_content (legacy) with 'contents' arg
        if hasattr(models_ns, "generate_content"):
            try:
                # Use GenerateContentConfig when available to pass temperature/max tokens
                cfg = types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )
                response = await asyncio.to_thread(
                    models_ns.generate_content,
                    model=model,
                    contents=full_prompt,
                    config=cfg,
                )
                return _extract_response_text(response)
            except Exception as e:
                raise

    # If we reach here, none of the known client methods worked
    raise AttributeError("No supported text-generation method found on provided client")


def _extract_response_text(response: Any) -> str:
    """Try multiple common response shapes to return a text string.

    The GenAI client and response objects change between releases; this helper
    inspects likely attributes in order and falls back to str(response).
    """
    # 1) direct simple text attribute
    try:
        if hasattr(response, "text") and isinstance(response.text, str):
            return response.text
    except Exception:
        pass

    # 2) output_text (sometimes present)
    try:
        if hasattr(response, "output_text") and isinstance(response.output_text, str):
            return response.output_text
    except Exception:
        pass

    # 3) choices -> message -> content
    try:
        choices = getattr(response, "choices", None)
        if choices:
            first = choices[0]
            # message could be a string or object
            msg = getattr(first, "message", None)
            if isinstance(msg, str):
                return msg
            if msg is not None:
                content = getattr(msg, "content", None)
                if isinstance(content, str):
                    return content
                if isinstance(content, list) and content:
                    c0 = content[0]
                    if isinstance(c0, str):
                        return c0
                    if isinstance(c0, dict):
                        return c0.get("text") or c0.get("content") or str(c0)
                    if hasattr(c0, "text"):
                        return getattr(c0, "text")
    except Exception:
        pass

    # 4) output -> content list
    try:
        output = getattr(response, "output", None)
        if output and len(output) > 0:
            first = output[0]
            if isinstance(first, dict):
                cont = first.get("content")
                if isinstance(cont, str):
                    return cont
                if isinstance(cont, list) and cont:
                    c0 = cont[0]
                    if isinstance(c0, str):
                        return c0
                    if isinstance(c0, dict):
                        return c0.get("text") or c0.get("content") or str(c0)
                    if hasattr(c0, "text"):
                        return getattr(c0, "text")
    except Exception:
        pass

    # Last resort
    try:
        return str(response)
    except Exception:
        return ""
