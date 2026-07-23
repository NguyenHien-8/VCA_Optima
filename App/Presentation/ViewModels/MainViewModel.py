# App/Presentation/ViewModels/MainViewModel.py
import os
from typing import List
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QCoreApplication, QThread

from App.Models.Vision.CameraManager import CameraManager
from App.Models.Controllers.HardwareManager import HardwareManager
from App.Models.ProjectManager import ProjectManager
from App.Models.ControlPanelManager import ControlPanelManager
from App.Presentation.ViewModels.Workers import FileOperationWorker, FileLoaderWorker, FileMediaWorker
from App.Infrastructure.Repositories.ConfigRepository import ConfigRepository
from App.Infrastructure.Repositories.SessionRepository import SessionRepository
from App.Models.SessionManager import SessionManager
from App.Models.Vision.CameraFrameDispatcher import CameraFrameDispatcher

class MainViewModel(QObject):
    status_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    project_added = pyqtSignal(str, str)
    project_removed = pyqtSignal(str)
    project_renamed = pyqtSignal(str, str)
    item_added = pyqtSignal(str, str, str)
    item_removed = pyqtSignal(str, str)
    item_renamed = pyqtSignal(str, str, str)
    file_loaded = pyqtSignal(bool, str, str, str, str)
    camera_error = pyqtSignal(str)
    open_editor_requested = pyqtSignal(str, str)  # full_path, project_name
    file_renamed = pyqtSignal(str, str, str, str, str)  # project_name, item_name, media_type, old_name, new_name

    # === SIGNAL FOR SPLASH SCREEN ===
    progress_update = pyqtSignal(str)
    
    # Signal to request MainView to close editors and remove watchers before file system operations
    request_close_editors_for_item = pyqtSignal(str, str)  # project_name, folder_name
    request_unwatch_item = pyqtSignal(str, str)  # project_name, folder_name
    request_unwatch_project = pyqtSignal(str)    # project_name

    # Signal to stop video player before renaming a video file
    request_stop_video_editor = pyqtSignal(str)  # full_path
    request_close_editor_for_file = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.progress_update.emit("Initializing components...")

        self.camera_manager = CameraManager()
        self.hardware_manager = HardwareManager()
        self.control_panel_manager = ControlPanelManager(self.hardware_manager)
        self.project_manager = ProjectManager()
        self.config_repo = ConfigRepository()
        self.pm = ProjectManager()

        self.progress_update.emit("Loading configurations...")
        self._load_saved_configurations()

        self.camera_dispatcher = CameraFrameDispatcher(self.camera_manager)

        self.untitled_count = 1
        self.clipboard_data = None
        self.file_clipboard = None
        self.active_workers = []
        self.opened_items = {}

        # === Initialize Session Management ===
        self.session_repo = SessionRepository()
        self.session_manager = SessionManager(self.session_repo)
        self.camera_manager.error_occurred_signal.connect(self.camera_error)

        self.progress_update.emit("Configuration loaded.")

    def _add_opened_item(self, project_name, item_name):
        if project_name not in self.opened_items:
            self.opened_items[project_name] = set()
        self.opened_items[project_name].add(item_name)

    def _remove_opened_item(self, project_name, item_name):
        if project_name in self.opened_items and item_name in self.opened_items[project_name]:
            self.opened_items[project_name].remove(item_name)
            if not self.opened_items[project_name]:
                del self.opened_items[project_name]

    def _remove_project_items(self, project_name):
        if project_name in self.opened_items:
            del self.opened_items[project_name]

    def get_camera_dispatcher(self):
        return self.camera_dispatcher

    def restore_session(self):
        self.progress_update.emit("Restoring session...")
        self.session_manager.load_all()
        project_paths = self.session_manager.get_open_projects()
        # Load saved opened_items
        saved_opened_items = self.session_manager.get_opened_items()

        for path in project_paths:
            self.progress_update.emit(f"Opening project: {os.path.basename(path)}")
            if os.path.isdir(path):
                self.handle_open_project(path)
            else:
                print(f"[Session] Project path not found, skipped: {path}")

        # After opening all projects, filter out items not saved in saved_opened_items
        for proj_name, saved_items in saved_opened_items.items():
            current_items = self.opened_items.get(proj_name, set())
            items_to_remove = current_items - saved_items
            for item in items_to_remove:
                self.item_removed.emit(proj_name, item)
                self._remove_opened_item(proj_name, item)

        editor_list = self.session_manager.get_open_editors()
        for editor_info in editor_list:
            full_path = editor_info.get("full_path")
            project_name = editor_info.get("project_name")
            if full_path and project_name and os.path.isfile(full_path):
                if project_name in self.project_manager.current_projects:
                    self.progress_update.emit(f"Opening file: {os.path.basename(full_path)}")
                    self.open_editor_requested.emit(full_path, project_name)
                else:
                    print(f"[Session] Editor's project '{project_name}' not found, skipped: {full_path}")
            else:
                print(f"[Session] Invalid editor info: {editor_info}")
        self.progress_update.emit("Session restored.")

    def get_expanded_paths(self) -> List[str]:
        return self.session_manager.get_expanded_paths()

    def save_session_with_editors(self, editor_list, expanded_paths):
        project_paths = list(self.project_manager.current_projects.values())
        self.session_manager.set_open_projects(project_paths)
        self.session_manager.set_open_editors(editor_list)
        self.session_manager.set_expanded_paths(expanded_paths)
        # Save opened_items
        self.session_manager.set_opened_items(self.opened_items)
        self.session_manager.save_all()

    def get_project_path(self, project_name: str) -> str:
        return self.project_manager.current_projects.get(project_name, "")

    def is_project_temp(self, project_name: str) -> bool:
        return self.project_manager.is_project_temp(project_name)

    def get_item_path(self, project_name: str, item_name: str) -> str:
        # If project_name is not in current_projects, treat item_name as full_path
        if project_name not in self.project_manager.current_projects:
            return item_name
        return self.project_manager.get_file_path(project_name, item_name)

    def get_all_project_names(self) -> list:
        return list(self.project_manager.current_projects.keys())

    def _load_saved_configurations(self):
        cam_index = self.config_repo.load_camera_index()
        if cam_index is not None:
            self.camera_manager.active_camera_index = cam_index
        else:
            self.camera_manager.active_camera_index = None

        hw_config = self.config_repo.load_hardware_config()
        port = hw_config.get("port", "")
        baud = hw_config.get("baud", 115200)
        period = hw_config.get("period", 100)

        self.hardware_manager.save_config({
            "port": port,
            "baud": baud,
            "query_period": period
        })

        if port and port.strip():
            self.hardware_manager.connect_hardware(port, baud)

    def on_editor_opened(self):
        self.camera_manager.acquire()

    def on_editor_closed(self):
        self.camera_manager.release()

    def start_worker(self, worker):
        self.active_workers.append(worker)
        worker.finished.connect(self.cleanup_worker)
        worker.start()

    @pyqtSlot()
    def cleanup_worker(self):
        worker = self.sender()
        if worker in self.active_workers:
            self.active_workers.remove(worker)

    def shutdown_workers(self):
        for worker in self.active_workers[:]: 
            if worker.isRunning():
                worker.quit()
                worker.wait()
            try:
                worker.finished.disconnect()
            except:
                pass
            self.active_workers.remove(worker)

    def handle_create_project(self):
        name = f"Untitled-{self.untitled_count}"
        try:
            success, result = self.project_manager.create_project(name)
            if success:
                self.project_added.emit(name, result)
                self.untitled_count += 1
                self.status_message.emit(f"Project '{name}' created.")
            else:
                self.error_occurred.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def handle_new_item(self, project_name: str, folder_name: str):
        success, msg = self.project_manager.create_structure(project_name, folder_name)
        if success:
            self.item_added.emit(project_name, folder_name, msg)
            self._add_opened_item(project_name, folder_name)
            self.status_message.emit(f"Item '{folder_name}' created.")
        else:
            self.error_occurred.emit(msg)

    def handle_open_project(self, folder_path):
        success, project_name, items = self.project_manager.open_project(folder_path)
        if success:
            self.project_added.emit(project_name, folder_path)
            for item_name in items:
                item_path = os.path.join(folder_path, item_name)
                self.item_added.emit(project_name, item_name, item_path)
                self._add_opened_item(project_name, item_name)
            self.status_message.emit(f"Project '{project_name}' loaded.")
        else:
            self.error_occurred.emit(project_name)

    def handle_open_item(self, project_name: str, folder_path: str):
        folder_name = os.path.basename(folder_path)
        # Check if item is already open in sidebar
        if project_name in self.opened_items and folder_name in self.opened_items[project_name]:
            self.error_occurred.emit(f"Item '{folder_name}' already exists in sidebar.")
            return

        success, msg, item_name, item_path = self.project_manager.open_item(project_name, folder_path)
        if success:
            self.item_added.emit(project_name, item_name, item_path)
            self._add_opened_item(project_name, item_name)
            self.status_message.emit(f"Item '{item_name}' opened.")
        else:
            self.error_occurred.emit(msg)

    def handle_delete_item(self, project_name: str, folder_name: str, delete_from_disk: bool):
        if delete_from_disk:
            self.request_unwatch_item.emit(project_name, folder_name)
            self.request_close_editors_for_item.emit(project_name, folder_name)
            QCoreApplication.processEvents()

            success, msg = self.project_manager.delete_item(project_name, folder_name)
            if success:
                self._remove_opened_item(project_name, folder_name)
                self.item_removed.emit(project_name, folder_name)
                self.status_message.emit(f"Item '{folder_name}' deleted permanently.")
            else:
                self.error_occurred.emit(msg)
        else:
            # Only remove from tree, do not delete files
            self._remove_opened_item(project_name, folder_name)
            self.item_removed.emit(project_name, folder_name)

    def handle_rename_item(self, project_name: str, old_name: str, new_name: str):
        if new_name and new_name != old_name:
            self.request_unwatch_item.emit(project_name, old_name)
            self.request_close_editors_for_item.emit(project_name, old_name)
            QCoreApplication.processEvents()

            success, msg = self.project_manager.rename_item(project_name, old_name, new_name)
            if success:
                # Update opened_items
                if project_name in self.opened_items and old_name in self.opened_items[project_name]:
                    self.opened_items[project_name].remove(old_name)
                    self.opened_items[project_name].add(new_name)
                self.item_renamed.emit(project_name, old_name, new_name)
                self.status_message.emit(f"Item renamed to '{new_name}'.")
            else:
                self.error_occurred.emit(msg)

    def handle_save_as_project(self, project_name: str, target_folder: str):
        if not target_folder:
            return
        self.request_unwatch_project.emit(project_name)
        self.request_close_editors_for_item.emit(project_name, "")
        QCoreApplication.processEvents()

        success, msg = self.project_manager.save_project_as(project_name, target_folder)
        if success:
            # Remove old project from sidebar and from opened_items
            self._remove_project_items(project_name)
            self.project_removed.emit(project_name)
            # Add new project
            new_path = self.project_manager.get_project_path(project_name)
            self.project_added.emit(project_name, new_path)
            # Add all items back
            items = self.project_manager.get_project_items(project_name)
            for item_name in items:
                item_path = os.path.join(new_path, item_name)
                self.item_added.emit(project_name, item_name, item_path)
                self._add_opened_item(project_name, item_name)
            self.status_message.emit(f"Project saved to {msg}")
        else:
            self.error_occurred.emit(msg)

    def handle_save_as_item(self, project_name: str, item_name: str):
        success, msg = self.project_manager.save_item_as(project_name, item_name)
        if success:
            self.status_message.emit(f"Item '{item_name}' marked as saved.")
        else:
            self.error_occurred.emit(msg)

    def handle_delete_project(self, project_name: str, delete_from_disk: bool):
        if delete_from_disk:
            self.request_unwatch_project.emit(project_name)
            self.request_close_editors_for_item.emit(project_name, "")
            QCoreApplication.processEvents()

            success, msg = self.project_manager.delete_project(project_name)
            if success:
                self._remove_project_items(project_name)
                self.project_removed.emit(project_name)
                self.status_message.emit(f"Project '{project_name}' deleted.")
            else:
                self.error_occurred.emit(msg)
        else:
            # Only close project, do not delete files
            self.project_manager.close_project(project_name)
            self._remove_project_items(project_name)
            self.project_removed.emit(project_name)

    def handle_rename_project(self, old_name: str, new_name: str):
        if new_name and new_name != old_name:
            self.request_unwatch_project.emit(old_name)
            self.request_close_editors_for_item.emit(old_name, "")
            QCoreApplication.processEvents()

            success, msg = self.project_manager.rename_project(old_name, new_name)
            if success:
                # Update opened_items
                if old_name in self.opened_items:
                    self.opened_items[new_name] = self.opened_items.pop(old_name)
                self.project_renamed.emit(old_name, new_name)
                self.status_message.emit(f"Project renamed to '{new_name}'.")
            else:
                self.error_occurred.emit(msg)

    def handle_copy_item(self, project_name: str, folder_name: str):
        self.clipboard_data = {'project': project_name, 'folder': folder_name, 'action': 'COPY'}
        self.status_message.emit(f"Copied '{folder_name}'.")

    def handle_cut_item(self, project_name: str, folder_name: str):
        self.clipboard_data = {'project': project_name, 'folder': folder_name, 'action': 'CUT'}
        self.status_message.emit(f"Cut '{folder_name}'.")

    def handle_paste_item(self, target_project_name: str):
        if not self.clipboard_data:
            self.error_occurred.emit("Clipboard is empty.")
            return
        src_project = self.clipboard_data['project']
        src_folder = self.clipboard_data['folder']
        action = self.clipboard_data['action']
        worker = FileOperationWorker(
            self.project_manager, src_project, src_folder, target_project_name, action
        )
        worker.sig_finished.connect(self._on_paste_finished)
        self.start_worker(worker)
        self.status_message.emit(f"Started {action} '{src_folder}' in background...")

    @pyqtSlot(bool, str, str, str, str)
    def _on_paste_finished(self, success, msg, new_name, action_type, target_project):
        if success:
            target_project_path = self.get_project_path(target_project)
            new_item_path = os.path.join(target_project_path, new_name)
            self.item_added.emit(target_project, new_name, new_item_path)
            self._add_opened_item(target_project, new_name)
            if action_type == 'CUT' and self.clipboard_data:
                src_project = self.clipboard_data['project']
                src_folder = self.clipboard_data['folder']
                self.item_removed.emit(src_project, src_folder)
                self._remove_opened_item(src_project, src_folder)
                self.clipboard_data = None
                self.status_message.emit(f"Moved '{new_name}'.")
            else:
                self.status_message.emit(f"Pasted '{new_name}'.")
        else:
            self.error_occurred.emit(msg)

    def handle_copy_file(self, project_name, item_name, media_type, file_name):
        self.file_clipboard = {
            'project': project_name,
            'item': item_name,
            'media': media_type,
            'file': file_name,
            'action': 'COPY'
        }
        self.status_message.emit(f"Copied file '{file_name}'.")

    def handle_cut_file(self, project_name, item_name, media_type, file_name):
        self.file_clipboard = {
            'project': project_name,
            'item': item_name,
            'media': media_type,
            'file': file_name,
            'action': 'CUT'
        }
        self.status_message.emit(f"Cut file '{file_name}'.")

    def handle_rename_file(self, project_name, item_name, media_type, old_name, new_name):
        # Build full old path
        project_path = self.get_project_path(project_name)
        if media_type and media_type.strip():
            old_full_path = os.path.join(project_path, item_name, media_type, old_name)
        else:
            old_full_path = os.path.join(project_path, item_name, old_name)

        # If it's a video file, stop player before renaming
        if old_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            self.request_stop_video_editor.emit(old_full_path)
            # Process events and wait a bit for player to release file
            from PyQt6.QtCore import QCoreApplication, QThread
            for _ in range(5):
                QCoreApplication.processEvents()
                QThread.msleep(20)

        success, msg = self.project_manager.rename_file(project_name, item_name, media_type, old_name, new_name)
        if success:
            self.status_message.emit(f"File renamed to '{new_name}'.")
            self.file_renamed.emit(project_name, item_name, media_type, old_name, new_name)
        else:
            self.error_occurred.emit(msg)

    def handle_delete_file(self, project_name, item_name, media_type, file_name):
        # Build full path
        project_path = self.get_project_path(project_name)
        if media_type and media_type.strip():
            full_path = os.path.join(project_path, item_name, media_type, file_name)
        else:
            full_path = os.path.join(project_path, item_name, file_name)

        # If it's a video file, stop player first
        if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):
            self.request_stop_video_editor.emit(full_path)
            # Process events to allow player to release file
            for _ in range(5):
                QCoreApplication.processEvents()
                QThread.msleep(20)

        # Request to close editor tab if open
        self.request_close_editor_for_file.emit(full_path)
        QCoreApplication.processEvents()  # Ensure tab is closed before deleting file

        # Perform file deletion
        success, msg = self.project_manager.delete_file(project_name, item_name, media_type, file_name)
        if success:
            self.status_message.emit(f"File '{file_name}' deleted.")
        else:
            self.error_occurred.emit(msg)

    def handle_paste_file(self, target_project, target_item, target_media):
        if not self.file_clipboard:
            self.error_occurred.emit("No file in clipboard.")
            return
        src_project = self.file_clipboard['project']
        src_item = self.file_clipboard['item']
        src_media = self.file_clipboard['media']
        src_file = self.file_clipboard['file']
        action = self.file_clipboard['action']
        if src_media != target_media:
            self.error_occurred.emit("Cannot paste to a different media folder.")
            return
        worker = FileMediaWorker(
            self.project_manager,
            src_project, src_item, src_media, src_file,
            target_project, target_item, target_media,
            action
        )
        worker.sig_finished.connect(self._on_file_paste_finished)
        self.start_worker(worker)
        self.status_message.emit(f"Pasting file '{src_file}'...")

    @pyqtSlot(bool, str, str, str, str, str, str)
    def _on_file_paste_finished(self, success, msg, new_file_name, action_type, target_project, target_item, target_media):
        if success:
            if action_type == 'CUT' and self.file_clipboard:
                self.file_clipboard = None
                self.status_message.emit(f"Moved file to '{new_file_name}'.")
            else:
                self.status_message.emit(f"Pasted file as '{new_file_name}'.")
        else:
            self.error_occurred.emit(msg)

    def load_file_confirmed(self, full_path: str, project_name: str):
        self._load_file(full_path, project_name)

    def _load_file(self, full_path: str, project_name: str):
        worker = FileLoaderWorker(full_path, project_name)
        worker.sig_loaded.connect(self.file_loaded)
        self.start_worker(worker)
        self.status_message.emit(f"Loading file...")

    def handle_save_file_content(self, content: str, project_name: str, file_name: str, full_path: str):
        try:
            if not full_path or not os.path.exists(os.path.dirname(full_path)):
                full_path = self.project_manager.get_file_path(project_name, file_name)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_message.emit(f"Saved changes to '{file_name}'.")
        except Exception as e:
            self.error_occurred.emit(f"Could not save file:\n{str(e)}")