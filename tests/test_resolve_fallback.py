from pathlib import Path

from baseline_warden.detect.common import Detection
from baseline_warden.index.cache import BaselineLock, LockFeature
from baseline_warden.evaluate.resolve import build_index, resolve_detection


def test_resolve_fallback_html_attribute_to_element() -> None:
    lock = BaselineLock(
        features=[LockFeature(feature_id="a", title="Anchor", status="widely", bcd_keys=["html.elements.a"])]
    )
    index = build_index(lock)
    d = Detection(path=Path("index.html"), line=1, bcd_key="html.elements.a.class")
    feat = resolve_detection(index, d)
    assert feat is not None and feat.feature_id == "a"


def test_resolve_fallback_css_value_to_property() -> None:
    lock = BaselineLock(
        features=[LockFeature(feature_id="font-size", title="font-size", status="widely", bcd_keys=["css.properties.font-size"])]
    )
    index = build_index(lock)
    d = Detection(path=Path("main.css"), line=1, bcd_key="css.properties.font-size.clamp")
    feat = resolve_detection(index, d)
    assert feat is not None and feat.feature_id == "font-size"

