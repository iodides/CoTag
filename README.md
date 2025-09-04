# CoTag

![CoTag logo](resource/CoTag.png)

Short summary: CoTag — a small Windows GUI tool to inspect and edit ComicInfo.xml metadata inside CBZ/ZIP comic archive files.

## Download
- Windows one-file executable: [CoTag_1.2.exe](https://github.com/iodides/CoTag/releases/download/v1.2/CoTag_1.2.exe)

This repository contains CoTag, a small Windows GUI tool to inspect and edit ComicInfo.xml metadata inside CBZ/ZIP comic archive files. The app is implemented in Python using PySide6 and lxml. It supports loading one or more .cbz/.zip files, viewing/editing common ComicInfo fields, batch-save, thumbnails and a full-size image viewer.

## Key features
- Load .cbz / .zip archives and cache ComicInfo.xml contents when present.
- Multi-select with common-field display; differing values show as "<individual>".
- Edit metadata fields (SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author) and save per-file or save all.
- Thumbnail extraction (first image inside archive) and clickable full-size viewer with maximize/scale behavior.
- Drag & drop support, F2 rename in file list, natural filename sorting.



## Usage
- Load one or more `.cbz` / `.zip` files via the "파일로드" button or by dragging files onto the window.
- Select a single file to edit its metadata, or select multiple files to edit common fields simultaneously.
- Edit metadata fields on the right: SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author (Author is shown as a single field for penciller/inker).
- When multiple files are selected, fields with differing values display as `"<개별값>"`.
- Use the "저장" button to save the currently selected file(s), or "전체저장" to save all modified files; during "전체저장" the status bar shows progress like `(3/16) 저장중...`.
- Thumbnails are shown for each file (first image in archive); click the thumbnail to open a full-size viewer.
- Keyboard shortcuts: F2 renames the selected file in the list; when a metadata textbox has focus, `Ctrl+B` moves to the previous file and `Ctrl+N` moves to the next file.
- Files are sorted naturally (numeric parts sort numerically) and multiple selection supports batch edits.

 - Image viewer controls (when you click a thumbnail):
  - Use the on-screen ◀ / ▶ buttons to move to the previous or next page.
  - Keyboard: Left / Right arrows move pages; Esc closes the viewer.
	- Mouse wheel: scroll up to go to the previous page, scroll down to go to the next page.
	- Click the image to close the viewer.
	- The viewer shows the current page index and total pages at the bottom center (e.g. "3 / 12").

 

## License
This project is available for use by anyone. You may use, modify, and distribute this software without restriction.

Note: This program was created using GPT-5 mini.

---

간단 요약: CoTag — CBZ/ZIP 아카이브 내의 ComicInfo.xml을 편집할 수 있는 Windows GUI 도구입니다.

## 다운로드
- Windows 단일 실행파일(.exe): [CoTag_1.2.exe](https://github.com/iodides/CoTag/releases/download/v1.2/CoTag_1.2.exe)

이 저장소는 CoTag라는 간단한 Windows GUI 도구를 포함합니다. CoTag는 CBZ/ZIP 만화 아카이브 안의 ComicInfo.xml 메타데이터를 열람/수정할 수 있으며, Python (PySide6)과 lxml로 구현되어 있습니다. 다중 파일 로드, 공통 메타 동시 편집, 배치 저장, 썸네일 및 전체 크기 이미지 뷰어를 제공합니다.

## 주요 기능
- .cbz / .zip 파일을 불러와 ComicInfo.xml 내용을 캐시합니다.
- 여러 파일 선택 시 공통 필드만 표시하며, 값이 서로 다르면 "<개별값>"로 표시합니다.
- 메타데이터 필드(SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author)를 편집하고 파일별/전체 저장이 가능합니다.
- 아카이브 내부의 첫 이미지를 썸네일로 보여주며 클릭하면 전체 크기 뷰어(최대화/창 크기 맞춤)를 표시합니다.
- 드래그앤드롭, 파일 목록에서 F2로 이름 변경, 자연수 정렬을 지원합니다.



## 사용법
- "파일로드" 버튼이나 파일을 드래그해서 `.cbz` / `.zip` 파일을 불러옵니다.
- 왼쪽 목록에서 한 개를 선택하면 해당 파일의 메타데이터를 편집할 수 있고, 여러 개를 선택하면 공통된 필드만 동시에 편집할 수 있습니다.
- 오른쪽에서 편집 가능한 메타데이터 필드: SeriesGroup, Series, Title, Volume, Number, Year, Month, Day, Author (작화가/원작자는 한 필드로 통합 표시).
- 여러 파일을 선택했을 때 값이 서로 다른 필드는 `"<개별값>"`으로 표시됩니다.
- "저장" 버튼은 현재 선택된 파일(들)을 저장하고, "전체저장"은 변경된 모든 파일을 저장합니다. "전체저장" 중에는 상태표시줄에 `(3/16) 저장중...` 같은 진행 표시가 나타납니다.
- 썸네일은 아카이브의 첫 이미지를 사용하며, 썸네일을 클릭하면 전체 크기 뷰어가 열립니다.
- 단축키: 목록에서 F2로 이름을 바꿀 수 있으며, 메타데이터 텍스트박스에 포커스가 있을 때 `Ctrl+B`로 이전 파일, `Ctrl+N`으로 다음 파일로 이동합니다.
- 파일명은 자연수 정렬로 정렬되며, 다중 선택을 통해 일괄 편집이 가능합니다.

 - 이미지 뷰어 사용법 (썸네일 클릭 시):
  - 화면의 ◀ / ▶ 버튼으로 이전/다음 페이지로 이동합니다.
  - 키보드: 좌/우 방향키로 페이지를 이동할 수 있으며, Esc로 뷰어를 닫습니다.
	- 마우스 휠: 위로 스크롤하면 이전 페이지, 아래로 스크롤하면 다음 페이지로 이동합니다.
	- 이미지를 클릭하면 뷰어가 닫힙니다.
	- 뷰어 하단 중앙에 현재 페이지 / 전체 페이지 수(예: "3 / 12")가 표시됩니다.

 

## 라이선스
이 프로젝트는 누구나 자유롭게 사용할 수 있습니다. 수정 및 재배포에 제한이 없습니다.

참고: 이 프로그램은 GPT-5 mini를 사용하여 만들어졌습니다.
