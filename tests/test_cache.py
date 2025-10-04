from pathlib import Path

from baseline_warden.index.cache import BaselineLock, LockFeature, load_lock, write_lock


def test_lock_roundtrip(tmp_path: Path) -> None:
    feature = LockFeature(
        feature_id="css.selectors.has",
        title=":has() relational selector",
        status="widely",
        bcd_keys=["css.selectors.has"],
    )
    lock = BaselineLock(features=[feature])

    path = tmp_path / "baseline.lock.json"
    write_lock(path, lock)

    assert path.exists()

    loaded = load_lock(path)

    assert loaded.feature_count == 1
    assert loaded.features[0].feature_id == feature.feature_id
    assert loaded.generated_at.tzinfo is not None
