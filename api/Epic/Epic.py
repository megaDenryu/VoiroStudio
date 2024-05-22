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

class Epic:
    massage_history:list[MassageHistoryUnit] = []
    def __init__(self):
        self.OnMessageEvent = Queue[MassageHistoryUnit]()

    @property
    def messageHistory(self):
        return self.massage_history

    async def appendMessage(self, message: dict[str,str]):
        print("epicでメッセージが来た",message)
        history_object:MassageHistoryUnit = {
            "message": MessageUnit(message),
            "現在の日付時刻": TimeExtend()
        }
        self.massage_history.append(history_object)
        await self.OnMessageEvent.put(history_object)

    


