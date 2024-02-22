$currentDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
# /で区切られた最後の文字列を取得
$currentDirectory = $currentDirectory -split "\\" | Select-Object -Last 1
if ($currentDirectory -eq "VoiroStudioReleaseVer") {
    Write-Host "成功"
    python3 -m virtualenv localenv
    .\activate_localenv.ps1
    python.exe -m pip install --upgrade pip
    pip install -r requirements_20240220.txt
} else {
    Write-Host "このファイルの場所が移動しています。VoiroStudioReleaseVerフォルダでこのプログラムを実行してください。"
}