from asyncio import Event, Queue
from typing import TypedDict
from api.DataStore.JsonAccessor import JsonAccessor
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend

class MessageUnit:
    def __init__(self, message: dict[str,str]):
        self.message = message
        self.speakers = message.keys()

class MassageHistoryUnit(TypedDict):
    message: MessageUnit
    現在の日付時刻: TimeExtend
    stop: bool

class Epic:
    massage_history:list[MassageHistoryUnit] = []
    def __init__(self):
        self.OnMessageEvent = Queue[MassageHistoryUnit]()

    @property
    def messageHistory(self):
        return self.massage_history
    
    def getLatestMessage(self):
        if len(self.massage_history) == 0:
            message = {
                "エラー":"メッセージが存在しません"
            }
            tmp_message = {
            "message": MessageUnit(message),
            "現在の日付時刻": TimeExtend()
            }
            return tmp_message
        return self.massage_history[-1]
    
    def appendMessage(self, message: dict[str,str]):
        history_object:MassageHistoryUnit = {
            "message": MessageUnit(message),
            "現在の日付時刻": TimeExtend(),
            "stop": False
        }
        self.massage_history.append(history_object)
        ExtendFunc.ExtendPrint("メッセージを追加しました")

    async def appendMessageAndNotify(self, message: dict[str,str]):
        print("epicでメッセージが来た",message)
        history_object:MassageHistoryUnit = {
            "message": MessageUnit(message),
            "現在の日付時刻": TimeExtend(),
            "stop": False
        }
        self.massage_history.append(history_object)
        ExtendFunc.ExtendPrint("メッセージを追加しました")
        await self.OnMessageEvent.put(history_object)

    


