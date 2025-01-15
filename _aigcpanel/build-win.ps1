# Enable echo
$VerbosePreference = "Continue"

# 环境准备
conda 'shell.powershell' 'hook' | Out-String | Invoke-Expression
conda env list
Remove-Item -Recurse -Force ./.aienv -ErrorAction SilentlyContinue -Verbose
conda create --prefix ./.aienv -y python=3.8
conda activate ./.aienv
# 环境准备

# 初始化环境
git submodule update --init --recursive
conda install -y -c conda-forge pynini==2.1.5
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com
python download_model.py
# 初始化环境

# 启动服务
python webui.py
# 启动服务

# 打包服务
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue -Verbose
# 打包服务

$VERSION = python -m aigcpanel.build
Write-Output "VERSION: $VERSION"

Copy-Item -Path ./aigcpanel/server.js -Destination ./dist/server-cosyvoice/server.js

Remove-Item -Recurse -Force .\server-cosyvoice*.zip -ErrorAction SilentlyContinue

Set-Location .\dist\server-cosyvoice
Compress-Archive -Path * -DestinationPath "..\..\server-cosyvoice-$VERSION.zip" -Verbose
Set-Location -Path ..\..