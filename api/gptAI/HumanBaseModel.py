from enum import Enum
from typing_extensions import Literal
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
    use_tool: Literal["なし","タスク分解","タスク実行","発言"]
    tool_query: str
    dependencies: list[str]

class TaskOutput(TypedDict):
    output:str

class TaskGraphUnit:
    _previous_tasks: list["TaskGraphUnit"]
    _next_tasks: list["TaskGraphUnit"]
    _previous_resolved:dict["TaskGraphUnit",bool]= {}
    _ready:bool = False
    task:Task
    @property
    def previous_tasks(self):
        return self._previous_tasks
    @property
    def next_tasks(self):
        return self._next_tasks
    @property
    def ready(self):
        return self._ready
    def __init__(self, task:Task) -> None:
        self.task = task
        self._previous_tasks = []
        self._next_tasks = []
    def registPreviousTask(self, previous_task:"TaskGraphUnit"):
        # 重複登録を防ぐ
        if previous_task not in self._previous_tasks:
            self._previous_tasks.append(previous_task)
    def registNextTask(self, next_task:"TaskGraphUnit"):
        # 重複登録を防ぐ
        if next_task not in self._next_tasks:
            self._next_tasks.append(next_task)
    def initPreviousResolvedStatus(self):
        for previous_task in self._previous_tasks:
            self._previous_resolved[previous_task] = False
    async def notifiedPreviousTaskResolvedAndExcuteTask(self, previous_task:"TaskGraphUnit"):
        self._previous_resolved[previous_task] = True
        if all(self._previous_resolved.values()):
            self._ready = True
            self.execute()
    def notifiedPreviousTaskResolved(self, previous_task:"TaskGraphUnit"):
        self._previous_resolved[previous_task] = True
        if all(self._previous_resolved.values()):
            self._ready = True
    async def notifyProcessComplete(self,):
        self._ready = False
        self._previous_resolved = {}
        for next_task in self._next_tasks:
            await next_task.notifiedPreviousTaskResolvedAndExcuteTask(self)
    def notifyProcessCompleteForCreateStepList(self,next_step_candidate:list["TaskGraphUnit"])->list["TaskGraphUnit"]:
        self._ready = False
        self._previous_resolved = {}
        for next_task in self._next_tasks:
            next_task.notifiedPreviousTaskResolved(self)
            next_step_candidate.extend(self._next_tasks)
        return next_step_candidate
    
    def execute(self):
        if all(self._previous_resolved.values()) == False:
            return
        # タスクを実行
        
        # タスクの実行結果を返す

        # 次のタスクに通知
        self.notifyProcessComplete()


    
    
class TaskGraph:
    task_dict:dict[str, TaskGraphUnit] = {}
    step_list: list[list[TaskGraphUnit]] = []
    non_dependent_tasks: list[TaskGraphUnit] = []
    non_next_tasks: list[TaskGraphUnit] = []
    def __init__(self,task_list:list[Task]) -> None:
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
    
    async def ExcuteStepList(self):
        pass
                




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