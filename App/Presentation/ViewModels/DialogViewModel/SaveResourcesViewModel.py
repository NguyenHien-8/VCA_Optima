###############################################################################
# @file App/Presentation/ViewModels/DialogViewModel/SaveResourcesViewModel.py
# Author: TRAN NGUYEN HIEN
# Email: trannguyenhien29085@gmail.com
###############################################################################
from PyQt6.QtCore import QObject

class SaveResourcesViewModel(QObject):
    def __init__(self, item_name: str):
        super().__init__()
        self._item_name = item_name
        self._action = "CANCEL"

    def get_item_name(self) -> str:
        return self._item_name

    def set_action_save(self) -> None:
        self._action = "SAVE"

    def set_action_dont_save(self) -> None:
        self._action = "DONT_SAVE"

    def set_action_cancel(self) -> None:
        self._action = "CANCEL"

    def get_action(self) -> str:
        return self._action