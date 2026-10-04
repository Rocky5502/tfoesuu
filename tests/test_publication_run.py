from pathlib import Path

from scripts.record_publication_run import sha256


def test_sha256_is_stable(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"tfoesuu\n")
    assert sha256(p) == "e9e7183b3452aead21e3bbf4b99d0c96d67bffb37a453c9e24b40e27fd55f034"
