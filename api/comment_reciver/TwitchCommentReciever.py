from dataclasses import dataclass
from twitchio import Channel, Message
from twitchio.ext import commands
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.DataStore.JsonAccessor import JsonAccessor
from api.Extend.ExtendFunc import ExtendFunc
from asyncio import Queue

@dataclass
class TwitchMessageUnit():
    message: str
    listner_name: str

class TwitchBot(commands.Bot):
    COMMAND_PREFIX = "!"

    def __init__(self, initial_channels:str|None=None, WTITCH_ACCESS_TOKEN:str|None = None):
        if WTITCH_ACCESS_TOKEN is None:
            raise ValueError("WTITCH_ACCESS_TOKENが指定されていません。")
        if initial_channels is None:
            raise ValueError("initial_channelsが指定されていません。")
        
        self.WTITCH_ACCESS_TOKEN = WTITCH_ACCESS_TOKEN
        self.initial_channels = initial_channels
        super().__init__(
            token=self.WTITCH_ACCESS_TOKEN,
            prefix=self.COMMAND_PREFIX,
            initial_channels=[initial_channels]
        )
        self.message_queue:Queue[TwitchMessageUnit] = Queue()
        

    #チャンネルにログイン
    def run(self):
        super().run()

    async def async_run(self):
        try:
            await self.connect()  # Use await instead of creating a task
        except KeyboardInterrupt:
            pass
        finally:
            if not self._closing.is_set():
                await self.close()
        
    

    #チャンネルからログアウト
    async def stop(self):
        await super().close()




    #チャンネルからログアウト
    async def event_channel_left(self, channel: Channel):
        ExtendFunc.ExtendPrint(f"ログアウトしました。チャンネル名: {channel.name}")
        await channel.send(f"{self.nick}は逃げ出した！")

    #チャンネルにログイン
    async def event_channel_joined(self, channel: Channel):
        print(f"ログインしました。チャンネル名: {channel.name}")
        if channel.chatters is None:
            ExtendFunc.ExtendPrint("チャンネルのチャッターが取得できませんでした。")
            return
        for chatter in channel.chatters:
            ExtendFunc.ExtendPrint(f'ユーザー名: {chatter.name}')
        
        if self.judgeConfirmingConnect(self.initial_channels, chatter) == True:
            await channel.send(f"{chatter.name}があらわれた！")

    #全てのチャンネルにログイン
    async def event_ready(self):
        print("全てのチャンネルにログインしました。")
        print(f'ユーザーID: {self.user_id}')
        print(f'ユーザー名: {self.nick}')

    
    #チャットメッセージを受信
    async def event_message(self, message: Message):
        #botのメッセージは無視
        if message.echo: 
            return
        
        message_dict = self.generateDictFromMessageRawData(message.raw_data)
        ExtendFunc.ExtendPrint(f"メッセージを受信しました。: {message.content}")
        ExtendFunc.ExtendPrint(message_dict)
        listener_name = message_dict["display-name"]
        message_unit = TwitchMessageUnit(str(message.content), listener_name)
        ExtendFunc.ExtendPrint(message_unit)
        await self.message_queue.put(message_unit)
        


    def judgeConfirmingConnect(self, initial_channels:str, chatter):
        if chatter.name == initial_channels:
            return True
        return False
    
    def generateDictFromMessageRawData(self, raw_data:str):
        """
        メッセージの生データを辞書型に変換します。
        """
        message_dict = {}
        raw_data_list = raw_data.split(";")
        for raw_data in raw_data_list:
            key_value = raw_data.split("=")
            message_dict[key_value[0]] = key_value[1]
        return message_dict
    
    @staticmethod
    def getAccessToken():
        return JsonAccessor.loadTwitchAccessToken()

if __name__ == "__main__":
    name = "rokkaman"
    key = "eftnrfpk0d5cf9yj7yodf6b3u6wxpz"
    bot = TwitchBot(name,key)
    bot.run()