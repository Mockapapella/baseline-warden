from __future__ import annotations

import json
from typing import Dict, List

import httpx
import pytest

from baseline_warden.index.fetch import FetchResult, fetch_features


def test_fetch_features_paginates_and_accumulates() -> None:
    calls: List[Dict[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        calls.append(params)
        if "page_token" not in params:
            body = {
                "data": [
                    {
                        "feature_id": "a",
                        "name": "Feature A",
                        "baseline": {"status": "widely", "low_date": "2020-01-01"},
                        "spec": {"links": [{"link": "https://spec.example/a"}]},
                    },
                    {
                        "feature_id": "b",
                        "name": "Feature B",
                        "baseline": {"status": "newly", "low_date": "2024-05-01"},
                        "spec": {"links": []},
                    },
                ],
                "metadata": {"next_page_token": "token-2", "total": 3},
            }
        else:
            assert params["page_token"] == "token-2"
            body = {
                "data": [
                    {
                        "feature_id": "c",
                        "name": "Feature C",
                        "baseline": {"status": "limited", "low_date": "2025-01-01"},
                        "spec": {"links": []},
                    }
                ],
                "metadata": {"next_page_token": None, "total": 3},
            }
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        result = fetch_features(client=client)

    assert isinstance(result, FetchResult)
    assert len(result.features) == 3
    assert result.total == 3
    assert calls[0]["q"].startswith("baseline_status:widely")
    assert "page_token" not in calls[0]
    assert calls[1]["page_token"] == "token-2"


def test_fetch_features_custom_statuses_and_headers() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        params = dict(request.url.params)
        assert params["q"] == "baseline_status:newly OR baseline_status:widely"
        assert request.headers["accept"] == "application/json"
        assert request.headers["user-agent"].startswith("baseline-warden/")
        body = {
            "data": [
                {
                    "feature_id": "d",
                    "name": "Feature D",
                    "baseline": {"status": "widely", "low_date": "2023-01-01"},
                    "spec": {"links": []},
                }
            ],
            "metadata": {"next_page_token": None, "total": 1},
        }
        return httpx.Response(200, json=body)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        result = fetch_features(statuses=["newly", "widely", "newly"], client=client)

    assert len(result.features) == 1
    assert result.features[0].feature_id == "d"


def test_fetch_features_requires_statuses_or_query() -> None:
    with pytest.raises(ValueError):
        fetch_features(statuses=[], query=None)
