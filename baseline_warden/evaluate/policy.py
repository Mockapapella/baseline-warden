"""Policy evaluation for Baseline detections."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List, Literal, Optional

from ..config import BaselineWardenConfig
from ..detect.common import Detection
from ..index.cache import LockFeature
from .resolve import BaselineIndex, resolve_detection

Outcome = Literal["pass", "warn", "fail"]
Severity = Literal["info", "warning", "error"]


@dataclass
class Finding:
    detection: Detection
    feature: Optional[LockFeature]
    status: str
    outcome: Outcome
    severity: Severity
    message: str
    allowlisted: bool = False


@dataclass
class EvaluationSummary:
    total: int
    outcomes: Counter
    statuses: Counter

    def has_failures(self) -> bool:
        return self.outcomes.get("fail", 0) > 0


STATUS_UNKNOWN = "unknown"
SEVERITY_BY_OUTCOME = {"pass": "info", "warn": "warning", "fail": "error"}


def evaluate_detections(
    index: BaselineIndex,
    detections: Iterable[Detection],
    config: BaselineWardenConfig,
) -> tuple[List[Finding], EvaluationSummary]:
    findings: List[Finding] = []
    outcome_counter: Counter = Counter()
    status_counter: Counter = Counter()
    allowlist_features = set(config.allowlist.feature_ids)
    allowlist_bcd = set(config.allowlist.bcd_keys)

    for detection in detections:
        feature = resolve_detection(index, detection)
        status = feature.status if feature and feature.status else STATUS_UNKNOWN
        allowlisted = False

        if detection.bcd_key in allowlist_bcd or (feature and feature.feature_id in allowlist_features):
            outcome: Outcome = "pass"
            message = "Allowlisted feature"
            allowlisted = True
        else:
            outcome, message = _evaluate_status(status, config)

        severity: Severity = SEVERITY_BY_OUTCOME[outcome]
        findings.append(
            Finding(
                detection=detection,
                feature=feature,
                status=status,
                outcome=outcome,
                severity=severity,
                message=message,
                allowlisted=allowlisted,
            )
        )
        outcome_counter[outcome] += 1
        status_counter[status] += 1

    summary = EvaluationSummary(total=len(findings), outcomes=outcome_counter, statuses=status_counter)
    return findings, summary


def _evaluate_status(status: str, config: BaselineWardenConfig) -> tuple[Outcome, str]:
    required_status = config.policy.required_status
    unknown_behavior = config.policy.unknown_behavior

    if status == "limited":
        return "fail", "Feature baseline status is limited"

    if status == "widely":
        return "pass", "Feature is widely available"

    if status == "newly":
        if required_status == "widely":
            return "warn", "Feature is newly available (policy requires widely)"
        return "pass", "Feature is newly available"

    # unknown handling
    if unknown_behavior == "fail":
        return "fail", "Feature mapping is unknown"
    if unknown_behavior == "ignore":
        return "pass", "Feature mapping is unknown (ignored)"
    return "warn", "Feature mapping is unknown"


__all__ = ["Finding", "EvaluationSummary", "evaluate_detections"]
