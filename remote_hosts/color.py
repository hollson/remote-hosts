import os
import sys
import atexit
import warnings
from typing import Dict, Union

# -------------------------- Platform & Terminal Detection (Precise Git Bash/MSYS2 Detection) --------------------------


def _detect_platform_and_terminal() -> Dict[str, bool]:
    """
    Precisely detect platform and terminal type, compatible with Python 3.8+
    Focus on identifying Git Bash/MSYS2/Cygwin on Windows
    """
    platform = {
        "is_win": sys.platform.startswith("win32"),
        "is_cygwin": sys.platform.startswith("cygwin"),
        "is_mac": sys.platform.startswith("darwin"),
        "is_linux": sys.platform.startswith("linux"),
        "is_msys2": False,
        "is_mingw": False,
        "is_git_bash": False,  # Added Git Bash detection
        "is_unix_like_terminal": False,  # Whether it's a Unix-like terminal (even on Windows)
    }

    # 1. Detect Git Bash (highest priority)
    try:
        # Git Bash characteristics: TERM contains "msys"/"cygwin", or process path contains "git-bash.exe"
        term = os.environ.get("TERM", "").lower()
        if "msys" in term or "cygwin" in term:
            platform["is_git_bash"] = True
            platform["is_unix_like_terminal"] = True

        # Additional process info detection (Git Bash window)
        if platform["is_win"]:
            import subprocess  # nosec

            # Python 3.8+ compatible subprocess call
            # tasklist is Windows built-in command, fixed parameters and safe
            result = subprocess.run(
                ["tasklist", "/fi", "PID eq {}".format(os.getpid()), "/fo", "csv"],  # nosec
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )
            if "git-bash.exe" in result.stdout.lower():
                platform["is_git_bash"] = True
                platform["is_unix_like_terminal"] = True
    except (ImportError, subprocess.SubprocessError, OSError):
        # Silent failure, doesn't affect core logic
        pass

    # 2. Detect MSYS2/MINGW
    msys_env = os.environ.get("MSYSTEM", "").lower()
    if msys_env or platform["is_git_bash"]:
        platform["is_msys2"] = True
        platform["is_mingw"] = "mingw" in msys_env
        platform["is_unix_like_terminal"] = True

    # 3. Cygwin is treated as Unix-like environment
    if platform["is_cygwin"]:
        platform["is_win"] = False
        platform["is_unix_like_terminal"] = True

    # 4. Unix systems are Unix-like terminals by default
    if platform["is_mac"] or platform["is_linux"]:
        platform["is_unix_like_terminal"] = True

    return platform


# Initialize platform detection (Python 3.8+ compatible)
_PLATFORM = _detect_platform_and_terminal()
_WIN = _PLATFORM["is_win"]
_CYGWIN = _PLATFORM["is_cygwin"]
_MSYS2 = _PLATFORM["is_msys2"]
_GIT_BASH = _PLATFORM["is_git_bash"]
_UNIX_LIKE_TERMINAL = _PLATFORM["is_unix_like_terminal"]

# -------------------------- Global State (Precise Management, Avoid Overwriting) --------------------------
State = Dict[str, Union[int, bool, None]]
_state: State = {
    "orig_stdout_mode": None,
    "orig_stderr_mode": None,
    "ansi_enabled": False,
    "deinit_registered": False,
    "init_called": False,
}

# Windows API constants
STD_OUTPUT_HANDLE: int = -11
STD_ERROR_HANDLE: int = -12
ENABLE_VIRTUAL_TERMINAL_PROCESSING: int = 0x0004

# -------------------------- Windows Console Operations (Python 3.8+ compatible) --------------------------


def _get_win_console_mode(handle: int) -> Union[int, None]:
    """Get Windows console mode (no side effects)"""
    if not _WIN or handle == -1 or _UNIX_LIKE_TERMINAL:
        return None
    try:
        from ctypes import windll, c_ulong, byref  # type: ignore[attr-defined]

        kernel32 = windll.kernel32
        mode = c_ulong()
        if kernel32.GetConsoleMode(handle, byref(mode)):
            return mode.value
        return None
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"Failed to read console mode: {e}")
        return None


def _set_win_console_mode(handle: int, mode: int) -> bool:
    """Set Windows console mode"""
    if not _WIN or handle == -1 or _UNIX_LIKE_TERMINAL:
        return False
    try:
        from ctypes import windll, c_ulong  # type: ignore[attr-defined]

        kernel32 = windll.kernel32
        return bool(kernel32.SetConsoleMode(handle, c_ulong(mode)))
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"Failed to set console mode: {e}")
        return False


def _enable_win_ansi() -> bool:
    """Enable Windows VT support (only for native CMD/PowerShell)"""
    # Git Bash/MSYS2/Cygwin directly return True (no need to enable VT)
    if _UNIX_LIKE_TERMINAL or not _WIN:
        return True
    if _state["ansi_enabled"]:
        return True

    try:
        from ctypes import windll  # type: ignore[attr-defined]

        kernel32 = windll.kernel32
        stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        stderr_handle = kernel32.GetStdHandle(STD_ERROR_HANDLE)

        if _state["orig_stdout_mode"] is None:
            _state["orig_stdout_mode"] = _get_win_console_mode(stdout_handle)
        if _state["orig_stderr_mode"] is None:
            _state["orig_stderr_mode"] = _get_win_console_mode(stderr_handle)

        current_mode = _get_win_console_mode(stdout_handle)
        if current_mode is None:
            return False
        if current_mode & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
            _state["ansi_enabled"] = True
            return True

        new_mode = current_mode | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        stdout_ok = _set_win_console_mode(stdout_handle, new_mode)
        stderr_ok = _set_win_console_mode(stderr_handle, new_mode)

        _state["ansi_enabled"] = stdout_ok or stderr_ok
        return bool(_state["ansi_enabled"])
    except Exception as e:
        warnings.warn(f"Failed to enable Windows ANSI: {e}")
        return False


def _disable_win_ansi() -> bool:
    """Restore Windows console original mode"""
    if _UNIX_LIKE_TERMINAL or not _WIN:
        return True
    if _state["orig_stdout_mode"] is None and _state["orig_stderr_mode"] is None:
        return True

    try:
        from ctypes import windll  # type: ignore[attr-defined]

        kernel32 = windll.kernel32
        stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        stderr_handle = kernel32.GetStdHandle(STD_ERROR_HANDLE)

        stdout_ok = True
        if _state["orig_stdout_mode"] is not None and stdout_handle != -1:
            stdout_ok = _set_win_console_mode(stdout_handle, _state["orig_stdout_mode"])

        stderr_ok = True
        if _state["orig_stderr_mode"] is not None and stderr_handle != -1:
            stderr_ok = _set_win_console_mode(stderr_handle, _state["orig_stderr_mode"])

        _state["orig_stdout_mode"] = None
        _state["orig_stderr_mode"] = None
        _state["ansi_enabled"] = False

        success = stdout_ok and stderr_ok
        if not success:
            warnings.warn("Failed to restore Windows console mode")
        return success
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"Exception restoring console mode: {e}")
        return False


# -------------------------- Color Control (Python 3.8+ compatible) --------------------------


def _check_term_support_color() -> bool:
    """Check if terminal supports color"""
    term = os.environ.get("TERM", "").lower()
    if term in ("dumb", ""):
        return False
    return any(keyword in term for keyword in ("color", "256color", "xterm", "vt100", "msys", "cygwin"))


def should_colorize() -> bool:
    """Determine whether to enable color output (no side effects, Python 3.8+ compatible)"""
    # 1. NO_COLOR has highest priority
    if os.environ.get("NO_COLOR") is not None:
        return False
    # 2. FORCE_COLOR forces enable
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    # 3. Git Bash/MSYS2/Cygwin directly enable
    if _UNIX_LIKE_TERMINAL:
        return True
    # 4. Windows native terminal checks ANSI enable status
    if _WIN:
        return bool(_state.get("ansi_enabled", False))
    # 5. Unix system checks TTY and TERM
    if not sys.stdout.isatty():
        return False
    return _check_term_support_color()


# -------------------------- Dynamic Color Class (Python 3.8+ compatible) --------------------------


class Color:
    """Simplified dynamic color class, Python 3.8+ compatible"""

    def __init__(self, codes: Dict[str, str]):
        self._codes = codes

    def __getattr__(self, name: str) -> str:
        """Dynamically return color code, check enable status each access"""
        if should_colorize():
            return self._codes.get(name, "")
        return ""


# Color code mapping (compatible with standard ANSI)
_fore_codes = {
    "BLACK": "\033[30m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "GRAY": "\033[90m",
    "RESET": "\033[39m",
}

_back_codes = {
    "BLACK": "\033[40m",
    "RED": "\033[101m",
    "GREEN": "\033[102m",
    "YELLOW": "\033[103m",
    "BLUE": "\033[104m",
    "MAGENTA": "\033[105m",
    "CYAN": "\033[106m",
    "WHITE": "\033[107m",
    "GRAY": "\033[100m",
    "RESET": "\033[49m",
}

_style_codes = {
    "BRIGHT": "\033[1m",
    "DIM": "\033[2m",
    "NORMAL": "\033[22m",
    "UNDERLINE": "\033[4m",
    "RESET_UNDERLINE": "\033[24m",
    "RESET_ALL": "\033[0m",
}

# Public instances
Fore = Color(_fore_codes)
Back = Color(_back_codes)
Style = Color(_style_codes)

# -------------------------- Convenience Exports (Python 3.8+ compatible) --------------------------
# Simplified convenience properties, avoid property compatibility issues


def END() -> str:
    return Style.RESET_ALL


def BOLD() -> str:
    return Style.BRIGHT


def RED() -> str:
    return Fore.RED


def GREEN() -> str:
    return Fore.GREEN


def YELLOW() -> str:
    return Fore.YELLOW


def BLUE() -> str:
    return Fore.BLUE


def HEADER() -> str:
    return Fore.MAGENTA


# -------------------------- Public Interface (Idempotent, Python 3.8+ compatible) --------------------------


def init() -> None:
    """Initialize color support (only for Windows native terminal)"""
    if _state["init_called"]:
        return
    # Only Windows native terminal (not Git Bash/MSYS2/Cygwin) needs VT enabled
    if _WIN and not _UNIX_LIKE_TERMINAL:
        _enable_win_ansi()
        if not _state["deinit_registered"]:
            atexit.register(deinit)
            _state["deinit_registered"] = True
    _state["init_called"] = True


def deinit() -> None:
    """Clean up console state"""
    if not _state["init_called"]:
        return
    if _WIN and not _UNIX_LIKE_TERMINAL:
        _disable_win_ansi()
    _state["init_called"] = False
    _state["deinit_registered"] = False


# -------------------------- Test Code (Python 3.8+ compatible) --------------------------
if __name__ == "__main__":
    # Initialize
    init()

    # Print detection info (help debugging)
    print("=== Terminal Detection Info ===")
    print(f"Windows system: {_WIN}")
    print(f"Git Bash: {_GIT_BASH}")
    print(f"MSYS2: {_MSYS2}")
    print(f"Unix-like terminal: {_UNIX_LIKE_TERMINAL}")
    print(f"Color enabled: {should_colorize()}")
    print(f"TERM environment variable: {os.environ.get('TERM', 'Not set')}")

    # Test color output
    print("\n=== Color Test ===")
    print(f"{Fore.RED}Red text{Style.RESET_ALL}")
    print(f"{Back.GREEN}Green background{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.BLUE}Bright blue bold{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.UNDERLINE}Purple underline{Style.RESET_ALL}")

    # Test dynamic disable
    os.environ["NO_COLOR"] = "1"
    print("\n=== After NO_COLOR disabled ===")
    print(f"{Fore.RED}Red text (should have no color){Style.RESET_ALL}")

    # Cleanup
    del os.environ["NO_COLOR"]
    if "FORCE_COLOR" in os.environ:
        del os.environ["FORCE_COLOR"]
    deinit()
