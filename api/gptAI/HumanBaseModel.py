from enum import Enum
from pydantic import BaseModel

from api.Extend.ExtendSet import Interval

class HumanName(BaseModel):
    front_name: str
    char_name: str

class EmotionName(BaseModel):
    emotion_name: str

class HumanEmotion(BaseModel):
    emotionVector: dict[EmotionName, float] #感情ベクトル。感情名とその強さの辞書。
    impression:str #印象

class BodypartState(BaseModel):
    health_state:str #健康状態。健康、痛い、筋肉痛、疲れ、痺れ、かゆい、熱い　など
    health_point:float #各パーツのヘルスポイント。0~100の間で表現。0になるとその部位は使えなくなる。時間がたつと回復する。低くなるほど使いたくなくなる。