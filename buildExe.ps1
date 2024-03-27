cd api
pyinstaller --noconfirm VoivoStudio.spec
cd ..
# api\dist\VoiroStudioをVoiroStudioにコピー
cp -r api/dist/VoiroStudio VoiroStudio