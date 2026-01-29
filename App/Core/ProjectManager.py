import os
import shutil
import tempfile

class ProjectManager:
    """
    Class chịu trách nhiệm xử lý logic hệ thống file/folder cho Project.
    """
    def __init__(self):
        self.current_projects = {} # Dict lưu {tên_project: đường_dẫn_path}

    def create_project(self, project_name, specific_path=None):
        """
        Tạo folder project. 
        Nếu specific_path = None, tạo trong thư mục Temp của hệ thống.
        """
        if specific_path:
            base_path = specific_path
        else:
            # Tạo trong thư mục Temp của OS
            base_path = os.path.join(tempfile.gettempdir(), "TNH_Optima_Projects")
        
        full_path = os.path.join(base_path, project_name)

        # Xử lý nếu trùng tên trong Temp (xóa cái cũ đi tạo lại hoặc báo lỗi tùy logic, ở đây mình reset nếu là temp)
        if os.path.exists(full_path) and specific_path is None:
            shutil.rmtree(full_path) 
            
        if os.path.exists(full_path):
             raise FileExistsError(f"Project '{project_name}' đã tồn tại.")

        try:
            os.makedirs(full_path, exist_ok=True)
            # Tạo file cấu hình mặc định
            with open(os.path.join(full_path, "config.json"), 'w') as f:
                f.write("{}")
            
            self.current_projects[project_name] = full_path
            return full_path
        except OSError as e:
            raise OSError(f"Không thể tạo project: {e}")

    def create_file(self, project_name, file_name):
        """Tạo file mới trong project"""
        if project_name not in self.current_projects:
            return False, "Project không tồn tại trong danh sách quản lý."
        
        path = self.current_projects[project_name]
        file_path = os.path.join(path, file_name)
        
        if os.path.exists(file_path):
            return False, "File đã tồn tại."
        
        try:
            with open(file_path, 'w') as f:
                f.write("") # Tạo file rỗng
            return True, file_path
        except Exception as e:
            return False, str(e)

    def save_project_as(self, project_name, target_folder):
        """
        Di chuyển project từ vị trí hiện tại (Temp) sang thư mục đích (Save As)
        """
        if project_name not in self.current_projects:
            return False, "Project không tìm thấy."

        current_path = self.current_projects[project_name]
        new_path = os.path.join(target_folder, project_name)

        if os.path.exists(new_path):
             return False, "Một project với tên này đã tồn tại ở thư mục đích."

        try:
            # Di chuyển thư mục từ Temp sang User Folder
            shutil.move(current_path, new_path)
            # Cập nhật đường dẫn mới
            self.current_projects[project_name] = new_path
            return True, new_path
        except Exception as e:
            return False, str(e)

    def delete_project(self, project_name):
        if project_name in self.current_projects:
            path = self.current_projects[project_name]
            try:
                shutil.rmtree(path)
                del self.current_projects[project_name]
                return True, "Đã xóa thành công."
            except Exception as e:
                return False, str(e)
        return False, "Không tìm thấy Project."

    def rename_project(self, old_name, new_name):
        if old_name in self.current_projects:
            old_path = self.current_projects[old_name]
            parent_dir = os.path.dirname(old_path)
            new_path = os.path.join(parent_dir, new_name)
            
            try:
                os.rename(old_path, new_path)
                del self.current_projects[old_name]
                self.current_projects[new_name] = new_path
                return True, new_path
            except Exception as e:
                return False, str(e)
        return False, "Project cũ không tồn tại."

    def save_project(self, project_name):
        # Lưu nội dung logic (nếu cần)
        return True