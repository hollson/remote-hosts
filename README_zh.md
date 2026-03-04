<div align="center">
<h1>Remote Hosts</h1>
<a href="https://pypi.org/project/remote-hosts/">
<img src="https://img.shields.io/pypi/v/remote-hosts.svg?style=flat-square" alt="PyPI Version"></a>
<a href="https://pypi.org/project/remote-hosts/"><img src="https://img.shields.io/pypi/pyversions/remote-hosts.svg?style=flat-square" alt="Python Versions"></a>
<a href="#">
<img src="https://img.shields.io/badge/SSH-2.0-blue?style=flat-square" alt="SSH Protocol"></a>
<a href="#">
<img src="https://img.shields.io/badge/Remote-Management-green?style=flat-square" alt="Remote Management"></a>
<a href="LICENSE"><img src="https://img.shields.io/github/license/hollson/remote-hosts.svg?style=flat-square" alt="License"></a>
<a href="https://github.com/hollson/remote-hosts/stargazers"><img src="https://img.shields.io/github/stars/hollson/remote-hosts.svg?style=flat-square" alt="Stars"></a>
<a href="#"><img src="https://img.shields.io/badge/Lightweight-Efficient-purple?style=flat-square" alt="Lightweight"></a>
<br/>
<b>一个轻量级、高效的SSH远程主机管理工具，让您的远程连接更加简单便捷</b>
<br/>
<a href="README.md">English</a> | <a href="README_zh.md">中文</a>
</div> 
<br/>



## 📦 安装方法

**从PyPI安装（推荐）**

```bash
pip install remote-hosts
```

**从源码安装**

```bash
# 克隆仓库
git clone https://github.com/hollson/remote-hosts.git
cd remote-hosts

# 安装
pip install -e .
```



<br/>



## 🎯 使用示例

- **显示帮助信息**

```bash
$ remote_hosts -h
==============================================
        SSH 远程主机管理工具        
==============================================

usage: remote_hosts [-h] [-v] [-e [editor]]

options:
  -l, --list      查看主机列表
  -e [editor]     编辑配置文件
  -m, --manual    查看操作指南
  -v, --version   显示版本信息
  -h, --help      显示帮助信息
```

- **登录远程主机**

```bash
$ remote_hosts
┌──────────┬────────────────┬──────────┬───────────────┬──────────┬───────────┬───────────┐
│    ID    │      主机      │   用户   │     系统      │   架构   │   区域    │   备注    │
├──────────┼────────────────┼──────────┼───────────────┼──────────┼───────────┼───────────┤
│1         │example.com    │root      │ubuntu22.04    │x86_64    │newyork    │example    │
│2         │172.16.1.10     │root      │-              │-         │-          │example    │
└──────────┴────────────────┴──────────┴───────────────┴──────────┴───────────┴───────────┘
请输入主机ID(q退出)：1
正在连接到 root@example.com:22...
```

- **编辑配置文件**

```bash
$ remote_hosts -e
请选择文本编辑器:
  1. default    系统默认文本编辑器
  2. vi         Vi编辑器
  3. vim        Vim编辑器
  4. nano       Nano编辑器
  5. code       Visual Studio Code
请输入选项编号: 
```



<br/>



## ⚙️ 配置示例

配置文件位于 `~/.ssh/term_hosts.json`，采用JSON格式。首次运行时会自动创建示例配置文件。

```json
[
	{
		"id": 1,
		"host": "example.com",
		"port": 22,
		"user": "root",
		"key": "~/.ssh/id_rsa",
		"os": "ubuntu22.04",
		"arch": "x86_64",
		"region": "newyork",
		"mark": "example"
	},
	{
		"id": 2,
		"host": "172.16.1.10",
		"user": "root",
		"mark": "example"
	}
]
```



<br/>



## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件



