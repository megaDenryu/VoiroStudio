### 各種ライブラリのインポート
import requests
import json
import time
import asyncio
import websockets.client
from bs4 import BeautifulSoup

### コメントを取得したい放送のURLを指定
live_id = "lv343601761"
#live_id = "co3000390" # コミュニティIDを指定すると放送中のものを取ってきてくれる
url = "https://live2.nicovideo.jp/watch/"+live_id

### htmlを取ってきてWebSocket接続のための情報を取得
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser") 
embedded_data = json.loads(soup.find('script', id='embedded-data')["data-props"])
url_system = embedded_data["site"]["relive"]["webSocketUrl"]

### websocketでセッションに送るメッセージ
message_system_1 = {"type":"startWatching",
                    "data":{"stream":{"quality":"abr",
                                      "protocol":"hls",
                                      "latency":"low",
                                      "chasePlay":False},
                            "room":{"protocol":"webSocket",
                                    "commentable":True},
                            "reconnect":False}}
message_system_2 ={"type":"getAkashic",
                   "data":{"chasePlay":False}}
message_system_1 = json.dumps(message_system_1)
message_system_2 = json.dumps(message_system_2)

### コメントセッション用のグローバル変数
uri_comment = None
message_comment = None

### 視聴セッションとのWebSocket接続関数
async def connect_WebSocket_system():
    global url_system
    global uri_comment
    global message_comment

    ### 視聴セッションとのWebSocket接続開始
    async with websockets.client.connect(url_system) as websocket:

        ### 最初のメッセージを送信
        await websocket.send(message_system_1)
        await websocket.send(message_system_2) # これ送らなくても動いてしまう？？
        print("SENT TO THE SYSTEM SERVER: ",message_system_1)
        print("SENT TO THE SYSTEM SERVER: ",message_system_2)

        ### 視聴セッションとのWebSocket接続中ずっと実行
        while True:
            message = await websocket.recv()
            message_dic = json.loads(message)
            print("RESPONSE FROM THE SYSTEM SERVER: ",message_dic)

            ### コメントセッションへ接続するために必要な情報が送られてきたら抽出してグローバル変数へ代入
            if(message_dic["type"]=="room"):
                uri_comment = message_dic["data"]["messageServer"]["uri"]
                threadID = message_dic["data"]["threadId"]
                message_comment = [{"ping": {"content": "rs:0"}},
                                    {"ping": {"content": "ps:0"}},
                                    {"thread": {"thread": threadID,
                                                "version": "20061206",
                                                "user_id": "guest",
                                                "res_from": -150,
                                                "with_global": 1,
                                                "scores": 1,
                                                "nicoru": 0}},
                                    {"ping": {"content": "pf:0"}},
                                    {"ping": {"content": "rf:0"}}]
                message_comment = json.dumps(message_comment)

            ### pingが送られてきたらpongとkeepseatを送り、視聴権を獲得し続ける
            if(message_dic["type"]=="ping"):
                pong = json.dumps({"type":"pong"})
                keepSeat = json.dumps({"type":"keepSeat"})
                await websocket.send(pong)
                await websocket.send(keepSeat)
                print("SENT TO THE SYSTEM SERVER: ",pong)
                print("SENT TO THE SYSTEM SERVER: ",keepSeat)

### コメントセッションとのWebSocket接続関数
async def connect_WebSocket_comment():
    loop = asyncio.get_event_loop()

    global uri_comment
    global message_comment

    ### 視聴セッションがグローバル変数に代入するまで1秒待つ
    await loop.run_in_executor(None, time.sleep, 1)

    ### コメントセッションとのWebSocket接続を開始
    async with websockets.client.connect(uri_comment) as websocket:

            ### 最初のメッセージを送信
        await websocket.send(message_comment)
        print("SENT TO THE COMMENT SERVER: ",message_comment)

        ### コメントセッションとのWebSocket接続中ずっと実行
        while True:
            message = await websocket.recv()
            message_dic = json.loads(message)
            print("RESPONSE FROM THE COMMENT SERVER: ",message_dic)

### asyncioを用いて上で定義した2つのWebSocket実行関数を並列に実行する
loop = asyncio.get_event_loop()
gather = asyncio.gather(
    connect_WebSocket_system(),
    connect_WebSocket_comment())
loop.run_until_complete(gather)
