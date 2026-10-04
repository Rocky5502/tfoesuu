from pathlib import Path

from scripts.record_publication_run import sha256


def test_sha256_is_stable(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"tfoesuu\n")
    assert sha256(p) == "69086d5cdea483ce50c206b366956fb029592a8cc7efb99dcebc5c79ff3ba43b"
