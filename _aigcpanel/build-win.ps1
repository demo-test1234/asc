# Enable echo
$VerbosePreference = "Continue"

# 工具准备
Get-Module -ListAvailable -Name PowerShellGet -ErrorAction SilentlyContinue
Install-Module -Name PowerShellGet -Force -Scope CurrentUser
Install-Module -Name 7Zip4Powershell -Force -Scope CurrentUser
Import-Module 7Zip4Powershell
# 工具准备

# 环境准备
conda 'shell.powershell' 'hook' | Out-String | Invoke-Expression
conda env list
Remove-Item -Recurse -Force ./_aienv -ErrorAction SilentlyContinue -Verbose
conda create --prefix ./_aienv -y python=3.8
conda activate ./_aienv
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
Move-Item -Path "__pycache__\webui.cpython-38.pyc" -Destination "webui.pyc"
Move-Item -Path "__pycache__\aigcpanelrun.cpython-38.pyc" -Destination "aigcpanelrun.pyc"
# 构建

# 启动服务
#python webui.pyc
# 启动服务

# 清除文件
Remove-Item -Path "webui.py" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "aigcpanelrun.py" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force asset -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force .\*.md -ErrorAction SilentlyContinue
#Remove-Item -Recurse -Force .\download_model.py -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\requirements.txt -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\third_party\Matcha-TTS\data -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\.git -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force .\.github -ErrorAction SilentlyContinue
Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
# 清除文件

# 打包服务
$VERSION = python -m _aigcpanel.build
$VERSION_ARCH = ($VERSION -split '-')[0..1] -join '-'
Write-Output "VERSION: $VERSION"
Write-Output "VERSION_ARCH: $VERSION_ARCH"
Invoke-WebRequest -Uri "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/aigcpanel-server-launcher/launcher-$VERSION_ARCH" -OutFile "launcher.exe"
Invoke-WebRequest -Uri "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/ffmpeg/ffmpeg-$VERSION_ARCH" -OutFile "binary\ffmpeg.exe"
Invoke-WebRequest -Uri "https://modstart-lib-public.oss-cn-shanghai.aliyuncs.com/ffprobe/ffprobe-$VERSION_ARCH" -OutFile "binary\ffprobe.exe"
Remove-Item -Path "_aigcpanel/build*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "_aigcpanel/config.json" -Recurse -Force -ErrorAction SilentlyContinue
Compress-7Zip -Path . -Format Zip -ArchiveFileName "..\aigcpanel-server-cosyvoice-$VERSION.zip"
Move-Item -Path "..\aigcpanel-server-cosyvoice-$VERSION.zip" -Destination "aigcpanel-server-cosyvoice-$VERSION.zip"
# 打包服务
