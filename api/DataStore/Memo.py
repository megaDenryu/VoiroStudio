import sys,os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend

class Memo:
    def __init__(self):
        self.memo_folder = "memo"
        self.createMemoFolder()
        pass

    def insertSentenceToMarkDown(self,file_name:str ,sentence:str):
        file_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / self.memo_folder / file_name
        # ファイルが存在しない場合は新規作成
        content = self.loadMarkDown(file_name)
        #改行して追記
        content += "\n" + sentence
        # ファイルを保存
        with open(file_path, mode="w", encoding="utf-8") as f:
            f.write(content)
        

    def loadMarkDown(self, file_name:str):
        file_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / self.memo_folder / file_name
        # ファイルが存在しない場合は作成
        if not file_path.exists():
            with open(file_path, mode='w') as f:
                f.write("")
            return ""
        # ファイルをロードし変数に格納
        with open(file_path, mode="r", encoding="utf-8") as f:
            content = f.read()
            #ファイルが空の場合は空文字を返す
        if content == "":
            return ""
        return content
    
    def createMemoFolder(self):
        file_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / self.memo_folder
        os.makedirs(file_path, exist_ok=True)
    
    def createTodayMemo(self):
        today = TimeExtend.nowDate()
        file_name = today + ".md"
        first_sentence = f"# {today}の日記"
        self.insertSentenceToMarkDown(file_name,first_sentence)

    def insertTodayMemo(self,sentence:str):
        today = TimeExtend.nowDate()
        file_name = today + ".md"
        file_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / self.memo_folder / file_name
        # ファイルが存在しない場合は新規作成
        if not file_path.exists():
            self.createTodayMemo()
        self.insertSentenceToMarkDown(file_name,sentence)
    

    
if __name__ == "__main__":
    memo = Memo()
    memo.insertTodayMemo("test")

