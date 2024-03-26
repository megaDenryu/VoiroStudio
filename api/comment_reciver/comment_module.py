import requests
import json
import time
from datetime import datetime, timedelta
import asyncio
import websockets.client
from bs4 import BeautifulSoup

class NicoNamaCommentReciever:
    """
    end_keyword: 終了キーワードを指定すると、そのキーワードがコメントに含まれた時点でコメント受信を終了する
    """
    def __init__(self, live_id, end_keyword=""):
        self.live_id = live_id
        self.url = "https://live2.nicovideo.jp/watch/" + live_id
        self.uri_comment = None
        self.message_comment = None
        self.websocket_system = None
        self.end_keyword = end_keyword
        self.recieve_status = "recieveing"

    async def _connect_WebSocket_system(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, "html.parser") 
        embedded_data = json.loads(soup.find('script', id='embedded-data')["data-props"])
        url_system = embedded_data["site"]["relive"]["webSocketUrl"]

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

        async with websockets.client.connect(url_system) as self.websocket_system:
            await self.websocket_system.send(message_system_1)
            await self.websocket_system.send(message_system_2)

            while True:
                message = await self.websocket_system.recv()
                message_dic = json.loads(message)

                if(message_dic["type"]=="room"):
                    self.uri_comment = message_dic["data"]["messageServer"]["uri"]
                    threadID = message_dic["data"]["threadId"]
                    self.message_comment = [{"ping": {"content": "rs:0"}},
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
                    self.message_comment = json.dumps(self.message_comment)
                    break  # uri_commentとmessage_commentが設定されたらループを抜ける

                if(message_dic["type"]=="ping"):
                    pong = json.dumps({"type":"pong"})
                    keepSeat = json.dumps({"type":"keepSeat"})
                    await self.websocket_system.send(pong)
                    await self.websocket_system.send(keepSeat)

    async def _connect_WebSocket_comment(self):
        await asyncio.sleep(1)  # 非同期版のスリープを使用

        async with websockets.client.connect(self.uri_comment) as websocket:
            await websocket.send(self.message_comment)

            while True:
                message = await websocket.recv()
                message_dic = json.loads(message)
                print("80行目:",self.end_keyword, message_dic.get('content', ''))
                # コメントに終了キーワードが含まれていたらループを抜ける
                if self.recieve_status == "end":
                    print("終了キーワードがコメントに含まれていたため、コメント受信を終了します")
                    break
                print("83行目:",message_dic)
                yield message_dic

    async def get_comments(self):
        await self._connect_WebSocket_system()
        async for recive_data in self._connect_WebSocket_comment():
            #print(recive_data)
            should_recive, comment_data = self.filterRecieveData(recive_data)
            # 現在時刻を取得し、comment_data["date"]との差分が1分以内のコメントのみを返す
            now = datetime.now()
            if "date" in comment_data:
                comment_date = datetime.strptime(comment_data["date"], "%Y/%m/%d %H:%M:%S")
                if (now - comment_date).total_seconds() < 60 and should_recive:
                    yield comment_data

    def filterRecieveData(self, recive_data):
        """
        recive_dataの例
        {'chat': {'thread': 'M.ZlttKBLUccDJawdwdetXH99w', 'no': 297, 'vpos': 783204, 'date': 1701864413, 'date_usec': 52269, 'mail': 'マリも', 'user_id': 'iQ9LQyzZVQ_fefsfe1LF5cp_I', 'premium': 3, 'anonymity': 1, 'content': '/emotion 草'}}
        
        dateは1970/1/1 09:00:00からの秒数
        mailはコメントした人の名前。184は匿名。
        contentはコメント内容
        """
        should_recive = False
        comment_data = {}
        if "chat" in recive_data:
            data = recive_data["chat"]
            if "content" in data:
                comment_data["comment"] = data["content"]
                should_recive = True
            
            if "date" in data:
                comment_data["date"] = self.calcDatetime(data["date"])

            if "mail" in data:
                comment_data["name"] = data["mail"]

            if "user_id" in data:
                comment_data["user_id"] = data["user_id"]

        return should_recive, comment_data
    
    

    def calcDatetime(self, seconds):
        # 1970/1/1 09:00:00から指定秒数後の日時を計算
        start = datetime(1970, 1, 1, 9, 0, 0)
        target = start + timedelta(seconds=seconds)
        return target.strftime("%Y/%m/%d %H:%M:%S")
    
    def checkAndStopRecieve(self,sentence):
        if self.end_keyword != "" and self.end_keyword in sentence:
            self.recieve_status = "end"
    


# 以下テスト用
async def main_niconama_comment_reciver():
    live_id = "lv343626019"
    end_keyword = "終了ビンビン終了ビンビン終了ビンビン終了ビンビン"
    nikonama_comment_reciever = NicoNamaCommentReciever(live_id, end_keyword)
    print("コメント受信開始")

    async for comment in nikonama_comment_reciever.get_comments():
        print(comment)

if __name__ == "__main__":
    asyncio.run(main_niconama_comment_reciver())