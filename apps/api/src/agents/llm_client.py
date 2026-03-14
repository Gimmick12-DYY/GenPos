from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

from openai import AsyncOpenAI

from src.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Async wrapper around OpenAI-compatible chat completions API."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,
    ) -> dict:
        """Send a chat completion request and return parsed response.

        Returns dict with keys: content (str), usage (dict), model (str).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await self._client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }

        return {"content": content, "usage": usage, "model": response.model}

    async def chat_completion_json(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """Send a chat completion and parse the response as JSON.

        Automatically sets ``response_format`` to ``json_object``.
        """
        result = await self.chat_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        raw = result["content"].strip()
        parsed = _parse_json_from_content(raw)
        if parsed is None:
            logger.warning(
                "Failed to parse LLM response as JSON (first 300 chars): %s",
                raw[:300],
            )
            parsed = {"raw_content": raw, "parse_error": True}

        return {"content": parsed, "usage": result["usage"], "model": result["model"]}


def _parse_json_from_content(content: str) -> dict | None:
    """Parse JSON from LLM content, tolerating markdown code blocks or surrounding text."""
    if not content:
        return None
    # Direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # Strip markdown code block
    s = content.strip()
    for marker in ("```json", "```"):
        if s.startswith(marker):
            s = s[len(marker) :].strip()
        if s.endswith("```"):
            s = s[: -3].strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    # Find first { and last } and try to parse that object
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(s[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None

    async def chat_completion_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream chat completion tokens. Yields content string chunks."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        stream = await self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content


llm_client = LLMClient()
