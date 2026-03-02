"""
generate.py -- Wrapper for calling Claude via the Anthropic API.

This module provides two functions for interacting with Claude:
  - call_claude: returns the text response
  - call_claude_with_usage: returns the text response plus token usage metadata

Usage:
    from src.s0_generation.generate import call_claude, call_claude_with_usage

    answer = call_claude("What is prompt engineering?")
    result = call_claude_with_usage("What is prompt engineering?")
"""

import anthropic
from dotenv import load_dotenv

load_dotenv()


def call_claude(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: str = "claude-sonnet-4-5",
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> str:
    """Send a single user message to Claude and return the text response.

    Args:
        prompt: The user message to send.
        system_prompt: System-level instruction for Claude.
        model: Model alias to use (default: claude-sonnet-4-5).
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = default).

    Returns:
        The text content of Claude's response.
    """
    client = anthropic.Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


def call_claude_with_usage(prompt: str, **kwargs) -> dict:
    """Send a message to Claude and return the response with usage metadata.

    Accepts the same parameters as call_claude via **kwargs.

    Args:
        prompt: The user message to send.
        **kwargs: Forwarded to call_claude (system_prompt, model, max_tokens, temperature).

    Returns:
        A dict containing:
            - text: The response text.
            - input_tokens: Tokens used by the prompt.
            - output_tokens: Tokens used by the response.
            - model: The model that handled the request.
            - stop_reason: Why the model stopped generating (e.g. "end_turn").
    """
    client = anthropic.Anthropic()

    system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")
    model = kwargs.get("model", "claude-sonnet-4-5")
    max_tokens = kwargs.get("max_tokens", 1024)
    temperature = kwargs.get("temperature", 1.0)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": response.model,
        "stop_reason": response.stop_reason,
    }
