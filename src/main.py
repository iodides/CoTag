import os
import zipfile
import sys
import re
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PySide6 import QtCore, QtGui, QtWidgets
from lxml import etree


APP_NAME = "CoTag"

# best-effort icon path (optional)
ICON_PATH = Path(__file__).with_name("icon.png")


class FileItem:
    """Lightweight container for a file entry."""
    def __init__(self, path: Path):
        self.path: Path = path
        self.meta: Dict[str, str] = {}
        self.saved_meta: Dict[str, str] = {}
        self.has_comicinfo: bool = False
        self.dirty: bool = False


def read_comicinfo_from_zip(path: Path) -> Optional[etree._Element]:
    """Return the root Element of ComicInfo.xml inside the zip, or None."""
    try:
        with zipfile.ZipFile(str(path), 'r') as z:
            # find ComicInfo.xml (case-insensitive)
            nam = None
            for n in z.namelist():
                if n.lower().endswith('comicinfo.xml'):
                    nam = n
                    break
            if not nam:
                return None
            data = z.read(nam)
            root = etree.fromstring(data)
            return root
    except Exception:
        return None


def write_comicinfo_to_zip(path: Path, root: etree._Element) -> bool:
    """Write ComicInfo.xml into the archive, returning True on success.

    This rebuilds the archive in-memory and overwrites the original file.
    """
    try:
        # gather existing entries except ComicInfo.xml
        with zipfile.ZipFile(str(path), 'r') as z:
            entries = [(n, z.read(n)) for n in z.namelist() if not n.lower().endswith('comicinfo.xml')]

        bio = BytesIO()
        compression = zipfile.ZIP_DEFLATED if 'ZIP_DEFLATED' in dir(zipfile) else zipfile.ZIP_STORED
        with zipfile.ZipFile(bio, 'w', compression=compression) as out:
            for n, b in entries:
                out.writestr(n, b)
            # write ComicInfo.xml at root
            xml_bytes = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True)
            out.writestr('ComicInfo.xml', xml_bytes)

        path.write_bytes(bio.getvalue())
        return True
    except Exception:
        return False


def get_first_image_from_zip(path: Path) -> Optional[bytes]:
    """Return raw bytes of the first image file inside the zip, or None."""
    try:
        with zipfile.ZipFile(str(path), 'r') as z:
            for n in z.namelist():
                lower = n.lower()
                if lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                    return z.read(n)
    except Exception:
        return None
    return None


def get_image_bytes_list_from_zip(path: Path) -> List[bytes]:
    """Return raw bytes of all image files inside the zip in archive order."""
    out: List[bytes] = []
    try:
        with zipfile.ZipFile(str(path), 'r') as z:
            for n in z.namelist():
                lower = n.lower()
                if lower.endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')):
                    try:
                        out.append(z.read(n))
                    except Exception:
                        # skip unreadable entries
                        continue
    except Exception:
        return []
    return out


class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.clicked.emit()
        super().mousePressEvent(ev)
    
    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        # forward key events to the top-level window (ImageViewer) so navigation keys work
        try:
            win = self.window()
            if win and hasattr(win, 'keyPressEvent'):
                win.keyPressEvent(ev)
                return
        except Exception:
            pass
        super().keyPressEvent(ev)

    def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
        # forward wheel events to the top-level window so scrolling can change pages
        try:
            win = self.window()
            if win and hasattr(win, 'wheelEvent'):
                win.wheelEvent(ev)
                return
        except Exception:
            pass
        super().wheelEvent(ev)


class ImageViewer(QtWidgets.QDialog):
    def __init__(self, pixmaps: List[QtGui.QPixmap], index: int = 0, parent=None):
        super().__init__(parent)
        self.setWindowTitle('이미지 보기')
        # enable maximize button on the dialog
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.resize(800, 600)

        self._pixmaps: List[QtGui.QPixmap] = pixmaps or []
        self._idx: int = max(0, min(index, len(self._pixmaps) - 1)) if self._pixmaps else 0

        layout = QtWidgets.QVBoxLayout(self)
        self._scroll = QtWidgets.QScrollArea()
        self._scroll.setWidgetResizable(True)

        self._img_label = ClickableLabel()
        self._img_label.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._img_label.setAlignment(QtCore.Qt.AlignCenter)

        # clicking the image will accept() the dialog (close)
        self._img_label.clicked.connect(self.accept)
        self._scroll.setWidget(self._img_label)
        layout.addWidget(self._scroll)

        # add navigation buttons under the image
        nav_widget = QtWidgets.QWidget()
        nav_layout = QtWidgets.QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 6, 0, 0)
        nav_layout.setSpacing(8)
        self.btn_prev = QtWidgets.QPushButton("◀")
        self.btn_next = QtWidgets.QPushButton("▶")
        self.btn_prev.setFixedWidth(40)
        self.btn_next.setFixedWidth(40)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addStretch(1)
        layout.addWidget(nav_widget)

        # page index label (centered under the image)
        self._pos_label = QtWidgets.QLabel()
        self._pos_label.setAlignment(QtCore.Qt.AlignCenter)
        self._pos_label.setContentsMargins(0, 4, 0, 0)
        layout.addWidget(self._pos_label)

        # wire navigation
        self.btn_prev.clicked.connect(self._show_prev)
        self.btn_next.clicked.connect(self._show_next)

        # initially show the selected image and focus the label so key events are delivered
        if self._pixmaps:
            self._orig_pixmap = self._pixmaps[self._idx]
        else:
            self._orig_pixmap = None
        QtCore.QTimer.singleShot(0, self._rescale_pixmap)
        QtCore.QTimer.singleShot(0, self._img_label.setFocus)
        QtCore.QTimer.singleShot(0, self._update_nav_buttons)

    def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
        # vertical wheel up -> previous, down -> next
        delta = ev.angleDelta().y()
        if delta > 0:
            self._show_prev()
        elif delta < 0:
            self._show_next()
        ev.accept()

    def keyPressEvent(self, ev: QtGui.QKeyEvent) -> None:
        if ev.key() == QtCore.Qt.Key_Escape:
            self.close()
            return
        if ev.key() == QtCore.Qt.Key_Left:
            self._show_prev()
            return
        if ev.key() == QtCore.Qt.Key_Right:
            self._show_next()
            return
        super().keyPressEvent(ev)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        super().resizeEvent(ev)
        # rescale image when the dialog is resized
        self._rescale_pixmap()

    def _rescale_pixmap(self) -> None:
        if not getattr(self, '_orig_pixmap', None):
            return
        if not getattr(self, '_scroll', None) or not getattr(self, '_img_label', None):
            return
        vp = self._scroll.viewport().size()
        if vp.width() <= 0 or vp.height() <= 0:
            return
        ow = self._orig_pixmap.width()
        oh = self._orig_pixmap.height()
        # do not upscale: if original fits within viewport, show original size
        if ow <= vp.width() and oh <= vp.height():
            self._img_label.setPixmap(self._orig_pixmap)
            return
        scaled = self._orig_pixmap.scaled(vp.width(), vp.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self._img_label.setPixmap(scaled)

    def _show_prev(self) -> None:
        if not getattr(self, '_pixmaps', None):
            return
        if self._idx <= 0:
            return
        self._idx -= 1
        self._orig_pixmap = self._pixmaps[self._idx]
        self._rescale_pixmap()
        self._update_nav_buttons()

    def _show_next(self) -> None:
        if not getattr(self, '_pixmaps', None):
            return
        if self._idx >= len(self._pixmaps) - 1:
            return
        self._idx += 1
        self._orig_pixmap = self._pixmaps[self._idx]
        self._rescale_pixmap()
        self._update_nav_buttons()

    def _update_nav_buttons(self) -> None:
        total = len(getattr(self, '_pixmaps', []))
        if total <= 1:
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return
        self.btn_prev.setEnabled(self._idx > 0)
        self.btn_next.setEnabled(self._idx < total - 1)
        # update position label
        try:
            self._pos_label.setText(f"{self._idx + 1} / {total}")
        except Exception:
            pass

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        if ICON_PATH.exists():
            self.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))

        self.resize(800, 600)

        self.files: List[FileItem] = []
        self.setAcceptDrops(True)

        self._suppress_table_item_changed = False

        # F2 rename action
        self.rename_action = QtGui.QAction(self)
        self.rename_action.setShortcut(QtGui.QKeySequence("F2"))
        self.rename_action.triggered.connect(self.start_rename)
        self.addAction(self.rename_action)

        # Ctrl+B / Ctrl+N for previous/next file navigation while editing metadata
        self.prev_action = QtGui.QAction(self)
        self.prev_action.setShortcut(QtGui.QKeySequence("Ctrl+B"))
        self.prev_action.triggered.connect(self.go_prev_file)
        self.addAction(self.prev_action)

        self.next_action = QtGui.QAction(self)
        self.next_action.setShortcut(QtGui.QKeySequence("Ctrl+N"))
        self.next_action.triggered.connect(self.go_next_file)
        self.addAction(self.next_action)

        # full-size pixmap cache for thumbnail -> full viewer
        self._full_pixmap = None

        self._build_ui()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        layout.addWidget(splitter)

        # left pane
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)

        btn_layout = QtWidgets.QHBoxLayout()
        self.btn_load = QtWidgets.QPushButton("파일로드")
        self.btn_clear = QtWidgets.QPushButton("목록지우기")
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_clear)
        left_layout.addLayout(btn_layout)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["*", "파일명", "크기"])
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setColumnWidth(0, 30)
        left_layout.addWidget(self.table)
        self.table.itemChanged.connect(self.on_table_item_changed)

        splitter.addWidget(left)

        # right pane
        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        form = QtWidgets.QFormLayout()
        self.fields = {}
        keys = [
            ("SeriesGroup", "시리즈그룹"),
            ("Series", "시리즈"),
            ("Title", "제목"),
            ("Volume", "권"),
            ("Number", "회차"),
            ("Year", "연도"),
            ("Month", "월"),
            ("Day", "일"),
            ("Author", "작화/원작자"),
        ]

        for key, label in keys:
            le = QtWidgets.QLineEdit()
            le.setObjectName(key)
            form.addRow(label, le)
            self.fields[key] = le

        right_layout.addLayout(form)

        # save buttons horizontally under Author (equal-width, no side margins)
        self.btn_save = QtWidgets.QPushButton("저장")
        self.btn_save.setEnabled(False)
        self.btn_save_all = QtWidgets.QPushButton("전체저장")
        self.btn_save_all.setEnabled(False)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(0)
        btn_row.addWidget(self.btn_save, 1)
        btn_row.addWidget(self.btn_save_all, 1)
        right_layout.addLayout(btn_row)

        # thumbnail under metadata and buttons (fill width, centered, no margins)
        self.thumb_label = ClickableLabel()
        self.thumb_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.thumb_label.setMinimumHeight(180)
        self.thumb_label.setAlignment(QtCore.Qt.AlignCenter)
        self.thumb_label.setStyleSheet("border: 1px solid #ccc; background: #f8f8f8;")
        self.thumb_label.clicked.connect(self.show_full_image)
        right_layout.addWidget(self.thumb_label)

        splitter.addWidget(right)

        # bottom single-line status bar
        status = QtWidgets.QStatusBar()
        status.setSizeGripEnabled(False)
        self.setStatusBar(status)
        self.statusBar().showMessage("파일을 선택하세요")

        # connections
        self.btn_load.clicked.connect(self.load_files_dialog)
        self.btn_clear.clicked.connect(self.clear_list)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.btn_save.clicked.connect(self.save_current)
        self.btn_save_all.clicked.connect(self.save_all)

        for f in self.fields.values():
            f.textChanged.connect(self.on_field_changed)

    def load_files_dialog(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "파일 선택", str(Path.home()), "CBZ/ZIP Files (*.cbz *.zip);;All Files (*)")
        if not paths:
            return
        self.load_paths([Path(p) for p in paths])

    def load_paths(self, paths: List[Path]):
        for p in paths:
            # skip duplicates
            if any(existing.path == p for existing in self.files):
                continue
            fi = FileItem(p)
            tree = read_comicinfo_from_zip(p)
            if tree is not None:
                fi.has_comicinfo = True
                fi.meta = self._meta_from_xml(tree)
                fi.saved_meta = fi.meta.copy()
            self.files.append(fi)

        # natural sort files by filename so numeric parts sort naturally (1,2,..10)
        def natural_key(s: str):
            parts = re.split(r"(\d+)", s)
            key = []
            for p in parts:
                if p.isdigit():
                    key.append(int(p))
                else:
                    key.append(p.lower())
            return tuple(key)

        self.files.sort(key=lambda fi: natural_key(fi.path.name))
        self.refresh_table()

    def refresh_table(self):
        try:
            selected_rows = [r.row() for r in self.table.selectionModel().selectedRows()]
            selected_paths = [self.table.item(r, 1).data(QtCore.Qt.UserRole) for r in selected_rows if self.table.item(r, 1) is not None]
        except Exception:
            selected_paths = []

        self.table.blockSignals(True)
        self.table.setRowCount(0)
        for fi in self.files:
            r = self.table.rowCount()
            self.table.insertRow(r)
            star = QtWidgets.QTableWidgetItem("*" if fi.dirty else "")
            star.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            display_name = fi.path.stem
            name = QtWidgets.QTableWidgetItem(display_name)
            name.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
            name.setData(QtCore.Qt.UserRole, str(fi.path))
            try:
                size = fi.path.stat().st_size
                size_mb = size / (1024.0 * 1024.0)
                size_str = f"{size_mb:.1f} MB"
            except Exception:
                size_str = ""
            size_item = QtWidgets.QTableWidgetItem(size_str)
            size_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.table.setItem(r, 0, star)
            self.table.setItem(r, 1, name)
            self.table.setItem(r, 2, size_item)

        if selected_paths:
            self.table.clearSelection()
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 1)
                if item and item.data(QtCore.Qt.UserRole) in selected_paths:
                    self.table.selectRow(row)

        self.table.blockSignals(False)
        self.update_status()

    def clear_list(self):
        self.files = []
        for f in self.fields.values():
            f.blockSignals(True)
            f.setText("")
            f.blockSignals(False)
        self.refresh_table()
        self.table.clearSelection()
        self.btn_save.setEnabled(False)
        self.btn_save_all.setEnabled(False)
        self.statusBar().showMessage("파일을 선택하세요")
        self._full_pixmap = None
        self.thumb_label.clear()

    def on_selection_changed(self):
        rows = {i.row() for i in self.table.selectedIndexes()}
        selected = [self.files[r] for r in sorted(rows)]
        count = len(selected)
        if count == 0:
            self.statusBar().showMessage("파일을 선택하세요")
            for f in self.fields.values():
                f.setText("")
            self.btn_save.setEnabled(False)
            self.btn_save_all.setEnabled(False)
            self._full_pixmap = None
            self.thumb_label.clear()
            return

        self.statusBar().showMessage(f"{count}개 파일 선택됨")
        common = self._common_meta(selected)
        for key, widget in self.fields.items():
            val = common.get(key, "")
            widget.blockSignals(True)
            widget.setText(val)
            widget.blockSignals(False)

        if count == 1:
            self.btn_save.setEnabled(selected[0].dirty)
        else:
            self.btn_save.setEnabled(any(s.dirty for s in selected))

        self.btn_save_all.setEnabled(any(fi.dirty for fi in self.files))
        self.update_thumbnail()

    def _common_meta(self, items: List[FileItem]) -> Dict[str, str]:
        keys = ["SeriesGroup", "Series", "Title", "Volume", "Number", "Year", "Month", "Day", "Author"]
        common = {}
        for k in keys:
            values = []
            for it in items:
                v = it.meta.get(k)
                values.append(v if v is not None else "")
            first = values[0]
            if all(v == first for v in values):
                common[k] = first
            else:
                if all(v == "" for v in values):
                    common[k] = ""
                else:
                    common[k] = "<개별값>"
        return common

    def _meta_from_xml(self, root: etree._Element) -> Dict[str, str]:
        out = {}
        mapping = {
            "SeriesGroup": "SeriesGroup",
            "Series": "Series",
            "Title": "Title",
            "Volume": "Volume",
            "Number": "Number",
            "Year": "Year",
            "Month": "Month",
            "Day": "Day",
            "Penciller": "Penciller",
            "Inker": "Inker",
        }
        for xmlk, tag in mapping.items():
            el = root.find(tag)
            if el is not None and el.text:
                out[xmlk] = el.text
        author = out.get("Penciller") or out.get("Inker")
        if author:
            out["Author"] = author
        return out

    def on_field_changed(self):
        rows = {i.row() for i in self.table.selectedIndexes()}
        selected = [self.files[r] for r in sorted(rows)]
        if not selected:
            return
        cur = {k: v.text() for k, v in self.fields.items()}
        any_dirty = False
        changed_any = False
        for it in selected:
            changed = False
            for k, v in cur.items():
                if v == "<개별값>":
                    continue
                old = it.saved_meta.get(k, "")
                it.meta[k] = v
                if v != old:
                    changed = True
            if it.dirty != changed:
                changed_any = True
                it.dirty = changed
            any_dirty = any_dirty or changed
        if changed_any:
            self.refresh_table()
        self.btn_save.setEnabled(any_dirty)
        self.btn_save_all.setEnabled(any(fi.dirty for fi in self.files))

    def save_current(self):
        rows = {i.row() for i in self.table.selectedIndexes()}
        selected = [self.files[r] for r in sorted(rows)]
        if not selected:
            return
        for it in selected:
            if not it.dirty:
                continue
            root = self._build_xml_from_meta(it, it.meta)
            ok = write_comicinfo_to_zip(it.path, root)
            if ok:
                it.saved_meta = {k: v for k, v in it.meta.items() if v and v != "<개별값>"}
                it.dirty = False
        self.refresh_table()
        QtWidgets.QMessageBox.information(self, "저장", "저장되었습니다")

    def save_all(self):
        # Gather dirty files first
        dirty_items = [it for it in self.files if it.dirty]
        total = len(dirty_items)
        if total == 0:
            QtWidgets.QMessageBox.information(self, "저장", "저장할 변경사항이 없습니다")
            return

        # Disable save buttons while operating
        self.btn_save_all.setEnabled(False)
        self.btn_save.setEnabled(False)

        any_saved = False
        try:
            for idx, it in enumerate(dirty_items, start=1):
                # Update status bar with progress like '(3/16) 저장중...'
                self.statusBar().showMessage(f"({idx}/{total}) 저장중...")
                QtWidgets.QApplication.processEvents()

                root = self._build_xml_from_meta(it, it.meta)
                ok = write_comicinfo_to_zip(it.path, root)
                if ok:
                    it.saved_meta = {k: v for k, v in it.meta.items() if v and v != "<개별값>"}
                    it.dirty = False
                    any_saved = True

            # final refresh and message
            self.refresh_table()
            if any_saved:
                QtWidgets.QMessageBox.information(self, "저장", "저장되었습니다")
            else:
                QtWidgets.QMessageBox.information(self, "저장", "저장할 변경사항이 없습니다")
        finally:
            # Restore status and button states
            self.update_status()
            self.btn_save_all.setEnabled(any(fi.dirty for fi in self.files))
            self.btn_save.setEnabled(False)

    def _build_xml_from_meta(self, it: FileItem, cur: Dict[str, str]) -> etree._Element:
        root = etree.Element("ComicInfo")
        def add(tag, value):
            if value and value != "<개별값>":
                el = etree.SubElement(root, tag)
                el.text = str(value)
        add("SeriesGroup", cur.get("SeriesGroup", ""))
        add("Series", cur.get("Series", ""))
        add("Title", cur.get("Title", ""))
        add("Volume", cur.get("Volume", ""))
        add("Number", cur.get("Number", ""))
        add("Year", cur.get("Year", ""))
        add("Month", cur.get("Month", ""))
        add("Day", cur.get("Day", ""))
        author = cur.get("Author", "")
        if author and author != "<개별값>":
            add("Penciller", author)
            add("Inker", author)
        return root


    def update_status(self):
        sel = len(self.table.selectionModel().selectedRows())
        if sel == 0:
            self.statusBar().showMessage("파일을 선택하세요")
        else:
            self.statusBar().showMessage(f"{sel}개 파일 선택됨")

    # Drag & drop support
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        urls = event.mimeData().urls()
        paths = []
        for u in urls:
            p = Path(u.toLocalFile())
            if p.suffix.lower() in (".cbz", ".zip"):
                paths.append(p)

        if paths:
            self.load_paths(paths)

    # start rename for selected row (F2)
    def start_rename(self):
        rows = [r.row() for r in self.table.selectionModel().selectedRows()]
        if not rows:
            return
        row = rows[0]
        item = self.table.item(row, 1)
        if item is None:
            return
        # make sure item is editable and start editing
        self.table.editItem(item)

    def go_next_file(self):
        """Select the next file in the table (if any)."""
        try:
            # Only perform navigation when focus is in one of the metadata fields
            focus = QtWidgets.QApplication.focusWidget()
            if not isinstance(focus, QtWidgets.QLineEdit) or focus not in self.fields.values():
                return
            rows = sorted({i.row() for i in self.table.selectedIndexes()})
            if not rows:
                return
            row = rows[0]
            if row >= self.table.rowCount() - 1:
                return
            target = row + 1
            self.table.clearSelection()
            self.table.selectRow(target)
            item = self.table.item(target, 1)
            if item:
                self.table.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)
        except Exception:
            return

    def go_prev_file(self):
        """Select the previous file in the table (if any)."""
        try:
            # Only perform navigation when focus is in one of the metadata fields
            focus = QtWidgets.QApplication.focusWidget()
            if not isinstance(focus, QtWidgets.QLineEdit) or focus not in self.fields.values():
                return
            rows = sorted({i.row() for i in self.table.selectedIndexes()})
            if not rows:
                return
            row = rows[0]
            if row <= 0:
                return
            target = row - 1
            self.table.clearSelection()
            self.table.selectRow(target)
            item = self.table.item(target, 1)
            if item:
                self.table.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)
        except Exception:
            return

    def on_table_item_changed(self, item: QtWidgets.QTableWidgetItem):
        # handle rename commits when user edits filename cell (col 1)
        if self._suppress_table_item_changed:
            return
        if item.column() != 1:
            return

        new_display = item.text()
        full_path_str = item.data(QtCore.Qt.UserRole)
        if not full_path_str:
            return
        old_path = Path(full_path_str)
        new_name = new_display + old_path.suffix
        new_path = old_path.with_name(new_name)

        # if nothing changed, ignore
        if new_path == old_path:
            return

        if new_path.exists():
            QtWidgets.QMessageBox.warning(self, "이름 변경 실패", f"대상 파일이 이미 존재합니다: {new_path}")
            # revert display to old stem
            self._suppress_table_item_changed = True
            item.setText(old_path.stem)
            self._suppress_table_item_changed = False
            return

        try:
            old_path.replace(new_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "이름 변경 실패", f"이름 변경 중 오류가 발생했습니다: {e}")
            self._suppress_table_item_changed = True
            item.setText(old_path.stem)
            self._suppress_table_item_changed = False
            return

        # success: update our model entry that matches the old path
        for fi in self.files:
            if fi.path == old_path:
                fi.path = new_path
                break

        # update the UserRole to new full path
        self._suppress_table_item_changed = True
        item.setData(QtCore.Qt.UserRole, str(new_path))
        # update size column
        try:
            size = new_path.stat().st_size
            size_mb = size / (1024.0 * 1024.0)
            size_str = f"{size_mb:.1f} MB"
        except Exception:
            size_str = ""
        size_item = self.table.item(item.row(), 2)
        if size_item:
            size_item.setText(size_str)
        self._suppress_table_item_changed = False

    def update_thumbnail(self):
        # show thumbnail for first selected file (if any)
        rows = [r.row() for r in self.table.selectionModel().selectedRows()]
        if not rows:
            self._full_pixmap = None
            self.thumb_label.clear()
            return
        first = rows[0]
        try:
            fi = self.files[first]
        except Exception:
            self._full_pixmap = None
            self.thumb_label.clear()
            return

        data = get_first_image_from_zip(fi.path)
        if not data:
            self._full_pixmap = None
            self.thumb_label.setText("썸네일 없음")
            return

        pix = QtGui.QPixmap()
        ok = pix.loadFromData(data)
        if not ok or pix.isNull():
            self._full_pixmap = None
            self.thumb_label.setText("썸네일 로드 실패")
            return

        self._full_pixmap = pix
        # scale for thumbnail area while preserving aspect ratio
        thumb = pix.scaled(self.thumb_label.width(), self.thumb_label.height(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.thumb_label.setPixmap(thumb)
    def show_full_image(self):
        # load all images from the currently selected archive and show viewer with navigation
        rows = [r.row() for r in self.table.selectionModel().selectedRows()]
        if not rows:
            return
        idx = rows[0]
        try:
            fi = self.files[idx]
        except Exception:
            return

        img_bytes_list = get_image_bytes_list_from_zip(fi.path)
        if not img_bytes_list:
            return

        pixmaps: List[QtGui.QPixmap] = []
        for b in img_bytes_list:
            p = QtGui.QPixmap()
            if p.loadFromData(b):
                pixmaps.append(p)
        if not pixmaps:
            return

        # open viewer with list of pixmaps, start at first image
        dlg = ImageViewer(pixmaps, index=0, parent=self)
        # open dialog at current image size but not larger than screen
        scr = QtWidgets.QApplication.primaryScreen().availableGeometry()
        ow = pixmaps[0].width()
        oh = pixmaps[0].height()
        w = min(ow, scr.width())
        h = min(oh, scr.height())
        dlg.resize(w, h)
        dlg.exec()


def main():
    app = QtWidgets.QApplication(sys.argv)
    # Ensure the application (and taskbar) uses our icon when possible.
    # When running as a PyInstaller onefile bundle, data files are unpacked to sys._MEIPASS.
    icon_path = None
    if getattr(sys, 'frozen', False) and getattr(sys, '_MEIPASS', None):
        candidate = Path(sys._MEIPASS) / 'CoTag.ico'
        if candidate.exists():
            icon_path = candidate
    if icon_path is None:
        # fallback to project resource folder when running from source
        project_root = Path(__file__).resolve().parent.parent
        candidate = project_root / 'resource' / 'CoTag.ico'
        if candidate.exists():
            icon_path = candidate
    if icon_path:
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
