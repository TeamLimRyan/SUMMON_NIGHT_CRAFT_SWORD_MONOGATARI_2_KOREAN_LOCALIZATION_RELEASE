# 설치 안내

## 준비물

- 대상 일본판 GBA ROM
- `xdelta3`
- 저장소 루트의 `Summon_Night_Craft_Sword_Monogatari_2_KO.xdelta`

원본 ROM은 이 저장소에서 제공하지 않습니다.

## 원본 확인

```powershell
Get-FileHash "Summon Night - Craft Sword Monogatari 2 (Japan).gba" -Algorithm SHA256
```

정상 원본은 크기 `16,777,216 bytes`, SHA-256 `9abbff51004531eb0f9ee4c15af5b53db7ffe5e9c47e1e225488c576db64360f`입니다. 해시가 다르면 적용하지 마십시오.

## 자동 적용과 검증

```powershell
python scripts/apply_patch.py "Summon Night - Craft Sword Monogatari 2 (Japan).gba"
```

기본 출력은 `summon_night_craft_sword_2_ko.gba`입니다. 출력 경로와 xdelta 실행 파일을 직접 지정할 수도 있습니다.

```powershell
python scripts/apply_patch.py "원본.gba" "내 폴더/크래프트 소드 이야기 2 한국어.gba" `
  --xdelta "C:\Tools\xdelta3.exe"
```

## 직접 적용

```powershell
xdelta3 -d -s "Summon Night - Craft Sword Monogatari 2 (Japan).gba" `
  "Summon_Night_Craft_Sword_Monogatari_2_KO.xdelta" `
  "summon_night_craft_sword_2_ko.gba"
```

## 결과 확인

```powershell
Get-FileHash "summon_night_craft_sword_2_ko.gba" -Algorithm SHA256
```

- 크기: `33,554,432 bytes`
- SHA-256: `5114235cb138ad3707da7750fd86c776b9c18b629bba2dcf0299159a6eba5300`

기존 일본판 세이브를 사용하기 전에는 별도 백업을 권장합니다.

기존 패치 결과 ROM에 다시 적용하지 말고, 항상 위 해시의 깨끗한 일본판 원본에 `v1.0.0` 패치를 적용하십시오.
