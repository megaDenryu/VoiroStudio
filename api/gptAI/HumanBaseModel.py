import asyncio
from enum import Enum
from typing import TypeVar
from typing_extensions import Literal
from pydantic import BaseModel
from typing_extensions import TypedDict

from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Epic.Epic import Epic
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
    task_title: str
    description: str
    use_tool: Literal["なし","タスク分解","タスク実行","発言","思考","目標決定"]
    tool_query: str
    dependencies: list[str]

class TaskOutput(TypedDict):
    output:str


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
class 自尊心自信評価Dict(TypedDict):
          知識やスキルへの自信: int
          想像力への自信: int
          創造性への自信: int
          対人関係のスキルへの自信: int
          社会的地位への自信: int
          身体的能力への自信: int
          外見への自信: int
          倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信: int
          社会や人類に貢献すること: int
          個性や独自性: int
          自己表現力への自信: int
          感情の安定性への自信: int
          共感力への自信: int

class 他者からの名誉Dict(TypedDict):
    愛: int
    友情: int
    尊敬: int
    信頼: int
    感謝: int
    認められること: int
    ユーモアがあること: int
    面白いことを言うこと: int

class 物理的コストDict(TypedDict):
    お金: int
    時間: int
    資源: int

class 利益ベクトル(TypedDict):
    精神エネルギー: int
    肉体エネルギー: int
    色々なことへの自尊心自信評価: 自尊心自信評価Dict
    他者からの名誉: 他者からの名誉Dict
    物理的コスト: 物理的コストDict

class 目標と利益ベクトル(TypedDict):
    目標: str
    利益ベクトル: 利益ベクトル
class SelfEsteemConfidenceDict:
    知識やスキルへの自信: int
    想像力への自信: int
    創造性への自信: int
    対人関係のスキルへの自信: int
    社会的地位への自信: int
    身体的能力への自信: int
    外見への自信: int
    倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信: int
    社会や人類に貢献すること: int
    個性や独自性: int
    自己表現力への自信: int
    感情の安定性への自信: int
    共感力への自信: int
    def __init__(self, 知識やスキルへの自信:int, 想像力への自信:int, 創造性への自信:int, 対人関係のスキルへの自信:int, 社会的地位への自信:int, 身体的能力への自信:int, 外見への自信:int, 倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信:int, 社会や人類に貢献すること:int, 個性や独自性:int, 自己表現力への自信:int, 感情の安定性への自信:int, 共感力への自信:int):
        self.知識やスキルへの自信 = 知識やスキルへの自信
        self.想像力への自信 = 想像力への自信
        self.創造性への自信 = 創造性への自信
        self.対人関係のスキルへの自信 = 対人関係のスキルへの自信
        self.社会的地位への自信 = 社会的地位への自信
        self.身体的能力への自信 = 身体的能力への自信
        self.外見への自信 = 外見への自信
        self.倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信 = 倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信
        self.社会や人類に貢献すること = 社会や人類に貢献すること
        self.個性や独自性 = 個性や独自性
        self.自己表現力への自信 = 自己表現力への自信
        self.感情の安定性への自信 = 感情の安定性への自信
        self.共感力への自信 = 共感力への自信
    @classmethod
    def from_dict(cls, dict:自尊心自信評価Dict)->"SelfEsteemConfidenceDict":
        return cls(
            知識やスキルへの自信=dict["知識やスキルへの自信"],
            想像力への自信=dict["想像力への自信"],
            創造性への自信=dict["創造性への自信"],
            対人関係のスキルへの自信=dict["対人関係のスキルへの自信"],
            社会的地位への自信=dict["社会的地位への自信"],
            身体的能力への自信=dict["身体的能力への自信"],
            外見への自信=dict["外見への自信"],
            倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信=dict["倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信"],
            社会や人類に貢献すること=dict["社会や人類に貢献すること"],
            個性や独自性=dict["個性や独自性"],
            自己表現力への自信=dict["自己表現力への自信"],
            感情の安定性への自信=dict["感情の安定性への自信"],
            共感力への自信=dict["共感力への自信"]
        )
    
    def __add__(self, other:"SelfEsteemConfidenceDict"):
        return SelfEsteemConfidenceDict(
            self.知識やスキルへの自信 + other.知識やスキルへの自信, 
            self.想像力への自信 + other.想像力への自信, 
            self.創造性への自信 + other.創造性への自信, 
            self.対人関係のスキルへの自信 + other.対人関係のスキルへの自信, 
            self.社会的地位への自信 + other.社会的地位への自信, 
            self.身体的能力への自信 + other.身体的能力への自信, 
            self.外見への自信 + other.外見への自信, 
            self.倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信 + other.倫理的な行動や自分の道徳的な価値観や倫理観に基づく自信, 
            self.社会や人類に貢献すること + other.社会や人類に貢献すること,
            self.個性や独自性 + other.個性や独自性,
            self.自己表現力への自信 + other.自己表現力への自信,
            self.感情の安定性への自信 + other.感情の安定性への自信,
            self.共感力への自信 + other.共感力への自信
            )

class ExternalRecognitionDict:
    愛: int
    友情: int
    尊敬: int
    信頼: int
    感謝: int
    認められること: int
    ユーモアがあること: int
    面白いことを言うこと: int
    def __init__(self, 愛:int, 友情:int, 尊敬:int, 信頼:int, 感謝:int, 認められること:int, ユーモアがあること:int, 面白いことを言うこと:int):
        self.愛 = 愛
        self.友情 = 友情
        self.尊敬 = 尊敬
        self.信頼 = 信頼
        self.感謝 = 感謝
        self.認められること = 認められること
        self.ユーモアがあること = ユーモアがあること
        self.面白いことを言うこと = 面白いことを言うこと

    @classmethod
    def from_dict(cls, dict:他者からの名誉Dict)->"ExternalRecognitionDict":
        return cls(
            愛=dict["愛"],
            友情=dict["友情"],
            尊敬=dict["尊敬"],
            信頼=dict["信頼"],
            感謝=dict["感謝"],
            認められること=dict["認められること"],
            ユーモアがあること=dict["ユーモアがあること"],
            面白いことを言うこと=dict["面白いことを言うこと"]
        )
    
    def __add__(self, other:"ExternalRecognitionDict"):
        return ExternalRecognitionDict(
            self.愛 + other.愛, 
            self.友情 + other.友情, 
            self.尊敬 + other.尊敬, 
            self.信頼 + other.信頼, 
            self.感謝 + other.感謝, 
            self.認められること + other.認められること, 
            self.ユーモアがあること + other.ユーモアがあること, 
            self.面白いことを言うこと + other.面白いことを言うこと
            )

class PhysicalCostDict:
    お金: int
    時間: int
    資源: int
    def __init__(self, お金:int, 時間:int, 資源:int):
        self.お金 = お金
        self.時間 = 時間
        self.資源 = 資源
    
    @classmethod
    def from_dict(cls, dict:物理的コストDict)->"PhysicalCostDict":
        return cls(
            お金=dict["お金"],
            時間=dict["時間"],
            資源=dict["資源"]
        )
    
    def __add__(self, other:"PhysicalCostDict"):
        return PhysicalCostDict(self.お金 + other.お金, self.時間 + other.時間, self.資源 + other.資源)

class ProfitVector:
    精神エネルギー: int
    肉体エネルギー: int
    色々なことへの自尊心自信評価: SelfEsteemConfidenceDict
    他者からの名誉: ExternalRecognitionDict
    物理的コスト: PhysicalCostDict
    
    def __init__(self, 精神エネルギー:int, 肉体エネルギー:int, 色々なことへの自尊心自信評価:SelfEsteemConfidenceDict, 他者からの名誉:ExternalRecognitionDict, 物理的コスト:PhysicalCostDict):
        self.精神エネルギー = 精神エネルギー
        self.肉体エネルギー = 肉体エネルギー
        self.色々なことへの自尊心自信評価 = 色々なことへの自尊心自信評価
        self.他者からの名誉 = 他者からの名誉
        self.物理的コスト = 物理的コスト
    
    @classmethod
    def from_dict(cls, dict:利益ベクトル)->"ProfitVector":
        return cls(
            精神エネルギー=dict["精神エネルギー"],
            肉体エネルギー=dict["肉体エネルギー"],
            色々なことへの自尊心自信評価=SelfEsteemConfidenceDict.from_dict(dict["色々なことへの自尊心自信評価"]),
            他者からの名誉=ExternalRecognitionDict.from_dict(dict["他者からの名誉"]),
            物理的コスト=PhysicalCostDict.from_dict(dict["物理的コスト"])
        )
    
    def __add__(self, other:"ProfitVector"):
        return ProfitVector(self.精神エネルギー + other.精神エネルギー, self.肉体エネルギー + other.肉体エネルギー, self.色々なことへの自尊心自信評価 + other.色々なことへの自尊心自信評価, self.他者からの名誉 + other.他者からの名誉, self.物理的コスト + other.物理的コスト)


    

class DestinationAndProfitVector:
    # 目標とそこから期待できる利益ベクトル
    目標:str
    期待利益ベクトル:ProfitVector
    def __init__(self,destination:str,benefit:ProfitVector):
        self.目標 = destination
        self.期待利益ベクトル = benefit
    
    @classmethod
    def from_dict(cls, dict:目標と利益ベクトル)->"DestinationAndProfitVector":
        return cls(
            destination=dict["目標"],
            benefit=ProfitVector.from_dict(dict["利益ベクトル"])
        )

class Test:
    目標:str
    期待利益ベクトル:str
    def __init__(self, 目標:str, 期待利益ベクトル:str):
        self.目標 = 目標
        self.期待利益ベクトル = 期待利益ベクトル

test_dict = {
    "目標":"test",
    "期待利益ベクトル":"test"
}

test = Test(**test_dict)


if __name__ == "__main__":
    a = 体の状態("健康", 100, "特になし")
    print(a.健康状態)