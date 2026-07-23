# App/Presentation/Views/Widgets/SideBar.py
import os
from PyQt6.QtWidgets import (QDockWidget, QTabWidget, QWidget, QVBoxLayout,
                             QTreeWidget, QTreeWidgetItem, QMenu, QAbstractItemView, QStyle)
from PyQt6.QtGui import QIcon, QDrag, QAction
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QMimeData, QFileSystemWatcher

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

class ProjectSidebar(QDockWidget):
    sig_new_item = pyqtSignal(str)
    sig_delete = pyqtSignal(str)
    sig_rename = pyqtSignal(str)
    sig_save = pyqtSignal(str)
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

    def __init__(self, parent=None):
        super().__init__("Project Manager", parent)
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setMinimumWidth(200)
        self.setMaximumWidth(800)

        self.app_config = {
            "main_extension": ".tnh",
            "sub_folders": ["Image", "Video"],
            "valid_extensions": [".tnh", ".jpg", ".jpeg", ".png", ".mp4", ".avi"]
        }

        self._init_icons()

        # --- File system watcher để tự cập nhật media files ---
        self.fs_watcher = QFileSystemWatcher(self)
        self.fs_watcher.directoryChanged.connect(self.on_directory_changed)
        self.watched_paths = {}  # key: đường dẫn tuyệt đối, value: (project_name, item_name, media_type)

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
        self.icon_file = style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self.icon_media = style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)

    def setup_tab_project(self):
        layout = QVBoxLayout(self.tab_project)
        layout.setContentsMargins(0, 0, 0, 0)

        self.project_tree = DraggableTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setStyleSheet("border: 1px solid #C0C0C0;")

        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.project_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

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
        else:
            folder_node = item
            while folder_node.parent() != project_root:
                folder_node = folder_node.parent()

            folder_name = folder_node.text(0)
            self._show_item_context_menu(project_name, folder_name, pos)

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
        act_save = menu.addAction("Save")
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
        elif action == act_save:
            self.sig_save.emit(project_name)
        elif action == act_save_as:
            self.sig_save_as.emit(project_name)

    def _show_item_context_menu(self, project_name, folder_name, pos):
        menu = QMenu(self)
        act_copy = menu.addAction("Copy")
        act_cut = menu.addAction("Cut")
        act_save = menu.addAction("Save")
        menu.addSeparator()
        act_rename = menu.addAction("Rename")
        act_delete = menu.addAction("Delete")

        action = menu.exec(self.project_tree.mapToGlobal(pos))

        if action == act_copy:
            self.sig_item_copy.emit(project_name, folder_name)
        elif action == act_cut:
            self.sig_item_cut.emit(project_name, folder_name)
        elif action == act_save:
            self.sig_item_save.emit(project_name, folder_name)
        elif action == act_rename:
            self.sig_item_rename.emit(project_name, folder_name)
        elif action == act_delete:
            self.sig_item_delete.emit(project_name, folder_name)

    def add_project_item(self, project_name, project_path):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if not items:
            item = QTreeWidgetItem(self.project_tree)
            item.setText(0, project_name)
            item.setIcon(0, self.icon_dir)
            item.setData(0, Qt.ItemDataRole.UserRole, project_path)   # lưu đường dẫn project
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
                # Tạo folder item chính
                folder_item = QTreeWidgetItem(project_item)
                folder_item.setText(0, folder_name)
                folder_item.setIcon(0, self.icon_dir_closed)
                folder_item.setData(0, Qt.ItemDataRole.UserRole, item_path)   # lưu đường dẫn item

                # File .tnh
                main_ext = self.app_config["main_extension"]
                tnh_item = QTreeWidgetItem(folder_item)
                tnh_item.setText(0, f"{folder_name}{main_ext}")
                tnh_item.setIcon(0, self.icon_file)

                # Thư mục Image
                image_node = QTreeWidgetItem(folder_item)
                image_node.setText(0, "Image")
                image_node.setIcon(0, self.icon_dir)

                # Thư mục Video
                video_node = QTreeWidgetItem(folder_item)
                video_node.setText(0, "Video")
                video_node.setIcon(0, self.icon_dir)

                # Quét các file media có sẵn
                self._populate_media_files(folder_item, item_path)

                # Bắt đầu theo dõi thư mục Image và Video
                self._watch_item_media(item_path, project_name, folder_name)

            project_item.setExpanded(True)

    def _populate_media_files(self, folder_item, item_path):
        """Quét thư mục Image và Video, thêm các file media vào cây."""
        # Tìm node Image và Video trong folder_item
        image_node = None
        video_node = None
        for i in range(folder_item.childCount()):
            child = folder_item.child(i)
            if child.text(0) == "Image":
                image_node = child
            elif child.text(0) == "Video":
                video_node = child
        if image_node is None or video_node is None:
            return

        # Thư mục Image
        image_dir = os.path.join(item_path, "Image")
        if os.path.exists(image_dir):
            try:
                for f in os.listdir(image_dir):
                    full_path = os.path.join(image_dir, f)
                    if os.path.isfile(full_path) and f.lower().endswith(('.jpg', '.jpeg', '.png')):
                        file_item = QTreeWidgetItem(image_node)
                        file_item.setText(0, f)
                        file_item.setIcon(0, self.icon_file)
            except Exception as e:
                print(f"Lỗi quét thư mục Image: {e}")

        # Thư mục Video
        video_dir = os.path.join(item_path, "Video")
        if os.path.exists(video_dir):
            try:
                for f in os.listdir(video_dir):
                    full_path = os.path.join(video_dir, f)
                    if os.path.isfile(full_path) and f.lower().endswith('.mp4'):
                        file_item = QTreeWidgetItem(video_node)
                        file_item.setText(0, f)
                        file_item.setIcon(0, self.icon_file)
            except Exception as e:
                print(f"Lỗi quét thư mục Video: {e}")

    # --- Quản lý FileSystemWatcher ---

    def _watch_item_media(self, item_path, project_name, item_name):
        """Theo dõi các thư mục Image và Video của item."""
        image_dir = os.path.join(item_path, "Image")
        video_dir = os.path.join(item_path, "Video")
        for media_dir in (image_dir, video_dir):
            if os.path.exists(media_dir) and media_dir not in self.watched_paths:
                self.fs_watcher.addPath(media_dir)
                self.watched_paths[media_dir] = (project_name, item_name, os.path.basename(media_dir))  # 'Image' or 'Video'

    def _unwatch_item_media(self, item_path):
        """Ngừng theo dõi các thư mục của item."""
        image_dir = os.path.join(item_path, "Image")
        video_dir = os.path.join(item_path, "Video")
        for media_dir in (image_dir, video_dir):
            if media_dir in self.watched_paths:
                self.fs_watcher.removePath(media_dir)
                del self.watched_paths[media_dir]

    @pyqtSlot(str)
    def on_directory_changed(self, path):
        """Xử lý khi có thay đổi trong thư mục được theo dõi."""
        info = self.watched_paths.get(path)
        if not info:
            return
        project_name, item_name, media_type = info
        self._refresh_media_node(project_name, item_name, media_type)

    def _refresh_media_node(self, project_name, item_name, media_type):
        """Cập nhật lại nội dung của node Image hoặc Video."""
        # Tìm project_item
        proj_items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if not proj_items:
            return
        proj_item = proj_items[0]

        # Tìm item_node
        item_node = None
        for i in range(proj_item.childCount()):
            if proj_item.child(i).text(0) == item_name:
                item_node = proj_item.child(i)
                break
        if not item_node:
            return

        # Tìm media_node
        media_node = None
        for i in range(item_node.childCount()):
            if item_node.child(i).text(0) == media_type:
                media_node = item_node.child(i)
                break
        if not media_node:
            return

        # Xóa các node con cũ (các file)
        media_node.takeChildren()

        # Quét lại thư mục
        item_path = item_node.data(0, Qt.ItemDataRole.UserRole)
        if not item_path:
            return
        media_dir = os.path.join(item_path, media_type)
        if not os.path.exists(media_dir):
            return

        try:
            for f in os.listdir(media_dir):
                full_path = os.path.join(media_dir, f)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(f)[1].lower()
                    if media_type == "Image" and ext in ('.jpg', '.jpeg', '.png'):
                        file_item = QTreeWidgetItem(media_node)
                        file_item.setText(0, f)
                        file_item.setIcon(0, self.icon_file)
                    elif media_type == "Video" and ext == '.mp4':
                        file_item = QTreeWidgetItem(media_node)
                        file_item.setText(0, f)
                        file_item.setIcon(0, self.icon_file)
        except Exception as e:
            print(f"Lỗi quét {media_dir}: {e}")

    # --- Các phương thức xóa, đổi tên (đã cập nhật watcher) ---

    def remove_project_item(self, project_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        for item in items:
            # Trước khi xóa project, unwatch tất cả các item con
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
                    # Lấy item_path để unwatch
                    item_path = child.data(0, Qt.ItemDataRole.UserRole)
                    if item_path:
                        self._unwatch_item_media(item_path)
                    project_item.removeChild(child)
                    del child
                    break

    def clear_all_items(self):
        # Xóa tất cả các theo dõi
        for path in list(self.watched_paths.keys()):
            self.fs_watcher.removePath(path)
        self.watched_paths.clear()
        self.project_tree.clear()

    def rename_project_item(self, old_name, new_name):
        items = self.project_tree.findItems(old_name, Qt.MatchFlag.MatchExactly)
        if items:
            items[0].setText(0, new_name)
            # Không cần cập nhật watcher vì đường dẫn project không thay đổi (chỉ tên hiển thị)

    def rename_item_node(self, project_name, old_name, new_name):
        items = self.project_tree.findItems(project_name, Qt.MatchFlag.MatchExactly)
        if items:
            project_item = items[0]
            for i in range(project_item.childCount()):
                child = project_item.child(i)
                if child.text(0) == old_name:
                    # Lấy item_path cũ
                    old_path = child.data(0, Qt.ItemDataRole.UserRole)
                    if old_path:
                        self._unwatch_item_media(old_path)

                    # Đổi tên
                    child.setText(0, new_name)

                    # Cập nhật item_path mới
                    project_path = project_item.data(0, Qt.ItemDataRole.UserRole)  # đường dẫn project
                    new_path = os.path.join(project_path, new_name)
                    child.setData(0, Qt.ItemDataRole.UserRole, new_path)

                    # Đổi tên file .tnh bên trong (nếu có)
                    main_ext = self.app_config["main_extension"]
                    old_filename = f"{old_name}{main_ext}"
                    new_filename = f"{new_name}{main_ext}"
                    for k in range(child.childCount()):
                        grand_child = child.child(k)
                        if grand_child.text(0) == old_filename:
                            grand_child.setText(0, new_filename)
                            break

                    # Theo dõi lại media với đường dẫn mới
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