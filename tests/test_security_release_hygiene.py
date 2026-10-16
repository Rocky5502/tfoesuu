"""Static regression checks for security-sensitive local orchestration contracts.

These tests deliberately read the repository's versioned source, not the
contents of a user's private SSH configuration or local environment.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_replication_script_requires_preverified_uv() -> None:
    text = (ROOT / "scripts" / "pc2_replicate_fairlearn_v2.sh").read_text(
        encoding="utf-8"
    )
    assert '[[ -x "$uv_root/uv" ]]' in text
    assert 'uv 0.12.20' in text
    assert 'Unexpected uv version' in text
    assert "curl --proto" not in text
    assert "command -v curl" not in text
    assert "uv-installer.sh" not in text


def test_ssh_dispatcher_has_no_hardcoded_endpoint() -> None:
    text = (ROOT / "scripts" / "pc1_dispatch_pc2.ps1").read_text(
        encoding="utf-8"
    )
    assert "$env:TFOESUU_PC2_HOST" in text
    assert "$env:TFOESUU_PC2_USER" in text
    assert "Set TFOESUU_PC2_HOST and TFOESUU_PC2_USER" in text
    assert '[string]$PC2Host = "192.' not in text
    assert '[string]$RemoteUser = "Administrator"' not in text
