# Enable echo
$VerbosePreference = "Continue"

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
python download_model.py
# 初始化环境

# 启动服务
#python webui.py
# 启动服务

# 打包服务
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue -Verbose
$VERSION = python -m _aigcpanel.build
Write-Output "VERSION: $VERSION"
Remove-Item -Recurse -Force .\*.zip -ErrorAction SilentlyContinue
Compress-Archive -DestinationPath "aigcpanel-server-cosyvoice-$VERSION.zip" -Verbose
# 打包服务
