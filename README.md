# CoTag

English | 한국어

----|----
This repository contains CoTag, a small Windows GUI tool to inspect and edit ComicInfo.xml metadata inside CBZ/ZIP comic archive files. The app is implemented in Python using PySide6 and lxml. It supports loading one or more .cbz/.zip files, viewing/editing common ComicInfo fields, batch-save, thumbnails and a full-size image viewer. | 이 저장소는 CoTag라는 간단한 Windows GUI 도구를 포함합니다. CoTag는 CBZ/ZIP 만화 아카이브 안의 ComicInfo.xml 메타데이터를 열람/수정할 수 있으며, Python (PySide6)과 lxml로 구현되어 있습니다. 다중 파일 로드, 공통 메타 동시 편집, 배치 저장, 썸네일 및 전체 크기 이미지 뷰어를 제공합니다.

## Key features — 주요 기능
- Load .cbz / .zip archives and cache ComicInfo.xml contents when present. | .cbz / .zip 파일을 불러와 ComicInfo.xml 내용을 캐시합니다.
- Multi-select with common-field display; differing values show as "<개별값>". | 여러 파일 선택 시 공통 필드만 표시하며, 값이 서로 다르면 "<개별값>"로 표시합니다.
- Edit metadata fields (SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author) and save per-file or save all. | 메타데이터 필드(SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author)를 편집하고 파일별/전체 저장이 가능합니다.
- Thumbnail extraction (first image inside archive) and clickable full-size viewer with maximize/scale behavior. | 아카이브 내부의 첫 이미지를 썸네일로 보여주며 클릭하면 전체 크기 뷰어(최대화/창 크기 맞춤)를 표시합니다.
- Drag & drop support, F2 rename in file list, natural filename sorting. | 드래그앤드롭, 파일 목록에서 F2로 이름 변경, 자연수 정렬을 지원합니다.

## Requirements / 요구사항
- Python 3.10+ (tested with 3.13) | Python 3.10+ (3.13에서 테스트됨)
- Virtual environment recommended | 가상환경(venv) 권장
- Python packages: PySide6, lxml, Pillow (for icon tooling) | 필요한 패키지: PySide6, lxml, Pillow (아이콘 처리용)

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

## Run (development) — 개발 모드 실행
Run the app from source:

```powershell
python .\src\main.py
```

This will open the CoTag GUI. The app will try to set the application icon from the bundled runtime (`sys._MEIPASS`) when packaged, otherwise from `resource/CoTag.ico` in the project root.

## Build for Windows (one-file .exe) — 윈도우용 단일 exe 빌드
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
- Make sure `resource/CoTag.ico` exists and contains the icon you want to embed. The build script copies and embeds this file. | `resource/CoTag.ico`가 존재해야 하며, 원하시는 아이콘을 넣어두세요. 빌드 스크립트가 이 파일을 사용합니다.
- If Explorer shows an old icon after building, try restarting Explorer or clearing the icon cache (the project includes a small helper script to regenerate a multi-resolution ICO if needed). | 빌드 후 탐색기에서 옛 아이콘이 보이면 Explorer 재시작 또는 아이콘 캐시 삭제를 시도하세요. 멀티 해상도 ICO 재생성 스크립트가 `build/generate_multires_icon.py`에 포함되어 있습니다.

## Project layout / 파일 구조
- `src/main.py` — main application GUI | 메인 GUI 구현
- `resource/CoTag.ico` — application icon used for builds | 빌드에 사용되는 아이콘
- `build_exe.bat` — PyInstaller helper script (Windows) | 빌드 스크립트
- `build/generate_multires_icon.py` — optional tool to create a multi-size ICO | 멀티 사이즈 ICO 생성 스크립트

## Contributing / 기여
Pull requests are welcome. For small fixes, include a short description and a minimal repro if relevant. | PR 환영합니다. 작은 수정도 환영하며 변경 내용과 간단한 설명을 포함해 주세요.

## License / 라이선스
Please add your preferred license file to the repository (e.g. `LICENSE`). This project currently has no license file in the repo. | 원하시는 라이선스 파일(`LICENSE`)을 추가해 주세요. 현재 저장소에는 라이선스 파일이 없습니다.

---

If you want, I can also:

- add a `requirements.txt` file, or
- run a clean build now and attach the resulting `dist\\CoTag_1.1.exe` checksum for verification.

If you'd like either, say which and I'll do it.
