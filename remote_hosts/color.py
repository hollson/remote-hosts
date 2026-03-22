import os
import sys
import atexit
from typing import Any, Dict

_WIN = sys.platform == "win32"
_state: Dict[str, Any] = {"orig_mode": None}


def _enable_win_ansi() -> bool:
    if not _WIN:
        return True
    try:
        from ctypes import windll, c_ulong  # type: ignore

        kernel32 = windll.kernel32
        STD_OUTPUT_HANDLE = c_ulong(0xFFFFFFF5)
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

        h = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        if h == -1:
            return False

        mode = c_ulong()
        if not kernel32.GetConsoleMode(h, mode):
            return False

        _state["orig_mode"] = mode.value

        if mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
            return True

        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
        return bool(kernel32.SetConsoleMode(h, mode))
    except Exception:
        return False


def _disable_win_ansi() -> None:
    if _WIN and _state["orig_mode"] is not None:
        try:
            from ctypes import windll, c_ulong  # type: ignore

            kernel32 = windll.kernel32
            STD_OUTPUT_HANDLE = c_ulong(0xFFFFFFF5)

            h = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            if h != -1:
                kernel32.SetConsoleMode(h, c_ulong(_state["orig_mode"]))
        except Exception:  # nosec B110
            pass
        _state["orig_mode"] = None


def init() -> None:
    if _WIN:
        _enable_win_ansi()
        atexit.register(deinit)


def deinit() -> None:
    _disable_win_ansi()


def should_colorize() -> bool:
    if "NO_COLOR" in os.environ:
        return False
    if _WIN:
        return _enable_win_ansi()
    if not sys.stdout.isatty():
        return False
    return True


_ENABLED = should_colorize()


def _s(code: str) -> str:
    return code if _ENABLED else ""


class Fore:
    RED = _s("\033[91m")
    GREEN = _s("\033[92m")
    YELLOW = _s("\033[93m")
    BLUE = _s("\033[94m")
    MAGENTA = _s("\033[95m")
    CYAN = _s("\033[96m")
    WHITE = _s("\033[97m")
    RESET = _s("\033[39m")


class Back:
    RED = _s("\033[101m")
    GREEN = _s("\033[102m")
    YELLOW = _s("\033[103m")
    BLUE = _s("\033[104m")
    MAGENTA = _s("\033[105m")
    CYAN = _s("\033[106m")
    WHITE = _s("\033[107m")
    RESET = _s("\033[49m")


class Style:
    BRIGHT = _s("\033[1m")
    DIM = _s("\033[2m")
    NORMAL = _s("\033[22m")
    RESET_ALL = _s("\033[0m")


END = Style.RESET_ALL
BOLD = Style.BRIGHT
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
HEADER = Fore.MAGENTA
