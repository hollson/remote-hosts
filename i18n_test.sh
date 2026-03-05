#!/usr/bin/env bash

# 测试多语言功能
export LANG=en_US.UTF-8
# export LANG=zh_CN.UTF-8

# Run the remote_hosts command with English language
python3 -c "import sys; sys.path.insert(0, '.'); from remote_hosts.cli import main; sys.argv = ['remote_hosts'] + sys.argv[1:]; main()" "$@"
