import os

import pytest

from yocal_rules import calfacts, cli

pytestmark = pytest.mark.skipif(not os.path.exists(calfacts.DEFAULT_DB), reason="calendar DB not built")


def _run(tmp_path, date):
    assert cli.main(["weekend", date, "--no-compare", "--out", str(tmp_path)]) == 0
    return {p.name for p in tmp_path.iterdir()}


@pytest.mark.parametrize("date", ["2026-10-31", "2026-11-01", "2026-10-28"])
def test_weekend_resolves_to_saturday_and_writes_files(tmp_path, date):
    names = _run(tmp_path, date)
    assert "2026-10-31-weekend.md" in names
    for s in ("vespers", "matins", "liturgy"):
        assert f"{'2026-10-31' if s == 'vespers' else '2026-11-01'}-{s}.md" in names
        assert f"{'2026-10-31' if s == 'vespers' else '2026-11-01'}-{s}-supplement.md" in names


def test_weekend_combined_has_three_services_one_h1(tmp_path):
    _run(tmp_path, "2026-10-31")
    text = (tmp_path / "2026-10-31-weekend.md").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert sum(1 for ln in lines if ln.startswith("# ")) == 1
    for h in ("## Great Vespers", "## Matins", "## Divine Liturgy"):
        assert any(ln.startswith(h) for ln in lines)


def test_existing_service_form_still_works(tmp_path):
    assert cli.main(["2026-11-01", "liturgy", "--no-compare", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "2026-11-01-liturgy.md").exists()
