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
<b>A lightweight and efficient SSH remote host management tool that makes your remote connections simpler and more convenient</b>
<br/>
<a href="README.md">English</a> | <a href="README_zh.md">中文</a>
</div> 


<br/>



## 📦 Installation

**Install from PyPI (recommended)**

```bash
pip install remote-hosts
```

**Install from source**

```bash
# Clone the repository
git clone https://github.com/hollson/remote-hosts.git
cd remote-hosts

# Install
pip install -e .
```



<br/>



## 🎯 Usage Examples

- **Display help information**

```bash
$ remote_hosts -h
==============================================
        SSH Remote Host Management Tool        
==============================================

usage: remote_hosts [-h] [-v] [-e [editor]]

options:
  -l, --list      View host list
  -e [editor]     Edit configuration file
  -m, --manual    View operation guide
  -v, --version   Display version information
  -h, --help      Display help information
```

- **Login to remote host**

```bash
$ remote_hosts
┌──────────┬────────────────┬──────────┬───────────────┬──────────┬───────────┬───────────┐
│    ID    │      Host      │   User   │     System    │   Arch   │   Region  │   Mark    │
├──────────┼────────────────┼──────────┼───────────────┼──────────┼───────────┼───────────┤
│1         │example.com     │root      │ubuntu22.04    │x86_64    │newyork    │example    │
│2         │172.16.1.10     │root      │-              │-         │-          │example    │
└──────────┴────────────────┴──────────┴───────────────┴──────────┴───────────┴───────────┘
Please enter host ID (q to exit): 1
Connecting to root@example.com:22...
```

- **Edit configuration file**

```bash
$ remote_hosts -e
Please select text editor:
  1. default    System default text editor
  2. vi         Vi editor
  3. vim        Vim editor
  4. nano       Nano editor
  5. code       Visual Studio Code
Please enter option number: 
```



<br/>



## ⚙️ Configuration Example

The configuration file is located at `~/.ssh/term_hosts.json` in JSON format. A sample configuration file will be automatically created when running for the first time.

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



## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
