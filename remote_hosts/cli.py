#!/usr/bin/env python3

import os
import json
import sys
import subprocess
from remote_hosts.i18n import _, LANG

__version__ = "0.1.1"

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    HEADER = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

class HostConfig:
    """Host configuration class for validating and managing host configuration information"""
    def __init__(self, host_data):
        self.id = host_data.get('id')
        self.host = host_data.get('host')
        self.port = host_data.get('port', 22)
        self.user = host_data.get('user')
        self.key = host_data.get('key')
        self.os = host_data.get('os', '-')
        self.arch = host_data.get('arch', '-')
        self.region = host_data.get('region', '-')
        self.mark = host_data.get('mark', '-')
    
    def is_valid(self):
        """Check if host configuration is valid"""
        return self.id is not None and self.host and self.user

class Config:
    """Configuration management class for loading and validating configuration files"""
    def __init__(self, config_path):
        self.config_path = os.path.expanduser(config_path)
        self.hosts = []
    
    def load(self):
        """Load configuration file"""
        try:
            with open(self.config_path, 'r') as file:
                data = json.load(file)
                # Check if data is a dict with 'hosts' key
                if isinstance(data, dict) and 'hosts' in data:
                    hosts_data = data['hosts']
                else:
                    hosts_data = data
                
                # Validate host list format
                if not isinstance(hosts_data, list):
                    print(f"{Color.RED}{_('config_error_array')}{Color.END}")
                    exit(1)
                
                # Validate and load host configurations
                self._validate_and_load_hosts(hosts_data)
                
        except FileNotFoundError:
            self._create_sample()
            print(f"{Color.BLUE} {_('init_config')}{Color.END}")
            exit(0)
        except json.JSONDecodeError:
            print(f"{Color.RED}{_('config_error_json')}{Color.END}")
            exit(1)
        
        return self.hosts
    
    def _validate_and_load_hosts(self, hosts_data):
        id_set = set()
        for host_data in hosts_data:
            host_config = HostConfig(host_data)
            
            if not host_config.is_valid():
                print(f"{Color.RED}{_('host_config_error')}{Color.END}")
                exit(1)
            
            if host_config.id in id_set:
                print(f"{Color.RED}{_('duplicate_host_id', id=host_config.id)}{Color.END}")
                exit(1)
            id_set.add(host_config.id)
            
            self.hosts.append(host_data)
    
    def _create_sample(self):
        """Create sample configuration file"""
        sample_data = [
            {"id": 1, "host": "example.com", "port": 22, "user": "root", "key": "~/.ssh/id_rsa", "os": "ubuntu22.04", "arch": "x86_64", "region": "newyork", "mark": "example"},
            {"id": 2, "host": "172.16.1.10", "user": "root", "mark": "example"},
        ]
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(sample_data, file, indent='\t', ensure_ascii=False)

def load_hosts(config_path):
    """Load hosts from configuration file"""
    config = Config(config_path)
    return config.load()

def print_hosts(hosts, config_path):
    """Print host list in table format"""
    # Prepare table data
    header_labels = [_('header_id'), _('header_host'), _('header_user'), _('header_os'), _('header_arch'), _('header_region'), _('header_mark')]
    headers = [f"{Color.BOLD}{Color.BLUE}{label}{Color.END}" for label in header_labels]
    
    rows = []
    for host in hosts:
        try:
            host_id = host.get('id')
            host_name = host.get('host')
            user_name = host.get('user')
            
            os_info = host.get('os', '-')
            arch_info = host.get('arch', '-')
            region_info = host.get('region', '-')
            mark_info = host.get('mark', '-')
            
            # Host and user cannot be empty
            if host_id is not None and host_name and user_name:
                rows.append([
                    f"{Color.GREEN}{host_id}{Color.END}",
                    f"{Color.GREEN}{host_name}{Color.END}",
                    f"{Color.GREEN}{user_name}{Color.END}",
                    os_info,
                    arch_info,
                    region_info,
                    mark_info
                ])
            
        except KeyError:
            print(f"{Color.RED}{_('host_info_missing')}{Color.END}")
            exit(1)
    
    if rows:
        # Calculate maximum width for each column, considering Chinese characters
        def get_clean_length(s):
            # Remove ANSI color codes
            import re
            clean = re.sub(r'\x1B\[[0-9;]*m', '', s)
            # Calculate string width, Chinese characters count as 2, English as 1
            width = 0
            for c in clean:
                if ord(c) > 127:
                    width += 2  # Chinese character
                else:
                    width += 1  # English character
            return width
        
        col_widths = [get_clean_length(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], get_clean_length(cell))
        
        # Add fixed extra space to each column for better appearance
        col_widths = [max(width + 4, 10) for width in col_widths]
        
        # Print top border
        top_border = '┌' + '┬'.join(['─' * width for width in col_widths]) + '┐'
        print(top_border)
        
        # Print header row
        header_row = '│'
        for header, width in zip(headers, col_widths):
            # Calculate actual content length (without color codes)
            clean_len = get_clean_length(header)
            # Calculate left padding
            left_pad = (width - clean_len) // 2
            # Calculate right padding
            right_pad = width - clean_len - left_pad
            # Build header cell
            header_row += ' ' * left_pad + header + ' ' * right_pad + '│'
        print(header_row)
        
        # Print header separator
        middle_border = '├' + '┼'.join(['─' * width for width in col_widths]) + '┤'
        print(middle_border)
        
        # Print data rows
        for row in rows:
            data_row = '│'
            for cell, width in zip(row, col_widths):
                # Calculate actual content length (without color codes)
                clean_len = get_clean_length(cell)
                # Left align, right padding
                right_pad = width - clean_len
                # Build data cell
                data_row += cell + ' ' * right_pad + '│'
            print(data_row)
        
        # Print bottom border
        bottom_border = '└' + '┴'.join(['─' * width for width in col_widths]) + '┘'
        print(bottom_border)
    else:
        print(f"{Color.RED}{_('all_rows_empty')}{Color.END}")

def show_manual():
    """Show operation manual"""
    # Select manual file based on language
    manual_file = 'manual_zh.txt' if LANG == 'zh' else 'manual.txt'
    try:
        import pkgutil
        content = pkgutil.get_data('remote_hosts', manual_file)
        if content:
            print(content.decode('utf-8'))
        else:
            print(f"{Color.RED}{_('manual_not_found', path=manual_file)}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}{_('manual_not_found', path=manual_file)}{Color.END}")
        print(f"{Color.RED}{_('manual_error', error=e)}{Color.END}")

def edit_config(config_path, editor=None):
    """Edit configuration file"""
    config_path = os.path.expanduser(config_path)
    
    # Check if configuration file exists, create if not
    if not os.path.exists(config_path):
        config = Config(config_path)
        config._create_sample()
    
    if not editor:
        print(f"{Color.BOLD}{Color.BLUE}{_('select_editor')}\n  1. default \t{_('editor_default')}\n  2. vi \t{_('editor_vi')}\n  3. vim \t{_('editor_vim')}\n  4. nano \t{_('editor_nano')}\n  5. code \t{_('editor_code')}{Color.END}")
        try:
            choice = int(input(_('enter_option')))
            if choice == 1:
                if sys.platform == 'darwin':
                    editor = 'open -a TextEdit'
                elif sys.platform == 'win32':
                    # Use notepad to open configuration file in Windows
                    editor = 'notepad'
                else:
                    editor = 'vi'
            elif choice == 2:
                editor = 'vi'
            elif choice == 3:
                editor = 'vim'
            elif choice == 4:
                editor = 'nano'
            elif choice == 5:
                # Try to find VS Code executable in common locations
                if sys.platform == 'win32':
                    # Common VS Code installation paths on Windows
                    vscode_paths = [
                        r'D:\Program\VSCode\Code.exe',      # Based on user's setup
                        r'D:\Program\VSCode\bin\code.cmd',  # Based on user's setup
                        r'C:\Program Files\Microsoft VS Code\Code.exe',
                        r'C:\Program Files\Microsoft VS Code\bin\code.cmd',
                    ]
                    for path in vscode_paths:
                        if os.path.exists(path):
                            editor = path
                            break
                    else:
                        # Fallback to just 'code' if no path found
                        editor = 'code'
                else:
                    editor = 'code'
            else:
                print(f"{Color.RED}{_('invalid_option')}{Color.END}")
                exit(1)
        except ValueError:
            print(f"{Color.RED}{_('invalid_input')}{Color.END}")
            exit(1)
    
    try:
        if ' ' in editor:
            # For commands with spaces, use shell=True
            full_command = f"{editor} {config_path}"
            subprocess.run(full_command, shell=True)
        else:
            # For VS Code and similar GUI editors, use shell=True
            if editor == 'code' or 'Code.exe' in editor:
                # Use shell=True to find code command
                full_command = f"{editor} {config_path}"
                subprocess.run(full_command, shell=True)
            else:
                # For other editors, use direct call
                subprocess.run([editor, config_path], check=True)
        print(f"{Color.BOLD}{Color.GREEN}{_('config_edited', path=config_path)}{Color.END}")
    except subprocess.CalledProcessError as e:
        print(f"{Color.RED}{_('editor_error', error=e)}{Color.END}")
    except FileNotFoundError:
        print(f"{Color.RED}{_('editor_not_found', editor=editor)}{Color.END}")
        edit_config(config_path)

def main():
    """Main function"""
    # Configuration file path
    config_path = "~/.remote_hosts.json"
    
    # Parse command line arguments manually
    args = sys.argv[1:]
    
    if not args or args[0] in ['-l', '--list']:
        # Initialize configuration file if not exists
        if not os.path.exists(os.path.expanduser(config_path)):
            config = Config(config_path)
            config._create_sample()
            print(f"{Color.BLUE} {_('init_config')}{Color.END}")
        # No arguments or -l/--list, show host list
        hosts = load_hosts(config_path)
        print_hosts(hosts, config_path)
        
        # Prompt user to enter host ID
        try:
            user_input = input(f"{Color.BOLD}{Color.BLUE}{_('enter_host_id')}{Color.END}").strip()
            if user_input.lower() == 'q':
                    print(f"{Color.BLUE}{_('exit_program')}{Color.END}")
                    return
            
            host_id = int(user_input)
            # Find corresponding host
            selected_host = None
            for host in hosts:
                if host.get('id') == host_id:
                    selected_host = host
                    break
            
            if selected_host:
                # Build SSH command
                user = selected_host.get('user')
                host = selected_host.get('host')
                port = selected_host.get('port', 22)
                key = selected_host.get('key')
                
                ssh_cmd = ['ssh']
                if key:
                    ssh_cmd.extend(['-i', os.path.expanduser(key)])
                ssh_cmd.extend(['-p', str(port)])
                ssh_cmd.append(f"{user}@{host}")
                
                print(f"{Color.GREEN}{_('connecting', user=user, host=host, port=port)}{Color.END}")
                try:
                    subprocess.run(ssh_cmd, check=True)
                except subprocess.CalledProcessError:
                    print(f"{Color.RED}{_('ssh_failed')}{Color.END}")
            else:
                print(f"{Color.RED}{_('host_not_found', id=host_id)}{Color.END}")
                return
        except ValueError:
            print(f"{Color.RED}{_('invalid_id')}{Color.END}")
            return
    elif args[0] in ['-h', '--help']:
        print('{}=============================================={}'.format(Color.BLUE, Color.END))
        print('{}        {}        {}'.format(Color.BOLD + Color.GREEN, _('help_title'), Color.END))
        print('{}=============================================={}'.format(Color.BLUE, Color.END))
        print()
        print(_('usage'))
        print()
        print(_('options'))
        print("  -l, --list      {}".format(_('option_list')))
        print("  -e [editor]     {}".format(_('option_edit')))
        print("  -m, --manual    {}".format(_('option_manual')))
        print("  -v, --version   {}".format(_('option_version')))
        print("  -h, --help      {}".format(_('option_help')))
        print("")
    elif args[0] in ['-v', '--version']:
        # Show version information
        print(f"remote-hosts v{__version__}")
    elif args[0] in ['-e', '--edit']:
        # Edit configuration file
        editor = None
        if len(args) > 1:
            editor = args[1]
        edit_config(config_path, editor)
    elif args[0] in ['-m', '--manual']:
        # Show operation manual
        show_manual()
    else:
        # Invalid argument, show help information
        print(_('usage'))
        print(_('invalid_args'))

def init_config():
    """Initialize configuration file during installation"""
    config_path = "~/.remote_hosts.json"
    config = Config(config_path)
    # Create sample configuration if not exists
    if not os.path.exists(os.path.expanduser(config_path)):
        config._create_sample()
        print(_('init_config'))

class InitConfigCommand:
    """Distutils command to initialize configuration file"""
    description = "Initialize configuration file"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        init_config()

if __name__ == "__main__":
    main()
