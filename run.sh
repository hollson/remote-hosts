#!/usr/bin/env bash

# 设置语言
# export LANG=en_US.UTF-8
export LANG=zh_CN.UTF-8

# 运行测试命令, 如: ./run.sh --help
python3 -c "import sys; sys.path.insert(0, '.'); from remote_hosts.cli import main; sys.argv = ['remote_hosts'] + sys.argv[1:]; main()" "$@"
