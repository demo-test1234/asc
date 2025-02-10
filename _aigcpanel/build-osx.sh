#!/bin/bash

set -x
set -e

# 环境准备
eval "$(conda shell.bash hook)"
conda env list
rm -rfv ./_aienv
conda create --prefix ./_aienv -y python=3.8
conda activate ./_aienv
conda info
# 环境准备

# 初始化环境
git submodule update --init --recursive
conda install -y -c conda-forge pynini==2.1.5
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
#python download_model.py
# 初始化环境

# 构建
python -m py_compile webui.py
python -m py_compile aigcpanelrun.py
mv __pycache__/webui.cpython-38.pyc webui.pyc
mv __pycache__/aigcpanelrun.cpython-38.pyc aigcpanelrun.pyc
# 构建

# 启动服务
# python webui.pyc
# 启动服务

# 清除文件
rm -rfv webui.py || true
rm -rfv aigcpanelrun.py || true
rm -rfv build || true
rm -rfv dist || true
rm -rfv asset || true
rm -rfv *.md || true
#rm -rfv download_model.py || true
rm -rfv requirements.txt || true
rm -rfv .git || true
rm -rfv .github || true
find . -type d -name "__pycache__" -print -exec rm -r {} +
# 清除文件

# 打包服务
VERSION=$(python -m _aigcpanel.build)
VERSION_ARCH=$(echo $VERSION | awk -F '-' '{print $1"-"$2}')
echo "VERSION: ${VERSION}"
echo "VERSION_ARCH: ${VERSION_ARCH}"
curl -o launcher "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/aigcpanel-server-launcher/launcher-${VERSION_ARCH}"
chmod +x launcher
curl -o binary/ffmpeg "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/ffmpeg/ffmpeg-${VERSION_ARCH}"
chmod +x binary/ffmpeg
curl -o binary/ffprobe "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/ffprobe/ffprobe-${VERSION_ARCH}"
chmod +x binary/ffprobe
rm -rfv "_aigcpanel/build*"
rm -rfv "_aigcpanel/config.json"
security find-identity -v -p codesigning
#find . \( -name "*.pyc" -o -name "*.dylib" -o -name "*.so" \) -print0 | xargs -0 -n 1 -P 4 sudo codesign --force --verbose --sign - || true
find . \( -name "*.pyc" -o -name "*.dylib" -o -name "*.so" \) -print0 | xargs -0 -n 1 -P 4 sudo codesign --force --verbose --sign "Xi'an Yanyi Information Technology Co., Ltd (Q96H3H33RK)" || true
zip -rv "./aigcpanel-server-cosyvoice-${VERSION}.zip" *
# 打包服务

