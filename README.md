## Overview
FastAPIでWebSocketsを動作させフロントとサーバーのリアルタイム通信を実現しています。

## markdowのvscodeでのプレビュー
ctr + k → vで可能

## Usage
複数ウィンドウを開き、それぞれ以下のリンクにアクセスする
http://localhost:8080

メッセージを送信すると、開いたウィンドウ全てににメッセージが表示される

## Install

```
# コードをクローンする
$ git clone https://github.com/sattosan/sample-fastapi-websockets.git

# クローンしたディレクトリへ移動
$ cd ./sample-fastapi-websockets

# コンテナの起動

```
# windows側で使うとき
このディレクトリで
```
pip3 install virtualenv
python -m virtualenv localenv
cd localenv
cd Scripts
.\activate.ps1  #(powershellの場合)
cd ../..
pip3 install --trusted-host pypi.python.org -r requirements_20230810.txt
cd ./api/web && uvicorn main:app --reload --port=8000 --host=0.0.0.0 && cd ../..
```

# requirements.txtの出力方法
pip freeze -l > requirements_20230810.txt

# ボイロキャラの立ち絵追加時にすること
1. api\images\psd_parser_python\parse_main.py にpsdファイルの絶対パスと、出力先フォルダの絶対パスを記入して実行
2. api\images\image_manager\HumanPart.py のsetCharFilePath関数のname_listのキャラ配列の先頭に表示したいpsdのフォルダを指定。
3. api\gptAI\voiceroid_api.pyを開き、
   1. cevio、AIVOICEならsetCharNameのname_dictにブラウザで入力したい名前とキャラ本名の対を入力
4. api\gptAI\Human.py

# iHumanManagerからHumanaManager2への移行
1. index.html
   1. 作成するインスタンスをiHumanManagerからHumanaManager2にする
   2. 読み込むアコーディオンのjsファイルを切り替える
2. HumanPart.pyのmode_human_part_managerを切り替える

# 設計とか
# ボイロ
## gptの制御
目的対立悩み決断とかのゲームデザインを入れる
- 問題解決型デザイン
  - pdca,
- 情緒型デザイン
  - 目的対立悩み決断
- 世界制御デザイン
## psdの制御
human_windowクラスが枠。
その中にbg_imgとhuman_imgクラスを画像そのままおいてるだけなので、枠の中をcanvasにすれば大丈夫そうな気がする。cssの制御は。。。

### パーツ出力時の注意
- 口のパーツはあいうえおがわかるように出力すること
- 感情は色々なパラメータが考えられるが、psdの特殊目に基づいた感情パラメータを考える必要がある。
- psdの制御を機械学習させたいので、データはおしゃべりしながらポーズ微調整してそのデータをため込めるようにする
  - 「その文章ならポーズはこうだろ！」て調整するのは画像バラバラにしたおかげでできるしそうしよう
- psdのレイヤー制御
  - 基本的にレイヤーN内ではどの画像もvisibleにできるが、*がついてるものは一つしかvisibleにできないという仕組み
  - レイヤーと画像の両方にvisibilityのパラメータが付与されている
- 結局のところgptに画像を制御してもらわないと行けない。
  - gptにどう投げればいいか？
    - psdからパースするときに構造を出力して
  - gptにどういう形式で返答してもらうか？
    - 返答される方法に合わせてjsを書かないと行けない
```

```

### パーツの取り扱いの確定事項
#### パーツ出力と送信と表示方法について
1. フォルダをjsonに変換したとき名前がキーで画像が値の辞書形式であり、キーが配列番号になってないので、表示するときに名前からレイヤーのz_indexを取得するしかない。
2. そのためフォルダや画像は番号を付けてpsdからフォルダ分けするが、3_ピアス のように、アンダースコアを入れること。
3. また、

### キャラの名前制御について
例えばおねちゃんを使うときはプログラムで4か所別々のオブジェクトで名前を扱う
- フロントで名前を入力
- gptの人格呼び出し用ができる名前
- ボイロエンジン呼び出し用の名前
- キャラパーツ呼び出し用の名前
キャラパーツはpsdごとのフォルダ名があるが、そのうえの階層はボイロエンジンとそろえられる
なので以下の様に設計する
- フロントで入力想定名⇒ボイロエンジン呼び出し用の名前の配列
- gptとパーツ呼び出しはいくつかのモードを作るので、
```
[ボイロエンジン呼び出し用の名前=>
  [
  モード1,
  モード2
  ]
]
```
とする
### OИE
パーツ構成は
- 0body
  - 何もしなくてよい
- 1尻尾
  - gptに制御させる必要ない。時間ごとにランダムに制御
- 2耳
  - gptに制御させる必要ない。時間ごとにランダムに制御
- 3腕
  - 2パターンしかないので、
- 4口
  - あ:0
  - い:1
  - う:2
  - え:3
  - お:4
  - ん:7(喜),8(悲),9(ムムム)
  - はわわ:5
  - おねー！:6
  - 
- 5眼球
  - 
- 6眉
- 7その他

## ポケモンの型、パーティーの管理画面
### 要件
- ポケモンの名前や技、特性などをテキストボックスに入力すると候補を出力する。
- sdの様な主要ポケモンの一覧も表示
- 典型的な努力値調整をできるようにする

### 手順
- とりあえずポケモンを入力してinputしたらそのデータを