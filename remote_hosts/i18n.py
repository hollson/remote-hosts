#!/usr/bin/env python3

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
        
        # Try to get language from environment variables
        import os
        env_lang = os.environ.get('LANG') or os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES')
        if env_lang and 'zh' in env_lang.lower():
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
        'config_error_array': '配置文件错误：主机列表必须是数组格式',
        'init_config': '已初始化配置文件: ~/.remote_hosts.json',
        'config_error_json': '配置文件错误，执行 remote_hosts -e 进行修复... ',
        'host_config_error': '主机配置错误：ID、主机名和用户名不能为空',
        'duplicate_host_id': '重复的主机ID: {id}, 请检查配置文件',
        'host_info_missing': '主机信息缺失或格式不正确，请检查配置文件',
        'all_rows_empty': '所有行都为空，无法生成表格',
        'manual_not_found': '操作指南文件未找到: {path}',
        'manual_error': '读取操作指南时发生错误: {error}',
        'select_editor': '请选择文本编辑器:',
        'editor_default': '系统默认文本编辑器',
        'editor_vi': 'Vi编辑器',
        'editor_vim': 'Vim编辑器',
        'editor_nano': 'Nano编辑器',
        'editor_code': 'Visual Studio Code',
        'enter_option': '请输入选项编号: ',
        'invalid_option': '无效选项，退出程序',
        'invalid_input': '无效输入，退出程序',
        'config_edited': '配置文件已编辑: {path}',
        'editor_error': '编辑配置文件时发生错误: {error}',
        'editor_not_found': '编辑器 {editor} 未找到，请尝试其他编辑器',
        'enter_host_id': '请输入主机ID(q退出)：',
        'exit_program': '退出程序',
        'connecting': '正在连接到 {user}@{host}:{port}...',
        'ssh_failed': 'SSH连接失败',
        'host_not_found': '未找到ID为 {id} 的主机',
        'invalid_id': '无效输入，请输入数字ID或q退出',
        'help_title': 'SSH 远程主机管理工具',
        'usage': 'usage: remote_hosts [-h] [-v] [-e [editor]]',
        'options': 'options:',
        'option_list': '查看主机列表',
        'option_edit': '编辑配置文件',
        'option_manual': '查看操作指南',
        'option_version': '显示版本信息',
        'option_help': '显示帮助信息',
        'invalid_args': '使用 -h 查看帮助信息',
        'header_id': 'ID',
        'header_host': '主机',
        'header_user': '用户',
        'header_os': '系统',
        'header_arch': '架构',
        'header_region': '区域',
        'header_mark': '备注'
    },
    'en': {
        'config_error_array': 'Configuration error: Host list must be in array format',
        'init_config': 'Configuration file initialized: ~/.remote_hosts.json',
        'config_error_json': 'Configuration file error, run remote_hosts -e to fix... ',
        'host_config_error': 'Host configuration error: ID, host and user cannot be empty',
        'duplicate_host_id': 'Duplicate host ID: {id}, please check configuration file',
        'host_info_missing': 'Host information missing or format incorrect, please check configuration file',
        'all_rows_empty': 'All rows are empty, cannot generate table',
        'manual_not_found': 'Manual file not found: {path}',
        'manual_error': 'Error reading manual: {error}',
        'select_editor': 'Please select text editor:',
        'editor_default': 'System default text editor',
        'editor_vi': 'Vi editor',
        'editor_vim': 'Vim editor',
        'editor_nano': 'Nano editor',
        'editor_code': 'Visual Studio Code',
        'enter_option': 'Please enter option number: ',
        'invalid_option': 'Invalid option, exiting program',
        'invalid_input': 'Invalid input, exiting program',
        'config_edited': 'Configuration file edited: {path}',
        'editor_error': 'Error editing configuration file: {error}',
        'editor_not_found': 'Editor {editor} not found, please try another editor',
        'enter_host_id': 'Please enter host ID (q to exit): ',
        'exit_program': 'Exiting program',
        'connecting': 'Connecting to {user}@{host}:{port}...',
        'ssh_failed': 'SSH connection failed',
        'host_not_found': 'Host with ID {id} not found',
        'invalid_id': 'Invalid input, please enter numeric ID or q to exit',
        'help_title': 'SSH Remote Host Management Tool',
        'usage': 'usage: remote_hosts [-h] [-v] [-e [editor]]',
        'options': 'options:',
        'option_list': 'View host list',
        'option_edit': 'Edit configuration file',
        'option_manual': 'View operation manual',
        'option_version': 'Show version information',
        'option_help': 'Show help information',
        'invalid_args': 'Use -h for help',
        'header_id': 'ID',
        'header_host': 'Host',
        'header_user': 'User',
        'header_os': 'OS',
        'header_arch': 'Arch',
        'header_region': 'Region',
        'header_mark': 'Mark'
    }
}

# Get translated text
def _(key, **kwargs):
    """Get translated text"""
    if key in TEXT.get(LANG, TEXT['en']):
        return TEXT[LANG][key].format(**kwargs)
    return TEXT['en'].get(key, key)