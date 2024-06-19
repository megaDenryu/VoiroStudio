import json
from typing import Literal
from api.gptAI.HumanBaseModel import BodypartState, HumanName, MemoryUnit
from api.gptAI.HumanBaseModel import HumanEmotion



class HumanState:
    def __init__(self, char_name:str):
        self.char_name = char_name
        self.emotion:dict[HumanName, HumanEmotion] = {}
        self.known_human:list[HumanName] = []
        self.body_condition:dict[str, float] = {
            "体温": 36.5,
            "脈拍": 70,
            "血圧": 120,
            "酸素飽和度": 98,
            "体重": 60,
            "身長": 140,
            "体脂肪率": 20
        }
        normal:BodypartState = BodypartState(health_state="健康", health_point=100)
        self.body_parts:dict[str, BodypartState] = {
            "頭": normal,
            "顔": normal,
            "首": normal,
            "肩": normal,
            "腕": normal,
            "手": normal,
            "胸": normal,
            "背中": normal,
            "腹": normal,
            "腰": normal,
            "尻": normal,
            "太もも": normal,
            "膝": normal,
            "足首": normal,
            "足の裏": normal,
            "つま先": normal,
        }
        self.isConversation = False

class HumanMemory:
    def __init__(self):
        self.memory:list[MemoryUnit] = []


