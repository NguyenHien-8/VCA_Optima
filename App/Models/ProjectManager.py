import os
import shutil
import json
import time
from pathlib import Path


class ProjectManager:
    """
    Class responsible for handling file/folder logic for Projects.
    Optimized for memory management and cleaning up temporary files.
    """

    def __init__(self):
        self.current_projects = {}
        self.project_states = {}
        self.item_states = {}

        documents_path = Path.home() / "Documents" / "TNH Optima Projects"
        self.temp_root = str(documents_path)
        os.makedirs(self.temp_root, exist_ok=True)

    def _get_project_root(self, project_name):
        return self.current_projects.get(project_name)

    def _cleanup_dict(self, project_name):
        if project_name in self.current_projects:
            del self.current_projects[project_name]
        if project_name in self.project_states:
            del self.project_states[project_name]
        if project_name in self.item_states:
            del self.item_states[project_name]

    def _safe_rename(self, old_path, new_path, retry_count=5, delay=0.3):
        for attempt in range(retry_count):
            try:
                os.rename(old_path, new_path)
                return True
            except OSError as e:
                if attempt < retry_count - 1:
                    time.sleep(delay)
                else:
                    raise e
        return False

    def create_project(self, project_name, specific_path=None):
        if specific_path:
            base_path = specific_path
            status = 'SAVED'
        else:
            base_path = self.temp_root
            status = 'TEMP'

        full_path = os.path.join(base_path, project_name)

        if os.path.exists(full_path):
            if specific_path is None:
                try:
                    shutil.rmtree(full_path)
                except OSError as e:
                    return False, f"Cannot clean old temp project: {e}"
            else:
                raise FileExistsError(f"Project '{project_name}' already exists.")

        try:
            os.makedirs(full_path, exist_ok=True)
            config_path = os.path.join(full_path, "config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

            self.current_projects[project_name] = full_path
            self.project_states[project_name] = status
            return True, full_path

        except Exception as e:
            return False, str(e)

    def save_project(self, project_name):
        if project_name not in self.current_projects:
            return False, "Project not found"
        return True, "Project Saved"

    def save_project_as(self, project_name, target_folder_path):
        source_path = self._get_project_root(project_name)
        if not source_path:
            return False, "Project not loaded"

        new_project_path = os.path.join(target_folder_path, project_name)

        if os.path.exists(new_project_path):
            return False, "Destination already exists."

        try:
            shutil.copytree(source_path, new_project_path)

            if self.is_project_temp(project_name):
                try:
                    shutil.rmtree(source_path)
                except Exception:
                    pass

            self.current_projects[project_name] = new_project_path
            self.project_states[project_name] = 'SAVED'

            return True, new_project_path
        except Exception as e:
            return False, str(e)

    def delete_project(self, project_name):
        full_path = self._get_project_root(project_name)
        if full_path and os.path.exists(full_path):
            try:
                shutil.rmtree(full_path)
                self._cleanup_dict(project_name)
                return True, "Deleted"
            except Exception as e:
                return False, str(e)
        return False, "Project path not found"
    
    def rename_project(self, old_name, new_name):
        if old_name not in self.current_projects:
            return False, "Project not found"

        old_path = self.current_projects[old_name]
        parent_dir = os.path.dirname(old_path)
        new_path = os.path.join(parent_dir, new_name)

        try:
            self._safe_rename(old_path, new_path)
            self.current_projects[new_name] = new_path
            self.project_states[new_name] = self.project_states[old_name]
            self._cleanup_dict(old_name)
            return True, "Success"
        except Exception as e:
            return False, str(e)
        
    def open_project(self, folder_path):
        project_name = os.path.basename(folder_path)

        abs_folder = os.path.abspath(folder_path)
        abs_temp = os.path.abspath(self.temp_root)
        status = 'TEMP' if abs_folder.startswith(abs_temp) else 'SAVED'

        if project_name in self.current_projects:
            self.current_projects[project_name] = folder_path
            self.project_states[project_name] = status
            return True, project_name, self._scan_project_items(folder_path)

        if not self.is_folder_project(folder_path):
            try:
                with open(os.path.join(folder_path, "config.json"), 'w', encoding='utf-8') as f:
                    f.write("{}")
            except Exception:
                return False, "Invalid Project Structure", []

        self.current_projects[project_name] = folder_path
        self.project_states[project_name] = status

        items = self._scan_project_items(folder_path)
        return True, project_name, items
    
    def get_project_items(self, project_name):
        project_path = self._get_project_root(project_name)
        if project_path:
            return self._scan_project_items(project_path)
        return []

    def get_project_path(self, project_name):
        return self.current_projects.get(project_name)

    def close_project(self, project_name):
        self._cleanup_dict(project_name)

    def create_structure(self, project_name, folder_name):
        project_path = self._get_project_root(project_name)
        if not project_path:
            return False, "Project not found"

        folder_path = os.path.join(project_path, folder_name)
        if os.path.exists(folder_path):
            return False, "Item already exists"

        try:
            os.makedirs(folder_path, exist_ok=True)
            os.makedirs(os.path.join(folder_path, "Image"), exist_ok=True)
            os.makedirs(os.path.join(folder_path, "Video"), exist_ok=True)

            if project_name not in self.item_states:
                self.item_states[project_name] = {}
            self.item_states[project_name][folder_name] = 'TEMP'

            return True, folder_path
        except Exception as e:
            return False, str(e)

    def delete_item(self, project_name, folder_name):
        project_path = self._get_project_root(project_name)
        if project_path:
            full_path = os.path.join(project_path, folder_name)
            if os.path.exists(full_path):
                try:
                    shutil.rmtree(full_path)
                    if project_name in self.item_states and folder_name in self.item_states[project_name]:
                        del self.item_states[project_name][folder_name]
                    return True, "Deleted"
                except Exception as e:
                    return False, str(e)
        return False, "Item not found"

    def rename_item(self, project_name, old_name, new_name):
        project_path = self._get_project_root(project_name)
        if not project_path:
            return False, "Project context lost"

        old_path = os.path.join(project_path, old_name)
        new_path = os.path.join(project_path, new_name)

        try:
            self._safe_rename(old_path, new_path)

            if project_name in self.item_states and old_name in self.item_states[project_name]:
                state = self.item_states[project_name][old_name]
                del self.item_states[project_name][old_name]
                self.item_states[project_name][new_name] = state

            return True, "Success"
        except Exception as e:
            return False, str(e)

    def get_file_path(self, project_name, relative_path):
        project_path = self._get_project_root(project_name)
        if project_path:
            return os.path.join(project_path, relative_path)
        return None

    def is_project_temp(self, project_name):
        return self.project_states.get(project_name) == 'TEMP'

    def is_item_temp(self, project_name, item_name):
        if project_name not in self.item_states:
            return False
        return self.item_states[project_name].get(item_name) == 'TEMP'

    def is_folder_project(self, folder_path):
        return os.path.exists(os.path.join(folder_path, "config.json"))

    def is_folder_item(self, folder_path):
        image_dir = os.path.join(folder_path, "Image")
        video_dir = os.path.join(folder_path, "Video")
        return os.path.isdir(folder_path) and os.path.isdir(image_dir) and os.path.isdir(video_dir)

    def verify_item_belongs_to_project(self, project_name, item_path):
        project_path = self._get_project_root(project_name)
        if not project_path:
            return False
        abs_project = os.path.abspath(project_path)
        abs_item = os.path.abspath(item_path)
        return abs_item.startswith(abs_project)

    def _scan_project_items(self, folder_path):
        items = []
        try:
            with os.scandir(folder_path) as entries:
                for entry in entries:
                    if entry.is_dir() and self.is_folder_item(entry.path):
                        items.append(entry.name)
        except Exception:
            pass
        return items

    def save_item_as(self, project_name, item_name):
        if project_name not in self.item_states:
            self.item_states[project_name] = {}
        self.item_states[project_name][item_name] = 'SAVED'
        return True, "Item marked as saved."

    def copy_item_structure(self, src_project_name, src_folder_name, target_project_name):
        src_root = self._get_project_root(src_project_name)
        tgt_root = self._get_project_root(target_project_name)

        if not src_root or not tgt_root:
            return False, "Project not found.", ""

        src_path = os.path.join(src_root, src_folder_name)

        new_name = src_folder_name
        dest_path = os.path.join(tgt_root, new_name)
        counter = 1
        while os.path.exists(dest_path):
            new_name = f"{src_folder_name}_Copy{counter}"
            dest_path = os.path.join(tgt_root, new_name)
            counter += 1

        try:
            shutil.copytree(src_path, dest_path)

            if target_project_name not in self.item_states:
                self.item_states[target_project_name] = {}
            self.item_states[target_project_name][new_name] = 'SAVED'

            return True, "Copied Successfully", new_name
        except Exception as e:
            return False, f"Copy Failed: {str(e)}", ""

    def move_item_structure(self, src_project_name, src_folder_name, target_project_name):
        success, msg, new_name = self.copy_item_structure(src_project_name, src_folder_name, target_project_name)

        if success:
            del_success, del_msg = self.delete_item(src_project_name, src_folder_name)
            if not del_success:
                return False, f"Moved but failed to cleanup source: {del_msg}", new_name
            return True, "Moved Successfully", new_name
        else:
            return False, msg, ""

    def _get_media_path(self, project_name, item_name, media_type):
        project_path = self._get_project_root(project_name)
        if not project_path:
            return None

        item_path = os.path.join(project_path, item_name)
        if not os.path.isdir(item_path):
            return None

        if media_type in ("Image", "Video"):
            return os.path.join(item_path, media_type)

        return None

    def copy_file(self, src_project, src_item, src_media, src_file,
                  dst_project, dst_item, dst_media, new_name=None):
        src_media_path = self._get_media_path(src_project, src_item, src_media)
        if not src_media_path:
            return False, "Source project/item not found", ""

        src_file_path = os.path.join(src_media_path, src_file)
        if not os.path.isfile(src_file_path):
            return False, f"Source file '{src_file}' not found", ""

        dst_media_path = self._get_media_path(dst_project, dst_item, dst_media)
        if not dst_media_path:
            return False, "Destination project/item not found", ""

        if new_name:
            dst_file_name = new_name
        else:
            base, ext = os.path.splitext(src_file)
            dst_file_name = src_file
            counter = 1
            while os.path.exists(os.path.join(dst_media_path, dst_file_name)):
                dst_file_name = f"{base}_Copy{counter}{ext}"
                counter += 1

        dst_file_path = os.path.join(dst_media_path, dst_file_name)

        try:
            shutil.copy2(src_file_path, dst_file_path)
            return True, "File copied successfully", dst_file_name
        except Exception as e:
            return False, f"Copy failed: {str(e)}", ""

    def move_file(self, src_project, src_item, src_media, src_file,
                  dst_project, dst_item, dst_media, new_name=None):
        success, msg, new_file_name = self.copy_file(
            src_project, src_item, src_media, src_file,
            dst_project, dst_item, dst_media, new_name
        )
        if success:
            del_success, del_msg = self.delete_file(src_project, src_item, src_media, src_file)
            if not del_success:
                return False, f"Moved but failed to delete source: {del_msg}", new_file_name
            return True, "File moved successfully", new_file_name
        else:
            return False, msg, ""

    def rename_file(self, project_name, item_name, media_type, old_name, new_name):
        media_path = self._get_media_path(project_name, item_name, media_type)
        if not media_path:
            return False, "Project/item not found"

        old_path = os.path.join(media_path, old_name)
        new_path = os.path.join(media_path, new_name)

        if not os.path.isfile(old_path):
            return False, f"File '{old_name}' not found"
        if os.path.exists(new_path):
            return False, f"File '{new_name}' already exists"

        try:
            os.rename(old_path, new_path)
            return True, "File renamed successfully"
        except Exception as e:
            return False, f"Rename failed: {str(e)}"

    def delete_file(self, project_name, item_name, media_type, file_name):
        media_path = self._get_media_path(project_name, item_name, media_type)
        if not media_path:
            return False, "Project/item not found"

        file_path = os.path.join(media_path, file_name)
        if not os.path.isfile(file_path):
            return False, f"File '{file_name}' not found"

        try:
            os.remove(file_path)
            return True, "File deleted successfully"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    def open_item(self, project_name, folder_path):
        if not self.is_folder_item(folder_path):
            return False, "Invalid item structure", "", ""

        item_name = os.path.basename(folder_path)
        project_path = self._get_project_root(project_name)
        if not project_path:
            return False, "Project not found", "", ""
        if not folder_path.startswith(project_path):
            return False, "Item does not belong to this project", "", ""

        abs_folder = os.path.abspath(folder_path)
        abs_temp = os.path.abspath(self.temp_root)
        status = 'TEMP' if abs_folder.startswith(abs_temp) else 'SAVED'

        if project_name not in self.item_states:
            self.item_states[project_name] = {}
        self.item_states[project_name][item_name] = status

        return True, "Item opened", item_name, folder_path