from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pprint import pprint
from pathlib import Path
from fastapi import WebSocket
from openai import OpenAI, AsyncOpenAI, AssistantEventHandler
import sys
import asyncio
from asyncio import Event, Queue, tasks
import re
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendSet import Interval
from api.gptAI.Human import Human
# from api.gptAI.AgenetResponseJsonType import ThinkAgentResponse
from api.Extend.ExtendFunc import ExtendFunc, RandomExtend, TimeExtend
from api.DataStore.JsonAccessor import JsonAccessor
from api.Epic.Epic import Epic, MassageHistoryUnit, MessageUnit
from typing import Literal, Protocol, TypedDict
from typing import Any, Dict, get_type_hints, get_origin
from pydantic import BaseModel, validator


class ChatGptApiUnit:
    """
    責務:APIにリクエストを送り、結果を受け取るだけ。クエリの調整は行わない。
    """
    class MessageQuery(TypedDict):
        role: Literal['system', 'user', 'assistant']
        content: str

    def __init__(self,test_mode:bool = False):
        try:
            api_key = JsonAccessor.loadOpenAIAPIKey()
            self.client = OpenAI(api_key = api_key)
            self.async_client = AsyncOpenAI(api_key = api_key)
            self.test_mode = test_mode

        except Exception as e:
            print("APIキーの読み込みに失敗しました。")
            raise e
    async def asyncGenereateResponseGPT4TurboJson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"

        response = await self.async_client.chat.completions.create (
                model="gpt-4o",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    
    def genereateResponseGPT4TurboJson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create (
                model="gpt-4o",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        pprint(response)
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT4TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = await self.async_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT4TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    
class MicInputJudgeAgentResponse(TypedDict):
    理由:str
    入力成功度合い:float

class SpeakerDistributeAgentResponse(TypedDict):
    理由考察:str
    次に発言するべきキャラクター:str
    
class TransportedItem(BaseModel):
    time:TimeExtend
    data:Any
    recieve_messages:str
    MicInputJudge_data:MicInputJudgeAgentResponse 
    SpeakerDistribute_data:SpeakerDistributeAgentResponse #dict[str,str]
    Listening_data:Any
    Think_data:dict[str,str]
    Serif_data:Any
    NonThinkingSerif_data:Any
    stop:bool = False
    class Config:
        arbitrary_types_allowed = True

class EventReciever(Protocol):
    name:str
    async def handleEvent(self, transported_item:TransportedItem):
        pass
class EventRecieverWaitFor(Protocol):
    name:str
    async def handleEvent(self, transported_item:TransportedItem):
        pass
    def timeOutSec(self)->float: # type: ignore
        pass
    def timeOutItem(self)->TransportedItem: # type: ignore
        pass

class EventNotifier(Protocol):
    event:Event
    async def notify(self, data):
        pass

class QueueNotifier(Protocol):
    event_queue:Queue[TransportedItem]
    async def notify(self, data:TransportedItem):
        pass

class QueueNotifierWaitFor(Protocol):
    event_queue:Queue[TransportedItem]
    async def notify(self, data:TransportedItem):
        pass
    def timeOutSec(self)->float: # type: ignore
        pass
    def timeOutItem(self)->TransportedItem: # type: ignore
        pass

class EventNode(EventReciever,EventNotifier,Protocol):
    pass
class QueueNode(EventReciever,QueueNotifier,Protocol):
    pass




"""
一人のHumanに対して複数のエージェントを動かしたい
Human→AgentManager→Agent→AgentRoutine
話すためには考える必要がある
手順１
手順２


エージェント１と２を作る。それらはAgentmanagerに登録される。
プロンプトのサンプルを取得し、名前を書き換える人
プロんプトを送り人結果を受け取る人
その結果を次のAgentに送る人


"""

class AgentManager:
    _message_memory:list[MassageHistoryUnit] = []
    input_reciever:"InputReciever"
    speaker_distribute_agent:"SpeakerDistributeAgent"
    mic_input_check_agent:"MicInputJudgeAgent"
    think_agent:"ThinkAgent"
    serif_agent:"SerifAgent"
    GPTModeSetting:dict[str,str] = {}
    def __init__(
            self,chara_name:str, 
            epic:Epic, 
            human_dict:dict[str,Human], 
            websocket:WebSocket,
            input_reciever:"InputReciever",
            ):
        self.chara_name:str = chara_name
        self.epic = epic
        self.human_dict:dict[str,Human] = human_dict
        self.chara_dict:dict[str,Agent] = {}
        self._message_memory:list[MassageHistoryUnit] = epic.messageHistory
        self.replace_dict = self.loadReplaceDict(self.chara_name)
        self.prepareAgents(self.replace_dict)
        self.websocket = websocket
        self.input_reciever = input_reciever
        self.GPTModeSetting = JsonAccessor.loadAppSetting()["GPT設定"]

    @property
    def message_memory(self) -> list[MassageHistoryUnit]:
        return self._message_memory
    
    @property
    def latest_message_time(self)->TimeExtend:
        return self._message_memory[-1]['現在の日付時刻']
    
    @message_memory.setter
    def message_memory(self, value: list[MassageHistoryUnit]):
        self._message_memory = value

    def addMessageMemory(self,message:MassageHistoryUnit):
        self._message_memory.append(message)
    
    def loadReplaceDict(self,chara_name:str)->dict[str,str]:
        replace_dict = {
            "gptキャラ":chara_name,
            "playerキャラ":"",
            "gptキャラのロール":"",
            "gptキャラの属性":""
        }
        return replace_dict

    @staticmethod
    def joinMessageMemory(message_memory:list[MassageHistoryUnit]):
        ret_string = ""
        for message in message_memory:
            ret_string = f"{ret_string}\n{message}"
        return ret_string
    
    async def sendCheck(self, old_latest_message_time, message_memory:list, time:TimeExtend, serif_agent_response):
        
        if self.isThereDiffNumMemory(old_latest_message_time):
            return False
        
        if TimeExtend.diffTime(time) < 3:
            await asyncio.sleep(3)
            if self.isThereDiffNumMemory(old_latest_message_time):
                return False

        return True
    
    def isThereDiffNumMemory(self, old_latest_message_time:TimeExtend)->bool:
        diff = self.latest_message_time.toSecond() - old_latest_message_time.toSecond()
        return diff > 0
    
    def diffTime(self, time:int)->int:
        return TimeExtend.nowSecond() - time

    def prepareAgents(self,replaced_dict:dict):
        self.mic_input_check_agent = MicInputJudgeAgent(self)
        self.speaker_distribute_agent = SpeakerDistributeAgent(self)
        # self.listening_agent = ListeningAgent(self)
        self.think_agent = ThinkAgent(self,replaced_dict)
        # self.memory_agent = MemoryAgent(replaced_dict)
        self.serif_agent = SerifAgent(self,self.chara_name)
        
    def createSendData(self, sentence:str, human:Human, chara_type:Literal["gpt","player"]):
        human.outputWaveFile(sentence)
        #wavデータを取得
        wav_info:list["WavInfo"] = human.human_Voice.output_wav_info_list
        sentence_info = {human.front_name:sentence}

        class WavInfo(BaseModel):
            path:str
            wav_data:str
            phoneme_time:list[str]
            phoneme_str:list[list[str]]
            char_name:str
            voice_system_name:str
        class SendData(BaseModel):
            sentence:dict[str,str]
            wav_info:list[WavInfo]
            chara_type:Literal["gpt","player"]

        send_data = {
            "sentence":sentence_info,
            "wav_info":wav_info,
            "chara_type":chara_type
        }
        # send_data = SendData(
        #     sentence = sentence_info,
        #     wav_info = wav_info,
        #     chara_type = chara_type
        # )
        return send_data
        # #バイナリーをjson形式で送信
        # print(f"{human_ai.char_name}のwavデータを送信します")
        # await websocket.send_json(json.dumps(wav_info))

    def modifyMemory(self):
        """
        区分音声の再生が完了した時点で次の音声を送る前にメモリが変わってるかチェックし、変わっていたら次の音声を送らない。
        この時喋った分だけメモリに追加
        これを実装するにはメモリに何を入れるかを考える必要がある
        """
        
    def loadCharaSetting(self):
        pass

    def clearInputRecieverMessageStack(self, time:TimeExtend):
        self.input_reciever.clearMessageStack(time)
        

class Agent:
    """
    エージェントの基底クラス。
    Humanの配下にあるので名前を持っている。
    プロンプトサンプルを受け取って名前などを書き換えてそれをもとにリクエストを作成し送る。
    gptから受け取るときの型を定義して毎回矯正する必要がある
    """
    replace_dict:dict[str,str] = {}
    def __init__(self,agent_manager: AgentManager,  replace_dict: dict[str,str] = {}):
        self.agent_manager = agent_manager
        self._gpt_api_unit = ChatGptApiUnit()
        ExtendFunc.ExtendPrint(replace_dict)
        self.replace_dict = replace_dict

    async def run(self,transported_item: TransportedItem)->TransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query)
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result)
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    @abstractmethod
    def prepareQuery(self,input: TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        pass

    @abstractmethod
    async def request(self,query:list[ChatGptApiUnit.MessageQuery])->str:
        """
        ここはjsonになっていようといまいとstrで返し、correctResultで型を矯正する
        """
        pass

    @abstractmethod
    def correctResult(self,result:str)->Dict[str, Any]:
        pass

    @abstractmethod
    def saveResult(self,result):
        pass

    @abstractmethod
    def clearMemory(self):
        pass

    @abstractmethod
    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        pass

class InputReciever():
    def __init__(self,epic:Epic, gpt_agent_dict:dict[str,"GPTAgent"], gpt_mode_dict:dict[str,str]):
        self.name = "入力受付エージェント"
        self.epic = epic
        self.gpt_agent_dict = gpt_agent_dict
        self.message_stack:list[MassageHistoryUnit] = []
        self.event_queue = Queue[TransportedItem]()
        self.gpt_mode_dict = gpt_mode_dict
        self.runnnig = False
    async def runObserveEpic(self):
        if self.runnnig == False:
            self.runnnig = True
            await self.observeEpic()
    
    async def stopObserveEpic(self):
        self.runnnig = False
        stop_object = MassageHistoryUnit(
            message = MessageUnit({"エラー":"エージェントを停止しました"}),
            現在の日付時刻 = TimeExtend(),
            stop = True
        )
        await self.epic.OnMessageEvent.put(stop_object)
        stop_ti = TransportedItem(
            time = self.epic.getLatestMessage()['現在の日付時刻'], 
            data = "",
            recieve_messages = self.convertMessageHistoryToTransportedItemData(self.message_stack, 0, len(self.message_stack)),
            MicInputJudge_data= MicInputJudgeAgentResponse(理由="", 入力成功度合い=0.0),
            SpeakerDistribute_data = SpeakerDistributeAgentResponse(理由考察="", 次に発言するべきキャラクター=""),
            Listening_data="",
            Think_data={},
            Serif_data="",
            stop=True
            )
        await self.notify(stop_ti)

    async def observeEpic(self):
        while True:
            if self.runnnig == False:
                return
            # epic.onMessageEventを監視する。メッセージが追加されれば3秒待って、また新しいメッセージが追加されればまた3秒待つ。３秒待ってもメッセージが追加されなければ次のエージェントに送る。
            message = await self.epic.OnMessageEvent.get()
            
            if self.runnnig == False:
                # 上で待っている間にキャンセルされてたら終了
                return

            ExtendFunc.ExtendPrint(message)
            self.appendMessageToStack(message)
            while not self.epic.OnMessageEvent.empty():
                message = await self.epic.OnMessageEvent.get()
                self.appendMessageToStack(message)
            # メッセージが追加されたらメッセージスタックに追加。送信したら解放する。
            await asyncio.sleep(3)
            if not self.epic.OnMessageEvent.empty():
                continue

            agent_stop = False
            for agent in self.gpt_agent_dict.values():
                # 全てのエージェントを確認
                last_speskers = self.message_stack[-1]["message"].speakers
                ExtendFunc.ExtendPrint(f"{agent.manager.chara_name}が{last_speskers}にあるか確認します")
                if agent.manager.chara_name in self.message_stack[-1]["message"].speakers:
                    # メッセージスタックの最後のメッセージがこのエージェントが送ったメッセージであれば送信しない
                    ExtendFunc.ExtendPrint(f"{agent.manager.chara_name}が最後に送ったメッセージがあったので次のエージェントには送信しませんでした。")
                    agent_stop = True
            
            if agent_stop:
                continue
                    
            # ここで次のエージェントに送る
            last = len(self.message_stack)
            transported_item:TransportedItem = TransportedItem(
                time = self.epic.messageHistory[-1]['現在の日付時刻'], 
                data = "",
                recieve_messages = self.convertMessageHistoryToTransportedItemData(self.message_stack, 0, len(self.message_stack)),
                MicInputJudge_data= MicInputJudgeAgentResponse(理由="", 入力成功度合い=0.0),
                SpeakerDistribute_data = SpeakerDistributeAgentResponse(理由考察="", 次に発言するべきキャラクター=""),
                Listening_data="",
                Think_data={},
                Serif_data=""
                )
            ExtendFunc.ExtendPrint(transported_item)
            await self.notify(transported_item)
            
    async def notify(self, data:TransportedItem):
        await self.event_queue.put(data)
            
    async def handleEvent(self, data = None):
        # x秒非同期に待つ
        await asyncio.sleep(3)
        # 次が来てるかどうかをチェック。

    @staticmethod
    def convertMessageHistoryToTransportedItemData(message_history:list[MassageHistoryUnit], start_index:int, end_index:int)->str:
        """
        message_historyをstart_indexからend_indexまでのメッセージを連結して文字列に変換して返す
        """
        ret_string = ""
        for i in range(start_index, end_index):
            ret_string = f"{ret_string}{ExtendFunc.dictToStr(message_history[i]['message'].message)}"
        return ret_string
    
    def appendMessageToStack(self, message:MassageHistoryUnit):
        self.message_stack.append(message)
    
    def judgeClearMessageStack(self)->bool:
        """
        thinkAgentに各セリフがたどり着くまでは送り続ける。thinkAgentにたどり着いたらメッセージスタックを解放する。
        """
        return True
    
    def addMessageStack(self, messages:list[MassageHistoryUnit]):
        self.message_stack += messages
    
    def clearMessageStack(self, time:TimeExtend):
        """
        timeより以前のメッセージは削除する
        """
        num = self.getMessageNumFromTime(time)
        if num is None:
            return
        else:
            if num == len(self.message_stack) - 1:
                self.message_stack = []
            else:
                self.message_stack = self.message_stack[num+1:]

    def getMessageNumFromTime(self, time:TimeExtend):
        length = len(self.message_stack)
        for i in range(length-1, -1, -1):
            if self.message_stack[i]['現在の日付時刻'] < time:
                return i
        return None


class MicInputJudgeAgent(Agent):
    @staticmethod
    def typeMicInputJudgeAgentResponse(replace_dict: dict):
        TypeDict = {
            "理由":str,
            "入力成功度合い":Interval("[",0,1,"]")
        }
        return TypeDict
    
    def replaceDictDef(self,input:str)->dict[str,str]:
        return {
            "{{input}}":input
        }
    
    def __init__(self, agent_manager: AgentManager):
        super().__init__(agent_manager, self.replaceDictDef(""))
        self.name = "マイク入力成否判定エージェント"
        self.request_template_name = "マイク入力成否判定エージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue = Queue()
    
    async def run(self,transported_item: TransportedItem)->TransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query)
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result)
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item

    async def handleEvent(self, transported_item:TransportedItem):
        # マイク入力成功判定エージェントがマイク入力に成功しているか判定
        ExtendFunc.ExtendPrint(self.name,transported_item)
        if transported_item.stop:
            await self.notify(transported_item)
            return
        output = await self.run(transported_item)
        if output.MicInputJudge_data["入力成功度合い"] <= 0.5:
            return
        await self.notify(output)

    async def notify(self, data:TransportedItem):
        # LLMが出力した成功か失敗かを通知
        await self.event_queue.put(data)

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        # 最新のメッセージを埋め込むのでここで新たにreplace_dictを作成
        self.replace_dict = {"{{input}}":input.recieve_messages}
        # プロンプトサンプルymlを好きなタイミングで修正したいので毎回読み込むようにしておく。todo 将来的にここは消す。
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        # クエリを作成
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str) -> MicInputJudgeAgentResponse:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        res = ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeMicInputJudgeAgentResponse(self.replace_dict))
        return MicInputJudgeAgentResponse(入力成功度合い=res["入力成功度合い"], 理由=res["理由"])
    
    def saveResult(self,result):
        # 必要ない
        pass

    def clearMemory(self):
        # 必要ない
        pass

    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:MicInputJudgeAgentResponse)->TransportedItem:
        transported_item.MicInputJudge_data = result
        return transported_item
    
class SpeakerDistributeAgent(Agent):
    def __init__(self, agent_manager: AgentManager):
        self.name = "発言者振り分けエージェント"
        self.request_template_name = "発言者振り分けエージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        print(f"{self.agent_manager=}")
        self.epic:Epic = agent_manager.epic
        super().__init__(agent_manager)
        
    @staticmethod
    def typeSpeakerDistributeAgentResponse(replace_dict: dict, chara_name_list: list[str]):
        TypeDict = {
            "理由考察":str,
            "次に発言するべきキャラクター": chara_name_list
        }
        return TypeDict
    def replaceDictDef(self,input:str)->dict[str,str]:
        return {
            "{{input}}":input,
            "{{character_list}}":self.createCharacterListStr()
        }

    async def handleEvent(self, transported_item:TransportedItem):
        # 話者割り振りエージェントが会話を見て次に喋るべきキャラクターを推論
        ExtendFunc.ExtendPrint(self.name,transported_item)
        if transported_item.stop:
            await self.notify(transported_item)
            return
        if self.agent_manager.GPTModeSetting["SpeakerDistributeAgentのmode"] == "全部通す":
            transported_item.SpeakerDistribute_data = {"理由考察":"全部通す" ,"次に発言するべきキャラクター":self.agent_manager.chara_name}
            output = transported_item
        else:
            output = await self.run(transported_item)
        # ランダムかどうかを判定
        if output.SpeakerDistribute_data["次に発言するべきキャラクター"] == "ランダム":
            ExtendFunc.ExtendPrint("次に喋るべきキャラクターがランダムだったのでサイコロを振ります")
            # 0~1の乱数を生成
            if RandomExtend.random0to1() > 0.5:
                # 0.5以上ならランダムでないキャラクターに変更
                output.SpeakerDistribute_data["次に発言するべきキャラクター"] = self.agent_manager.chara_name

        # 次に喋るべきキャラクターが自分でなければキャンセル
        if output.SpeakerDistribute_data["次に発言するべきキャラクター"] != self.agent_manager.chara_name:
            next_chara = output.SpeakerDistribute_data["次に発言するべきキャラクター"]
            ExtendFunc.ExtendPrint(f"結果は{next_chara}でした。{self.agent_manager.chara_name}は次に喋るべきキャラクターではありません")
            return
        ExtendFunc.ExtendPrint(f"結果は{self.agent_manager.chara_name}でしたので喋ります。")
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.messageHistory[-1]['現在の日付時刻'].date != output.time.date:
            new_time = self.epic.messageHistory[-1]['現在の日付時刻'].date
            ExtendFunc.ExtendPrint(f"{new_time}に追加発言があるため{output.time.date}の分はキャンセルします")
            return
        ExtendFunc.ExtendPrint(f"{self.name}はすべて成功したので次のエージェントに行きます。{self.agent_manager.chara_name}が喋ります。")
        await self.notify(output)

    async def notify(self, data: TransportedItem):
        # 次に喋るべきキャラクターを通知
        await self.event_queue.put(data)

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input.recieve_messages)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str) -> SpeakerDistributeAgentResponse:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        res = ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeSpeakerDistributeAgentResponse(self.replace_dict, self.createCharacterList()))
        return SpeakerDistributeAgentResponse(次に発言するべきキャラクター=res["次に発言するべきキャラクター"], 理由考察=res["理由考察"])
    
    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:SpeakerDistributeAgentResponse)->TransportedItem:
        transported_item.SpeakerDistribute_data = result
        return transported_item

    def createCharacterList(self)->list[str]:
        """
        キャラ名のリストを返す。例：['きりたん', 'ずんだもん', 'ゆかり','おね','あかり']
        """
        chara_name_list = ["ランダム"]
        for key in self.agent_manager.human_dict.keys():
            chara_name_list.append(key)
        ExtendFunc.ExtendPrint(chara_name_list)
        return chara_name_list
    def createCharacterListStr(self)->str:
        """
        キャラ名のリストを文字列で返す。例："['きりたん', 'ずんだもん', 'ゆかり','おね','あかり']"
        """
        ret = str(self.createCharacterList())
        ExtendFunc.ExtendPrint(ret)
        return ret
    

class ListeningAgent(Agent):
    @staticmethod
    def typeListeningAgentResponse(replace_dict: dict):
        TypeDict = {
            "文章の長さ": ['とても短い','短い', '中', '長い', 'とても長い'],
            "文章の属性": [['不明', '一人ごと', '鼻歌', '重要でない声', '不完全な文章', '話しかけているつもり', '考えごと', '重要な発言']],
            "状況考察": str,
            "結論": ["話を聞く", "話をさえぎる", "相手の話は一区切りついた"]
            }
        return TypeDict
    
    def replaceDictDef(self,input:str)->dict[str,str]:
        return {
            "{{input}}":input
        }

    def __init__(self, agent_manager: AgentManager):
        super().__init__(agent_manager, self.replaceDictDef(""))
        self.name = "傾聴エージェント"
        self.request_template_name = "傾聴エージェントリクエストひな形"
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()

    async def handleEvent(self, transported_item:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)
        output = await self.run(transported_item)
        if output.Listening_data["結論"] == "話を聞く":
            return
        await self.notify(output)

    async def notify(self, data):
        # 読み上げるための文章を通知
        await self.event_queue.put(data)
    
    def loadAgentSetting(self)->list[ChatGptApiUnit.MessageQuery]:
        return JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",self.replace_dict)[self.name]
    
    def prepareQuery(self, input:str)->list[ChatGptApiUnit.MessageQuery]:
        replace_dict = {"{{input}}":input}
        self.agent_setting = self.loadAgentSetting()
        query = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting,replace_dict)
        return query
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        return ExtendFunc.correctDictToTypeDict(jsonnized_result, ThinkAgent.typeThinkAgentResponse(self.replace_dict, self.agent_manager.chara_name))
    
    def addInfoToTransportedItem(self, transported_item: TransportedItem, result: Dict[str, Any]) -> TransportedItem:
        transported_item.Listening_data = result
        return transported_item


class ThinkAgent(Agent,QueueNode):
    _previous_situation:list[str] = []
    speak_or_silent:Literal["話す","傾聴思考","独り言orつっこみorボケを話す"] = "傾聴思考"

    def __init__(self, agent_manager: AgentManager, replace_dict: dict):
        super().__init__(agent_manager, replace_dict)
        self.name = "思考エージェント"
        self.request_template_name = "思考エージェントリクエストひな形"
        self.chara_name = agent_manager.chara_name
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()

    @staticmethod
    def typeThinkAgentResponse(replace_dict: dict, chara_name:str)->dict[str,str]:
        TypeDict = {
            "以前と今を合わせた周囲の状況の要約": str,
            "どのキャラがどのキャラに話しかけているか？または独り言か？": str,
            "他のキャラの会話ステータス": {str:['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現']},
            "ロール": ['アシスタント', 'キャラクターなりきり'],
            "あなたの属性": ['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ'],
            f"{chara_name}のこれからの感情": ['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠'],
            f"{chara_name}のこれからの会話ステータス": ['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う'],
            "今まで起きたことの要約": str,
            f"{chara_name}の次の行動を見据えた心内セリフと思考": str
            }
        return TypeDict
    
    def replaceDictDef(self, tI:TransportedItem | None = None, previous_situation:str = "なし")->dict[str,str]:
        # gpt_behavior = JsonAccessor.loadGPTBehaviorYaml(self.replace_dict["gpt_character"])
        gpt_behavior = JsonAccessor.loadGPTBehaviorYaml("一般")
        ExtendFunc.ExtendPrint(gpt_behavior)
        if tI == None:
            ExtendFunc.ExtendPrint("tIがNoneです")
            return {
                "{{gptキャラ}}":self.chara_name,
                "{{Playerキャラ}}":"ゆかり",
                "{{前の状況}}":previous_situation,
                "{{input}}":"",
                "{{gptキャラのロール}}":gpt_behavior["gptキャラのロール"],
                "{{gptキャラの属性}}":gpt_behavior["gptキャラの属性"],
                "{{喋るか黙るか}}":"傾聴思考"
            }
        ExtendFunc.ExtendPrint("tIがNoneではありません")
        input = tI.recieve_messages
        self.speak_or_silent:Literal["話す","傾聴思考","独り言orつっこみorボケを話す"] = self.speakOrSilent(tI)
        
        # キャラのロールや属性は別のキャラクター設定ymlから取得する
        relace_dict = {
            "{{gptキャラ}}":self.chara_name,
            "{{Playerキャラ}}":"ゆかり",
            "{{前の状況}}":previous_situation,
            "{{input}}":input,
            "{{gptキャラのロール}}":gpt_behavior["gptキャラのロール"],
            "{{gptキャラの属性}}":gpt_behavior["gptキャラの属性"],
            "{{喋るか黙るか}}":self.speak_or_silent,
        }
        return relace_dict
    
    def speakOrSilent(self, tI:TransportedItem)->Literal["話す","傾聴思考","独り言orつっこみorボケを話す"]:
        if "次に発言するべきキャラクター" not in tI.SpeakerDistribute_data:
            ExtendFunc.ExtendPrint("SpeakerDistribute_dataに次に発言するべきキャラクターがありません")
            return "傾聴思考"
        ExtendFunc.ExtendPrint(self.chara_name)
        if tI.SpeakerDistribute_data["次に発言するべきキャラクター"] == self.chara_name:
            if tI.SpeakerDistribute_data["理由考察"] == "タイムアウト":
                ExtendFunc.ExtendPrint("SpeakerDistribute_dataに次に発言するべきキャラクターが自分で、タイムアウトを検知したので独り言を話します")
                return "独り言orつっこみorボケを話す"
            ExtendFunc.ExtendPrint("SpeakerDistribute_dataに次に発言するべきキャラクターが自分です")
            return "話す"
        ExtendFunc.ExtendPrint("SpeakerDistribute_dataに次に発言するべきキャラクターが自分ではありません")
        return "傾聴思考"
    
    async def run(self,transported_item: TransportedItem)->TransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query)
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result)
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item

    async def handleEvent(self, transported_item:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)

        if transported_item.stop:
            await self.notify(transported_item)
            return

        output = await self.run(transported_item)
        if self.speak_or_silent == "傾聴思考":
            return
        
        latest_message_time:TimeExtend = output.time
        self.notifyReceivedMessageTimeToInputReciever(latest_message_time)
        

        await self.notify(output)

    async def notify(self, data):
        # 読み上げるための文章を通知
        await self.event_queue.put(data)


    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        ExtendFunc.ExtendPrint(all_template_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]

    def prepareQuery(self, tI:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(tI, self.previous_situation)
        # ExtendFunc.ExtendPrint(self.replace_dict)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_setting = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting,self.replace_dict)
        # ExtendFunc.ExtendPrint(replaced_setting)
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template,self.replace_dict)
        # ExtendFunc.ExtendPrint(replaced_template)
        query = replaced_setting + replaced_template
        # ExtendFunc.ExtendPrint(query)
        return query

    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        #result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
        
        

    def correctResult(self,result: str) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        return ExtendFunc.correctDictToTypeDict(jsonnized_result, ThinkAgent.typeThinkAgentResponse(self.replace_dict, self.chara_name))

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    
    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.Think_data = result
        return transported_item
    
    @property
    def previous_situation(self)->str:
        if len(self._previous_situation) > 0:
            return self._previous_situation[-1]
        else:
            return "なし"
    
    @previous_situation.setter
    def previous_situation(self, gpt_response:dict):
        """
        レスポンスは以下のような形式なのでここから必要な情報を取り出して保存
        class ThinkAgentResponse(TypedDict):
          以前と今を合わせた周囲の状況の要約: str
          どのキャラがどのキャラに話しかけているか？または独り言か？: str
          他のキャラの会話ステータス: dict[str//キャラ名 , Literal['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現']]
          ロール: Literal['アシスタント', 'キャラクターなりきり']
          あなたの属性: Literal['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ']
          {{gptキャラ}}のこれからの感情: Literal['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠']
          {{gptキャラ}}のこれからの会話ステータス: Literal['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う']
          今まで起きたことの要約: str
          {{gptキャラ}}の次の行動を見据えた心内セリフと思考: str
        """
        t = self.replace_dict["{{gptキャラ}}"]
        situation_dict = {
            "周囲の状況要約":gpt_response["以前と今を合わせた周囲の状況の要約"],
            f"{t}の心内思考":gpt_response[f"{t}の次の行動を見据えた心内セリフと思考"],
        }

        if self.fail_serif:
            situation_dict["割り込みがあって言えなかったセリフ"] = self.fail_serif

        self._previous_situation.append(ExtendFunc.dictToStr(situation_dict))
        self.fail_serif = ""
    
    def failSerifFeedBack(self, fail_serif_list:list[str]):
        # 失敗したセリフを受け取って、失敗したセリフを保存する
        fail_sentence = ""
        for fail_serif in fail_serif_list:
            fail_sentence = f"{fail_sentence}\n{fail_serif}"
        
        self.fail_serif = fail_sentence

    def notifyReceivedMessageTimeToInputReciever(self, time:TimeExtend):
        # input_recieverのmessage_stackを解放するために、受信に成功したメッセージの時間を通知する
        self.agent_manager.clearInputRecieverMessageStack(time)

    def timeOutSec(self)->float:
        """
        黙ってとお願いされてる場合など、エージェントの状態によってタイムアウト時間を変える
        """
        return 60
    
    def timeOutItem(self):
        """
        このtiは自分自身で受け取るので
        """
        ir = self.agent_manager.input_reciever
        rm = ir.convertMessageHistoryToTransportedItemData(ir.message_stack, 0, len(ir.message_stack))
        return TransportedItem(
            time = TimeExtend(),
            data = None,
            recieve_messages = rm,
            MicInputJudge_data = {"理由":"タイムアウト","入力成功度合い":0.0},
            SpeakerDistribute_data = {"次に発言するべきキャラクター":self.chara_name , "理由考察":"タイムアウト"},
            Listening_data = "",
            Think_data = {},
            Serif_data = {},
            NonThinkingSerif_data={},
            stop = False
        )
        
class SerifAgent(Agent):
    # class SerifAgentResponse(TypedDict):
    #     {{character}}の発言: str
    #     あなたの発言も踏まえた現在の全体状況: str
    @staticmethod
    def typeSerifAgentResponse(replace_dict: dict, chara_name:str):
        TypeDict = {
                f'{chara_name}の発言': str
            }
        return TypeDict
    
    def replaceDictDef(self,think_agent_output:str)->dict[str,str]:
        return {
            "{{think_agent_output}}":think_agent_output,
            "{{gptキャラ}}":self.chara_name,
            "{{Playerキャラ}}":"ゆかり"
        }

    def __init__(self, agent_manager: AgentManager, chara_name:str):
        super().__init__(agent_manager)
        self.name = "発言エージェント"
        self.request_template_name = "発言エージェントリクエストひな形"
        self.chara_name = chara_name
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        self.epic:Epic = agent_manager.epic
        self.replace_dict = self.replaceDictDef("")

    async def handleEvent(self, transported_item:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)

        if transported_item.stop:
            await self.notify(transported_item)
            return

        output = await self.run(transported_item)
        # 新たな発言があった場合はキャンセル
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.getLatestMessage()['現在の日付時刻'] != output.time:
            ExtendFunc.ExtendPrint(f"{self.epic.messageHistory[-1]['現在の日付時刻']}に追加発言があるため{output.time}の分はキャンセルします")
            return
        ExtendFunc.ExtendPrint(f"{self.name}はすべて成功したので次のエージェントに行きます。{self.chara_name}が喋ります。")

        serif_list = self.getSerifList(output.Serif_data)
        for serif in serif_list:
            send_data = self.agent_manager.createSendData(serif, self.agent_manager.human_dict[self.agent_manager.chara_name],"gpt")
            # await self.agent_manager.websocket.send_json(json.dumps(send_data))
            # await self.saveSuccesSerifToMemory(serif)
            # # 区分音声の再生が完了したかメッセージを貰う
            # end_play_data = await self.agent_manager.websocket.receive_json()
            # 同時に実行するコルーチンをリストにまとめます
            tasks = [
                self.agent_manager.websocket.send_json(json.dumps(send_data)),
                self.saveSuccesSerifToMemory(serif),
                self.agent_manager.websocket.receive_json()
            ]

            # asyncio.gatherを使用して全てのコルーチンが終了するのを待ちます
            results = await asyncio.gather(*tasks)

            # resultsには各コルーチンの結果が格納されています
            end_play_data = results[2]
            ExtendFunc.ExtendPrint(end_play_data) # { "gpt_voice_complete": "complete" }という形式でメッセージが送られてくる
            # 区分音声の再生が完了した時点で次の音声を送る前にメモリが変わってるかチェックし、変わっていたら次の音声を送らない。
            if self.judgeNextSerifSend(output) == False:
                ExtendFunc.ExtendPrint("次の音声を送らない")
                now_index = serif_list.index(serif)
                fail_serifs = serif_list[now_index+1:]
                self.saveFailSerifToMemory(fail_serifs)
                return
            
        else:
            # forが正常に終了した場合はelseが実行されて、メモリ解放処理を行う
            pass
    
    def judgeNextSerifSend(self,ti: TransportedItem)->bool:
        # output.time以降のメッセージリストのspeakerを列挙して自分以外がいればFalseを返す
        judge_time = ti.time
        # 反転しているのは最新のメッセージから見ていくため
        for message_unit in self.epic.messageHistory[::-1]:
            ExtendFunc.ExtendPrint(f"{message_unit['現在の日付時刻']} <= {judge_time} を確認")
            if message_unit['現在の日付時刻'] <= judge_time:
                ExtendFunc.ExtendPrint(f"{message_unit['現在の日付時刻']} <= {judge_time} なのでTrueを返します")
                return True
            ExtendFunc.ExtendPrint(f"{self.chara_name}が{message_unit['message'].speakers}に入っているか確認")
            if self.chara_name not in message_unit["message"].speakers:
                ExtendFunc.ExtendPrint(f"{self.chara_name}が{message_unit['message'].speakers}に入っていないためFalseを返します")
                return False
        return True

    async def saveSuccesSerifToMemory(self,serif:str):
        # InputRecieverのメッセージスタックに追加するために、epic経由でメッセージを追加する
        await self.epic.appendMessageAndNotify({self.chara_name:serif})
    
    def saveFailSerifToMemory(self,serifs:list[str]):
        # 失敗したセリフの情報をthinkエージェントに保存
        self.agent_manager.think_agent.failSerifFeedBack(serifs)


    async def notify(self, data):
        # 読み上げるための文章を通知
        await self.event_queue.put(data)
    

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        # return JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})[self.name]#self.replace_dict)[self.name]

        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        ExtendFunc.ExtendPrint(all_template_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]


    def prepareQuery(self, ti:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        input = JsonAccessor.dictToJsonString(ti.Think_data)
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        query = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting,self.replace_dict)
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template,self.replace_dict)
        query = query + replaced_template

        return query

    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        #result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result    

    def correctResult(self,result: str) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        return ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeSerifAgentResponse(self.replace_dict, self.chara_name))
    
    # 読み上げるための文章を取り出す
    def getSerifList(self,result: Dict[str, Any]) -> list[str]:
        serif = result[f'{self.chara_name}の発言']
        return re.split(r'\. |\? |\。|\, |、 |\n', serif)

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.Serif_data = result
        return transported_item
    
class NonThinkingSerifAgent(Agent):
    """
    思考を挟まないで高速に返答するエージェント
    """
    @staticmethod
    def typeNonThinkingSerifAgentRespons (replace_dict: dict, chara_name:str):
        TypeDict = {
                f'{chara_name}の発言': str
            }
        return TypeDict
    
    def replaceDictDef(self,previous_situation:str, input_conversations:str)->dict[str,str]:
        return {
            "{{前の状況}}":previous_situation,
            "{{gptキャラ}}":self.chara_name,
            "{{会話}}":input_conversations,
            "{{Playerキャラ}}":"ゆかり"
        }
    
    def __init__(self, agent_manager: AgentManager, chara_name:str):
        super().__init__(agent_manager)
        self.name = "思考停止発言エージェント"
        self.request_template_name = "思考停止発言エージェントリクエストひな形"
        self.chara_name = chara_name
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        self.epic:Epic = agent_manager.epic
        self.replace_dict = self.replaceDictDef("", "")

    async def handleEvent(self, transported_item:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)

        if transported_item.stop:
            await self.notify(transported_item)
            return

        output = await self.run(transported_item)
        # 新たな発言があった場合はキャンセル
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.getLatestMessage()['現在の日付時刻'] != output.time:
            ExtendFunc.ExtendPrint(f"{self.epic.messageHistory[-1]['現在の日付時刻']}に追加発言があるため{output.time}の分はキャンセルします")
            return
        ExtendFunc.ExtendPrint(f"{self.name}はすべて成功したので次のエージェントに行きます。{self.chara_name}が喋ります。")

        # 思考エージェントにメッセージを送る
        serif_list = self.getSerifList(output.Serif_data)
        for serif in serif_list:
            send_data = self.agent_manager.createSendData(serif, self.agent_manager.human_dict[self.agent_manager.chara_name],"gpt")
            # await self.agent_manager.websocket.send_json(json.dumps(send_data))
            # await self.saveSuccesSerifToMemory(serif)
            # # 区分音声の再生が完了したかメッセージを貰う
            # end_play_data = await self.agent_manager.websocket.receive_json()
            # 同時に実行するコルーチンをリストにまとめます
            tasks = [
                self.agent_manager.websocket.send_json(json.dumps(send_data)),
                self.saveSuccesSerifToMemory(serif),
                self.agent_manager.websocket.receive_json()
            ]

            # asyncio.gatherを使用して全てのコルーチンが終了するのを待ちます
            results = await asyncio.gather(*tasks)

            # resultsには各コルーチンの結果が格納されています
            end_play_data = results[2]
            ExtendFunc.ExtendPrint(end_play_data) # { "gpt_voice_complete": "complete" }という形式でメッセージが送られてくる
            # 区分音声の再生が完了した時点で次の音声を送る前にメモリが変わってるかチェックし、変わっていたら次の音声を送らない。
            if self.judgeNextSerifSend(output) == False:
                ExtendFunc.ExtendPrint("次の音声を送らない")
                now_index = serif_list.index(serif)
                fail_serifs = serif_list[now_index+1:]
                self.saveFailSerifToMemory(fail_serifs)
                return
            
        else:
            # forが正常に終了した場合はelseが実行されて、メモリ解放処理を行う
            pass

    def judgeNextSerifSend(self,ti: TransportedItem)->bool:
        # output.time以降のメッセージリストのspeakerを列挙して自分以外がいればFalseを返す
        judge_time = ti.time
        # 反転しているのは最新のメッセージから見ていくため
        for message_unit in self.epic.messageHistory[::-1]:
            ExtendFunc.ExtendPrint(f"{message_unit['現在の日付時刻']} <= {judge_time} を確認")
            if message_unit['現在の日付時刻'] <= judge_time:
                ExtendFunc.ExtendPrint(f"{message_unit['現在の日付時刻']} <= {judge_time} なのでTrueを返します")
                return True
            ExtendFunc.ExtendPrint(f"{self.chara_name}が{message_unit['message'].speakers}に入っているか確認")
            if self.chara_name not in message_unit["message"].speakers:
                ExtendFunc.ExtendPrint(f"{self.chara_name}が{message_unit['message'].speakers}に入っていないためFalseを返します")
                return False
        return True
    
    async def saveSuccesSerifToMemory(self,serif:str):
        # InputRecieverのメッセージスタックに追加するために、epic経由でメッセージを追加する
        await self.epic.appendMessageAndNotify({self.chara_name:serif})
    
    def saveFailSerifToMemory(self,serifs:list[str]):
        # 失敗したセリフの情報をthinkエージェントに保存
        self.agent_manager.think_agent.failSerifFeedBack(serifs)


    async def notify(self, data):
        # 読み上げるための文章を通知
        await self.event_queue.put(data)

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        # return JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})[self.name]#self.replace_dict)[self.name]

        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        ExtendFunc.ExtendPrint(all_template_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, ti:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        previous_situation = self.agent_manager.think_agent.previous_situation
        conversations = ti.recieve_messages
        self.replace_dict = self.replaceDictDef(previous_situation, conversations)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        query = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting, self.replace_dict)
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = query + replaced_template

        return query

    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        #result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result    

    def correctResult(self,result: str) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        # strからjsonLoadしてdictに変換
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        return ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeNonThinkingSerifAgentRespons(self.replace_dict, self.chara_name))
    
    # 読み上げるための文章を取り出す
    def getSerifList(self,result: Dict[str, Any]) -> list[str]:
        serif = result[f'{self.chara_name}の発言']
        return re.split(r'\. |\? |\。|\, |、 |\n', serif)

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.NonThinkingSerif_data = result
        return transported_item

class AgentEventManager:
    def __init__(self, chara_name:str, gpt_mode_dict:dict[str,str]):
        self.gpt_mode_dict = gpt_mode_dict
        self.chara_name = chara_name
    async def addEventWebsocketOnMessage(self, websocket: WebSocket, reciever: EventReciever):
        while True:
            data = await websocket.receive_json()
            await reciever.handleEvent(data)
    async def setEventArrow(self, notifier: EventNotifier, reciever: EventReciever):
        while True:
            await notifier.event.wait()
            notifier.event.clear()
            none_transported_data = TransportedItem(
                time=TimeExtend(), 
                data=None,
                recieve_messages="",
                MicInputJudge_data = MicInputJudgeAgentResponse(理由="タイムアウト",入力成功度合い=0.0),
                SpeakerDistribute_data = SpeakerDistributeAgentResponse(次に発言するべきキャラクター="ゆかり",理由考察="タイムアウト"),
                Listening_data=None,
                Think_data={},
                Serif_data=None,
                NonThinkingSerif_data=None,
                )
            await reciever.handleEvent(none_transported_data)
    async def setEventQueueArrow(self, notifier: QueueNotifier, reciever: EventReciever):
        while True:
            ExtendFunc.ExtendPrint(f"{reciever.name}イベント待機中")
            if self.gpt_mode_dict[self.chara_name] != "individual_process0501dev":
                ExtendFunc.ExtendPrint(f"{self.gpt_mode_dict[self.chara_name]}はindividual_process0501devではないため、{reciever.name}イベントを終了します")
                return
            item = await notifier.event_queue.get()
            ExtendFunc.ExtendPrint(item)
            await reciever.handleEvent(item)
            ExtendFunc.ExtendPrint(f"{reciever.name}イベントを処理しました")
    
    async def setEventQueueArrowWithTimeOutByHandler(self, notifier: QueueNotifier, reciever: EventRecieverWaitFor):
        while True:
            ExtendFunc.ExtendPrint(f"{reciever.name}イベント待機中")
            if self.gpt_mode_dict[self.chara_name] != "individual_process0501dev":
                ExtendFunc.ExtendPrint(f"{self.gpt_mode_dict[self.chara_name]}はindividual_process0501devではないため、{reciever.name}イベントを終了します")
                return
            try:
                item = await asyncio.wait_for(notifier.event_queue.get(), timeout=reciever.timeOutSec())
            except asyncio.TimeoutError:
                ExtendFunc.ExtendPrint(f"{reciever.name}イベントがタイムアウトしました")
                item = reciever.timeOutItem()
            ExtendFunc.ExtendPrint(item)
            await reciever.handleEvent(item)
            ExtendFunc.ExtendPrint(f"{reciever.name}イベントを処理しました")

@dataclass
class GPTAgent:
    manager: AgentManager
    event_manager: AgentEventManager

        

    
    
if __name__ == "__main__":
    def te1():
        test = MicInputJudgeAgent()
        query = test.prepareQuery("ポケモンは{{input}}")
        pprint(query, indent=4)

    def te2():
        test = MicInputJudgeAgent()
        task = tasks.create_task(test.run("ほげほげほげ"))

    def te3():
        
        message_history:list[MassageHistoryUnit] = []
        for i in range(10):
            message_history_unit = MassageHistoryUnit(
                message = {f"ゆかり{i}":f"ほげほげほげ{i}"},
                現在の日付時刻 = TimeExtend()
            )
            message_history.append(message_history_unit)

        te = InputReciever.convertMessageHistoryToTransportedItemData(message_history, 6, len(message_history))
        print(te)
    def te4():
        a = ["あ","い","う","え","お"]
        for string in str(a):
            print(string)
    def te5():
        print(JsonAccessor.loadGPTBehaviorYaml("一般"))

    def te6():
        a = ThinkAgent.typeThinkAgentResponse({"gpt_character":"ゆかり"})
        t = a["他のキャラの会話ステータス"]
        pprint(t, indent=4)
        bool = isinstance(t, dict)
        print(bool)

    def te7():
        gpt_unit = ChatGptApiUnit(True)
        test_message_query:list[ChatGptApiUnit.MessageQuery] = [
            {
                "role":"system",
                "content":""""
                マイクによる音声認識での文章の入力は間違いや、発話の途中で認識が止まって聞き漏らしがあります。そこであなたには入力された文章が完全な物かを判断するエージェントとして動いてもらいます。
         次の文章はマイク入力された文章ですが、入力成功度合いを成功1、失敗0として、0から1の間で答えてください。返答は以下のpythonで定義されるjson形式で答えてください。
        ```
        class MicInputJudgeAgentResponse(TypedDict):
            理由: str
            入力成功度合い: float
        ```
                """
            },
            {
                "role":"user",
                "content":"ほげほげ"
            }
        ]
        test = gpt_unit.genereateResponseGPT4TurboJson(test_message_query)
        print(test)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", test)
        ExtendFunc.ExtendPrint(test)
    
    def te8():
        a = {"a":"b","c":"d"}
        print("a" not in a)

    def te9():
        dict_a = {
            "a":0,
            "c":2
        }
        
        print(dict_a.keys())
        print("a" in dict_a.keys())
    
    te9()