import os
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QVBoxLayout,
                             QTreeWidget, QTreeWidgetItem, QMenu, QAbstractItemView, QStyle)
from PyQt6.QtGui import QDrag, QIcon
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QMimeData, QFileSystemWatcher, QSize, QTimer

from App.Infrastructure.Helpers.ResourceHelper import resource_path
from App.Presentation.ViewModels.Workers import FunctionWorker


class DraggableTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item or item.childCount() > 0:
            return

        temp = item
        path_parts = []
        while temp.parent() is not None:
            path_parts.insert(0, temp.text(0))
            temp = temp.parent()

        if not path_parts:
            return

        project_name = temp.text(0)
        file_relative_path = os.path.join(*path_parts)

        mime_data = QMimeData()
        mime_data.setText(f"{project_name}|{file_relative_path}")

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

    def drawBranches(self, painter, rect, index):
        item = self.itemFromIndex(index)
        if item is None:
            return
        has_indicator = (
            item.childCount() > 0
            or item.childIndicatorPolicy()
            == QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator
        )
        if has_indicator:
            if self.isExpanded(index):
                icon = self.window().sidebar.icon_branch_open if hasattr(self.window(), "sidebar") else self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
            else:
                icon = self.window().sidebar.icon_branch_closed if hasattr(self.window(), "sidebar") else self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight)

            pm = icon.pixmap(12, 12)
            
            # --- BẢN SỬA LỖI UI ---
            # Lấy chiều rộng chuẩn của 1 cấp (level)
            indent = self.indentation() 
            
            # Tính toán x dựa vào mép phải (right) của rect thay vì mép trái (x).
            # Điều này ép mũi tên luôn nằm gọn trong ô cuối cùng, sát cạnh với Folder icon.
            x = rect.right() - indent + (indent - pm.width()) // 2 + 6
            y = rect.y() + (rect.height() - pm.height()) // 2
            
            painter.drawPixmap(x, y, pm)


class ProjectSidebar(QDockWidget):
    MEDIA_LOADED_ROLE = int(Qt.ItemDataRole.UserRole) + 1
    MAX_CONCURRENT_MEDIA_SCANS = 2
    MEDIA_EXTENSIONS = {
        "Image": (".jpg", ".jpeg", ".png", ".bmp", ".gif"),
        "Video": (".mp4", ".avi", ".mov", ".mkv", ".flv"),
    }

    sig_new_item = pyqtSignal(str)
    sig_delete = pyqtSignal(str)
    sig_rename = pyqtSignal(str)
    sig_save_as = pyqtSignal(str)
    sig_import_file = pyqtSignal(str)
    sig_import_item = pyqtSignal(str)

    sig_paste_to_project = pyqtSignal(str)
    sig_item_copy = pyqtSignal(str, str)
    sig_item_cut = pyqtSignal(str, str)
    sig_item_save = pyqtSignal(str, str)
    sig_item_delete = pyqtSignal(str, str)
    sig_item_rename = pyqtSignal(str, str)
    sig_open_editor = pyqtSignal(str, str)

    sig_file_copy = pyqtSignal(str, str, str, str)
    sig_file_cut = pyqtSignal(str, str, str, str)
    sig_file_rename = pyqtSignal(str, str, str, str, str)
    sig_file_delete = pyqtSignal(str, str, str, str)
    sig_file_paste = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__("Project Manager", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setMinimumWidth(100)
        self.setMaximumWidth(1000)

        self.app_config = {
            "sub_folders": ["Image", "Video"],
            "valid_extensions": sorted(
                {
                    extension
                    for extensions in self.MEDIA_EXTENSIONS.values()
                    for extension in extensions
                }
            ),
        }

        self._init_icons()

        self.fs_watcher = QFileSystemWatcher(self)
        self.fs_watcher.directoryChanged.connect(self.on_directory_changed)
        self.watched_paths = {}
        self._media_scan_workers = {}
        self._media_scan_queue = {}
        self._media_name_cache = {}
        self._pending_media_refreshes = set()
        self._shutting_down = False

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        self.tab_project = QWidget()
        self.setup_tab_project()
        self.tabs.addTab(self.tab_project, "Project")

        self.tab_calibration = QWidget()
        self.setup_tab_calibration()
        self.tabs.addTab(self.tab_calibration, "Calibration Tool")

        layout.addWidget(self.tabs)
        self.setWidget(container)

    def _init_icons(self):
        style = self.style()
        self.icon_dir = style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.icon_dir_closed = style.standardIcon(QStyle.StandardPixmap.SP_DirClosedIcon)

        icon_path = resource_path(os.path.join("App", "ReSource", "Icon", "SideBar"))

        path_img = os.path.join(icon_path, "image_file.svg")
        path_vid = os.path.join(icon_path, "video_file.svg")
        path_arrow_down = os.path.join(icon_path, "arrow_down.svg")
        path_arrow_next = os.path.join(icon_path, "arrow_next.svg")

        self.icon_branch_open = QIcon(path_arrow_down) if os.path.exists(path_arrow_down) else style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.icon_branch_closed = QIcon(path_arrow_next) if os.path.exists(path_arrow_next) else style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)

        if os.path.exists(path_img):
            self.icon_image = QIcon(path_img)
        else:
            self.icon_image = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

        if os.path.exists(path_vid):
            self.icon_video = QIcon(path_vid)
        else:
            self.icon_video = style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)

    def _get_sidebar_style(self):
        resource_dir = resource_path(os.path.join("App", "ReSource", "Icon", "SideBar"))
        arrow_down_path = os.path.join(resource_dir, "arrow_down.svg")
        arrow_next_path = os.path.join(resource_dir, "arrow_next.svg")

        if os.path.exists(arrow_down_path) and os.path.exists(arrow_next_path):
            style = """
            QTreeWidget {
                border: 1px solid #C0C0C0;
                outline: none;
            }
            QTreeWidget::item {
                padding: 2px 0px;
                border: none;
                min-height: 18px;
            }
            QTreeWidget::item:selected {
                background-color: #3399FF;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #E0E0E0;
            }
            QTreeWidget::branch {
                background: transparent;
                border-image: none;
                image: none;
            }
            """
            return style
        return ""

    def setup_tab_project(self):
        layout = QVBoxLayout(self.tab_project)
        layout.setContentsMargins(0, 0, 0, 0)

        self.project_tree = DraggableTreeWidget()
        self.project_tree.setRootIsDecorated(True)
        self.project_tree.setItemsExpandable(True)
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setIndentation(18)
        self.project_tree.setUniformRowHeights(True)
        self.project_tree.setIconSize(QSize(14, 14))
        self.project_tree.setStyleSheet(self._get_sidebar_style())

        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.project_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.project_tree.itemExpanded.connect(self._on_item_expanded)

        layout.addWidget(self.project_tree)

    def setup_tab_calibration(self):
        layout = QVBoxLayout(self.tab_calibration)
        layout.setContentsMargins(0, 0, 0, 0)
        self.calibration_list = QTreeWidget()
        self.calibration_list.setHeaderHidden(True)
        self.calibration_list.setStyleSheet("border: 1px solid #C0C0C0;")
        layout.addWidget(self.calibration_list)

    def _get_project_root_of(self, item):
        if item is None:
            return None
        temp = item
        while temp.parent() is not None:
            temp = temp.parent()
        return temp

    def on_item_double_clicked(self, item, column):
        if item.childCount() == 0:
            text = item.text(0)
            _, ext = os.path.splitext(text)
            if ext.lower() in self.app_config["valid_extensions"]:
                path_parts = []
                temp = item
                project_root = None

                while temp.parent() is not None:
                    if temp.parent().parent() is None:
                        project_root = temp.parent()
                        path_parts.insert(0, temp.text(0))
                        break
                    else:
                        path_parts.insert(0, temp.text(0))
                        temp = temp.parent()

                if project_root:
                    project_name = project_root.text(0)
                    relative_path = os.path.join(*path_parts)
                    self.sig_open_editor.emit(project_name, relative_path)

    def show_context_menu(self, pos):
        item = self.project_tree.itemAt(pos)
        if item is None:
            return

        project_root = self._get_project_root_of(item)
        project_name = project_root.text(0)

        if item == project_root:
            self._show_project_context_menu(project_name, pos)
            return

        parent = item.parent()
        if parent == project_root:
            self._show_item_context_menu(project_name, item.text(0), pos)
            return

        item_node = item
        while item_node.parent() != project_root:
            item_node = item_node.parent()
        item_name = item_node.text(0)

        if item.text(0) in ["Image", "Video"]:
            self._show_media_folder_context_menu(project_name, item_name, item.text(0), pos)
        elif item.parent() and item.parent().text(0) in ["Image", "Video"]:
            media_type = item.parent().text(0)
            file_name = item.text(0)
            self._show_file_context_menu(project_name, item_name, media_type, file_name, pos)

    def _show_project_context_menu(self, project_name, pos):
        menu = QMenu(self)
        act_new_item = menu.addAction("New Item...")
        act_open_proj = menu.addAction("Open Project...")
        act_open_item = menu.addAction("Open Item...")
        act_paste = menu.addAction("Paste")
        menu.addSeparator()
        act_rename = menu.addAction("Rename")
        act_delete = menu.addAction("Delete")
        menu.addSeparator()
        act_save_as = menu.addAction("Save As...")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_new_item:
            self.sig_new_item.emit(project_name)
        elif action == act_open_proj:
            self.sig_import_file.emit(project_name)
        elif action == act_open_item:
            self.sig_import_item.emit(project_name)
        elif action == act_paste:
            self.sig_paste_to_project.emit(project_name)
        elif action == act_delete:
            self.sig_delete.emit(project_name)
        elif action == act_rename:
            self.sig_rename.emit(project_name)
        elif action == act_save_as:
            self.sig_save_as.emit(project_name)

    def _show_item_context_menu(self, project_name, folder_name, pos):
        menu = QMenu(self)
        act_copy = menu.addAction("Copy")
        act_cut = menu.addAction("Cut")
        menu.addSeparator()
        act_rename = menu.addAction("Rename")
        act_delete = menu.addAction("Delete")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_copy:
            self.sig_item_copy.emit(project_name, folder_name)
        elif action == act_cut:
            self.sig_item_cut.emit(project_name, folder_name)
        elif action == act_rename:
            self.sig_item_rename.emit(project_name, folder_name)
        elif action == act_delete:
            self.sig_item_delete.emit(project_name, folder_name)

    def _show_file_context_menu(self, project_name, item_name, media_type, file_name, pos):
        menu = QMenu(self)
        act_copy = menu.addAction("Copy")
        act_cut = menu.addAction("Cut")
        menu.addSeparator()
        act_rename = menu.addAction("Rename")
        act_delete = menu.addAction("Delete")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_copy:
            self.sig_file_copy.emit(project_name, item_name, media_type, file_name)
        elif action == act_cut:
            self.sig_file_cut.emit(project_name, item_name, media_type, file_name)
        elif action == act_rename:
            self.sig_file_rename.emit(project_name, item_name, media_type, file_name, "")
        elif action == act_delete:
            self.sig_file_delete.emit(project_name, item_name, media_type, file_name)

    def _show_media_folder_context_menu(self, project_name, item_name, media_type, pos):
        menu = QMenu(self)
        act_paste = menu.addAction("Paste")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_paste:
            self.sig_file_paste.emit(project_name, item_name, media_type)

    def add_project_item(self, project_name, project_path):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if not items:
            item = QTreeWidgetItem(self.project_tree)
            item.setText(0, project_name)
            item.setIcon(0, self.icon_dir)
            item.setData(0, Qt.ItemDataRole.UserRole, project_path)
            self.project_tree.addTopLevelItem(item)
            item.setExpanded(True)
            self.project_tree.setCurrentItem(item)

    def add_structure_item(self, project_name, folder_name, item_path):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            project_item = items[0]
            found = False
            for i in range(project_item.childCount()):
                if project_item.child(i).text(0) == folder_name:
                    found = True
                    break

            if not found:
                folder_item = QTreeWidgetItem(project_item)
                folder_item.setText(0, folder_name)
                folder_item.setIcon(0, self.icon_dir_closed)
                folder_item.setData(0, Qt.ItemDataRole.UserRole, item_path)

                image_node = QTreeWidgetItem(folder_item)
                image_node.setText(0, "Image")
                image_node.setIcon(0, self.icon_dir)
                image_node.setData(0, self.MEDIA_LOADED_ROLE, False)
                image_node.setChildIndicatorPolicy(
                    QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
                )

                video_node = QTreeWidgetItem(folder_item)
                video_node.setText(0, "Video")
                video_node.setIcon(0, self.icon_dir)
                video_node.setData(0, self.MEDIA_LOADED_ROLE, False)
                video_node.setChildIndicatorPolicy(
                    QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
                )

                self._watch_item_media(item_path, project_name, folder_name)
                self._refresh_media_node(
                    project_name, folder_name, "Image"
                )
                self._refresh_media_node(
                    project_name, folder_name, "Video"
                )

            project_item.setExpanded(True)

    @pyqtSlot(QTreeWidgetItem)
    def _on_item_expanded(self, item):
        if item is None or item.text(0) not in ("Image", "Video"):
            return
        if item.data(0, self.MEDIA_LOADED_ROLE):
            return
        folder_item = item.parent()
        if folder_item is None:
            return
        project_item = folder_item.parent()
        if project_item is None:
            return
        item_path = folder_item.data(0, Qt.ItemDataRole.UserRole)
        media_dir = (
            os.path.join(item_path, item.text(0)) if item_path else None
        )
        cached_names = self._media_name_cache.get(media_dir)
        if (
            cached_names is not None
            and media_dir not in self._media_scan_workers
            and media_dir not in self._pending_media_refreshes
        ):
            self._apply_media_scan(
                project_item.text(0),
                folder_item.text(0),
                item.text(0),
                media_dir,
                cached_names,
            )
            return
        self._refresh_media_node(
            project_item.text(0), folder_item.text(0), item.text(0)
        )

    def _watch_item_media(self, item_path, project_name, item_name):
        image_dir = os.path.join(item_path, "Image")
        video_dir = os.path.join(item_path, "Video")
        for media_dir in (image_dir, video_dir):
            if os.path.exists(media_dir) and media_dir not in self.watched_paths:
                self.fs_watcher.addPath(media_dir)
                self.watched_paths[media_dir] = (project_name, item_name, os.path.basename(media_dir))

    def _unwatch_item_media(self, item_path):
        image_dir = os.path.join(item_path, "Image")
        video_dir = os.path.join(item_path, "Video")
        for media_dir in (image_dir, video_dir):
            if media_dir in self.watched_paths:
                self.fs_watcher.removePath(media_dir)
                del self.watched_paths[media_dir]
            self._media_scan_queue.pop(media_dir, None)
            self._media_name_cache.pop(media_dir, None)
            self._pending_media_refreshes.discard(media_dir)

    @pyqtSlot(str, str)
    def unwatch_item_media(self, project_name, folder_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            for i in range(items[0].childCount()):
                child = items[0].child(i)
                if child.text(0) == folder_name:
                    item_path = child.data(0, Qt.ItemDataRole.UserRole)
                    if item_path:
                        self._unwatch_item_media(item_path)
                    break

    @pyqtSlot(str)
    def unwatch_project_media(self, project_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            proj_item = items[0]
            for i in range(proj_item.childCount()):
                child = proj_item.child(i)
                item_path = child.data(0, Qt.ItemDataRole.UserRole)
                if item_path:
                    self._unwatch_item_media(item_path)

    @pyqtSlot(str)
    def on_directory_changed(self, path):
        info = self.watched_paths.get(path)
        if not info:
            return
        project_name, item_name, media_type = info
        self._refresh_media_node(project_name, item_name, media_type)

    @pyqtSlot(str, str, str, str)
    def notify_media_created(
        self, project_name, item_name, media_type, full_path
    ):
        """Reveal a newly captured media file without relying on OS watcher timing."""
        if media_type not in ("Image", "Video") or not os.path.isfile(full_path):
            return

        project_items = self.project_tree.findItems(
            project_name, Qt.MatchFlag.MatchExactly
        )
        if not project_items:
            return
        project_item = project_items[0]
        item_node = next(
            (
                project_item.child(index)
                for index in range(project_item.childCount())
                if project_item.child(index).text(0) == item_name
            ),
            None,
        )
        if item_node is None:
            return

        item_path = item_node.data(0, Qt.ItemDataRole.UserRole)
        if not item_path:
            return
        media_dir = os.path.join(item_path, media_type)
        expected_dir = os.path.normcase(os.path.abspath(media_dir))
        actual_dir = os.path.normcase(
            os.path.abspath(os.path.dirname(full_path))
        )
        if actual_dir != expected_dir:
            return

        media_node = next(
            (
                item_node.child(index)
                for index in range(item_node.childCount())
                if item_node.child(index).text(0) == media_type
            ),
            None,
        )
        if media_node is None:
            return

        filename = os.path.basename(full_path)
        media_node.setChildIndicatorPolicy(
            QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator
        )
        existing_names = [
            media_node.child(index).text(0)
            for index in range(media_node.childCount())
        ]
        if filename not in existing_names:
            file_item = QTreeWidgetItem()
            file_item.setText(0, filename)
            file_item.setIcon(
                0,
                self.icon_image if media_type == "Image" else self.icon_video,
            )
            sort_key = filename.casefold()
            insert_at = next(
                (
                    index
                    for index, name in enumerate(existing_names)
                    if sort_key < name.casefold()
                ),
                media_node.childCount(),
            )
            media_node.insertChild(insert_at, file_item)

        cached_names = self._media_name_cache.get(media_dir)
        if cached_names is not None:
            self._media_name_cache[media_dir] = sorted(
                set(cached_names) | {filename},
                key=str.casefold,
            )
        project_item.setExpanded(True)
        item_node.setExpanded(True)
        was_expanded = media_node.isExpanded()
        media_node.setExpanded(True)
        if was_expanded:
            self._refresh_media_node(project_name, item_name, media_type)

    def _refresh_media_node(self, project_name, item_name, media_type):
        if self._shutting_down:
            return
        proj_items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if not proj_items:
            return
        proj_item = proj_items[0]

        item_node = None
        for i in range(proj_item.childCount()):
            if proj_item.child(i).text(0) == item_name:
                item_node = proj_item.child(i)
                break
        if not item_node:
            return

        media_node = None
        for i in range(item_node.childCount()):
            if item_node.child(i).text(0) == media_type:
                media_node = item_node.child(i)
                break
        if not media_node:
            return

        item_path = item_node.data(0, Qt.ItemDataRole.UserRole)
        if not item_path:
            return
        media_dir = os.path.join(item_path, media_type)
        if not os.path.exists(media_dir):
            return

        existing_worker = self._media_scan_workers.get(media_dir)
        if existing_worker is not None and existing_worker.isRunning():
            self._pending_media_refreshes.add(media_dir)
            return
        if media_dir in self._media_scan_queue:
            return

        media_node.setData(0, self.MEDIA_LOADED_ROLE, False)
        self._media_scan_queue[media_dir] = (
            project_name,
            item_name,
            media_type,
        )
        self._start_queued_media_scans()

    def _start_queued_media_scans(self):
        while (
            not self._shutting_down
            and self._media_scan_queue
            and len(self._media_scan_workers)
            < self.MAX_CONCURRENT_MEDIA_SCANS
        ):
            media_dir = next(iter(self._media_scan_queue))
            project_name, item_name, media_type = (
                self._media_scan_queue.pop(media_dir)
            )
            if media_dir not in self.watched_paths:
                continue

            worker = FunctionWorker(
                self._scan_media_directory, media_dir, media_type
            )
            self._media_scan_workers[media_dir] = worker
            worker.result_ready.connect(
                lambda names, p=project_name, i=item_name, m=media_type,
                       path=media_dir: self._apply_media_scan(
                    p, i, m, path, names
                )
            )
            worker.error_occurred.connect(
                lambda message, path=media_dir: print(
                    f"Error scanning {path}: {message}"
                )
            )
            worker.finished.connect(
                lambda path=media_dir, current=worker: self._finish_media_scan(
                    path, current
                )
            )
            worker.finished.connect(worker.deleteLater)
            worker.start()

    @staticmethod
    def _scan_media_directory(media_dir, media_type):
        valid_extensions = ProjectSidebar.MEDIA_EXTENSIONS.get(
            media_type, ()
        )
        with os.scandir(media_dir) as entries:
            names = [
                entry.name
                for entry in entries
                if entry.is_file()
                and os.path.splitext(entry.name)[1].lower() in valid_extensions
            ]
        return sorted(names, key=str.casefold)

    def _finish_media_scan(self, media_dir, worker):
        if self._media_scan_workers.get(media_dir) is worker:
            del self._media_scan_workers[media_dir]
        if media_dir in self._pending_media_refreshes:
            self._pending_media_refreshes.discard(media_dir)
            info = self.watched_paths.get(media_dir)
            if info and not self._shutting_down:
                self._media_scan_queue[media_dir] = info
        self._start_queued_media_scans()

    def _apply_media_scan(
        self, project_name, item_name, media_type, media_dir, names
    ):
        if media_dir in self._pending_media_refreshes:
            return
        current_info = self.watched_paths.get(media_dir)
        if current_info != (project_name, item_name, media_type):
            return

        project_items = self.project_tree.findItems(
            project_name, Qt.MatchFlag.MatchExactly
        )
        if not project_items:
            return
        project_item = project_items[0]
        item_node = next(
            (
                project_item.child(index)
                for index in range(project_item.childCount())
                if project_item.child(index).text(0) == item_name
            ),
            None,
        )
        if item_node is None:
            return
        media_node = next(
            (
                item_node.child(index)
                for index in range(item_node.childCount())
                if item_node.child(index).text(0) == media_type
            ),
            None,
        )
        if media_node is None:
            return

        names = list(names)
        self._media_name_cache[media_dir] = names
        media_node.setChildIndicatorPolicy(
            QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator
            if names
            else QTreeWidgetItem.ChildIndicatorPolicy.DontShowIndicatorWhenChildless
        )
        self.project_tree.viewport().update()

        if not media_node.isExpanded():
            media_node.takeChildren()
            media_node.setData(0, self.MEDIA_LOADED_ROLE, False)
            return

        media_node.takeChildren()
        self._append_media_batch(media_node, media_type, names, 0)

    def _append_media_batch(self, media_node, media_type, names, start):
        if media_node.treeWidget() is not self.project_tree:
            return
        end = min(start + 200, len(names))
        icon = self.icon_image if media_type == "Image" else self.icon_video
        for name in names[start:end]:
            file_item = QTreeWidgetItem(media_node)
            file_item.setText(0, name)
            file_item.setIcon(0, icon)
        if end < len(names):
            QTimer.singleShot(
                0,
                lambda: self._append_media_batch(
                    media_node, media_type, names, end
                ),
            )
        else:
            media_node.setData(0, self.MEDIA_LOADED_ROLE, True)

    def shutdown(self, wait_ms=500):
        self._shutting_down = True
        self._media_scan_queue.clear()
        self._pending_media_refreshes.clear()
        still_running = False
        for worker in list(self._media_scan_workers.values()):
            if worker.isRunning():
                worker.requestInterruption()
                worker.wait(wait_ms)
            still_running = still_running or worker.isRunning()
        if not still_running:
            self._media_scan_workers.clear()
            self._media_name_cache.clear()
        return not still_running

    def remove_project_item(self, project_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        for item in items:
            for i in range(item.childCount()):
                child = item.child(i)
                item_path = child.data(0, Qt.ItemDataRole.UserRole)
                if item_path:
                    self._unwatch_item_media(item_path)
            index = self.project_tree.indexOfTopLevelItem(item)
            removed = self.project_tree.takeTopLevelItem(index)
            del removed

    def remove_item_node(self, project_name, folder_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            project_item = items[0]
            for i in range(project_item.childCount()):
                child = project_item.child(i)
                if child.text(0) == folder_name:
                    item_path = child.data(0, Qt.ItemDataRole.UserRole)
                    if item_path:
                        self._unwatch_item_media(item_path)
                    project_item.removeChild(child)
                    del child
                    break

    def clear_all_items(self):
        for path in list(self.watched_paths.keys()):
            self.fs_watcher.removePath(path)
        self.watched_paths.clear()
        self.project_tree.clear()

    def collapse_all(self):
        root = self.project_tree.invisibleRootItem()

        def collapse_recursive(item):
            if item.isExpanded():
                item.setExpanded(False)
            for i in range(item.childCount()):
                collapse_recursive(item.child(i))

        collapse_recursive(root)

    def rename_project_item(self, old_name, new_name):
        items = self.project_tree.findItems(old_name, Qt.MatchFlag.MatchExactly)
        if items:
            proj_item = items[0]
            proj_item.setText(0, new_name)

            old_proj_path = proj_item.data(0, Qt.ItemDataRole.UserRole)
            parent_dir = os.path.dirname(old_proj_path)
            new_proj_path = os.path.join(parent_dir, new_name)
            proj_item.setData(0, Qt.ItemDataRole.UserRole, new_proj_path)

            for i in range(proj_item.childCount()):
                child = proj_item.child(i)
                item_name = child.text(0)
                new_item_path = os.path.join(new_proj_path, item_name)
                child.setData(0, Qt.ItemDataRole.UserRole, new_item_path)
                self._watch_item_media(new_item_path, new_name, item_name)

    def rename_item_node(self, project_name, old_name, new_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            project_item = items[0]
            for i in range(project_item.childCount()):
                child = project_item.child(i)
                if child.text(0) == old_name:
                    child.setText(0, new_name)

                    project_path = project_item.data(0, Qt.ItemDataRole.UserRole)
                    new_path = os.path.join(project_path, new_name)
                    child.setData(0, Qt.ItemDataRole.UserRole, new_path)

                    self._watch_item_media(new_path, project_name, new_name)
                    break

    def get_current_project(self):
        root = self._get_project_root_of(self.project_tree.currentItem())
        return root.text(0) if root else None

    def get_current_selection_info(self):
        item = self.project_tree.currentItem()
        if not item:
            return None, None, None
        project_root = self._get_project_root_of(item)
        if not project_root:
            return None, None, None
        project_name = project_root.text(0)

        if item == project_root:
            return project_name, None, 'PROJECT'

        folder_node = item
        while folder_node.parent() != project_root:
            folder_node = folder_node.parent()
            if folder_node is None:
                return project_name, None, 'PROJECT'
        return project_name, folder_node.text(0), 'ITEM'

    def get_expanded_paths(self):
        paths = []
        root = self.project_tree.invisibleRootItem()

        def traverse(item, parent_path):
            if item.isExpanded():
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data:
                    paths.append(data)
                else:
                    if item.text(0) in ["Image", "Video"] and parent_path:
                        paths.append(os.path.join(parent_path, item.text(0)))
            for i in range(item.childCount()):
                child = item.child(i)
                child_parent_path = None
                child_data = child.data(0, Qt.ItemDataRole.UserRole)
                if child_data:
                    child_parent_path = child_data
                elif parent_path and child.text(0) in ["Image", "Video"]:
                    child_parent_path = os.path.join(parent_path, child.text(0))
                else:
                    child_parent_path = parent_path
                traverse(child, child_parent_path)

        traverse(root, None)
        return paths

    def restore_expanded_paths(self, paths):
        expanded_set = set(os.path.normpath(p) for p in paths)
        self.collapse_all()

        def expand_node(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                norm_data = os.path.normpath(data)
                if norm_data in expanded_set:
                    self._expand_with_parents(item)
            parent = item.parent()
            if parent and item.text(0) in ["Image", "Video"]:
                parent_path = parent.data(0, Qt.ItemDataRole.UserRole)
                if parent_path:
                    media_path = os.path.normpath(os.path.join(parent_path, item.text(0)))
                    if media_path in expanded_set:
                        self._expand_with_parents(item)
            for i in range(item.childCount()):
                expand_node(item.child(i))

        root = self.project_tree.invisibleRootItem()
        expand_node(root)

    def _expand_with_parents(self, item):
        while item is not None:
            item.setExpanded(True)
            item = item.parent()
