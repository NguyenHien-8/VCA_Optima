# App/Presentation/ViewModels/DialogViewModel/DeleteResourcesViewModel.py
from PyQt6.QtCore import QObject

class DeleteResourcesViewModel(QObject):
    def __init__(self, title: str, message: str, location_path: str, show_checkbox: bool):
        super().__init__()
        self._title = title
        self._message = message
        self._location_path = location_path
        self._show_checkbox = show_checkbox
        self._delete_disk_checked = False

    def get_title(self) -> str:
        return self._title

    def get_message(self) -> str:
        return self._message

    def get_location_path(self) -> str:
        return self._location_path

    def get_show_checkbox(self) -> bool:
        return self._show_checkbox

    def set_delete_disk_checked(self, checked: bool) -> None:
        self._delete_disk_checked = checked

    def get_delete_disk_checked(self) -> bool:
        return self._delete_disk_checked