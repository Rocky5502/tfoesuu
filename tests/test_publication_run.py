from pathlib import Path

from tfoesuu.provenance import sha256_file, sha256_lf_normalized_text


def test_sha256_is_stable(tmp_path: Path):
    p = tmp_path / "x.txt"
    p.write_bytes(b"tfoesuu\n")
    assert sha256_file(p) == "69086d5cdea483ce50c206b366956fb029592a8cc7efb99dcebc5c79ff3ba43b"


def test_lf_normalized_sha256_is_portable_across_line_endings(tmp_path: Path):
    lf = tmp_path / "lf.jsonl"
    crlf = tmp_path / "crlf.jsonl"
    cr = tmp_path / "cr.jsonl"
    lf.write_bytes(b'{"id":1}\n{"id":2}\n')
    crlf.write_bytes(b'{"id":1}\r\n{"id":2}\r\n')
    cr.write_bytes(b'{"id":1}\r{"id":2}\r')

    normalized = sha256_lf_normalized_text(lf)
    assert sha256_lf_normalized_text(crlf) == normalized
    assert sha256_lf_normalized_text(cr) == normalized
    assert sha256_file(crlf) != sha256_file(lf)
