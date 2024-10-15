#!/bin/sh

pyinstaller -y build.spec

rm -rfv ./dist/server-cosyvoice/_dep/pretrained_models/CosyVoice-300M/.git

cp aigcpanel/config.json ./dist/server-cosyvoice/config.json

sed -i '' 's/__ENV__/macOS/g' dist/server-cosyvoice/config.json

sed -i '' 's/__ARCH__/arm64/g' dist/server-cosyvoice/config.json

rm -rfv ./server-cosyvoice.zip

cd ./dist/server-cosyvoice && zip -rv ../../server-cosyvoice.zip * && cd ../..