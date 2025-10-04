"""Resolve detections against Baseline lock data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ..detect.common import Detection
from ..index.cache import BaselineLock, LockFeature


@dataclass
class BaselineIndex:
    features_by_id: Dict[str, LockFeature]
    features_by_bcd: Dict[str, LockFeature]


def build_index(lock: BaselineLock) -> BaselineIndex:
    features_by_id: Dict[str, LockFeature] = {}
    features_by_bcd: Dict[str, LockFeature] = {}

    for feature in lock.features:
        features_by_id[feature.feature_id] = feature
        for key in feature.bcd_keys:
            features_by_bcd.setdefault(key, feature)

    return BaselineIndex(features_by_id=features_by_id, features_by_bcd=features_by_bcd)


def resolve_detection(index: BaselineIndex, detection: Detection) -> Optional[LockFeature]:
    """Return the lock feature associated with the detection, if any."""
    key = detection.bcd_key
    feat = index.features_by_bcd.get(key)
    if feat is not None:
        return feat
    # Fallbacks: degrade attribute/value-specific keys to their base when unmapped
    # html.elements.<tag>.<attr> -> html.elements.<tag>
    if key.startswith("html.elements."):
        parts = key.split(".")
        if len(parts) >= 4:  # html, elements, tag, attr
            base = ".".join(parts[:3])
            return index.features_by_bcd.get(base)
    # css.properties.<name>.<value> -> css.properties.<name>
    if key.startswith("css.properties."):
        parts = key.split(".")
        if len(parts) >= 4:
            base = ".".join(parts[:3])
            return index.features_by_bcd.get(base)
    return None


__all__ = ["BaselineIndex", "build_index", "resolve_detection"]
