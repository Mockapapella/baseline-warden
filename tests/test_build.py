from baseline_warden.index.build import (
    WebFeaturesDataset,
    assemble_lock_features,
    build_web_features_index,
)
from baseline_warden.index.fetch import BaselineInfo, SpecInfo, SpecLink, WebStatusFeature


def _dataset() -> WebFeaturesDataset:
    return WebFeaturesDataset.model_validate(
        {
            "features": {
                "feature-a": {
                    "name": "Feature A",
                    "compat_features": ["css.properties.feature-a", "api.FeatureA"],
                    "spec": ["https://example.com/spec-a"],
                    "group": "css",
                    "kind": "css",
                },
                "feature-b": {
                    "name": "Feature B",
                    "compat_features": ["css.properties.feature-b"],
                    "spec": ["https://example.com/spec-b"],
                    "group": "css",
                    "kind": "css",
                },
                "feature-c": {
                    "name": "Feature C",
                    "compat_features": ["css.properties.shared"],
                    "spec": [],
                },
            }
        }
    )


def test_build_web_features_index_creates_metadata_and_bcd_map() -> None:
    dataset = _dataset()
    index = build_web_features_index(dataset)

    assert "feature-a" in index.features
    assert index.features["feature-a"].spec_urls == ["https://example.com/spec-a"]
    assert index.bcd_to_feature["css.properties.feature-a"] == "feature-a"
    # ensure first registration wins when duplicates occur
    assert index.bcd_to_feature["css.properties.shared"] == "feature-c"


def test_assemble_lock_features_merges_baseline_data() -> None:
    dataset = _dataset()
    index = build_web_features_index(dataset)
    baseline_features = [
        WebStatusFeature(
            feature_id="feature-a",
            name="Feature A Baseline",
            baseline=BaselineInfo(status="widely", low_date="2023-01-01"),
            spec=SpecInfo(links=[SpecLink(link="https://status.example/a")]),
        ),
        WebStatusFeature(
            feature_id="feature-d",
            name="Feature D",
            baseline=BaselineInfo(status="limited", low_date="2024-02-02"),
            spec=SpecInfo(links=[SpecLink(link="https://status.example/d")]),
        ),
    ]

    entries = assemble_lock_features(index=index, baseline_features=baseline_features)

    feature_ids = [entry.feature_id for entry in entries]
    assert feature_ids == sorted(set(feature_ids))
    assert "feature-a" in feature_ids
    assert "feature-d" in feature_ids

    feature_a = next(entry for entry in entries if entry.feature_id == "feature-a")
    assert feature_a.title == "Feature A Baseline"
    assert feature_a.bcd_keys == ["css.properties.feature-a", "api.FeatureA"]
    assert feature_a.status == "widely"

    feature_d = next(entry for entry in entries if entry.feature_id == "feature-d")
    assert feature_d.bcd_keys == []
    assert feature_d.status == "limited"
