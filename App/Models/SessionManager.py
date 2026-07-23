# App/Models/SessionManager.py
from typing import List, Dict, Set
from App.Infrastructure.Repositories.SessionRepository import SessionRepository

class SessionManager:
    """
    Quản lý phiên làm việc: lưu và khôi phục danh sách project, editor, trạng thái expanded, và các item đang mở.
    """

    SESSION_KEY_OPEN_PROJECTS = "open_projects"
    SESSION_KEY_OPEN_EDITORS = "open_editors"
    SESSION_KEY_EXPANDED_PATHS = "expanded_paths"
    SESSION_KEY_OPENED_ITEMS = "opened_items"

    def __init__(self, repo: SessionRepository):
        self.repo = repo
        self._open_projects: List[str] = []
        self._open_editors: List[Dict[str, str]] = []
        self._expanded_paths: List[str] = []
        self._opened_items_serializable: Dict[str, List[str]] = {}

    # --- Projects ---
    def set_open_projects(self, project_paths: List[str]):
        self._open_projects = project_paths[:]

    def get_open_projects(self) -> List[str]:
        return self._open_projects[:]

    def save_projects(self):
        self.repo.save_session(self.SESSION_KEY_OPEN_PROJECTS, self._open_projects)

    def load_projects(self) -> List[str]:
        data = self.repo.load_session(self.SESSION_KEY_OPEN_PROJECTS)
        if isinstance(data, list):
            self._open_projects = data
        else:
            self._open_projects = []
        return self.get_open_projects()

    # --- Editors ---
    def set_open_editors(self, editor_list: List[Dict[str, str]]):
        self._open_editors = editor_list[:]

    def get_open_editors(self) -> List[Dict[str, str]]:
        return self._open_editors[:]

    def save_editors(self):
        self.repo.save_session(self.SESSION_KEY_OPEN_EDITORS, self._open_editors)

    def load_editors(self) -> List[Dict[str, str]]:
        data = self.repo.load_session(self.SESSION_KEY_OPEN_EDITORS)
        if isinstance(data, list):
            self._open_editors = data
        else:
            self._open_editors = []
        return self.get_open_editors()

    # --- Expanded paths ---
    def set_expanded_paths(self, paths: List[str]):
        self._expanded_paths = paths[:]

    def get_expanded_paths(self) -> List[str]:
        return self._expanded_paths[:]

    def save_expanded_paths(self):
        self.repo.save_session(self.SESSION_KEY_EXPANDED_PATHS, self._expanded_paths)

    def load_expanded_paths(self) -> List[str]:
        data = self.repo.load_session(self.SESSION_KEY_EXPANDED_PATHS)
        if isinstance(data, list):
            self._expanded_paths = data
        else:
            self._expanded_paths = []
        return self.get_expanded_paths()

    # --- Opened items ---
    def set_opened_items(self, opened_items: Dict[str, Set[str]]):
        """Convert the set into a list to save it."""
        self._opened_items_serializable = {}
        for proj, items_set in opened_items.items():
            self._opened_items_serializable[proj] = list(items_set)

    def get_opened_items(self) -> Dict[str, Set[str]]:
        """Returns a dict with a value of set."""
        return {proj: set(items) for proj, items in self._opened_items_serializable.items()}

    def save_opened_items(self):
        self.repo.save_session(self.SESSION_KEY_OPENED_ITEMS, self._opened_items_serializable)

    def load_opened_items(self) -> Dict[str, Set[str]]:
        data = self.repo.load_session(self.SESSION_KEY_OPENED_ITEMS)
        if isinstance(data, dict):
            self._opened_items_serializable = data
            return self.get_opened_items()
        return {}

    # --- Combined save/load ---
    def save_all(self):
        self.save_projects()
        self.save_editors()
        self.save_expanded_paths()
        self.save_opened_items()

    def load_all(self):
        self.load_projects()
        self.load_editors()
        self.load_expanded_paths()
        self.load_opened_items()