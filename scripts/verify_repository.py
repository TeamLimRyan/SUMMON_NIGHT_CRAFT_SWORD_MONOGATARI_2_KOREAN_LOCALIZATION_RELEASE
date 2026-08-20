#!/usr/bin/env python3
"""Verify public patch metadata and forbid ROM, save, and credential files."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STATUS.json"
FORBIDDEN = {".gba", ".sav", ".srm", ".state", ".ss0", ".ss1", ".bios", ".bin"}
SKIP = {".git", "__pycache__"}
REQUIRED = {
    ".gitattributes",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/workflows/repository-integrity.yml",
    ".gitignore",
    "COMPATIBILITY_KO.md",
    "INSTALL_KO.md",
    "NOTICE.md",
    "PATCH_FORMAT.md",
    "README.md",
    "RELEASE_NOTES.md",
    "SHA256SUMS.txt",
    "STATUS.json",
    "SUPPORT_KO.md",
    "TROUBLESHOOTING_KO.md",
    "scripts/apply_patch.py",
    "scripts/verify_repository.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    patch = ROOT / status["patch"]["path"]
    errors: list[str] = []
    missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
    if missing:
        errors.append("missing required files: " + ", ".join(missing))
    if status.get("release_state") not in {"LOCAL_PREPARED", "PUBLISHED"}:
        errors.append("invalid release_state")
    if status.get("repository") != "TeamLimRyan/SUMMON_NIGHT_CRAFT_SWORD_MONOGATARI_2_KOREAN_LOCALIZATION_RELEASE":
        errors.append("repository identity mismatch")
    if not patch.is_file():
        errors.append(f"missing patch: {patch.relative_to(ROOT)}")
    else:
        if patch.stat().st_size != status["patch"]["size"]:
            errors.append("patch size mismatch")
        if sha256_file(patch) != status["patch"]["sha256"]:
            errors.append("patch SHA-256 mismatch")
        if patch.read_bytes()[:4] != bytes.fromhex("D6C3C400"):
            errors.append("xdelta is not headerless VCDIFF")

    sums = (ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8")
    expected_lines = {
        f'{status["patch"]["sha256"]}  {status["patch"]["path"]}',
        f'{status["source"]["sha256"]}  Summon Night - Craft Sword Monogatari 2 (Japan).gba',
        f'{status["target"]["sha256"]}  summon_night_craft_sword_2_ko.gba',
    }
    for line in expected_lines:
        if line not in sums:
            errors.append("SHA256SUMS missing: " + line)

    forbidden: list[str] = []
    oversized: list[str] = []
    for directory, names, filenames in os.walk(ROOT):
        names[:] = [name for name in names if name not in SKIP]
        for filename in filenames:
            path = Path(directory, filename)
            relative = path.relative_to(ROOT).as_posix()
            if path.suffix.lower() in FORBIDDEN:
                forbidden.append(relative)
            if path.stat().st_size > 95 * 1024 * 1024:
                oversized.append(relative)
            if path.suffix.lower() in {".md", ".txt", ".json", ".py", ".yml", ".yaml"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                if ("C:" + "\\sn2\\") in text or ("C:" + "/sn2/") in text:
                    errors.append(f"local workspace path leaked: {relative}")
                if ("gh" + "o_") in text or ("github_" + "pat_") in text:
                    errors.append(f"credential-like text found: {relative}")
    if forbidden:
        errors.append("forbidden files: " + ", ".join(forbidden))
    if oversized:
        errors.append("oversized files: " + ", ".join(oversized))
    if errors:
        raise SystemExit("FAIL\n" + "\n".join(f"- {error}" for error in errors))
    print("PASS: patch metadata matches and no ROM/save/BIOS files are present")


if __name__ == "__main__":
    main()
