from enum import Enum
from pydantic import BaseModel
from typing import TypedDict

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendSet import Interval

class HumanName(BaseModel):
    front_name: str
    char_name: str

class EmotionName(BaseModel):
    emotion_name: str
    def __init__(self, emotion_name:str):
        self.emotion_name = emotion_name

class HumanEmotion(BaseModel):
    emotionVector: dict[EmotionName, float] #感情ベクトル。感情名とその強さの辞書。
    impression:str #印象

class 体の状態(BaseModel):
    健康状態: str
    疲労レベル: int
    特筆すべき身体的な特徴や問題: str
    def __init__(self, 健康状態:str, 疲労レベル:int, 特筆すべき身体的な特徴や問題:str):
        return super().__init__(健康状態=健康状態, 疲労レベル=疲労レベル, 特筆すべき身体的な特徴や問題=特筆すべき身体的な特徴や問題)
    

class BodypartState(BaseModel):
    health_state:str #健康状態。健康、痛い、筋肉痛、疲れ、痺れ、かゆい、熱い　など
    health_point:float #各パーツのヘルスポイント。0~100の間で表現。0になるとその部位は使えなくなる。時間がたつと回復する。低くなるほど使いたくなくなる。
    def __init__(self, health_state:str, health_point:float):
        health_point_interval = Interval("[", 0, 100, "]")
        if health_point in health_point_interval:
            health_point = health_point
        elif health_point > health_point_interval.end:
            health_point = health_point_interval.end
        elif health_point < health_point_interval.start:
            health_point = health_point_interval.start
        return super().__init__(health_state=health_state, health_point=health_point)
        

    @staticmethod
    def normal():
        return BodypartState("健康", 100)


class MemoryUnit(BaseModel):
    type:str
    title:str
    #要約
    summary:str

class Task(TypedDict):
    id: str
    task_species: str
    description: str
    dependencies: list[str]
class MentalEnergy:
    mental_energy_interval:Interval = Interval("[", 0, 100, "]")
    def __init__(self, energy_value:int):
        if energy_value in self.mental_energy_interval:
            self.MentalEnergy = energy_value
        elif energy_value > self.mental_energy_interval.end:
            self.MentalEnergy = self.mental_energy_interval.end
        elif energy_value < self.mental_energy_interval.start:
            self.MentalEnergy = self.mental_energy_interval.start

class MentalStateDescription:
    description:str
    def __init__(self, description:str):
        self.description = description


if __name__ == "__main__":
    a = 体の状態("健康", 100, "特になし")
    print(a.健康状態)