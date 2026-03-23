#!/usr/bin/env bash

# 设置语言
# export LANG=en_US.UTF-8
export LANG=zh_CN.UTF-8

# 选择 Python 解释器
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
elif command -v py >/dev/null 2>&1; then
    PY=py
else
    echo "ERROR: no Python executable found (python3/python/py)" >&2
    exit 1
fi

# 运行测试命令, 如: ./run.sh --help
$PY -c "import sys; sys.path.insert(0, '.'); from remote_hosts.cli import main; sys.argv = ['remote_hosts'] + sys.argv[1:]; main()" "$@"
