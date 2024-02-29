# このアプリでできること。

# 準備するものの手順
1. PowerShellをインストール
2. vscodeをインストール
3. pythonをインストール。バージョンはpython3.11以上（多分最新バージョンなら何でもいいかも）
   
# gitを用いたダウンロード、インストール、初めてのアプリ起動の手順
4. gitをインストール
5. githubにアカウント登録
6. 本アプリをダウンロードして保存したいフォルダを好きな場所に作る。
7. 作ったフォルダで右クリック→「ターミナルで開く」をクリック。するとPowerShellが開きます。
8. パワーシェルに以下のコマンドを1行ずつコピペして実行します。１行コピーして、パワーシェルで右クリックするかctr+vで貼り付けできます。
   ```
   # コードをクローンする
   git clone https://github.com/megaDenryu/VoiroStudio.git
   # クローンしたディレクトリへ移動
   cd .\VoiroStudioReleaseVer\
   # pythonにvirtualenvをインストール。pythonのインストールが終わっていない場合は準備するものに戻ってpythonをインストールしてください。
   pip install virtualenv
   # CreateEnv.ps1を実行。virtualenvで仮想環境を作ってその中でライブラリのインストールを自動実行します。
   .\CreateEnv.ps1
   # 「環境構築が完了しました。run.ps1を実行するとアプリが起動できます。」とパワーシェルに表示されると成功なのでサーバーを起動します。
   .\run.ps1
   ```
9. ブラウザで http://localhost:8010/ にアクセス。
10. サーバーを終了するには ctr+Cを連打してください。途中でエラーが出るのでctr+Cを２~３回連打すると終了できます。もしくはパワーシェルを閉じてください。

# アプリの起動方法
このアプリはあなたのパソコンの中でwebサーバーを起動してブラウザで使うアプリになっています。
1. VoiroStudioReleaseVerフォルダで右クリック→「ターミナルで開く」をクリック。するとPowerShellが開きます。
2. PowerShellで以下のコマンドを実行
   ```
    .\run.ps1
   ```
3. ブラウザで http://localhost:8010/ にアクセス。複数ウインドウからアクセスできます。

# ボイスロイドの立ち絵の追加方法

# ニコ生のコメントの取得方法
コメントを取得したいニコ生のURLを、コメントを読んでもらいたいボイロのテキストボックスに貼り付けて送信してください。

# ボイスロイドの背景をグリーンバックにする方法
グリーンバックにしたいボイロのウインドウのテキストボックスに
GBmode:
と入力して送信してください。


# dockerについて
cevioとAIVOICEをdockerからだと触り方がわからなかったのでdockerでの起動はお勧めしていません。分から方がいたらgithubの方にプルリクをくれるとハッピーハッピーです。

# ボイロキャラの立ち絵追加時にすること
1. api\images\psd_parser_python\parse_main.py にpsdファイルの絶対パスと、出力先フォルダの絶対パスを記入して実行
2. api\images\image_manager\HumanPart.py のsetCharFilePath関数のname_listのキャラ配列の先頭に表示したいpsdのフォルダを指定。
3. api\gptAI\voiceroid_api.pyを開き、
   1. cevio、AIVOICEならsetCharNameのname_dictにブラウザで入力したい名前とキャラ本名の対を入力
4. api\gptAI\Human.py

# 対応機器
自分のパソコンでサーバーを起動すると、ご家庭のwifi経由で他のパソコンやスマホのブラウザからもipアドレス経由でこのアプリを使えます。
ただしipadやiphoneでは音がならせないです。