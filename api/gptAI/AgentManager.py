from abc import ABC, abstractmethod
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
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend
from api.DataStore.JsonAccessor import JsonAccessor
from api.Epic.Epic import Epic, MassageHistoryUnit
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

    def __init__(self):
        try:
            api_key = JsonAccessor.loadOpenAIAPIKey()
            self.client = OpenAI(api_key = api_key)
            self.async_client = AsyncOpenAI(api_key = api_key)
        except Exception as e:
            print("APIキーの読み込みに失敗しました。")
            raise e
    async def asyncGenereateResponseGPT4TurboJson(self,message_query:list[MessageQuery]):
        response = await self.async_client.chat.completions.create (
                model="gpt-4-turbo-preview",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    
    def genereateResponseGPT4TurboJson(self,message_query:list[MessageQuery]):
        response = self.client.chat.completions.create (
                model="gpt-4-turbo-preview",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT4TurboText(self,message_query:list[MessageQuery]):
        response = await self.async_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT4TurboText(self,message_query:list[MessageQuery]):
        response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        response = await self.async_client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=message_query,
                temperature=0.7
            )
        return response.choices[0].message.content
class TransportedItem(BaseModel):
    time:TimeExtend
    data:Any
    recieve_messages:str
    MicInputJudge_data:Any
    SpeakerDistribute_data:Any
    Listening_data:Any
    Think_data:Any
    Serif_data:Any
    class Config:
        arbitrary_types_allowed = True

class EventReciever(Protocol):
    async def handleEvent(self, data:TransportedItem):
        pass

class EventNotifier(Protocol):
    event:Event
    async def notify(self, data):
        pass

class QueueNotifier(Protocol):
    event_queue:Queue[TransportedItem]
    async def notify(self, data:TransportedItem):
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
    def __init__(
            self,chara_name:str, 
            epic:Epic, 
            human_dict:dict[str,Human], 
            websocket:WebSocket
            ):
        self.chara_name:str = chara_name
        self.epic = epic
        self.human_dict:dict[str,Human] = human_dict
        self.chara_dict:dict[str,Agent] = {}
        self._message_memory:list[MassageHistoryUnit] = epic.messageHistory
        self.replace_dict = self.loadReplaceDict(self.chara_name)
        self.prepareAgents(self.replace_dict)
        self.websocket = websocket

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
            "gptキャラ":self.chara_name,
            "playerキャラ":"",
            "gpt_role":"",
            "gpt_attribute":""
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
        self.input_reciever:QueueNotifier = InputReciever(self.epic)
        self.mic_input_check_agent:QueueNode = MicInputJudgeAgent(self, replaced_dict)
        self.speaker_distribute_agent:QueueNode = SpeakerDistributeAgent(self, replaced_dict)
        self.think_agent:QueueNode = ThinkAgent(self,replaced_dict)
        # self.memory_agent = MemoryAgent(replaced_dict)
        self.serif_agent:QueueNode = SerifAgent(replaced_dict)
        self.listening_agent = ListeningAgent(replaced_dict)
    


    def createSendData(self, sentence:str, human:Human):
        human.outputWaveFile(sentence)
        #wavデータを取得
        wav_info = human.human_Voice.output_wav_info_list
        send_data = {
            "sentence":sentence,
            "wav_info":wav_info
        }
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



class Agent:
    """
    エージェントの基底クラス。
    Humanの配下にあるので名前を持っている。
    プロンプトサンプルを受け取って名前などを書き換えてそれをもとにリクエストを作成し送る。
    gptから受け取るときの型を定義して毎回矯正する必要がある
    """
    def __init__(self,agent_manager: AgentManager,  replace_dict: dict):
        self._gpt_api_unit = ChatGptApiUnit()
        self.replace_dict = replace_dict
        pass
    async def run(self,transported_item: TransportedItem)->TransportedItem:
        query = self.prepareQuery(transported_item)
        result = await self.request(query)
        corrected_result = self.correctResult(result)
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addIndoToTransportedItem(transported_item, corrected_result)
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
    def addIndoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        pass

    @abstractmethod
    def loadReturnType(self)->dict:
        pass

class InputReciever():
    def __init__(self,epic:Epic):
        self.name = "入力受付エージェント"
        self.epic = epic
        self.message_stack:list[MassageHistoryUnit] = []
        self.event_queue = Queue[TransportedItem]()
    async def observeEpic(self):
        while True:
            # epic.onMessageEventを監視する。メッセージが追加されれば3秒待って、また新しいメッセージが追加されればまた3秒待つ。３秒待ってもメッセージが追加されなければ次のエージェントに送る。
            messages:list[MassageHistoryUnit] = [await self.epic.OnMessageEvent.get()]
            while not self.epic.OnMessageEvent.empty():
                message = await self.epic.OnMessageEvent.get()
                messages.append(message)
            # メッセージが追加されたらメッセージスタックに追加。送信したら解放する。
            self.message_stack += messages
            await asyncio.sleep(3)
            if not self.epic.OnMessageEvent.empty():
                continue
            # ここで次のエージェントに送る
            last = len(self.message_stack)
            transported_item:TransportedItem = TransportedItem(
                time = self.epic.messageHistory[-1]['現在の日付時刻'], 
                data = "",
                recieve_messages = self.convertMessageHistoryToTransportedItemData(self.message_stack, 0, len(self.message_stack)),
                MicInputJudge_data="",
                SpeakerDistribute_data="",
                Listening_data="",
                Think_data="",
                Serif_data=""
                )
            # 送信後にメッセージスタックを解放
            self.message_stack = []
            await self.notify(transported_item)
            
    async def notify(self, data:TransportedItem):
        await self.event_queue.put(data)
            
    async def handleEvent(self, data = None):
        # x秒非同期に待つ
        await asyncio.sleep(3)
        # 次が来てるかどうかをチェック。
    @staticmethod
    def convertMessageHistoryToTransportedItemData(message_history:list[MassageHistoryUnit], start_index:int, end_index:int)->str:
        ret_string = ""
        for i in range(start_index, end_index):
            ret_string = f"{ret_string}{ExtendFunc.dictToStr(message_history[i]['message'])}"
        return ret_string

class MicInputJudgeAgent(Agent):
    @staticmethod
    def typeMicInputJudgeAgentResponse(replace_dict: dict):
        TypeDict = {
            "理由":str,
            "入力成功度合い":Interval("[",0,1,"]")
        }
        return 
    
    def replaceDictDef(self,input:str)->dict[str,str]:
        return {
            "{{input}}":input
        }
    
    def __init__(self, agent_manager: AgentManager, replace_dict: dict = {}):
        super().__init__(agent_manager, replace_dict)
        self.name = "マイク入力成否判定エージェント"
        self.request_template_name = "マイク入力成否判定エージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue = Queue()

    async def handleEvent(self, data:TransportedItem):
        # マイク入力成功判定エージェントがマイク入力に成功しているか判定
        output = await self.run(data)
        if output.MicInputJudge_data["入力成功度合い"] <= 0.5:
            return
        await self.notify(output)

    async def notify(self, data):
        # LLMが出力した成功か失敗かを通知
        await self.event_queue.put(data)

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        # 最新のメッセージを埋め込むのでここで新たにreplace_dictを作成
        replace_dict = {"{{input}}":input.recieve_messages}
        # プロンプトサンプルymlを好きなタイミングで修正したいので毎回読み込むようにしておく。todo 将来的にここは消す。
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        # クエリを作成
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        result = self._gpt_api_unit.genereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: Dict[str, Any]) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        return ExtendFunc.correctDictToTypeDict(result, self.typeMicInputJudgeAgentResponse(self.replace_dict))
    
    def saveResult(self,result):
        # 必要ない
        pass

    def clearMemory(self):
        # 必要ない
        pass

    def addIndoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.MicInputJudge_data = result
        return transported_item
    

class SpeakerDistributeAgent(Agent):
    @staticmethod
    def typeSpeakerDistributeAgentResponse(replace_dict: dict, chara_name_list: str):
        TypeDict = {
            "次に発言するべきキャラクター": chara_name_list
        }
        return TypeDict
    def replaceDictDef(self,input:str)->dict[str,str]:
        return {
            "{{input}}":input,
            "{{character_list}}":self.createCharacterListStr()
        }

    def __init__(self, agent_manager: AgentManager, replace_dict: dict):
        super().__init__(agent_manager, replace_dict)
        self.name = "発言者振り分けエージェント"
        self.request_template_name = "発言者振り分けエージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        self.epic:Epic = agent_manager.epic

    async def handleEvent(self, transported_item:TransportedItem):
        # 話者割り振りエージェントが会話を見て次に喋るべきキャラクターを推論
        output = await self.run(transported_item)
        # 次に喋るべきキャラクターが自分でなければキャンセル
        if output.SpeakerDistribute_data["次に発言するべきキャラクター"] != self.agent_manager.chara_name:
            return
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.messageHistory[-1]['現在の日付時刻'].date != output.time:
            return
        await self.notify(output)

    async def notify(self, data: TransportedItem):
        # 次に喋るべきキャラクターを通知
        await self.event_queue.put(data)

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        input_replace_dict = {
            "{{input}}":input.recieve_messages,
            "{{character_list}}":f"[{self.createCharacterListStr()}]"
            }
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, input_replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        result = self._gpt_api_unit.genereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: Dict[str, Any]) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        return ExtendFunc.correctDictToTypeDict(result, self.typeSpeakerDistributeAgentResponse(self.replace_dict, self.createCharacterListStr()))
    
    def addIndoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.SpeakerDistribute_data = result
        return transported_item

    def createCharacterListStr(self)->str:
        """
        キャラ名のリストを文字列で返す。例：['きりたん', 'ずんだもん', 'ゆかり','おね','あかり']
        """
        chara_name_list = []
        for key in self.agent_manager.human_dict.keys():
            chara_name_list.append(key)
        return str(chara_name_list)

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

    def __init__(self, agent_manager: AgentManager, replace_dict: dict):
        super().__init__(agent_manager, replace_dict)
        self.name = "傾聴エージェント"
        self.request_template_name = "傾聴エージェントリクエストひな形"
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()

    async def handleEvent(self, data:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        output = await self.run(data)
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
        result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: Dict[str, Any]) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        return ExtendFunc.correctDictToTypeDict(result, ThinkAgent.typeThinkAgentResponse(self.replace_dict))
    
    def addIndoToTransportedItem(self, transported_item: TransportedItem, result: Dict[str, Any]) -> TransportedItem:
        transported_item.Listening_data = result
        return transported_item


class ThinkAgent(Agent):

    class ThinkAgentResponse(TypedDict):
        現在の相手の状況の要約: str
        誰に話しかけてるか: Literal['キャラ1', '独り言']
        相手の会話ステータス: Literal['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現']
        ロール: Literal['アシスタント', 'キャラクターなりきり']
        あなたの属性: Literal['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ']
        感情: Literal['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠']
        会話ステータス: Literal['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う']
        あなたの発言も踏まえた現在の全体状況: str

    @staticmethod
    def typeThinkAgentResponse(replace_dict: dict):
        TypeDict = {
            "現在の相手の状況の要約": str,
            "誰に話しかけてるか": ['キャラ1', '独り言'],
            "相手の会話ステータス": ['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現'],
            "ロール": ['アシスタント', 'キャラクターなりきり'],
            "あなたの属性": ['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ'],
            "感情": ['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠'],
            "会話ステータス": ['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う'],
            "あなたの発言も踏まえた現在の全体状況": str
            }
        return TypeDict
    
    def replaceDictDef(self, input:str, previous_situation:str)->dict[str,str]:
        
        # gpt_behavior = JsonAccessor.loadGPTBehaviorYaml(self.replace_dict["gpt_character"])
        gpt_behavior = JsonAccessor.loadGPTBehaviorYaml("一般")
        # キャラのロールや属性は別のキャラクター設定ymlから取得する
        relace_dict = {
            "{{gptキャラ}}":self.replace_dict["gpt_character"],
            "{{playerキャラ}}":"",
            "{{前の状況}}":previous_situation,
            "{{input}}":input,
            "{{gptキャラのロール}}":gpt_behavior["gptキャラのロール"],
            "{{gptキャラの属性}}":gpt_behavior["gptキャラの属性"],
        }

        return relace_dict
    

    def __init__(self, agent_manager: AgentManager, replace_dict: dict):
        super().__init__(agent_manager, replace_dict)
        self.name = "思考エージェント"
        self.request_template_name = "思考エージェントリクエストひな形"
        self.agent_setting = self.loadAgentSetting()
        self.replace_dict = self.replaceDictDef("", "")
        self.event_queue = Queue()

    async def handleEvent(self, data:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        output = await self.run(data)
        if output.Think_data["会話ステータス"] == "続きを言う":
            return
        

        await self.notify(output)

    async def notify(self, data):
        # 読み上げるための文章を通知
        await self.event_queue.put(data)


    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]

    def prepareQuery(self, input:str)->list[ChatGptApiUnit.MessageQuery]:
        replace_dict = self.replaceDictDef(input, "")
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_setting = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting,replace_dict)
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template,replace_dict)
        query = replaced_setting + replaced_template
        return query

    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
        
        

    def correctResult(self,result: Dict[str, Any]) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        return ExtendFunc.correctDictToTypeDict(result, ThinkAgent.typeThinkAgentResponse(self.replace_dict))

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    def loadReturnType(self)->ThinkAgentResponse:
        res:ThinkAgent.ThinkAgentResponse = {
            "現在の相手の状況の要約": "今日はいい天気ですね",
            "誰に話しかけてるか": "キャラ1",
            "相手の会話ステータス": "質問",
            "ロール": "アシスタント",
            "あなたの属性": "先生",
            "感情": "喜",
            "会話ステータス": "傾聴",
            "あなたの発言も踏まえた現在の全体状況": "今日はいい天気ですね"
        }
        test = ThinkAgent.ThinkAgentResponse(**res)

        return res
    
    def addIndoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, Any])->TransportedItem:
        transported_item.Think_data = result
        return transported_item
    
    def saveSituation(self, gpt_response:dict):
        TypeDict = {
            "現在の相手の状況の要約": str,
            "誰に話しかけてるか": ['キャラ1', '独り言'],
            "相手の会話ステータス": ['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現'],
            "ロール": ['アシスタント', 'キャラクターなりきり'],
            "あなたの属性": ['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ'],
            "感情": ['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠'],
            "会話ステータス": ['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う'],
            "あなたの発言も踏まえた現在の全体状況": str
            }
        gpt_response = 

class SerifAgent(Agent):
    # class SerifAgentResponse(TypedDict):
    #     {{character}}の発言: str
    #     あなたの発言も踏まえた現在の全体状況: str
    @staticmethod
    def typeSerifAgentResponse(replace_dict: dict):
        TypeDict = {
                f'{replace_dict["gpt_character"]}の発言': str,
                'あなたの発言も踏まえた現在の全体状況': str,
            }
        return TypeDict
    
    def replaceDictDef(self,think_agent_output:str)->dict[str,str]:
        return {
            "{{think_agent_output}}":think_agent_output,
            "{{gptキャラ}}":self.replace_dict["gpt_character"],
        }

    def __init__(self, replace_dict: dict, agent_manager: AgentManager):
        super().__init__(agent_manager, replace_dict)
        self.name = "セリフエージェント"
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        self.epic:Epic = agent_manager.epic

    async def handleEvent(self, data:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        output = await self.run(data)
        # 新たな発言があった場合はキャンセル
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.messageHistory[-1]['現在の日付時刻'].date != output.time:
            return

        # 思考エージェントにメッセージを送る
        serif_list = self.getSerifList(output.Serif_data)
        for serif in serif_list:
            send_data = self.agent_manager.createSendData(serif, self.agent_manager.human_dict[self.agent_manager.chara_name])
            await self.agent_manager.websocket.send_json(send_data)
            # 区分音声の再生が完了したかメッセージを貰う
            end_play_data = await self.agent_manager.websocket.receive_json()
            # 区分音声の再生が完了した時点で次の音声を送る前にメモリが変わってるかチェックし、変わっていたら次の音声を送らない。
            if self.epic.messageHistory[-1]['現在の日付時刻'].date != output.time:
                return
        else:
            # forが正常に終了した場合はelseが実行されて、メモリ解放処理を行う
            pass



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
        result = await self._gpt_api_unit.asyncGenereateResponseGPT4TurboJson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
        
        

    def correctResult(self,result: Dict[str, Any]) -> dict:
        """
        resultがThinkAgentResponseの型になるように矯正する
        """
        return ExtendFunc.correctDictToTypeDict(result, SerifAgent.typeSerifAgentResponse(self.replace_dict))
    
    # 読み上げるための文章を取り出す
    def getSerifList(self,result: Dict[str, Any]) -> list[str]:
        serif = result[f'{self.replace_dict["gpt_character"]}の発言']
        return re.split(r'\. |\? |\。|\, |、 |\n', serif)

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass


class AgentEventManager:
    def __init__(self, chara_name:str, epic: Epic):
        self.input_reciever = InputReciever(epic)
        pass
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
                MicInputJudge_data=None,
                SpeakerDistribute_data=None,
                Listening_data=None,
                Think_data=None,
                Serif_data=None
                )
            await reciever.handleEvent(none_transported_data)
    async def setEventQueueArrow(self, notifier: QueueNotifier, reciever: EventReciever):
        while True:
            item = await notifier.event_queue.get()
            await reciever.handleEvent(item)


        

    
    
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
    te5()