from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import json
import locale

# Language detection
def get_system_language():
    """Get system language setting"""
    try:
        # Get system language
        lang, _ = locale.getlocale()
        if lang:
            # Check if language code contains Chinese
            if 'zh' in lang.lower():
                return 'zh'
        # Default to English
        return 'en'
    except:
        # Default to English on error
        return 'en'

# Language code
LANG = get_system_language()

# Text translation dictionary
TEXT = {
    'zh': {
        'init_config': '已初始化配置文件: ~/.remote_hosts.json'
    },
    'en': {
        'init_config': 'Configuration file initialized: ~/.remote_hosts.json'
    }
}

# Get translated text
def _(key, **kwargs):
    """Get translated text"""
    if key in TEXT.get(LANG, TEXT['en']):
        return TEXT[LANG][key].format(**kwargs)
    return TEXT['en'].get(key, key)

class PostInstallCommand(install):
    """Post-installation command to initialize configuration file"""
    def run(self):
        install.run(self)
        # Initialize configuration file
        config_path = os.path.expanduser("~/.remote_hosts.json")
        if not os.path.exists(config_path):
            # Create sample configuration file
            sample_data = [
                {"id": 1, "host": "example.com", "port": 22, "user": "root", "key": "~/.ssh/id_rsa", "os": "ubuntu22.04", "arch": "x86_64", "region": "newyork", "mark": "example"},
                {"id": 2, "host": "172.16.1.10", "user": "root", "mark": "example"},
            ]
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(sample_data, file, indent='\t', ensure_ascii=False)
            print(_('init_config'))

class PostDevelopCommand(develop):
    """Post-development installation command to initialize configuration file"""
    def run(self):
        develop.run(self)
        # Initialize configuration file
        config_path = os.path.expanduser("~/.remote_hosts.json")
        if not os.path.exists(config_path):
            # Create sample configuration file
            sample_data = [
                {"id": 1, "host": "example.com", "port": 22, "user": "root", "key": "~/.ssh/id_rsa", "os": "ubuntu22.04", "arch": "x86_64", "region": "newyork", "mark": "example"},
                {"id": 2, "host": "172.16.1.10", "user": "root", "mark": "example"},
            ]
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(sample_data, file, indent='\t', ensure_ascii=False)
            print(_('init_config'))
