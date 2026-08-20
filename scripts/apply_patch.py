#!/usr/bin/env python3
"""Apply the supported xdelta patch and verify all relevant hashes."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "Summon_Night_Craft_Sword_Monogatari_2_KO.xdelta"
SOURCE_SIZE = 16_777_216
SOURCE_SHA256 = "9abbff51004531eb0f9ee4c15af5b53db7ffe5e9c47e1e225488c576db64360f"
PATCH_SIZE = 1_486_587
PATCH_SHA256 = "e4717aae681e55b0906615382197005bc4cdbe211298436a7d5ca1e336fa285f"
TARGET_SIZE = 33_554_432
TARGET_SHA256 = "5114235cb138ad3707da7750fd86c776b9c18b629bba2dcf0299159a6eba5300"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_file(path: Path, size: int, digest: str, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"{label} 파일이 없습니다: {path}")
    actual_size = path.stat().st_size
    actual_digest = sha256_file(path)
    if actual_size != size or actual_digest != digest:
        raise SystemExit(
            f"{label} 검증 실패\n"
            f"  경로: {path}\n"
            f"  크기: {actual_size} (예상 {size})\n"
            f"  SHA-256: {actual_digest}\n"
            f"  예상값: {digest}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="서몬나이트 크래프트 소드 이야기 2 한국어 xdelta 적용기")
    parser.add_argument("source", type=Path, help="지원 대상 일본판 원본 ROM")
    parser.add_argument("output", type=Path, nargs="?", default=Path("summon_night_craft_sword_2_ko.gba"))
    parser.add_argument("--xdelta", default="xdelta3", help="xdelta3 실행 파일 또는 경로")
    parser.add_argument("--force", action="store_true", help="기존 출력 파일 덮어쓰기")
    args = parser.parse_args()

    source = args.source.resolve()
    output = args.output.resolve()
    candidate = Path(args.xdelta)
    xdelta = shutil.which(args.xdelta) or (str(candidate.resolve()) if candidate.is_file() else None)
    if xdelta is None:
        raise SystemExit("xdelta3를 찾을 수 없습니다. PATH에 추가하거나 --xdelta로 경로를 지정하십시오.")
    if output.exists() and not args.force:
        raise SystemExit(f"출력 파일이 이미 있습니다: {output}\n덮어쓰려면 --force를 사용하십시오.")

    require_file(source, SOURCE_SIZE, SOURCE_SHA256, "원본 ROM")
    require_file(PATCH, PATCH_SIZE, PATCH_SHA256, "xdelta 패치")
    output.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=output.name + ".", suffix=".tmp", dir=output.parent, delete=False) as handle:
            temp_path = Path(handle.name)
        subprocess.run([xdelta, "-f", "-d", "-s", str(source), str(PATCH), str(temp_path)], check=True)
        require_file(temp_path, TARGET_SIZE, TARGET_SHA256, "패치 결과")
        os.replace(temp_path, output)
        temp_path = None
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"xdelta3 적용 실패: 종료 코드 {exc.returncode}") from exc
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    print(f"PASS: {output}")
    print(f"SIZE: {TARGET_SIZE}")
    print(f"SHA-256: {TARGET_SHA256}")


if __name__ == "__main__":
    main()
