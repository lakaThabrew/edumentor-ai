"""
GenAI Utilities - Simplified async wrapper for Google GenAI API
"""

import asyncio
from typing import Any
from google.genai import types


async def async_chat(client: Any, model: str, system_prompt: str, user_prompt: str,
                     temperature: float = 0.7, max_output_tokens: int = 800) -> str:
    """Call GenAI models.generate_content in a thread and return the text result.

    Args:
        client: GenAI Client instance
        model: Model name (e.g., 'gemini-2.0-flash')
        system_prompt: System instruction for the model
        user_prompt: User's query/prompt
        temperature: Sampling temperature (0.0 to 1.0)
        max_output_tokens: Maximum tokens in response

    Returns:
        Generated text response from the model
    """
    
    # Use client.models.generate_content (modern google-genai SDK)
    if hasattr(client, "models") and hasattr(client.models, "generate_content"):
        try:
            # Build configuration
            config_kwargs = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
            if system_prompt:
                config_kwargs["system_instruction"] = system_prompt
            
            cfg = types.GenerateContentConfig(**config_kwargs)
            
            # Call generate_content in a thread to not block async loop
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=model,
                contents=user_prompt,
                config=cfg,
            )
            
            # Extract text from response
            text = _extract_response_text(response)
            if text:
                return text
            
            # If no text extracted, return diagnostic
            return (
                "[No model output captured] The API call succeeded but no text was returned. "
                "Check your API key and model name."
            )
        except Exception as e:
            # Re-raise the exception to be handled by caller
            raise

    # If we reach here, the client doesn't have the expected API
    raise AttributeError("No supported text-generation method found on provided client. "
                         "Ensure you're using google-genai >= 0.4.0")


def _extract_response_text(response: Any) -> str:
    """Extract text from GenAI response object.

    The GenAI response objects may have different structures; this helper
    tries multiple common patterns to extract the generated text.
    
    Args:
        response: Response object from generate_content
        
    Returns:
        Extracted text string, or empty string if extraction fails
    """
    # 1) Direct .text attribute (most common for GenerateContentResponse)
    try:
        if hasattr(response, "text") and response.text:
            return response.text
    except Exception:
        pass

    # 2) candidates[0].content.parts[0].text (detailed response structure)
    try:
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                content = candidate.content
                if hasattr(content, "parts") and content.parts:
                    for part in content.parts:
                        if hasattr(part, "text") and part.text:
                            return part.text
    except Exception:
        pass

    # 3) Check for parts directly on response
    try:
        if hasattr(response, "parts") and response.parts:
            for part in response.parts:
                if hasattr(part, "text") and part.text:
                    return part.text
    except Exception:
        pass

    # 4) output_text attribute (some versions)
    try:
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text
    except Exception:
        pass

    # 5) Last resort: stringify the response
    try:
        result = str(response)
        # Avoid returning object repr strings
        if result and not result.startswith("<"):
            return result
    except Exception:
        pass

    return ""
