#!/bin/sh

conda activate cosyvoice

rm -rfv build/ dist/

pyinstaller -y build.spec

rm -rfv ./dist/server-cosyvoice/_dep/pretrained_models/CosyVoice-300M/.git

VERSION=$(python -m aigcpanel.build)
echo "VERSION: ${VERSION}"

rm -rfv ./server-cosyvoice*.zip

cd ./dist/server-cosyvoice && zip -rv "../../server-cosyvoice-${VERSION}.zip" * && cd ../..


