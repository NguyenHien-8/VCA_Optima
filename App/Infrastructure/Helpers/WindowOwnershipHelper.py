import ctypes
import logging
import sys


APP_USER_MODEL_ID = "TNH.Optima"

_GWL_EXSTYLE = -20
_WS_EX_TOOLWINDOW = 0x00000080
_WS_EX_APPWINDOW = 0x00040000
_SWP_NOSIZE = 0x0001
_SWP_NOMOVE = 0x0002
_SWP_NOZORDER = 0x0004
_SWP_NOACTIVATE = 0x0010
_SWP_FRAMECHANGED = 0x0020

logger = logging.getLogger(__name__)


def initialize_taskbar_identity(app_user_model_id=APP_USER_MODEL_ID):
    """
    Give every native window in the process one stable Windows taskbar identity.

    The call is intentionally a no-op outside Windows and never prevents the
    application from starting if the shell API is unavailable.
    """
    if not sys.platform.startswith("win"):
        return True

    try:
        set_app_id = ctypes.WinDLL("shell32", use_last_error=True)
        set_app_id = set_app_id.SetCurrentProcessExplicitAppUserModelID
        set_app_id.argtypes = [ctypes.c_wchar_p]
        set_app_id.restype = ctypes.c_long
        result = set_app_id(app_user_model_id)
        if result != 0:
            logger.warning(
                "Could not set Windows AppUserModelID %r (HRESULT=%#x).",
                app_user_model_id,
                result & 0xFFFFFFFF,
            )
            return False
        return True
    except (AttributeError, OSError, TypeError, ValueError, ctypes.ArgumentError):
        logger.exception("Could not initialize the Windows taskbar identity.")
        return False


def resolve_window_owner(widget):
    """Return the top-level QWidget that should own a secondary window."""
    if widget is None:
        return None

    try:
        owner = widget.window()
    except (AttributeError, RuntimeError):
        return None

    return owner if owner is not None else widget


def configure_owned_window(window, owner, show_in_taskbar=True):
    """
    Apply a consistent owner and taskbar policy to a secondary top-level window.

    Qt's transient parent provides native owner/Z-order/minimize coordination.
    On Windows, WS_EX_APPWINDOW keeps the owned window eligible for a grouped
    taskbar thumbnail, while removing WS_EX_TOOLWINDOW avoids conflicting shell
    treatment. The operation is idempotent and safe to repeat from showEvent.
    """
    owner = resolve_window_owner(owner)
    if window is None or owner is None or owner is window:
        return False

    try:
        # winId() creates the native handles before the first show, allowing the
        # taskbar style to be correct from the first visible frame.
        owner.winId()
        window.winId()
        owner_handle = owner.windowHandle()
        window_handle = window.windowHandle()
        if owner_handle is None or window_handle is None:
            return False
        window_handle.setTransientParent(owner_handle)
    except (AttributeError, RuntimeError):
        logger.exception("Could not assign the native owner window.")
        return False

    if show_in_taskbar and sys.platform.startswith("win"):
        return _enable_windows_taskbar_thumbnail(window)
    return True


def _enable_windows_taskbar_thumbnail(window):
    try:
        hwnd = int(window.winId())
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        get_window_long = getattr(user32, "GetWindowLongPtrW", None)
        set_window_long = getattr(user32, "SetWindowLongPtrW", None)
        long_ptr_type = ctypes.c_ssize_t

        if get_window_long is None or set_window_long is None:
            get_window_long = user32.GetWindowLongW
            set_window_long = user32.SetWindowLongW
            long_ptr_type = ctypes.c_long

        get_window_long.argtypes = [ctypes.c_void_p, ctypes.c_int]
        get_window_long.restype = long_ptr_type
        set_window_long.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            long_ptr_type,
        ]
        set_window_long.restype = long_ptr_type

        current_style = int(get_window_long(hwnd, _GWL_EXSTYLE))
        desired_style = (
            current_style | _WS_EX_APPWINDOW
        ) & ~_WS_EX_TOOLWINDOW

        if desired_style != current_style:
            ctypes.set_last_error(0)
            previous_style = set_window_long(
                hwnd,
                _GWL_EXSTYLE,
                desired_style,
            )
            error_code = ctypes.get_last_error()
            if previous_style == 0 and error_code:
                logger.warning(
                    "Could not update taskbar style for HWND=%#x (WinError=%d).",
                    hwnd,
                    error_code,
                )
                return False

            set_window_pos = user32.SetWindowPos
            set_window_pos.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_uint,
            ]
            set_window_pos.restype = ctypes.c_bool
            flags = (
                _SWP_NOSIZE
                | _SWP_NOMOVE
                | _SWP_NOZORDER
                | _SWP_NOACTIVATE
                | _SWP_FRAMECHANGED
            )
            if not set_window_pos(hwnd, None, 0, 0, 0, 0, flags):
                logger.warning(
                    "Taskbar style changed but frame refresh failed for HWND=%#x.",
                    hwnd,
                )

        return True
    except (
        AttributeError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        ctypes.ArgumentError,
    ):
        logger.exception("Could not enable the owned-window taskbar thumbnail.")
        return False
