"""Client for the Web Status Baseline API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Sequence

import httpx
from pydantic import BaseModel, Field

from .. import __version__

BASE_URL = "https://api.webstatus.dev/v1/features"
DEFAULT_TIMEOUT = httpx.Timeout(30.0)
DEFAULT_STATUSES = ("widely", "newly", "limited")
USER_AGENT = f"baseline-warden/{__version__}"


class BaselineInfo(BaseModel):
    status: Optional[str] = None
    low_date: Optional[str] = None
    high_date: Optional[str] = Field(default=None, alias="high_date")


class SpecLink(BaseModel):
    link: str


class SpecInfo(BaseModel):
    links: List[SpecLink] = Field(default_factory=list)


class WebStatusFeature(BaseModel):
    feature_id: str
    name: Optional[str] = None
    baseline: Optional[BaselineInfo] = None
    spec: Optional[SpecInfo] = None

    model_config = {"extra": "allow"}


class Metadata(BaseModel):
    next_page_token: Optional[str] = None
    total: Optional[int] = None


class FeaturesResponse(BaseModel):
    data: List[WebStatusFeature]
    metadata: Metadata


@dataclass
class FetchResult:
    features: List[WebStatusFeature]
    total: Optional[int]


def _build_query(statuses: Iterable[str]) -> str:
    parts = [f"baseline_status:{status}" for status in statuses]
    if not parts:
        raise ValueError("At least one status must be provided")
    return " OR ".join(parts)


def fetch_features(
    *,
    statuses: Sequence[str] = DEFAULT_STATUSES,
    query: Optional[str] = None,
    client: Optional[httpx.Client] = None,
    base_url: str = BASE_URL,
    timeout: httpx.Timeout = DEFAULT_TIMEOUT,
) -> FetchResult:
    """Fetch features from the Web Status API with pagination."""

    effective_query = query or _build_query(dict.fromkeys(statuses))
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    collected: List[WebStatusFeature] = []
    next_token: Optional[str] = None
    total: Optional[int] = None

    def _request_loop(http_client: httpx.Client) -> None:
        nonlocal next_token, total
        while True:
            params = {"q": effective_query}
            if next_token:
                params["page_token"] = next_token
            response = http_client.get(base_url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            payload = FeaturesResponse.model_validate_json(response.text)
            collected.extend(payload.data)
            total = payload.metadata.total
            next_token = payload.metadata.next_page_token
            if not next_token:
                break

    if client:
        _request_loop(client)
    else:
        with httpx.Client() as http_client:
            _request_loop(http_client)

    return FetchResult(features=collected, total=total)


__all__ = ["fetch_features", "FetchResult", "WebStatusFeature", "BaselineInfo", "SpecInfo", "SpecLink"]
