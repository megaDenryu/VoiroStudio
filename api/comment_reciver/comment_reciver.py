import websocket._app
import json
import requests

class NikoNamaCommentReciever:
    def __init__(self):
        self.ws = None

    def get_room_info(self, room_id):
        url = f"https://live2.nicovideo.jp/watch/{room_id}/programinfo"
        response = requests.get(url)
        data = response.json()
        message_server_uri = f"wss://a.live2.nicovideo.jp/wsapi/v1/watch/{room_id}/timeshift?audience_token={data['program']['audienceToken']}"
        return message_server_uri

    def on_message(self, ws, message):
        comment = json.loads(message)
        print(comment)

    def main(self, room_id):
        message_server_uri = self.get_room_info(room_id)
        self.ws = websocket._app.WebSocketApp(message_server_uri, on_message=self.on_message)
        self.ws.run_forever()

if __name__ == "__main__":
    room_id = 'lv343601761'  # ニコニコ生放送の部屋IDを指定します。
    nikonama_comment_reciever = NikoNamaCommentReciever()
    nikonama_comment_reciever.main(room_id)