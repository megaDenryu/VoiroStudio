from starlette.websockets import WebSocket
from enum import Enum
import pydantic
from api.DataStore.JsonAccessor import JsonAccessor

class PageMode(str, Enum):
    Setting = "Setting"
    Chat = "Chat"


class ConnectionStatus(pydantic.BaseModel):
    client_id: str
    ws: WebSocket
    page_mode: PageMode
    setting_mode: str

class AppSettingModule:
    def __init__(self):
        self.setting_client_ws:dict[str,dict[PageMode,list[ConnectionStatus]]] = {}
        self.setting = self.loadSetting()

    def addWs(self, setting_mode: str, page_mode:PageMode , client_id:str, ws:WebSocket):
        connction = ConnectionStatus(client_id=client_id, ws=ws, page_mode=page_mode, setting_mode=setting_mode)
        if page_mode not in self.setting_client_ws[setting_mode]:
            dict = {
                PageMode.Setting: [],
                PageMode.Chat: []
            }
            self.setting_client_ws[setting_mode] = dict
        self.setting_client_ws[setting_mode][page_mode].append(connction)


    async def notify(self, message_dict:dict, setting_mode: str):
        """
        同じsetting_modeのws全てにメッセージを送信します。
        """
        connections = self.setting_client_ws[setting_mode]
        for ws in connections[PageMode.Setting]:
            await ws.ws.send_json(message_dict)
        for ws in connections[PageMode.Chat]:
            await ws.ws.send_json(message_dict)

    def setSetting(self, setting_mode:str, page_mode:PageMode, client_id:str, setting_dict:dict):
        """
        setting_dictをsetting_modeのjsonに保存し、対応するオブジェクトに反映します。
        """
        self.setting = self.loadSetting()
        for key in setting_mode:
            self.setting[setting_mode][key] = setting_dict[key]
        self.saveSetting(self.setting)


    def loadSetting(self):
        return JsonAccessor.loadAppSetting()
    
    def saveSetting(self, setting):
        JsonAccessor.saveAppSetting(setting)




    

