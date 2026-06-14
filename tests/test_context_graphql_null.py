"""Regression tests for fetch_github_event_context GraphQL-null handling.

GitHub's GraphQL API returns ``null`` (not ``{}``) for an absent node - e.g.
``repository.issue`` is ``null`` when the queried number is a PR, or when a
partial error nulls a field. ``dict.get(key, {})`` does NOT guard against a key
that is present with a ``None`` value, so the old code crashed with::

    AttributeError: 'NoneType' object has no attribute 'get'

at ``issue_data.get("comments", {})``. These tests pin the fix: a null node must
degrade gracefully (return context built so far), never raise.
"""

from __future__ import annotations

import json
from unittest.mock import patch

import importlib.util as _ilu
import os as _os

_CTX_PATH = _os.path.join(
    _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
    "strands_coder",
    "context.py",
)
_spec = _ilu.spec_from_file_location("strands_coder_context", _CTX_PATH)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
fetch_github_event_context = _mod.fetch_github_event_context


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _ctx(event_name: str, event: dict) -> str:
    return json.dumps(
        {
            "event_name": event_name,
            "event": event,
            "repository": "owner/repo",
            "actor": "tester",
        }
    )


def test_issue_node_null_does_not_raise(monkeypatch):
    """repository.issue == null (number is actually a PR) must not crash."""
    monkeypatch.setenv("GITHUB_CONTEXT", _ctx("issues", {"issue": {"number": 7}, "action": "opened"}))
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    with patch("requests.post", return_value=_FakeResponse({"data": {"repository": {"issue": None}}})):
        out = fetch_github_event_context()

    assert isinstance(out, str)
    assert "owner/repo" in out  # raw context header still rendered


def test_repository_null_does_not_raise(monkeypatch):
    """data.repository == null (partial error) must not crash."""
    monkeypatch.setenv("GITHUB_CONTEXT", _ctx("issues", {"issue": {"number": 7}, "action": "opened"}))
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    with patch("requests.post", return_value=_FakeResponse({"data": {"repository": None}})):
        out = fetch_github_event_context()

    assert isinstance(out, str)


def test_pull_request_node_null_does_not_raise(monkeypatch):
    """repository.pullRequest == null must not crash."""
    monkeypatch.setenv(
        "GITHUB_CONTEXT",
        _ctx("pull_request", {"pull_request": {"number": 9}, "action": "opened"}),
    )
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    with patch("requests.post", return_value=_FakeResponse({"data": {"repository": {"pullRequest": None}}})):
        out = fetch_github_event_context()

    assert isinstance(out, str)


def test_discussion_node_null_does_not_raise(monkeypatch):
    """repository.discussion == null must not crash."""
    monkeypatch.setenv(
        "GITHUB_CONTEXT",
        _ctx("discussion", {"discussion": {"number": 3}, "action": "created"}),
    )
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    with patch("requests.post", return_value=_FakeResponse({"data": {"repository": {"discussion": None}}})):
        out = fetch_github_event_context()

    assert isinstance(out, str)


def test_null_comment_author_does_not_raise(monkeypatch):
    """A comment whose author is null (deleted user) must not crash."""
    monkeypatch.setenv("GITHUB_CONTEXT", _ctx("issues", {"issue": {"number": 7}, "action": "opened"}))
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    monkeypatch.delenv("PAT_TOKEN", raising=False)

    payload = {
        "data": {
            "repository": {
                "issue": {
                    "comments": {
                        "totalCount": 1,
                        "nodes": [{"author": None, "body": "hi", "createdAt": "2026-01-01"}],
                    },
                    "timelineItems": {"nodes": [{"source": None}]},
                }
            }
        }
    }
    with patch("requests.post", return_value=_FakeResponse(payload)):
        out = fetch_github_event_context()

    assert isinstance(out, str)
    assert "@unknown" in out
