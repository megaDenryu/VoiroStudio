from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pprint import pprint
from pathlib import Path
import sys

from api.DataStore.PickleAccessor import PickleAccessor
from api.gptAI.HumanBaseModel import DestinationAndProfitVector, ProfitVector, 目標と利益ベクトル
sys.path.append(str(Path(__file__).parent.parent.parent))
from fastapi import WebSocket
from openai import OpenAI, AsyncOpenAI, AssistantEventHandler
import asyncio
from asyncio import Event, Queue, tasks
import re

from api.gptAI.HumanState import Task
from api.Extend.ExtendSet import Interval
from api.gptAI.Human import Human
# from api.gptAI.AgenetResponseJsonType import ThinkAgentResponse
from api.Extend.ExtendFunc import ExtendFunc, RandomExtend, TimeExtend
from api.DataStore.JsonAccessor import JsonAccessor
from api.Epic.Epic import Epic, MassageHistoryUnit, MessageUnit
from typing import Literal, Protocol
from typing import Any, Dict, get_type_hints, get_origin,TypeVar, Generic
from typing_extensions import TypedDict
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
                messages=message_query, # type: ignore
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
                messages=message_query,# type: ignore
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
                model="gpt-4o",
                messages=message_query,# type: ignore
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT4TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=message_query,# type: ignore
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = await self.async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_query,# type: ignore
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3Turbojson(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_query,# type: ignore
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        return response.choices[0].message.content
    

    async def asyncGenereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = await self.async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_query,# type: ignore
                temperature=0.7
            )
        return response.choices[0].message.content
    def genereateResponseGPT3TurboText(self,message_query:list[MessageQuery]):
        if self.test_mode == True:
            print("テストモードです")
            return "テストモードです"
        response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=message_query,# type: ignore
                temperature=0.7
            )
        return response.choices[0].message.content
    
class MicInputJudgeAgentResponse(TypedDict):
    理由:str
    入力成功度合い:float

class SpeakerDistributeAgentResponse(TypedDict):
    理由考察:str
    次に発言するべきキャラクター:str

class GeneralTransportedItem(BaseModel):
    usage_purpose:str
    @classmethod
    def init(cls) -> "GeneralTransportedItem":
        raise NotImplementedError("initメソッドをオーバーライドしてください")


class TransportedItem(GeneralTransportedItem):
    time:TimeExtend
    data:Any
    recieve_messages:str
    MicInputJudge_data:MicInputJudgeAgentResponse
    SpeakerDistribute_data:SpeakerDistributeAgentResponse #dict[str,str]
    Listening_data:Any
    Think_data:dict[str,str]
    Serif_data:dict[str,str]
    NonThinkingSerif_data:dict[str,str]|None
    stop:bool = False
    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def init():
        return TransportedItem(
            usage_purpose = "会話",
            time = TimeExtend(),
            data = "",
            recieve_messages = "",
            MicInputJudge_data = MicInputJudgeAgentResponse(理由="", 入力成功度合い=0.0),
            SpeakerDistribute_data = SpeakerDistributeAgentResponse(理由考察="", 次に発言するべきキャラクター=""),
            Listening_data = "",
            Think_data = {},
            Serif_data = {},
            NonThinkingSerif_data = None,
            stop = False
        )




class TaskBrekingDownConversationUnit(BaseModel):
    speaker:str
    solution_step_idea:str
    problem_point:str
    check_result:str

    @staticmethod
    def init(speaker:str, solution_step_idea:str, problem_point:str = "", check_result:str = ""):
        return TaskBrekingDownConversationUnit(
            speaker = speaker,
            solution_step_idea = solution_step_idea,
            problem_point = problem_point,
            check_result = check_result
        )

class ProblemDecomposedIntoTasks(BaseModel):
    problem_title:str
    role_in_task_graph: str|None  #タスクグラフ内での役割または解決するべき問題
    result_of_previous_task: str|None  #前のタスクの結果
    def __init__(self, task:Task, result_of_previous_task:"TaskToolOutput|None" = None):
        self.problem_title = task["task_title"]
        self.role_in_task_graph = self.TaskToRoleInTaskGraph(task)
        self.result_of_previous_task = self.perviousTaskToResultToString(result_of_previous_task)
    def TaskToRoleInTaskGraph(self, task:Task|None)->str:
        if task is None:
            #todo :最初のタスクだがまだ実装していない
            raise NotImplementedError("最初のタスクの時だがまだ実装していない")

        else:
            return ExtendFunc.dictToStr({"タスクの種類":task["task_species"],"タスクの説明":task["description"]})
    def perviousTaskToResultToString(self, result_of_previous_task:"TaskToolOutput|None")->str:
        if result_of_previous_task is None:
            return "なし"
        else:
            return ExtendFunc.dictToMarkdownTitleEntry({"前回のタスク結果":result_of_previous_task.task_exec_result},2)
    
    def summarizeProblem(self):
        if self.role_in_task_graph is None:
            return f"## 問題\n{self.result_of_previous_task}"
        return ExtendFunc.dictToMarkdownTitleEntry({"前のタスクの結果":self.result_of_previous_task,"問題":self.role_in_task_graph},2)

class TaskBreakingDownTransportedItem(GeneralTransportedItem):
    usage_purpose:str
    problem:ProblemDecomposedIntoTasks
    comlete_breaking_down_task:bool
    conversation:list[TaskBrekingDownConversationUnit]
    breaking_downed_task:list[Task]
    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def init(problem):
        return TaskBreakingDownTransportedItem(
            usage_purpose = "タスク分解",
            problem = problem,
            comlete_breaking_down_task = False,
            conversation = [],
            breaking_downed_task = []
        )
    @staticmethod
    def conversationToString(conversation:list[TaskBrekingDownConversationUnit]):
        ret_string = ""
        for unit in conversation:
            ret_string = f"{ret_string}\n{unit.speaker}:{unit.solution_step_idea}"
        return ret_string

class LifeProcessTransportedItem(GeneralTransportedItem):
    fast_input:str
    task_list:list[Task]
    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def init():
        return TaskBreakingDownTransportedItem(
            usage_purpose = "タスク分解",
            problem = None,
            comlete_breaking_down_task = False,
            conversation = [],
            breaking_downed_task = []
        )




GeneralTransportedItem_T_contra = TypeVar("GeneralTransportedItem_T_contra", bound=GeneralTransportedItem, contravariant=True)
GeneralTransportedItem_T = TypeVar("GeneralTransportedItem_T", bound=GeneralTransportedItem)

class EventReciever(Protocol, Generic[GeneralTransportedItem_T_contra]):
    name:str
    async def handleEvent(self, transported_item:GeneralTransportedItem_T_contra):
        pass
class EventRecieverWaitFor(Protocol, Generic[GeneralTransportedItem_T]):
    name:str
    async def handleEvent(self, transported_item:GeneralTransportedItem_T):
        pass
    def timeOutSec(self)->float: # type: ignore
        pass
    def timeOutItem(self)->GeneralTransportedItem_T: # type: ignore
        pass

class EventNotifier(Protocol):
    event:Event
    async def notify(self, data):
        pass

class QueueNotifier(Protocol, Generic[GeneralTransportedItem_T]):
    event_queue_dict:dict[EventReciever,Queue[GeneralTransportedItem_T]]
    async def notify(self, data:GeneralTransportedItem_T):
        pass
    # 購読者をリストにしておく
    def appendReciever(self, reciever:EventReciever)->Queue[GeneralTransportedItem_T]:
        return self.event_queue_dict[reciever]

class QueueNotifierWaitFor(Protocol, Generic[GeneralTransportedItem_T]):
    event_queue:Queue[GeneralTransportedItem_T]
    async def notify(self, data:GeneralTransportedItem_T):
        pass
    def timeOutSec(self)->float: # type: ignore
        pass
    def timeOutItem(self)->GeneralTransportedItem_T: # type: ignore
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
    non_thinking_serif_agent:"NonThinkingSerifAgent"
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
        self.non_thinking_serif_agent = NonThinkingSerifAgent(self,self.chara_name)
        
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
    name:str
    def __init__(self,agent_manager: AgentManager,  replace_dict: dict[str,str] = {}):
        self.agent_manager = agent_manager
        self._gpt_api_unit = ChatGptApiUnit()
        ExtendFunc.ExtendPrint(replace_dict)
        self.replace_dict = replace_dict
        self.event_queue_dict:dict[EventReciever,Queue[TransportedItem]] = {}

    async def run(self,transported_item: TransportedItem)->TransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def appendReciever(self,reciever:EventReciever):
        self.event_queue_dict[reciever] = Queue[TransportedItem]()
        return self.event_queue_dict[reciever]
    
    async def notify(self, data:TransportedItem):
        # LLMが出力した成功か失敗かを通知
        task = []
        for event_queue in self.event_queue_dict.values():
            task.append(event_queue.put(data))
        await asyncio.gather(*task)
    
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
        self.event_queue_dict:dict[EventReciever,Queue[TransportedItem]] = {}
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
        stop_ti = TransportedItem.init()
        stop_ti.stop = True
        stop_ti.time = self.epic.getLatestMessage()['現在の日付時刻']
        stop_ti.recieve_messages = self.convertMessageHistoryToTransportedItemData(self.message_stack, 0, len(self.message_stack))
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
            transported_item:TransportedItem = TransportedItem.init()
            transported_item.time = self.message_stack[-1]['現在の日付時刻']
            transported_item.recieve_messages = self.convertMessageHistoryToTransportedItemData(self.message_stack, 0, last)
            ExtendFunc.ExtendPrint(transported_item)
            await self.notify(transported_item)

    def appendReciever(self, reciever:EventReciever):
        self.event_queue_dict[reciever] = Queue[TransportedItem]()
        return self.event_queue_dict[reciever]
            
    async def notify(self, data:TransportedItem):
        # LLMが出力した成功か失敗かを通知
        task = []
        for event_queue in self.event_queue_dict.values():
            task.append(event_queue.put(data))
        await asyncio.gather(*task)
            
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

class AgentEventManager:
    def __init__(self, chara_name:str, gpt_mode_dict:dict[str,str]):
        self.gpt_mode_dict = gpt_mode_dict
        self.chara_name = chara_name
    async def addEventWebsocketOnMessage(self, websocket: WebSocket, reciever: EventReciever):
        while True:
            data = await websocket.receive_json()
            await reciever.handleEvent(data)
    
    async def setEventQueueArrow(self, notifier: QueueNotifier[GeneralTransportedItem_T], reciever: EventReciever[GeneralTransportedItem_T]):
        # notifierの中のreciever_dictにrecieverを追加
        event_queue_for_reciever:Queue[GeneralTransportedItem_T] =notifier.appendReciever(reciever)
        while True:
            ExtendFunc.ExtendPrint(f"{reciever.name}イベント待機中")
            if self.gpt_mode_dict[self.chara_name] != "individual_process0501dev":
                ExtendFunc.ExtendPrint(f"{self.gpt_mode_dict[self.chara_name]}はindividual_process0501devではないため、{reciever.name}イベントを終了します")
                return
            item = await event_queue_for_reciever.get()
            ExtendFunc.ExtendPrint(item)
            await reciever.handleEvent(item)
            ExtendFunc.ExtendPrint(f"{reciever.name}イベントを処理しました")
    
    async def setEventQueueArrowWithTimeOutByHandler(self, notifier: QueueNotifier[GeneralTransportedItem_T], reciever: EventRecieverWaitFor[GeneralTransportedItem_T]):
        event_queue_for_reciever:Queue[GeneralTransportedItem_T] =notifier.appendReciever(reciever)
        while True:
            ExtendFunc.ExtendPrint(f"{reciever.name}イベント待機中")
            if self.gpt_mode_dict[self.chara_name] != "individual_process0501dev":
                ExtendFunc.ExtendPrint(f"{self.gpt_mode_dict[self.chara_name]}はindividual_process0501devではないため、{reciever.name}イベントを終了します")
                return
            try:
                item = await asyncio.wait_for(event_queue_for_reciever.get(), timeout=reciever.timeOutSec())
            except asyncio.TimeoutError:
                ExtendFunc.ExtendPrint(f"{reciever.name}イベントがタイムアウトしました")
                item = reciever.timeOutItem()
            ExtendFunc.ExtendPrint(item)
            try:
                await asyncio.wait_for(reciever.handleEvent(item),40)
                ExtendFunc.ExtendPrint(f"{reciever.name}イベントを処理しました")
            except asyncio.TimeoutError:
                ExtendFunc.ExtendPrint(f"{reciever.name}のハンドルイベントがタイムアウトしました")
    
    async def setEventQueueConfluenceArrow(self, notifier_list: list[QueueNotifier[GeneralTransportedItem_T]], reciever: EventReciever[GeneralTransportedItem_T]):
        list_event_queue_for_reciever:list[Queue[GeneralTransportedItem_T]] = []
        for notifier in notifier_list:
            event_queue_for_reciever:Queue[GeneralTransportedItem_T] =notifier.appendReciever(reciever)
            list_event_queue_for_reciever.append(event_queue_for_reciever)
        while True:
            ExtendFunc.ExtendPrint(f"{reciever.name}イベント待機中")
            if self.gpt_mode_dict[self.chara_name] != "individual_process0501dev":
                ExtendFunc.ExtendPrint(f"{self.gpt_mode_dict[self.chara_name]}はindividual_process0501devではないため、{reciever.name}イベントを終了します")
                return
            task = [event_queue.get() for event_queue in list_event_queue_for_reciever]
            resluts = await asyncio.gather(*task)
            # tiをマージする
            ti = resluts[0]
            for item in resluts[1:]:
                ti = self.mergeTransportedItem(ti, item)
            ExtendFunc.ExtendPrint(ti)
            try:
                await asyncio.wait_for(reciever.handleEvent(ti), 40)
                ExtendFunc.ExtendPrint(f"{reciever.name}イベントを処理しました")
            except asyncio.TimeoutError:
                ExtendFunc.ExtendPrint(f"{reciever.name}のハンドルイベントがタイムアウトしました")     
    
    @staticmethod
    def mergeTransportedItem(ti:GeneralTransportedItem_T, item:GeneralTransportedItem_T)->GeneralTransportedItem_T:
        init_ti = ti.init()
        #init_tiの各要素を参照して、tiの情報がinit_tiの情報と異なるならtiの情報を採用し、同じならitemの情報を参照してinit_tiと異なるならitemの情報を採用し、両方とも同じならそのまま
        for key in init_ti.__dict__.keys():
            if ti.__dict__[key] != init_ti.__dict__[key]:
                #tiの情報がinit_tiの情報と異なるならtiの情報を採用
                ti.__dict__[key] = item.__dict__[key]
            else:
                #tiの情報がinit_tiの情報と同じならitemの情報を参照
                if item.__dict__[key] != init_ti.__dict__[key]:
                    #itemの情報がinit_tiの情報と異なるならitemの情報を採用
                    ti.__dict__[key] = item.__dict__[key]
                else:
                    #両方とも同じならそのまま
                    pass
        return ti


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

    # async def notify(self, data: TransportedItem):
    #     # 次に喋るべきキャラクターを通知
    #     await self.event_queue.put(data)

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

    # async def notify(self, data):
    #     # 読み上げるための文章を通知
    #     await self.event_queue.put(data)
    
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


class ThinkAgent2(Agent,QueueNode):
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

    # async def notify(self, data):
    #     # 読み上げるための文章を通知
    #     await self.event_queue.put(data)


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
        ret_ti = TransportedItem.init()
        ret_ti.recieve_messages = rm
        ret_ti.MicInputJudge_data = {"理由":"タイムアウト","入力成功度合い":0.0}
        ret_ti.SpeakerDistribute_data = {"次に発言するべきキャラクター":self.chara_name , "理由考察":"タイムアウト"}

        return ret_ti
    
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

    # async def notify(self, data):
    #     # 読み上げるための文章を通知
    #     await self.event_queue.put(data)


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
        ret_ti = TransportedItem.init()
        ret_ti.recieve_messages = rm
        ret_ti.MicInputJudge_data = {"理由":"タイムアウト","入力成功度合い":0.0}
        ret_ti.SpeakerDistribute_data = {"次に発言するべきキャラクター":self.chara_name , "理由考察":"タイムアウト"}

        return ret_ti
        
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
    
    def replaceDictDef(self,think_agent_output:str, non_thinking_serif:list[str]|None)->dict[str,str]:
        
        ret = {
            "{{think_agent_output}}":think_agent_output,
            "{{gptキャラ}}":self.chara_name,
            "{{Playerキャラ}}":"ゆかり"
        }
        if non_thinking_serif != None:
            ret["{{思考停止セリフの場合}}"] = f"また思考しながら同時に{self.chara_name}は口が勝手に動いてしまい、思考停止セリフを発しています。会話は現状次のように進んでいます。{non_thinking_serif}"
        return ret
    def __init__(self, agent_manager: AgentManager, chara_name:str):
        super().__init__(agent_manager)
        self.name = "発言エージェント"
        self.request_template_name = "発言エージェントリクエストひな形"
        self.chara_name = chara_name
        self.agent_setting = self.loadAgentSetting()
        self.event_queue = Queue()
        self.agent_manager = agent_manager
        self.epic:Epic = agent_manager.epic
        self.replace_dict = self.replaceDictDef("",None)

    async def handleEvent(self, transported_item:TransportedItem):
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)

        if transported_item.stop:
            await self.notify(transported_item)
            return

        output = await self.run(transported_item)
        # 新たな発言があった場合はキャンセル
        # プレイヤーの追加発言があればキャンセル.追加発言があるかどうかの判定は最新メッセージの時間とoutput.timeを比較して行う
        if self.epic.getLatestMessage()['現在の日付時刻'] != output.time and (self.chara_name not in self.epic.getLatestMessage()['message'].speakers):
            ExtendFunc.ExtendPrint(f"{self.epic.getLatestMessage()['message'].speakers}と{self.chara_name}を比較しました。{self.epic.messageHistory[-1]['現在の日付時刻']}に追加発言があるため{output.time}の分はキャンセルします。")
            return
        ExtendFunc.ExtendPrint(f"{self.name}はすべて成功したので次のエージェントに行きます。{self.chara_name}が喋ります。")

        serif_list = self.getSerifList(output.Serif_data)
        if serif_list == None:
            return
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


    # async def notify(self, data):
    #     # 読み上げるための文章を通知
    #     await self.event_queue.put(data)
    

    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        # return JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})[self.name]#self.replace_dict)[self.name]

        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        ExtendFunc.ExtendPrint(all_template_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]


    def prepareQuery(self, ti:TransportedItem)->list[ChatGptApiUnit.MessageQuery]:
        think_data = JsonAccessor.dictToJsonString(ti.Think_data)
        non_think_serif_list = self.getSerifList(ti.NonThinkingSerif_data)
        self.replace_dict = self.replaceDictDef(think_data, non_think_serif_list)
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
    def getSerifList(self,result: dict[str,str]|None) -> list[str]|None:
        if result == None:
            return None

        serif = result[f'{self.chara_name}の発言']
        # 修正した正規表現パターン（キャプチャグループを追加）
        split_pattern = r'([。！？\.\?\!\n])'
        split_serif = re.split(split_pattern, serif)
        
        # 区切り文字を前の部分に結合
        # combined_serif = [split_serif[i] + split_serif[i + 1] for i in range(0, len(split_serif) - 1, 2)]

        return split_serif

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, str])->TransportedItem:
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
        if output.NonThinkingSerif_data != None:
            serif_list = self.getSerifList(output.NonThinkingSerif_data)
        else:
            return
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
            await self.notify(output)
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


    # async def notify(self, data):
    #     # 読み上げるための文章を通知
    #     await self.event_queue.put(data)

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
        # 修正した正規表現パターン（キャプチャグループを追加）
        split_pattern = r'([。！？\.\?\!\n])'
        split_serif = re.split(split_pattern, serif)
        
        # 区切り文字を前の部分に結合
        # combined_serif = [split_serif[i] + split_serif[i + 1] for i in range(0, len(split_serif) - 1, 2)]

        return split_serif

    def saveResult(self,result):

        pass

    def clearMemory(self):
        pass

    def addInfoToTransportedItem(self,transported_item:TransportedItem, result:Dict[str, str])->TransportedItem:
        transported_item.NonThinkingSerif_data = result
        return transported_item    


class LifeProcessModule:
    """
    タスク分解
    タスク実行
    Bios
    ネット検索
    タイマー
    制御（if、for、goto）
    などを行う
    """
    replace_dict:dict[str,str] = {}
    name:str
    event_queue_dict = {}
    def __init__(self, replace_dict: dict[str,str] = {}):
        self._gpt_api_unit = ChatGptApiUnit()
        ExtendFunc.ExtendPrint(replace_dict)
        self.replace_dict = replace_dict

    async def run(self,transported_item: GeneralTransportedItem)->GeneralTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def appendReciever(self,reciever:EventReciever):
        self.event_queue_dict[reciever] = Queue[GeneralTransportedItem]()
        return self.event_queue_dict[reciever]
    
    @abstractmethod
    async def notify(self, data:GeneralTransportedItem):
        pass
    
    @abstractmethod
    def prepareQuery(self,input: GeneralTransportedItem)->list[ChatGptApiUnit.MessageQuery]:
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
    def addInfoToTransportedItem(self,transported_item:GeneralTransportedItem, result:Dict[str, Any])->GeneralTransportedItem:
        pass

class LifeProcessModuleManager:
    def __init__(self) -> None:
        pass

# タスク分解の案を出すエージェント
class TaskDecompositionProposerAgent(LifeProcessModule):
    def __init__(self):
        super().__init__()
        self.name = "タスク分解提案エージェント"
        self.request_template_name = "タスク分解提案エージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue_dict:dict[EventReciever,Queue[TaskBreakingDownTransportedItem]] = {}

    def typeTaskDecompositionProposerAgentResponse(self, replace_dict: dict[str,str]):
        TypeDict = {
            "提案": str
        }
        return TypeDict

    async def handleEvent(self, transported_item:TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        # 思考エージェントが状況を整理し、必要なタスクなどを分解し、思考
        ExtendFunc.ExtendPrint(self.name,transported_item)
        output = await self.run(transported_item)
        return output
    
    async def notify(self, data:TaskBreakingDownTransportedItem):
        task = []
        for event_queue in self.event_queue_dict.values():
            task.append(event_queue.put(data))
        await asyncio.gather(*task)

    async def run(self,transported_item: TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})#self.replace_dict)
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input: TaskBreakingDownTransportedItem) -> list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def replaceDictDef(self, input: TaskBreakingDownTransportedItem)->dict[str,str]:
        if input.problem is None:
            raise ValueError("問題点が設定されていません。")
        return {
            "{{problem}}":input.problem.summarizeProblem(),
        }
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str) -> str:
        #このエージェントは文章をそのまま使うので、そのまま返す
        return result
    
    def addInfoToTransportedItem(self,transported_item:TaskBreakingDownTransportedItem, result:str)->TaskBreakingDownTransportedItem:
        item = TaskBrekingDownConversationUnit.init(self.name, result)
        transported_item.conversation.append(item)
        return transported_item





# タスク分解の案をチェックし、反論や修正や承認を行うエージェント
class TaskDecompositionCheckerAgent(LifeProcessModule):
    def __init__(self):
        super().__init__()
        self.name = "タスク分解チェッカーエージェント"
        self.request_template_name = "タスク分解チェッカーエージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue_dict:dict[EventReciever,Queue[TaskBreakingDownTransportedItem]] = {}

    def typeTaskDecompositionCheckerAgentResponse(self, replace_dict: dict[str,str]):
        TypeDict = {
            "問題点": str,
            "修正案": str,
            "チェック結果": ["承認", "修正"]
        }
        return TypeDict
    
    async def handleEvent(self, transported_item:TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        ExtendFunc.ExtendPrint(self.name,transported_item)
        output = await self.run(transported_item)
        return output

    async def notify(self, data:TaskBreakingDownTransportedItem):
        task = []
        for event_queue in self.event_queue_dict.values():
            task.append(event_queue.put(data))
        await asyncio.gather(*task)

    async def run(self,transported_item: TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input: TaskBreakingDownTransportedItem) -> list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    

    def replaceDictDef(self, input: TaskBreakingDownTransportedItem)->dict[str,str]:
        if input.problem is None:
            raise ValueError("問題点が設定されていません。")

        return {
            "{{problem}}":input.problem.summarizeProblem(),
            "{{conversation}}":TaskBreakingDownTransportedItem.conversationToString(input.conversation)
        }
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str)->dict:
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        return ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeTaskDecompositionCheckerAgentResponse(self.replace_dict))
    
    def addInfoToTransportedItem(self,transported_item:TaskBreakingDownTransportedItem, result:dict)->TaskBreakingDownTransportedItem:
        # resultは{"問題点":str, "修正案":str, "チェック結果":str}の形式
        problem_point = result["問題点"]
        fix_step_idea = result["修正案"]
        check_result = result["チェック結果"]
        item = TaskBrekingDownConversationUnit.init(self.name, fix_step_idea, problem_point, check_result)
        transported_item.conversation.append(item)
        return transported_item

class TaskUnit(BaseModel):
        id:str
        description:str
        dependencies:list[str]
        def __init__(self):
            return self

        @staticmethod
        def init(id:str|None, タスクの説明:str|None, 依存するタスクのid:list[str]|None)->"TaskUnit":
            tu = TaskUnit()
            return tu
class TaskToJsonConverterAgent(LifeProcessModule):
    def __init__(self):
        super().__init__()
        self.name = "タスクJSON変換エージェント"
        self.request_template_name = "タスクJSON変換エージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.event_queue_dict:dict[EventReciever,Queue[TaskBreakingDownTransportedItem]] = {}

    def typeTaskToJsonConverterAgentResponse(self, replace_dict: dict[str,str]):
        #JsonSchemaの型を定義
        TypeDict = {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "default": ""},
                        "description": {"type": "string", "default": ""},
                        "dependencies": {"type": "array", "items": {"type": "string"}, "default": []}
                    },
                    "required": ["id", "description", "dependencies"]
                }
            }
        }
        return TypeDict


    async def handleEvent(self, transported_item:TaskBreakingDownTransportedItem):
        ExtendFunc.ExtendPrint(transported_item)
        result = await self.run(transported_item)
        return result


    async def notify(self, data:TaskBreakingDownTransportedItem):
        task = []
        for event_queue in self.event_queue_dict.values():
            task.append(event_queue.put(data))
        await asyncio.gather(*task)

    async def run(self,transported_item: TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item

    def prepareQuery(self, input: TaskBreakingDownTransportedItem) -> list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def replaceDictDef(self, input: TaskBreakingDownTransportedItem)->dict[str,str]:
        return {
            "{{task_breaking_down_idea}}":input.conversationToString(input.conversation)
        }
    
    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
        
    def correctResult(self, result: str)->list[Task]:
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        ret:list[Task] = ExtendFunc.correctDictToJsonSchemaTypeDictRecursive(jsonnized_result, self.typeTaskToJsonConverterAgentResponse(self.replace_dict)) # type: ignore
        return ret
    def addInfoToTransportedItem(self,transported_item:TaskBreakingDownTransportedItem, result:list[Task])->TaskBreakingDownTransportedItem:
        #内容未定
        transported_item.breaking_downed_task = result
        return transported_item
    
class TaskDecompositionProcessManager:
    _proposer = TaskDecompositionProposerAgent()
    _checker = TaskDecompositionCheckerAgent()
    _converter = TaskToJsonConverterAgent()
    def __init__(self) -> None:
        pass

    async def taskDecompositionProcess(self, transported_item:TaskBreakingDownTransportedItem)->TaskBreakingDownTransportedItem:
        while transported_item.comlete_breaking_down_task == False:
            transported_item = await self._proposer.handleEvent(transported_item)
            transported_item = await self._checker.handleEvent(transported_item)
        transported_item = await self._converter.handleEvent(transported_item)
        return transported_item

class DestinationTransportedItem(GeneralTransportedItem):
    """
    resultの中身が決まってない
    """
    result: | None
    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def init():
        return DestinationTransportedItem(
            usage_purpose="Destination"
            result= None
        )

class DestinationAgent(LifeProcessModule):
    """
    Q1 : 目標エージェントはどこで生成するのがよいのか？ A:
    Q2 : Memoryオブジェクトはシングルトンだが、どこで生成してこのクラスにバインドするのか？ A:
    
    """
    name:str = "目標決定エージェント"
    request_template_name:str = "目標決定エージェントリクエストひな形"
    本能yml:dict
    gptキャラの本能:str
    memory:"Memory"

    def __init__(self):
        super().__init__()
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        self.load本能()

    def typeDestinationAgentResponse(self, replace_dict: dict[str,str]):
        #JsonSchemaの型を定義
        TypeDict = {
            "type": "object",
            "properties": {
                "目標": {"type": "string"},
                "利益ベクトル": {
                    "type": "object",
                    "properties": {
                        "精神エネルギー": {"type": "integer","default":0},
                        "肉体エネルギー": {"type": "integer","default":0},
                        "色々なことへの自尊心自信評価": {
                            "type": "object",
                            "properties": {
                                "知識やスキルへの自信": {"type": "integer","default":0},
                                "想像力への自信": {"type": "integer","default":0},
                                "創造性への自信": {"type": "integer","default":0},
                                "対人関係のスキルへの自信": {"type": "integer","default":0},
                                "社会的地位への自信": {"type": "integer","default":0},
                                "身体的能力への自信": {"type": "integer","default":0},
                                "外見への自信": {"type": "integer","default":0},
                                "倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信": {"type": "integer","default":0},
                                "社会や人類に貢献すること": {"type": "integer","default":0},
                                "個性や独自性": {"type": "integer","default":0},
                                "自己表現力への自信": {"type": "integer","default":0},
                                "感情の安定性への自信": {"type": "integer","default":0},
                                "共感力への自信": {"type": "integer","default":0}
                            },
                            "required": [
                                "知識やスキルへの自信",
                                "想像力への自信",
                                "創造性への自信",
                                "対人関係のスキルへの自信",
                                "社会的地位への自信",
                                "身体的能力への自信",
                                "外見への自信",
                                "倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信",
                                "社会や人類に貢献すること",
                                "個性や独自性",
                                "自己表現力への自信",
                                "感情の安定性への自信",
                                "共感力への自信"
                            ]
                        },
                        "他者からの名誉": {
                            "type": "object",
                            "properties": {
                                "愛": {"type": "integer","default":0},
                                "友情": {"type": "integer","default":0},
                                "尊敬": {"type": "integer","default":0},
                                "信頼": {"type": "integer","default":0},
                                "感謝": {"type": "integer","default":0},
                                "認められること": {"type": "integer","default":0},
                                "ユーモアがあること": {"type": "integer","default":0},
                                "面白いことを言うこと": {"type": "integer","default":0}
                            },
                            "required": [
                                "愛",
                                "友情",
                                "尊敬",
                                "信頼",
                                "感謝",
                                "認められること",
                                "ユーモアがあること",
                                "面白いことを言うこと"
                            ]
                        },
                        "物理的コスト": {
                            "type": "object",
                            "properties": {
                                "お金": {"type": "integer","default":0},
                                "時間": {"type": "integer","default":0},
                                "資源": {"type": "integer","default":0}
                            },
                            "required": [
                                "お金",
                                "時間",
                                "資源"
                            ]
                        }
                    },
                    "required": [
                        "精神エネルギー",
                        "肉体エネルギー",
                        "色々なことへの自尊心自信評価",
                        "他者からの名誉",
                        "物理的コスト"
                    ]
                    }
                },
            "required": [
                "目標",
                "利益ベクトル"
            ]
            }

        return TypeDict
    def handleEvent(self, transported_item:DestinationTransportedItem):
        ExtendFunc.ExtendPrint(self.name,transported_item)
        result = self.run(transported_item)
        return result
    
    async def run(self,transported_item: DestinationTransportedItem)->GeneralTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def correctResult(self, result: str) -> DestinationAndProfitVector:
        jsonnized_result = JsonAccessor.extendJsonLoad(result)
        corrected_profit_dict:目標と利益ベクトル = ExtendFunc.correctDictToTypeDict(jsonnized_result, self.typeDestinationAgentResponse(self.replace_dict))  # type: ignore
        return DestinationAndProfitVector.from_dict(corrected_profit_dict)
    
    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input: DestinationTransportedItem) -> list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def replaceDictDef(self, input: DestinationTransportedItem)->dict[str,str]:
        # raise NotImplementedError("未定義・未使用")
        return {
            "{{gptキャラの本能}}":self.gptキャラの本能
        }
    
    def load本能(self):
        self.本能yml = JsonAccessor.loadGptBehaviorYaml("一般")
        replace_dict = {
            "{{利益重みベクトル}}" : self.本能yml["利益重みベクトル"],
            "{{目標と利益ベクトルの辞書}}" : self.本能yml["目標と利益ベクトルの辞書"],
        }
        gptキャラの本能 = self.本能yml["gptキャラの本能"]
        self.gptキャラの本能 = ExtendFunc.replaceBulkStringRecursiveCollection(gptキャラの本能, replace_dict)
    
    def addInfoToTransportedItem(self,transported_item:DestinationTransportedItem, result:DestinationAndProfitVector)->DestinationTransportedItem:
        transported_item.result = result
        return transported_item

    

class TaskExecutorAgent(LifeProcessModule):
    """
    未定義・未使用
    """
    def __init__(self, agent_manager: AgentManager, replace_dict: Dict[str, str] = {}):
        raise NotImplementedError("未定義・未使用")
        pass
    def handleEvent(self, transported_item:LifeProcessTransportedItem):
        task_graph = self.createTaskGraph(transported_item.task_list)
        pass
    
    def createTaskGraph(self, task_list:list[Task]):#->TaskGraph:
        pass
class FileOperator(LifeProcessModule):
    # todo: ファイル操作を行うエージェント。未定義・未使用
    def __init__(self):
        raise NotImplementedError("未定義・未使用")

class NormalChatTransportedItem(GeneralTransportedItem):
    task:Task | None
    previous_task_result:"TaskToolOutput | None"
    result:str | None
    class Config:
        arbitrary_types_allowed = True
    
    @staticmethod
    def init():
        return NormalChatTransportedItem(
            usage_purpose="NormalChat",
            task = None,
            previous_task_result = None,
            result = None
        )

class NormalChatAgent(LifeProcessModule):
    def __init__(self):
        super().__init__()
        self.name = "汎用チャットエージェント"
        self.request_template_name = "汎用チャットエージェントリクエストひな形"
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
    
    async def handleEvent(self, transported_item:NormalChatTransportedItem)->NormalChatTransportedItem:
        ExtendFunc.ExtendPrint(self.name,transported_item)
        output = await self.run(transported_item)
        return output

    async def run(self,transported_item: NormalChatTransportedItem)->NormalChatTransportedItem:
        query = self.prepareQuery(transported_item)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", query, f"{self.name} : リクエスト")
        result = await self.request(query)
        # ExtendFunc.ExtendPrint(result)
        corrected_result = self.correctResult(result)
        # ExtendFunc.ExtendPrint(corrected_result)
        JsonAccessor.insertLogJsonToDict(f"test_gpt_routine_result.json", corrected_result, f"{self.name} : レスポンス")
        self.saveResult(result)
        self.clearMemory()
        transported_item = self.addInfoToTransportedItem(transported_item, corrected_result)
        ExtendFunc.ExtendPrint(transported_item)
        return transported_item
    
    def loadAgentSetting(self)->tuple[list[ChatGptApiUnit.MessageQuery],list[ChatGptApiUnit.MessageQuery]]:
        all_template_dict: dict[str,list[ChatGptApiUnit.MessageQuery]] = JsonAccessor.loadAppSettingYamlAsReplacedDict("AgentSetting.yml",{})
        return all_template_dict[self.name], all_template_dict[self.request_template_name]
    
    def prepareQuery(self, input: NormalChatTransportedItem) -> list[ChatGptApiUnit.MessageQuery]:
        self.replace_dict = self.replaceDictDef(input)
        self.agent_setting, self.agent_setting_template = self.loadAgentSetting()
        replaced_template = ExtendFunc.replaceBulkStringRecursiveCollection(self.agent_setting_template, self.replace_dict)
        query = self.agent_setting + replaced_template
        return query
    
    def replaceDictDef(self, input: NormalChatTransportedItem)->dict[str,str]:
        if input.task is None or input.previous_task_result is None:
            raise ValueError("タスクが設定されていません")
        return {
            "{{previous_task_result}}":input.previous_task_result.summarizeOutputs(),
            "{{task}}":input.task["description"]
        }
    
    async def request(self, query:list[ChatGptApiUnit.MessageQuery])->str:
        print(f"{self.name}がリクエストを送信します")
        result = await self._gpt_api_unit.asyncGenereateResponseGPT3Turbojson(query)
        if result is None:
            raise ValueError("リクエストに失敗しました。")
        return result
    
    def correctResult(self,result: str)->str:
        #何もしない
        return result
    
    def addInfoToTransportedItem(self,transported_item:NormalChatTransportedItem, result:str)->NormalChatTransportedItem:
        transported_item.result = result
        return transported_item

class TaskToolOutput:
    taskGraph:"TaskGraph | None" = None
    thinking: str | None = None
    serif: str | None = None
    task_exec_result: str | None = None # タスクのidや題名、問題、解決過程、結果をまとめたもの。jsonの文字列形式で保持する

    def __init__(self,taskGraph:"TaskGraph | None" = None, taask_exec_result:str|None = None) -> None:
        self.taskGraph = taskGraph
        self.task_exec_result = taask_exec_result
    
    def summarizeOutputs(self)->str:
        """
        タスクグラフの現状までの実行結果をまとめる
        """
        if self.taskGraph is not None:
            return self.taskGraph.summarizeOutputs()
        
        raise ValueError("タスクグラフが作成されていません")

    

class TaskTool:
    def __init__(self, task:Task) -> None:
        self.task = task
    @abstractmethod
    async def execute(self,previows_output:TaskToolOutput)->TaskToolOutput:
        # TaskToolOutputのresultに結果を格納して返す、結果の書き込み責務はTaskTool側にある
        pass
    @abstractmethod
    def report(self, ti:GeneralTransportedItem)->str:
        pass

class TaskDecompositionTool(TaskTool):
    def __init__(self, task:Task) -> None:
        super().__init__(task)
        self.task_decomposition_process_manager = TaskDecompositionProcessManager()
    async def execute(self, taskToolOutput: TaskToolOutput) -> TaskToolOutput:
        problem = ProblemDecomposedIntoTasks(self.task, taskToolOutput)
        task_breaking_down_ti = TaskBreakingDownTransportedItem.init(problem)
        taskBreakingDown:TaskBreakingDownTransportedItem = await self.task_decomposition_process_manager.taskDecompositionProcess(task_breaking_down_ti)
        taskGraph = TaskGraph(taskBreakingDown)
        return TaskToolOutput(taskGraph)

class TaskExecutionTool(TaskTool):
    def __init__(self, task:Task) -> None:
        super().__init__(task)

    async def execute(self,previows_output:TaskToolOutput)->TaskToolOutput:
        if previows_output.taskGraph is None:
            raise ValueError("前の出力がタスクグラフではありません")
        taskGraph:TaskGraph = previows_output.taskGraph
        previows_output.task_exec_result = await taskGraph.excuteRecursive()
        return previows_output
    
    def report(self, taskGraph: "TaskGraph")->str:
        # 子タスクたちは全員結果を文字列で保持してるから、それをまとめて返す
        return taskGraph.summarizeOutputs()

class NormalChatTool(TaskTool):
    def __init__(self, task:Task) -> None:
        super().__init__(task)
        self.normalChatAgenet = NormalChatAgent()
    async def execute(self,previows_output:TaskToolOutput)->TaskToolOutput:
        normalChatTransportedItem = NormalChatTransportedItem.init()
        normalChatTransportedItem.task = self.task
        normalChatTransportedItem.previous_task_result = previows_output
        normalChatTransportedItem = await self.normalChatAgenet.handleEvent(normalChatTransportedItem)
        previows_output.task_exec_result = self.report(normalChatTransportedItem)
        return previows_output
    
    def report(self, ti:NormalChatTransportedItem)->str:
        if ti.result is None:
            raise ValueError("結果が設定されていません")
        return ti.result
        

        
        
    
class SpeakTool(TaskTool):
    def __init__(self, task:Task) -> None:
        super().__init__(task)


    
TaskToolType = TypeVar("TaskToolType", bound=TaskTool)

class TaskGraphUnit:
    _previous_tasks: list["TaskGraphUnit"]
    _next_tasks: list["TaskGraphUnit"]
    _previous_resolved:dict["TaskGraphUnit",bool]= {}
    _ready:bool = False
    task:Task
    tool:TaskTool|None
    _output:TaskToolOutput|None = None
    @property
    def previous_tasks(self):
        return self._previous_tasks
    @property
    def next_tasks(self):
        return self._next_tasks
    @property
    def ready(self):
        return self._ready
    @property
    def usetool(self):
        return self.task["use_tool"]
    @property
    def isLastTask(self):
        return len(self._next_tasks) == 0
    @property
    def output(self):
        return self._output
    @output.setter
    def output(self, value:TaskToolOutput):
        self._output = value
    def __init__(self, task:Task) -> None:
        self.task = task
        self._previous_tasks = []
        self._next_tasks = []
        self.tool = self.selectTool(task)
    def registPreviousTask(self, previous_task:"TaskGraphUnit"):
        # 重複登録を防ぐ
        if previous_task not in self._previous_tasks:
            self._previous_tasks.append(previous_task)
    def registNextTask(self, next_task:"TaskGraphUnit"):
        # 重複登録を防ぐ
        if next_task not in self._next_tasks:
            self._next_tasks.append(next_task)

    def initPreviousResolvedStatus(self):
        # 依存関係の解決状況を初期化
        for previous_task in self._previous_tasks:
            self._previous_resolved[previous_task] = False

    async def recievePreviousTaskResolvedAndExcuteTask(self, previous_task:"TaskGraphUnit", previows_output:TaskToolOutput):
        # 前のタスクが解決されたことを受信し、自身のタスクを実行
        self._previous_resolved[previous_task] = True
        if all(self._previous_resolved.values()):
            self._ready = True
            await self.executeAndRecursiveNextTaskExcute(previows_output)

    def recievePreviousTaskResolved(self, previous_task:"TaskGraphUnit"):
        # 前のタスクが解決されたことを受信
        self._previous_resolved[previous_task] = True
        if all(self._previous_resolved.values()):
            self._ready = True

    def notifyProcessComplete(self):
        # 完了したことを次のタスクに通知
        self._ready = False
        self._previous_resolved = {}
        for next_task in self._next_tasks:
            next_task.recievePreviousTaskResolved(self)
    async def notifyProcessCompleteAndNextTaskExcute(self, previows_output:TaskToolOutput):
        # 完了したことを次のタスクに通知し、次のタスクを実行
        next_tasks = asyncio.gather(*[next_task.recievePreviousTaskResolvedAndExcuteTask(self,previows_output) for next_task in self._next_tasks])
        await next_tasks

    def notifyProcessCompleteForCreateStepList(self,next_step_candidate:list["TaskGraphUnit"])->list["TaskGraphUnit"]:
        # ステップリストを作る手続きのために完了したことを次のタスクに通知
        self._ready = False
        self._previous_resolved = {}
        for next_task in self._next_tasks:
            next_task.recievePreviousTaskResolved(self)
            next_step_candidate.extend(self._next_tasks)
        return next_step_candidate
    
    async def executeAndRecursiveNextTaskExcute(self, previows_output:TaskToolOutput):
        if all(self._previous_resolved.values()) == False:
            return
        # タスクを実行
        if self.tool is not None:
            tool_output = await self.tool.execute(previows_output)
            self.output = tool_output
        
        if self.isLastTask == True:
            return tool_output
        else:
            # 次のタスクに通知して可能なら実行する
            await self.notifyProcessCompleteAndNextTaskExcute(tool_output)
    
    def selectTool(self,task:Task)->TaskTool|None:
        if task["use_tool"] == "タスク分解":
            return TaskDecompositionTool(task)
        elif task["use_tool"] == "タスク実行":
            return TaskExecutionTool(task)
        elif task["use_tool"] == "思考":
            return NormalChatTool(task)
        elif task["use_tool"] == "発言":
            return SpeakTool(task)
        else:
            return None
    
class TaskGraph:
    problem_title:str
    task_dict:dict[str, TaskGraphUnit] = {}
    step_list: list[list[TaskGraphUnit]] = []
    non_dependent_tasks: list[TaskGraphUnit] = []
    non_next_tasks: list[TaskGraphUnit] = []
    task_breaking_down_ti: TaskBreakingDownTransportedItem
    run_state:Literal["not_ready", "ready", "not_start", "running", "stop", "complete", "error"]
    
    def __init__(self,task_breaking_down_ti:TaskBreakingDownTransportedItem) -> None:
        self.problem_title = task_breaking_down_ti.problem.problem_title
        self.task_breaking_down_ti = task_breaking_down_ti
        task_list = task_breaking_down_ti.breaking_downed_task
        # 辞書に登録
        for task in task_list:
            tmp_task_unit = TaskGraphUnit(task)
            self.task_dict[task["id"]] = tmp_task_unit
        # 依存関係を登録
        for task_unit in self.task_dict.values():
            for dependency_id in task_unit.task["dependencies"]:
                dependency_task = self.task_dict[dependency_id]
                task_unit.registPreviousTask(dependency_task)
                dependency_task.registNextTask(task_unit)
            if len(task_unit.previous_tasks) == 0:
                self.non_dependent_tasks.append(task_unit)
            if len(task_unit.next_tasks) == 0:
                self.non_next_tasks.append(task_unit)
        # ステップリストを作成
        step_list = [self.non_dependent_tasks]
        not_raady_next_step:list[TaskGraphUnit] = []
        while len(step_list[-1]) > 0:
            next_step_candidate:list[TaskGraphUnit] = []
            for task in step_list[-1]:
                next_step_candidate = task.notifyProcessCompleteForCreateStepList(next_step_candidate)
            next_step:list[TaskGraphUnit] = []
            for task in next_step_candidate:
                if task.ready:
                    next_step.append(task)
                else:
                    not_raady_next_step.append(task)
            step_list.append(next_step)
    
    async def excuteStepList(self):
        raise NotImplementedError("taskを単独で実行するメソッドが未実装です")
        for step in self.step_list:
            # 並列処理をする
            await asyncio.gather(*[task.execute() for task in step])

    async def excuteRecursive(self)->str:
        fast_step = self.step_list[0]
        fast_input:TaskToolOutput = TaskToolOutput(None,"最初のタスク")
        #todo 一番最初のpreviows_outputが未実装です
        # raise NotImplementedError("一番最初のpreviows_outputが未実装です")
        tasks = asyncio.gather(*[task.executeAndRecursiveNextTaskExcute(fast_input) for task in fast_step])
        output = await tasks
        # 最後のタスクが終わったらサマライズする
        return self.summarizeOutputs()
    
    def summarizeOutputs(self)->str:
        """
        タスクグラフの結果履歴をどのようにまとめるか考える
        タスクグラフユニットごとに結果を持っておいて、ステップごとに結果をまとめる
        """
        summary = ""
        step_index = 0
        for step in self.step_list:
            step_index += 1
            summary += f"# ステップ{step_index}の結果\n"
            for task in step:
                if task.output is None:
                    continue
                output:TaskToolOutput = task.output
                if output.task_exec_result is None:
                    continue
                task_exec_result = output.task_exec_result
                summary += f"\n{task_exec_result}"
            summary += "\n" 
        return summary

class TaskProgress:
    # タスクの進捗
    task_graphs:dict[str,TaskGraph] = {} # タスクグラフ
    
    def __init__(self) -> None:
        pass
    def addTaskGraph(self, task_graph:TaskGraph):
        self.task_graphs[task_graph.problem_title] = task_graph

class ThirdPersonEvaluation:
    # 第三者評価
    pass

class Memory:
    destinations:list[DestinationAndProfitVector] # 目標リスト
    holding_profit_vector:ProfitVector # 保持している利益ベクトル
    past_conversation:Epic # 過去の会話
    task_progress:TaskProgress # タスクの進捗
    third_person_evaluation: ThirdPersonEvaluation # 第三者評価
    def __init__(self, chara_name:str) -> None:
        self.chara_name = chara_name
        self.loadInitialMemory()
    def loadMemory(self, chara_name:str)->"Memory | None":
        memory = self.loadSelfPickle(chara_name)
        if memory is None:
            memory = self.loadInitialMemory()
        return memory

    def addDestination(self, destination:DestinationAndProfitVector):
        self.destinations.append(destination)

    def addHoldingProfitVector(self, profit_vector:ProfitVector):
        self.holding_profit_vector += profit_vector

    def saveSelfPickle(self,chara_name:str):
        """
        pickleで保存
        """
        PickleAccessor.saveMemory(self, chara_name)

    def loadSelfPickle(self,chara_name:str)->"Memory | None":
        """
        pickleで読み込み
        """
        memory = PickleAccessor.loadMemory(chara_name)
        # memoryの型がMemoryであることを確認
        if isinstance(memory, Memory) == False:
            return None
        return memory
    
    def loadInitialMemory(self):
        """ 
        初期のMemoryをロード
        いろいろなjsonファイルから読み込む.
        各プロパティごとに分かれているのでそれを読み込む
        """
        behavior:dict = JsonAccessor.loadGptBehaviorYaml()
        self.destination = behavior["目標"]
        self.profit_vector = behavior["利益ベクトル"]
        self.past_conversation = behavior["過去の会話"]
        self.task_progress = behavior["タスクの進捗"]
        self.third_person_evaluation = behavior["第三者評価"]
        
    
    def loadDestinations(self)->list[DestinationAndProfitVector]:
        """
        目標:str は文章なので、キャラクターごとに目標の文章を設定する
        利益ベクトル:ProfitVector

        使用用途：目標決定エージェントが目標を決定する際に使用
        """
        



            
class LifeProcessState:
    """
    LifeProcessの状態
    """
    実行状態:bool = False
    def __init__(self) -> None:
        pass

class LifeProcessBrain:
    task_graph_process:TaskGraph
    memory:Memory
    state:LifeProcessState = LifeProcessState()

    def __init__(self) -> None:
        """
        メモリーをロードor初期化
        task_graph_processをメモリーから生成
        task_graph_processを実行
        """
        self.memory = Memory()
        self.task_graph_process = TaskGraph(self.memory.task_progress.task_graphs[""])






    





@dataclass
class GPTAgent:
    manager: AgentManager
    event_manager: AgentEventManager


    
if __name__ == "__main__":
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
    
    def te10():
        ti = TaskBreakingDownTransportedItem.init()
        ExtendFunc.ExtendPrint(ti)

    import re

    def te11():
        serif = "鬼ってことは、みんなを追いかける役かな？それなら、隠れる場所やアイテムを考えたりして、面白い要素を追加できそうだね！"
        # 修正した正規表現パターン（キャプチャグループを追加）
        split_pattern = r'([。！？、,\.\?\!\n])'
        split_serif = re.split(split_pattern, serif)
        
        # 区切り文字を前の部分に結合
        combined_serif = [split_serif[i] + split_serif[i + 1] for i in range(0, len(split_serif) - 1, 2)]
        
        ExtendFunc.ExtendPrint(combined_serif)

    # 実行例