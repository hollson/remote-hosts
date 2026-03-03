#!/usr/bin/env bash

# Python项目构建脚本，基于全流程指南

show_menu() {
    echo "Python项目构建脚本"
    echo "=================="
    echo "请选择要执行的操作："
    echo "1. 安装构建依赖 (build, twine)"
    echo "2. 构建项目"
    echo "3. 查看构建文件"
    echo "4. 上传到PyPI"
    echo "5. 退出"
    echo
}

install_deps() {
    echo "安装构建依赖..."
    pip3 install build twine
    echo "依赖安装完成！"
    echo
}

build_project() {
    echo "构建项目..."
    python3 -m build
    echo "项目构建完成！"
    echo
}

check_files() {
    echo "构建文件："
    if [ -d "dist" ]; then
        ls -la dist/
    else
        echo "dist目录不存在，请先构建项目"
    fi
    echo
}

upload_pypi() {
    echo "上传到PyPI..."
    echo "注意：系统将提示您输入PyPI API令牌"
    echo "如果没有令牌，请在以下地址创建：https://pypi.org/manage/account/token/"
    echo
    if [ -d "dist" ] && [ "$(ls -A dist)" ]; then
        twine upload dist/*
        echo "上传完成！"
        echo "查看您的包：https://pypi.org/project/remote-hosts/"
    else
        echo "dist目录为空，请先构建项目"
    fi
    echo
}

while true; do
    show_menu
    read -p "请输入选项编号：" choice
    echo
    case $choice in
        1)
            install_deps
            ;;
        2)
            build_project
            ;;
        3)
            check_files
            ;;
        4)
            upload_pypi
            ;;
        5)
            echo "退出脚本"
            exit 0
            ;;
        *)
            echo "无效选项，请重新输入"
            echo
            ;;
    esac
done


