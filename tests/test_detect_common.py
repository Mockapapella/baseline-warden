from pathlib import Path

from baseline_warden.detect.common import Detection, iter_included_files


def test_iter_included_files_respects_patterns(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.html").write_text("")
    (tmp_path / "src" / "ignore.html").write_text("")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "lib.html").write_text("")

    files = list(
        iter_included_files(
            tmp_path,
            include_patterns=["src/**/*.html", "node_modules/**/*.html"],
            ignore_patterns=["src/ignore.html", "node_modules/**"],
            extensions={".html"},
        )
    )

    assert len(files) == 1
    assert files[0].name == "index.html"
