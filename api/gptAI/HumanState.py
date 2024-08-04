import json
from typing import Literal
from api.Extend.ExtendSet import Interval
from api.gptAI.HumanBaseModel import *
from api.gptAI.HumanBaseModel import HumanEmotion
from typing import TypedDict




class HumanState:
    def __init__(self, char_name:str):
        self.char_name = char_name
        self.emotion:dict[HumanName, HumanEmotion] = {}
        self.known_human:list[HumanName] = []
        
        self.isConversation = False
        self.body_state:BodyState = BodyState()
        self.life_goal_state:LifeGoalState = LifeGoalState()
        self.mental_state:MentalState = MentalState()
        self.memory_state:MemoryState = MemoryState()

class BodyState:
    body_condition_rough:体の状態 = 体の状態("普通", 0, "特になし")
    body_condition:dict[str, float] = {
            "体温": 36.5,
            "脈拍": 70,
            "血圧": 120,
            "酸素飽和度": 98,
            "体重": 60,
            "身長": 140,
            "体脂肪率": 20
        }
    body_parts:dict[str, BodypartState] = {
            "頭": BodypartState.normal(),
            "顔": BodypartState.normal(),
            "首": BodypartState.normal(),
            "肩": BodypartState.normal(),
            "腕": BodypartState.normal(),
            "手": BodypartState.normal(),
            "胸": BodypartState.normal(),
            "背中": BodypartState.normal(),
            "腹": BodypartState.normal(),
            "腰": BodypartState.normal(),
            "尻": BodypartState.normal(),
            "太もも": BodypartState.normal(),
            "膝": BodypartState.normal(),
            "足首": BodypartState.normal(),
            "足の裏": BodypartState.normal(),
            "つま先": BodypartState.normal(),
        }
    def __init__(self) -> None:
        self.body_condition:dict[str, float]
        self.body_parts:dict[str, BodypartState]

class LifeGoalState:
    life_goals:list[Task] = []
    def __init__(self):
        pass

    # 会話と、メンタル、ボディー、ライフゴール、メモリーの状態からどのような目標を持つべきか探り、明確化する
    async def clarificateGoals(self, conversation:bool, mental:"MentalState", body:BodyState, memory:"MemoryState"):
        golas_idea = await self.findGoals(conversation, mental, body, memory)
        # 考えた目標がどれくらい達成できそうか確率を出力
        gials = await judgeGoals(golas_idea)
        # 

class MentalState:
    mental_energy:MentalEnergy = MentalEnergy(100)
    mental_state_description:MentalStateDescription = MentalStateDescription("普通")
    emotion_vector:dict[EmotionName, float] = {}
    def __init__(self):
        pass


class MemoryState:
    memory_list:list[MemoryUnit] = []
    





class HumanMemory:
    def __init__(self):
        self.memory:list[MemoryUnit] = []


