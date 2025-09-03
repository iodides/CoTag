# CoTag

Short summary: CoTag — a small Windows GUI tool to inspect and edit ComicInfo.xml metadata inside CBZ/ZIP comic archive files.

## Download
- Windows one-file executable: https://github.com/iodides/CoTag/releases/download/v1.1/CoTag_1.1.exe

This repository contains CoTag, a small Windows GUI tool to inspect and edit ComicInfo.xml metadata inside CBZ/ZIP comic archive files. The app is implemented in Python using PySide6 and lxml. It supports loading one or more .cbz/.zip files, viewing/editing common ComicInfo fields, batch-save, thumbnails and a full-size image viewer.

## Key features
- Load .cbz / .zip archives and cache ComicInfo.xml contents when present.
- Multi-select with common-field display; differing values show as "<individual>".
- Edit metadata fields (SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author) and save per-file or save all.
- Thumbnail extraction (first image inside archive) and clickable full-size viewer with maximize/scale behavior.
- Drag & drop support, F2 rename in file list, natural filename sorting.

## Requirements
- Python 3.10+ (tested with 3.13)
- Virtual environment recommended
- Python packages: PySide6, lxml, Pillow (for icon tooling)

Install requirements (in project root):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell
python -m pip install -r requirements.txt
```

If `requirements.txt` is not present, install directly:

```powershell
python -m pip install PySide6 lxml Pillow
```

## Run (development)
Run the app from source:

```powershell
python .\src\main.py
```

This will open the CoTag GUI. The app will try to set the application icon from the bundled runtime (`sys._MEIPASS`) when packaged, otherwise from `resource/CoTag.ico` in the project root.

## Build for Windows (one-file .exe)
There is a helper batch script `build_exe.bat` in the project root that runs PyInstaller and embeds `resource/CoTag.ico` into the bundle.

Default (clean) build:

```cmd
build_exe.bat
```

Faster incremental build (reuse PyInstaller cache):

```cmd
build_exe.bat fast
```

Notes:
- Make sure `resource/CoTag.ico` exists and contains the icon you want to embed. The build script copies and embeds this file.
- If Explorer shows an old icon after building, try restarting Explorer or clearing the icon cache (the project includes a small helper script to regenerate a multi-resolution ICO if needed).

## Project layout
- `src/main.py` — main application GUI
- `resource/CoTag.ico` — application icon used for builds
- `build_exe.bat` — PyInstaller helper script (Windows)
- `build/generate_multires_icon.py` — optional tool to create a multi-size ICO

## Contributing
Pull requests are welcome. For small fixes, include a short description and a minimal repro if relevant.

## License
Please add your preferred license file to the repository (e.g. `LICENSE`). This project currently has no license file in the repo.

---

간단 요약: CoTag — CBZ/ZIP 아카이브 내의 ComicInfo.xml을 편집할 수 있는 Windows GUI 도구입니다.

## 다운로드
- Windows 단일 실행파일(.exe): https://github.com/iodides/CoTag/releases/download/v1.1/CoTag_1.1.exe

이 저장소는 CoTag라는 간단한 Windows GUI 도구를 포함합니다. CoTag는 CBZ/ZIP 만화 아카이브 안의 ComicInfo.xml 메타데이터를 열람/수정할 수 있으며, Python (PySide6)과 lxml로 구현되어 있습니다. 다중 파일 로드, 공통 메타 동시 편집, 배치 저장, 썸네일 및 전체 크기 이미지 뷰어를 제공합니다.

## 주요 기능
- .cbz / .zip 파일을 불러와 ComicInfo.xml 내용을 캐시합니다.
- 여러 파일 선택 시 공통 필드만 표시하며, 값이 서로 다르면 "<개별값>"로 표시합니다.
- 메타데이터 필드(SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author)를 편집하고 파일별/전체 저장이 가능합니다.
- 아카이브 내부의 첫 이미지를 썸네일로 보여주며 클릭하면 전체 크기 뷰어(최대화/창 크기 맞춤)를 표시합니다.
- 드래그앤드롭, 파일 목록에서 F2로 이름 변경, 자연수 정렬을 지원합니다.

## 요구사항
- Python 3.10+ (3.13에서 테스트됨)
- 가상환경(venv) 권장
- 필요한 패키지: PySide6, lxml, Pillow (아이콘 처리용)

프로젝트 루트에서 의존성 설치:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell
python -m pip install -r requirements.txt
```

`requirements.txt`가 없으면 직접 설치:

```powershell
python -m pip install PySide6 lxml Pillow
```

## 개발 모드 실행
소스에서 앱을 실행하려면:

```powershell
python .\src\main.py
```

앱은 패키징된 런타임(`sys._MEIPASS`)에서 애플리케이션 아이콘을 설정하려 시도하며, 패키징되지 않은 경우 프로젝트 루트의 `resource/CoTag.ico`를 사용합니다.

## 윈도우용 단일 exe 빌드
프로젝트 루트에 있는 `build_exe.bat`는 PyInstaller를 실행하고 `resource/CoTag.ico`를 번들에 포함합니다.

기본(클린) 빌드:

```cmd
build_exe.bat
```

증분 빌드 (PyInstaller 캐시 재사용):

```cmd
build_exe.bat fast
```

참고:
- `resource/CoTag.ico`가 존재해야 하며, 원하는 아이콘을 넣어두세요. 빌드 스크립트가 이 파일을 사용합니다.
- 빌드 후 탐색기에서 옛 아이콘이 보이면 Explorer 재시작 또는 아이콘 캐시 삭제를 시도하세요. 멀티 해상도 ICO 재생성 스크립트가 `build/generate_multires_icon.py`에 포함되어 있습니다.

## 파일 구조
- `src/main.py` — 메인 GUI 구현
- `resource/CoTag.ico` — 빌드에 사용되는 아이콘
- `build_exe.bat` — 빌드 스크립트
- `build/generate_multires_icon.py` — 멀티 사이즈 ICO 생성 스크립트

- ## 기여
PR 환영합니다. 작은 수정도 환영하며 변경 내용과 간단한 설명을 포함해 주세요.

## 라이선스
원하시는 라이선스 파일(`LICENSE`)을 추가해 주세요. 현재 저장소에는 라이선스 파일이 없습니다.
