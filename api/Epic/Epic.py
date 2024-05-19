from asyncio import Event, Queue
from typing import TypedDict
from api.DataStore.JsonAccessor import JsonAccessor
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend

class MassageHistoryUnit(TypedDict):
    message: dict[str,str]
    現在の日付時刻: TimeExtend

class Epic:
    massage_history:list[MassageHistoryUnit] = []
    def __init__(self):
        self.OnMessageEvent = Queue[MassageHistoryUnit]()

    @property
    def messageHistory(self):
        return self.massage_history

    async def appendMessage(self, message: dict[str,str]):
        history_object:MassageHistoryUnit = {
            "message": message,
            "現在の日付時刻": TimeExtend()
        }
        self.massage_history.append(history_object)
        await self.OnMessageEvent.put(history_object)

    


