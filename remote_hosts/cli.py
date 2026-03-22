#!/usr/bin/env python3
import os
import json
import sys
import subprocess  # nosec B404
import shutil
import hashlib

try:
    from importlib.metadata import version

    __version__ = version("remote-hosts")
except Exception:
    __version__ = "0.1.3"

DEFAULT_SAMPLE_MD5 = "5FACF518B4AD006EA238A27BD60B7BD7"


def _compute_md5(data: bytes) -> str:
    """Compute MD5 hash of data, compatible with Python 3.8+."""
    normalized_data = data.replace(b"\r\n", b"\n")
    try:
        return hashlib.md5(normalized_data, usedforsecurity=False).hexdigest().upper()  # pylint: disable=unexpected-keyword-arg
    except TypeError:
        return hashlib.md5(normalized_data).hexdigest().upper()  # nosec B324


from remote_hosts.i18n import _, LANG
from remote_hosts.color import END, BOLD, RED, GREEN, BLUE


class Config:
    """Configuration management class for loading and validating configuration files"""

    def __init__(self, config_path):
        self.config_path = os.path.expanduser(config_path)
        self.hosts = []

    def load(self):
        """Load configuration file"""
        try:
            with open(self.config_path, "r") as file:
                data = json.load(file)
                if isinstance(data, dict) and "hosts" in data:
                    hosts_data = data["hosts"]
                else:
                    hosts_data = data
                if not isinstance(hosts_data, list):
                    print(f"{RED}{_('config_error_array')}{END}")
                    exit(1)
                self._validate_and_load_hosts(hosts_data)
        except FileNotFoundError:
            self._create_sample()
            print(f"{BLUE} {_('init_config')}{END}")
            exit(0)
        except json.JSONDecodeError:
            print(f"{RED}{_('config_error_json')}{END}")
            exit(1)
        return self.hosts

    def _validate_and_load_hosts(self, hosts_data):
        id_set = set()
        for host_data in hosts_data:
            host_id = host_data.get("id")
            host_name = host_data.get("host")
            user_name = host_data.get("user")
            if host_id is None or not host_name or not user_name:
                print(f"{RED}{_('host_config_error')}{END}")
                exit(1)
            if host_id in id_set:
                print(f"{RED}{_('duplicate_host_id', id=host_id)}{END}")
                exit(1)
            id_set.add(host_id)
            self.hosts.append(host_data)

    def _create_sample(self):
        """Create sample configuration file"""
        sample_data = [
            {
                "id": 1,
                "host": "example.com",
                "port": 22,
                "user": "root",
                "key": "~/.ssh/id_rsa",
                "os": "ubuntu22.04",
                "arch": "x86_64",
                "region": "Beijing",
                "mark": "example",
            },
            {"id": 2, "host": "192.168.1.1", "user": "root", "mark": "example"},
        ]
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(sample_data, file, indent="\t", ensure_ascii=False)


def load_hosts(config_path):
    """Load hosts from configuration file"""
    config = Config(config_path)
    return config.load()


def print_hosts(hosts, config_path):
    """Print host list in table format"""
    header_labels = [
        _("header_id"),
        _("header_host"),
        _("header_user"),
        _("header_os"),
        _("header_arch"),
        _("header_region"),
        _("header_mark"),
    ]
    headers = [f"{BOLD}{BLUE}{label}{END}" for label in header_labels]
    rows = []
    for host in hosts:
        try:
            host_id = host.get("id")
            host_name = host.get("host")
            user_name = host.get("user")
            os_info = host.get("os", "-")
            arch_info = host.get("arch", "-")
            region_info = host.get("region", "-")
            mark_info = host.get("mark", "-")
            if host_id is not None and host_name and user_name:
                rows.append(
                    [
                        f"{GREEN}{host_id}{END}",
                        f"{GREEN}{host_name}{END}",
                        f"{GREEN}{user_name}{END}",
                        os_info,
                        arch_info,
                        region_info,
                        mark_info,
                    ]
                )
        except KeyError:
            print(f"{RED}{_('host_info_missing')}{END}")
            exit(1)
    if rows:

        def get_clean_length(s):
            import re

            clean = re.sub(r"\x1B\[[0-9;]*m", "", s)
            width = 0
            for c in clean:
                if ord(c) > 127:
                    width += 2
                else:
                    width += 1
            return width

        col_widths = [get_clean_length(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], get_clean_length(cell))

        col_widths = [max(width + 4, 10) for width in col_widths]
        top_border = "┌" + "┬".join(["─" * width for width in col_widths]) + "┐"
        print(top_border)
        header_row = "│"
        for header, width in zip(headers, col_widths):
            clean_len = get_clean_length(header)
            left_pad = (width - clean_len) // 2
            right_pad = width - clean_len - left_pad
            header_row += " " * left_pad + header + " " * right_pad + "│"
        print(header_row)
        middle_border = "├" + "┼".join(["─" * width for width in col_widths]) + "┤"
        print(middle_border)
        for i, row in enumerate(rows):
            data_row = "│"
            for cell, width in zip(row, col_widths):
                clean_len = get_clean_length(cell)
                import re

                clean_content = re.sub(r"\x1B\[[0-9;]*m", "", cell)
                if clean_content == "-":
                    left_pad = (width - clean_len) // 2
                    right_pad = width - clean_len - left_pad
                    data_row += " " * left_pad + cell + " " * right_pad + "│"
                else:
                    right_pad = width - clean_len
                    data_row += cell + " " * right_pad + "│"
            print(data_row)
            if i < len(rows) - 1:
                row_separator = "├" + "┼".join(["─" * width for width in col_widths]) + "┤"
                print(row_separator)
        bottom_border = "└" + "┴".join(["─" * width for width in col_widths]) + "┘"
        print(bottom_border)
    else:
        print(f"{RED}{_('all_rows_empty')}{END}")


def show_manual():
    """Show operation manual"""
    manual_file = "manual_zh.txt" if LANG == "zh" else "manual.txt"
    try:
        import pkgutil

        content = pkgutil.get_data("remote_hosts", manual_file)
        if content:
            print(content.decode("utf-8"))
        else:
            print(f"{RED}{_('manual_not_found', path=manual_file)}{END}")
    except Exception as e:
        print(f"{RED}{_('manual_not_found', path=manual_file)}{END}")
        print(f"{RED}{_('manual_error', error=e)}{END}")


def edit_config(config_path, editor=None):
    """Edit configuration file"""
    config_path = os.path.expanduser(config_path)
    if not os.path.exists(config_path):
        config = Config(config_path)
        config._create_sample()
    if not editor:
        print(
            f"{BOLD}{BLUE}{_('select_editor')}\n  1. default \t{_('editor_default')}\n  2. vi \t{_('editor_vi')}\n  3. vim \t{_('editor_vim')}\n  4. nano \t{_('editor_nano')}\n  5. code \t{_('editor_code')}{END}"
        )
        try:
            choice = int(input(_("enter_option")))
            if choice == 1:
                if sys.platform == "darwin":
                    editor = "open -a TextEdit"
                elif sys.platform == "win32":
                    editor = "notepad"
                else:
                    editor = "vi"
            elif choice == 2:
                editor = "vi"
            elif choice == 3:
                editor = "vim"
            elif choice == 4:
                editor = "nano"
            elif choice == 5:
                code_path = shutil.which("code")
                if code_path:
                    editor = code_path
                else:
                    editor = "code"
            else:
                print(f"{RED}{_('invalid_option')}{END}")
                exit(1)
        except ValueError:
            print(f"{RED}{_('invalid_input')}{END}")
            exit(1)
    try:
        if " " in editor:
            full_command = f"{editor} {config_path}"
            subprocess.run(full_command, shell=True)  # nosec B602
        else:
            if editor == "code" or "Code.exe" in editor:
                full_command = f"{editor} {config_path}"
                subprocess.run(full_command, shell=True)  # nosec B602
            else:
                subprocess.run([editor, config_path], check=True)  # nosec B603
        print(f"{BOLD}{GREEN}{_('config_edited', path=config_path)}{END}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}{_('editor_error', error=e)}{END}")
    except FileNotFoundError:
        print(f"{RED}{_('editor_not_found', editor=editor)}{END}")
        edit_config(config_path)


def main():
    """Main function"""
    config_path = "~/.remote_hosts.json"
    args = sys.argv[1:]
    if not args or args[0] in ["-l", "--list"]:
        if not os.path.exists(os.path.expanduser(config_path)):
            config = Config(config_path)
            config._create_sample()
        hosts = load_hosts(config_path)
        print_hosts(hosts, config_path)

        expanded_config_path = os.path.expanduser(config_path)
        with open(expanded_config_path, "rb") as f:
            file_md5 = _compute_md5(f.read())
        if file_md5 == DEFAULT_SAMPLE_MD5:
            print(f"{RED}{_('config_not_edited')}{END}")
            sys.exit(0)

        try:
            user_input = input(f"{BOLD}{BLUE}{_('enter_host_id')}{END}").strip()
            if user_input.lower() == "q":
                print(f"{BLUE}{_('exit_program')}{END}")
                return
            host_id = int(user_input)
            selected_host = None
            for host in hosts:
                if host.get("id") == host_id:
                    selected_host = host
                    break

            if selected_host:
                user = selected_host.get("user")
                host = selected_host.get("host")
                port = selected_host.get("port", 22)
                key = selected_host.get("key")
                ssh_cmd = ["ssh"]
                if key:
                    ssh_cmd.extend(["-i", os.path.expanduser(key)])
                ssh_cmd.extend(["-p", str(port)])
                ssh_cmd.append(f"{user}@{host}")
                print(f"{GREEN}{_('connecting', user=user, host=host, port=port)}{END}")
                try:
                    subprocess.run(ssh_cmd, check=True)  # nosec B603
                except subprocess.CalledProcessError:
                    print(f"{RED}{_('ssh_failed')}{END}")
            else:
                print(f"{RED}{_('host_not_found', id=host_id)}{END}")
                return
        except ValueError:
            print(f"{RED}{_('invalid_id')}{END}")
            return
    elif args[0] in ["-h", "--help"]:
        print("{}=============================================={}".format(BLUE, END))
        print("{}        {}        {}".format(BOLD + GREEN, _("help_title"), END))
        print("{}=============================================={}".format(BLUE, END))
        print()
        print(_("usage"))
        print()
        print(_("options"))
        print("  -l, --list      {}".format(_("option_list")))
        print("  -e [editor]     {}".format(_("option_edit")))
        print("  -m, --manual    {}".format(_("option_manual")))
        print("  -v, --version   {}".format(_("option_version")))
        print("  -h, --help      {}".format(_("option_help")))
        print("")
    elif args[0] in ["-v", "--version"]:
        print(f"remote-hosts v{__version__}")
    elif args[0] in ["-e", "--edit"]:
        editor = None
        if len(args) > 1:
            editor = args[1]
        edit_config(config_path, editor)
    elif args[0] in ["-m", "--manual"]:
        show_manual()
    else:
        print(_("usage"))
        print(_("invalid_args"))


if __name__ == "__main__":
    main()
