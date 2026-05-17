"""Tests for the OpenRouter LLM provider.

We mock the HTTP layer with httpx.MockTransport so the tests run with no
network and no API key. The point is to verify request construction,
response parsing, and the JSON retry loop — not to actually call OpenRouter.
"""

from __future__ import annotations

import json

import httpx
import pytest
from pydantic import BaseModel

from arr.providers.llm import LLMError, OpenRouterLLM, _strip_code_fences


def _make_llm(handler) -> OpenRouterLLM:
    llm = OpenRouterLLM(api_key="sk-or-test")
    llm._client = httpx.Client(
        base_url="https://openrouter.ai/api/v1",
        transport=httpx.MockTransport(handler),
        headers={"Authorization": "Bearer sk-or-test"},
    )
    return llm


def _completion_response(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={"choices": [{"message": {"role": "assistant", "content": content}}]},
    )


def test_complete_returns_message_content():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["model"] == "anthropic/claude-haiku-4-5"
        assert body["messages"][0]["content"] == "ping"
        return _completion_response("pong")

    with _make_llm(handler) as llm:
        out = llm.complete(
            [{"role": "user", "content": "ping"}],
            "anthropic/claude-haiku-4-5",
        )
    assert out == "pong"


def test_complete_raises_llmerror_on_http_failure():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="boom")

    with _make_llm(handler) as llm:
        with pytest.raises(LLMError):
            llm.complete([{"role": "user", "content": "x"}], "anthropic/claude-haiku-4-5")


def test_complete_raises_llmerror_on_malformed_payload():
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"oops": "no choices"})

    with _make_llm(handler) as llm:
        with pytest.raises(LLMError):
            llm.complete([{"role": "user", "content": "x"}], "anthropic/claude-haiku-4-5")


class _Schema(BaseModel):
    in_scope: bool
    primary_topic: str


def test_complete_json_validates_against_schema():
    def handler(_: httpx.Request) -> httpx.Response:
        return _completion_response('{"in_scope": true, "primary_topic": "rag"}')

    with _make_llm(handler) as llm:
        result = llm.complete_json(
            [{"role": "user", "content": "classify"}],
            "anthropic/claude-haiku-4-5",
            _Schema,
        )
    assert result.in_scope is True
    assert result.primary_topic == "rag"


def test_complete_json_retries_once_then_succeeds():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls.append(body)
        if len(calls) == 1:
            return _completion_response('not json at all')
        return _completion_response('{"in_scope": false, "primary_topic": "other"}')

    with _make_llm(handler) as llm:
        result = llm.complete_json(
            [{"role": "user", "content": "classify"}],
            "anthropic/claude-haiku-4-5",
            _Schema,
        )
    assert result.in_scope is False
    # Second call should include the retry context (assistant + user repair message).
    assert len(calls) == 2
    second_messages = calls[1]["messages"]
    assert any("could not be parsed" in m["content"] for m in second_messages)


def test_complete_json_raises_after_two_failures():
    def handler(_: httpx.Request) -> httpx.Response:
        return _completion_response("still not json")

    with _make_llm(handler) as llm:
        with pytest.raises(LLMError):
            llm.complete_json(
                [{"role": "user", "content": "x"}],
                "anthropic/claude-haiku-4-5",
                _Schema,
            )


def test_strip_code_fences_handles_fenced_json():
    assert _strip_code_fences("```json\n{\"a\": 1}\n```") == '{"a": 1}'
    assert _strip_code_fences("```\n{\"a\": 1}\n```") == '{"a": 1}'
    assert _strip_code_fences('{"a": 1}') == '{"a": 1}'


def test_missing_api_key_raises():
    with pytest.raises(LLMError):
        OpenRouterLLM(api_key="")
