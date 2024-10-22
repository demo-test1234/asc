# Enable echo
$VerbosePreference = "Continue"

conda 'shell.powershell' 'hook' | Out-String | Invoke-Expression

conda activate cosyvoice

Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue -Verbose
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue -Verbose

pyinstaller -y build.spec

Remove-Item -Recurse -Force dist\server-cosyvoice\_dep\pretrained_models\CosyVoice-300M\.git -ErrorAction SilentlyContinue

$VERSION = python -m aigcpanel.build
Write-Output "VERSION: $VERSION"

Copy-Item -Path ./aigcpanel/server.js -Destination ./dist/server-cosyvoice/server.js

Remove-Item -Recurse -Force .\server-cosyvoice*.zip -ErrorAction SilentlyContinue

Set-Location .\dist\server-cosyvoice
Compress-Archive -Path * -DestinationPath "..\..\server-cosyvoice-$VERSION.zip" -Verbose
Set-Location -Path ..\..