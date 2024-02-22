$currentDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
# /で区切られた最後の文字列を取得
$currentDirectory = $currentDirectory -split "\\" | Select-Object -Last 1
if ($currentDirectory -eq "VoiroStudioReleaseVer") {
    Write-Host "正しい位置でこのファイルが実行されたので環境構築を開始します"
    python3 -m virtualenv localenv
    .\activate_localenv.ps1
    python.exe -m pip install --upgrade pip
    pip install -r requirements_20240220.txt
    Write-Host "環境構築が完了しました。run.ps1を実行するとアプリが起動できます。"
} else {
    Write-Host "このファイルの場所が移動しています。VoiroStudioReleaseVerフォルダでこのプログラムを実行してください。"
}