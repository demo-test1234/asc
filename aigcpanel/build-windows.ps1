# Enable echo
$VerbosePreference = "Continue"

conda activate cosyvoice

Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

pyinstaller -y build.spec

Remove-Item -Recurse -Force dist\server-cosyvoice\_dep\pretrained_models\CosyVoice-300M\.git -ErrorAction SilentlyContinue

$VERSION = python -m aigcpanel.build
Write-Output "VERSION: $VERSION"

Remove-Item -Recurse -Force .\server-cosyvoice*.zip -ErrorAction SilentlyContinue

Set-Location .\dist\server-cosyvoice
Compress-Archive -Path * -DestinationPath "..\..\server-cosyvoice-$VERSION.zip" -Verbose
Set-Location -Path ..\..