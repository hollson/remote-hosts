import os
import sys
import atexit
import warnings
from typing import Dict, Union

# -------------------------- 平台&终端检测（精准识别 Git Bash/MSYS2） --------------------------


def _detect_platform_and_terminal() -> Dict[str, bool]:
    """
    精准检测平台和终端类型，兼容 Python 3.8+
    重点识别 Windows 下的 Git Bash/MSYS2/Cygwin
    """
    platform = {
        "is_win": sys.platform.startswith("win32"),
        "is_cygwin": sys.platform.startswith("cygwin"),
        "is_mac": sys.platform.startswith("darwin"),
        "is_linux": sys.platform.startswith("linux"),
        "is_msys2": False,
        "is_mingw": False,
        "is_git_bash": False,  # 新增 Git Bash 检测
        "is_unix_like_terminal": False,  # 是否为类 Unix 终端（即使在 Windows 上）
    }

    # 1. 检测 Git Bash（优先级最高）
    try:
        # Git Bash 特征：TERM 包含 "msys"/"cygwin"，或进程路径包含 "git-bash.exe"
        term = os.environ.get("TERM", "").lower()
        if "msys" in term or "cygwin" in term:
            platform["is_git_bash"] = True
            platform["is_unix_like_terminal"] = True

        # 补充检测进程信息（Git Bash 窗口）
        if platform["is_win"]:
            import subprocess  # nosec

            # 兼容 Python 3.8+ 的 subprocess 调用
            # tasklist 是 Windows 系统内置命令，参数固定且安全
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
        # 静默失败，不影响核心逻辑
        pass

    # 2. 检测 MSYS2/MINGW
    msys_env = os.environ.get("MSYSTEM", "").lower()
    if msys_env or platform["is_git_bash"]:
        platform["is_msys2"] = True
        platform["is_mingw"] = "mingw" in msys_env
        platform["is_unix_like_terminal"] = True

    # 3. Cygwin 视为类 Unix 环境
    if platform["is_cygwin"]:
        platform["is_win"] = False
        platform["is_unix_like_terminal"] = True

    # 4. Unix 系统默认是类 Unix 终端
    if platform["is_mac"] or platform["is_linux"]:
        platform["is_unix_like_terminal"] = True

    return platform


# 初始化平台检测（兼容 Python 3.8+）
_PLATFORM = _detect_platform_and_terminal()
_WIN = _PLATFORM["is_win"]
_CYGWIN = _PLATFORM["is_cygwin"]
_MSYS2 = _PLATFORM["is_msys2"]
_GIT_BASH = _PLATFORM["is_git_bash"]
_UNIX_LIKE_TERMINAL = _PLATFORM["is_unix_like_terminal"]

# -------------------------- 全局状态（精准管理，避免覆盖） --------------------------
State = Dict[str, Union[int, bool, None]]
_state: State = {
    "orig_stdout_mode": None,
    "orig_stderr_mode": None,
    "ansi_enabled": False,
    "deinit_registered": False,
    "init_called": False,
}

# Windows API 常量
STD_OUTPUT_HANDLE: int = -11
STD_ERROR_HANDLE: int = -12
ENABLE_VIRTUAL_TERMINAL_PROCESSING: int = 0x0004

# -------------------------- Windows 控制台操作（兼容 Python 3.8+） --------------------------


def _get_win_console_mode(handle: int) -> Union[int, None]:
    """获取 Windows 控制台模式（无副作用）"""
    if not _WIN or handle == -1 or _UNIX_LIKE_TERMINAL:
        return None
    try:
        from ctypes import windll, c_ulong, byref

        kernel32 = windll.kernel32
        mode = c_ulong()
        if kernel32.GetConsoleMode(handle, byref(mode)):
            return mode.value
        return None
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"读取控制台模式失败: {e}")
        return None


def _set_win_console_mode(handle: int, mode: int) -> bool:
    """设置 Windows 控制台模式"""
    if not _WIN or handle == -1 or _UNIX_LIKE_TERMINAL:
        return False
    try:
        from ctypes import windll, c_ulong

        kernel32 = windll.kernel32
        return bool(kernel32.SetConsoleMode(handle, c_ulong(mode)))
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"设置控制台模式失败: {e}")
        return False


def _enable_win_ansi() -> bool:
    """启用 Windows VT 支持（仅对原生 CMD/PowerShell 生效）"""
    # Git Bash/MSYS2/Cygwin 直接返回 True（无需启用 VT）
    if _UNIX_LIKE_TERMINAL or not _WIN:
        return True
    if _state["ansi_enabled"]:
        return True

    try:
        from ctypes import windll

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
        warnings.warn(f"启用 Windows ANSI 失败: {e}")
        return False


def _disable_win_ansi() -> bool:
    """恢复 Windows 控制台原始模式"""
    if _UNIX_LIKE_TERMINAL or not _WIN:
        return True
    if _state["orig_stdout_mode"] is None and _state["orig_stderr_mode"] is None:
        return True

    try:
        from ctypes import windll

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
            warnings.warn("恢复 Windows 控制台模式失败")
        return success
    except (ImportError, AttributeError, OSError) as e:
        warnings.warn(f"恢复控制台模式异常: {e}")
        return False


# -------------------------- 颜色控制（兼容 Python 3.8+） --------------------------


def _check_term_support_color() -> bool:
    """检查终端是否支持颜色"""
    term = os.environ.get("TERM", "").lower()
    if term in ("dumb", ""):
        return False
    return any(keyword in term for keyword in ("color", "256color", "xterm", "vt100", "msys", "cygwin"))


def should_colorize() -> bool:
    """判断是否启用颜色输出（无副作用，兼容 Python 3.8+）"""
    # 1. NO_COLOR 优先级最高
    if os.environ.get("NO_COLOR") is not None:
        return False
    # 2. FORCE_COLOR 强制启用
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    # 3. Git Bash/MSYS2/Cygwin 直接启用
    if _UNIX_LIKE_TERMINAL:
        return True
    # 4. Windows 原生终端检查 ANSI 启用状态
    if _WIN:
        return bool(_state.get("ansi_enabled", False))
    # 5. Unix 系统检查 TTY 和 TERM
    if not sys.stdout.isatty():
        return False
    return _check_term_support_color()


# -------------------------- 动态颜色类（兼容 Python 3.8+） --------------------------


class Color:
    """简化的动态颜色类，兼容 Python 3.8+"""

    def __init__(self, codes: Dict[str, str]):
        self._codes = codes

    def __getattr__(self, name: str) -> str:
        """动态返回颜色码，每次访问都检查启用状态"""
        if should_colorize():
            return self._codes.get(name, "")
        return ""


# 颜色码映射（兼容标准 ANSI）
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

# 公开实例
Fore = Color(_fore_codes)
Back = Color(_back_codes)
Style = Color(_style_codes)

# -------------------------- 便捷导出（兼容 Python 3.8+） --------------------------
# 简化便捷属性，避免 property 兼容性问题


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


# -------------------------- 公开接口（幂等，兼容 Python 3.8+） --------------------------


def init() -> None:
    """初始化颜色支持（仅对 Windows 原生终端生效）"""
    if _state["init_called"]:
        return
    # 仅 Windows 原生终端（非 Git Bash/MSYS2/Cygwin）需要启用 VT
    if _WIN and not _UNIX_LIKE_TERMINAL:
        _enable_win_ansi()
        if not _state["deinit_registered"]:
            atexit.register(deinit)
            _state["deinit_registered"] = True
    _state["init_called"] = True


def deinit() -> None:
    """清理控制台状态"""
    if not _state["init_called"]:
        return
    if _WIN and not _UNIX_LIKE_TERMINAL:
        _disable_win_ansi()
    _state["init_called"] = False
    _state["deinit_registered"] = False


# -------------------------- 测试代码（兼容 Python 3.8+） --------------------------
if __name__ == "__main__":
    # 初始化
    init()

    # 打印检测信息（帮助调试）
    print("=== 终端检测信息 ===")
    print(f"Windows 系统: {_WIN}")
    print(f"Git Bash: {_GIT_BASH}")
    print(f"MSYS2: {_MSYS2}")
    print(f"类 Unix 终端: {_UNIX_LIKE_TERMINAL}")
    print(f"颜色启用状态: {should_colorize()}")
    print(f"TERM 环境变量: {os.environ.get('TERM', '未设置')}")

    # 测试颜色输出
    print("\n=== 颜色测试 ===")
    print(f"{Fore.RED}红色文字{Style.RESET_ALL}")
    print(f"{Back.GREEN}绿色背景{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}{Fore.BLUE}亮蓝色粗体{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{Style.UNDERLINE}紫色下划线{Style.RESET_ALL}")

    # 测试动态禁用
    os.environ["NO_COLOR"] = "1"
    print("\n=== 禁用 NO_COLOR 后 ===")
    print(f"{Fore.RED}红色文字（应无颜色）{Style.RESET_ALL}")

    # 清理
    del os.environ["NO_COLOR"]
    if "FORCE_COLOR" in os.environ:
        del os.environ["FORCE_COLOR"]
    deinit()
