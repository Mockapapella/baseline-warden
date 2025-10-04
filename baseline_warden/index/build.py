"""Build Baseline feature indices from web-features and Web Status data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

import httpx
from pydantic import BaseModel, Field

from .fetch import BaselineInfo, WebStatusFeature
from .cache import LockFeature
from .. import __version__

WEB_FEATURES_URL = "https://unpkg.com/web-features@latest/data.json"
WEB_FEATURES_TIMEOUT = httpx.Timeout(30.0)
USER_AGENT = f"baseline-warden/{__version__}"


class WebFeatureEntry(BaseModel):
    name: Optional[str] = None
    compat_features: List[str] = Field(default_factory=list)
    spec: List[str] = Field(default_factory=list)
    group: Optional[Union[str, List[str]]] = None
    kind: Optional[Union[str, List[str]]] = None
    status: Optional[Any] = None

    model_config = {"extra": "allow"}


class WebFeaturesDataset(BaseModel):
    features: Dict[str, WebFeatureEntry] = Field(default_factory=dict)

    model_config = {"extra": "allow"}


@dataclass
class FeatureMetadata:
    feature_id: str
    name: str
    compat_features: List[str]
    spec_urls: List[str]
    group: Optional[str] = None
    kind: Optional[str] = None
    status: Optional[str] = None


@dataclass
class WebFeaturesIndex:
    features: Dict[str, FeatureMetadata]
    bcd_to_feature: Dict[str, str]


def fetch_web_features_dataset(
    *,
    client: Optional[httpx.Client] = None,
    url: str = WEB_FEATURES_URL,
    timeout: httpx.Timeout = WEB_FEATURES_TIMEOUT,
) -> WebFeaturesDataset:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}

    def _do_request(http_client: httpx.Client) -> WebFeaturesDataset:
        response = http_client.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return WebFeaturesDataset.model_validate_json(response.text)

    if client:
        return _do_request(client)
    with httpx.Client(follow_redirects=True) as http_client:
        return _do_request(http_client)


def build_web_features_index(dataset: WebFeaturesDataset) -> WebFeaturesIndex:
    feature_metadata: Dict[str, FeatureMetadata] = {}
    bcd_to_feature: Dict[str, str] = {}

    for feature_id, entry in dataset.features.items():
        metadata = FeatureMetadata(
            feature_id=feature_id,
            name=entry.name or feature_id,
            compat_features=list(entry.compat_features),
            spec_urls=list(entry.spec),
            group=entry.group,
            kind=entry.kind,
            status=entry.status,
        )
        feature_metadata[feature_id] = metadata

        for bcd_key in entry.compat_features:
            bcd_to_feature.setdefault(bcd_key, feature_id)

    return WebFeaturesIndex(features=feature_metadata, bcd_to_feature=bcd_to_feature)


def assemble_lock_features(
    *,
    index: WebFeaturesIndex,
    baseline_features: Sequence[WebStatusFeature],
) -> List[LockFeature]:
    """Combine feature metadata with baseline status information."""

    baseline_by_id: Dict[str, WebStatusFeature] = {feat.feature_id: feat for feat in baseline_features}
    lock_entries: List[LockFeature] = []

    for feature_id, metadata in index.features.items():
        baseline_feature = baseline_by_id.get(feature_id)
        baseline_info = baseline_feature.baseline if baseline_feature else None
        title = (
            baseline_feature.name
            if baseline_feature and baseline_feature.name
            else metadata.name
        )
        lock_entries.append(
            LockFeature(
                feature_id=feature_id,
                title=title,
                status=baseline_info.status if baseline_info else None,
                low_date=baseline_info.low_date if baseline_info else None,
                high_date=baseline_info.high_date if baseline_info else None,
                bcd_keys=list(metadata.compat_features),
            )
        )

    for feature_id, baseline_feature in baseline_by_id.items():
        if feature_id in index.features:
            continue
        baseline_info = baseline_feature.baseline
        lock_entries.append(
            LockFeature(
                feature_id=feature_id,
                title=baseline_feature.name or feature_id,
                status=baseline_info.status if baseline_info else None,
                low_date=baseline_info.low_date if baseline_info else None,
                high_date=baseline_info.high_date if baseline_info else None,
                bcd_keys=[],
            )
        )

    lock_entries.sort(key=lambda entry: entry.feature_id)
    return lock_entries


__all__ = [
    "FeatureMetadata",
    "WebFeaturesDataset",
    "WebFeaturesIndex",
    "fetch_web_features_dataset",
    "build_web_features_index",
    "assemble_lock_features",
]
