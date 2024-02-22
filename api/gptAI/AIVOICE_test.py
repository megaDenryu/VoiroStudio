# 確認環境
# Python 3.10.2
# pip install pythonnet==3.0.0a2

# 普段からPython書いてるわけではない人がひとまず公式ガイドのサンプルコードを元に試してみただけなので参考程度に

# A.I.VOICE Editor API 公式ガイド https://aivoice.jp/manual/editor/api.html

import os
import clr
import time

_editor_dir = os.environ['ProgramW6432'] + '\\AI\\AIVoice\\AIVoiceEditor\\'

if not os.path.isfile(_editor_dir + 'AI.Talk.Editor.Api.dll'):
  print("A.I.VOICE Editor (v1.3.0以降) がインストールされていません。")
  exit()

# pythonnet DLLの読み込み
clr.AddReference(_editor_dir + "AI.Talk.Editor.Api")
from AI.Talk.Editor.Api import TtsControl, HostStatus

tts_control = TtsControl()

# A.I.VOICE Editor APIの初期化
host_name = tts_control.GetAvailableHostNames()[0]
tts_control.Initialize(host_name)

# A.I.VOICE Editorの起動
if tts_control.Status == HostStatus.NotRunning:
  tts_control.StartHost()

# A.I.VOICE Editorへ接続
tts_control.Connect()
host_version = tts_control.Version
print(f"{host_name} (v{host_version}) へ接続しました。")

# テキストを設定
tts_control.Text = "A.I.VOICE Editor API work with Python"

# 再生
play_time = tts_control.GetPlayTime()
tts_control.Play()
# Play()は再生完了を待たないので予め取得した再生時間+α分sleepで待つ
time.sleep((play_time + 500) / 1000)

# 音声を保存
tts_control.SaveAudioToFile("C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\web\\output_wav\\AIVoice_test.wav")

# A.I.VOICE Editorとの接続を終了する
tts_control.Disconnect()
print(f"{host_name} (v{host_version}) との接続を終了しました。")