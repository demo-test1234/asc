
build_clean:
	rm -rfv dist
	rm -rfv build

build_pyinstaller:
	pyinstaller -y build.spec
	rm -rfv ./dist/server-cosyvoice/_dep/pretrained_models/CosyVoice-300M/.git

build_run:
    ./dist/server-cosyvoice/main --port=50000