from collections import Counter
from pathlib import Path

from baseline_warden.config import BaselineWardenConfig
from baseline_warden.detect.common import Detection
from baseline_warden.index.cache import BaselineLock, LockFeature
from baseline_warden.evaluate.policy import evaluate_detections
from baseline_warden.evaluate.resolve import build_index


def _lock() -> BaselineLock:
    return BaselineLock(
        features=[
            LockFeature(
                feature_id="feature-widely",
                title="Widely Feature",
                status="widely",
                bcd_keys=["css.properties.display.grid"],
            ),
            LockFeature(
                feature_id="feature-newly",
                title="Newly Feature",
                status="newly",
                bcd_keys=["html.elements.dialog"],
            ),
            LockFeature(
                feature_id="feature-limited",
                title="Limited Feature",
                status="limited",
                bcd_keys=["css.properties.position.sticky"],
            ),
        ]
    )


def test_evaluate_detections_applies_policy() -> None:
    lock = _lock()
    index = build_index(lock)
    config = BaselineWardenConfig()
    detections = [
        Detection(path=Path("a.html"), line=1, bcd_key="html.elements.dialog"),
        Detection(path=Path("b.css"), line=2, bcd_key="css.properties.display.grid"),
        Detection(path=Path("c.css"), line=3, bcd_key="css.properties.position.sticky"),
        Detection(path=Path("d.css"), line=4, bcd_key="css.properties.unknown"),
    ]

    findings, summary = evaluate_detections(index, detections, config)

    outcomes = {f.detection.bcd_key: f.outcome for f in findings}
    assert outcomes["css.properties.display.grid"] == "pass"
    assert outcomes["html.elements.dialog"] == "pass"  # newly default pass
    assert outcomes["css.properties.position.sticky"] == "fail"
    assert outcomes["css.properties.unknown"] == "warn"

    assert summary.total == 4
    assert summary.outcomes["pass"] == 2
    assert summary.outcomes["fail"] == 1
    assert summary.outcomes["warn"] == 1


def test_evaluate_detections_respects_allowlist_and_unknown_behavior() -> None:
    lock = _lock()
    index = build_index(lock)
    config = BaselineWardenConfig()
    config.policy.required_status = "widely"
    config.policy.unknown_behavior = "fail"
    config.allowlist.feature_ids = ["feature-limited"]
    config.allowlist.bcd_keys = ["css.properties.unknown"]

    detections = [
        Detection(path=Path("a"), line=1, bcd_key="css.properties.position.sticky"),
        Detection(path=Path("b"), line=1, bcd_key="css.properties.unknown"),
        Detection(path=Path("c"), line=1, bcd_key="html.elements.dialog"),
    ]

    findings, summary = evaluate_detections(index, detections, config)
    outcomes = {f.detection.bcd_key: f.outcome for f in findings}

    assert outcomes["css.properties.position.sticky"] == "pass"  # allowlisted feature
    assert outcomes["css.properties.unknown"] == "pass"  # allowlisted bcd
    assert outcomes["html.elements.dialog"] == "warn"  # newly but policy requires widely

    assert summary.outcomes == Counter({"pass": 2, "warn": 1})
