
from api.gptAI.Human import Human
import json


class NiconamaUserLinkVoiceroidModule:
    

    def __init__(self):
        self.user_data = self.loadNikonamaUserIdToCharaNameJson()
    
    def loadNikonamaUserIdToCharaNameJson(self):
        try:
            with open('user_data.json', 'r') as f:
                user_data = json.load(f)
        except FileNotFoundError:
            user_data = {}
        return user_data
    
    def getCharaNameByNikonamaUser(self,NikonamaUserId):
        """
        ユーザーIDからキャラ名を取得する
        """
        if NikonamaUserId in self.user_data:
            return self.user_data[NikonamaUserId]
        else:
            return "キャラ名は登録されていませんでした"
    
    
    def registerNikonamaUserIdToCharaName(self,comment,NikonamaUserId):
        chara_name = self.getCharaNameFromComment(comment)
        if chara_name != "名前が無効です":
            self.saveNikonamaUserIdToCharaName(NikonamaUserId, chara_name)
            self.user_data = self.loadNikonamaUserIdToCharaNameJson()
        

    
    def getCharaNameFromComment(self,comment):
        """
        コメントから@の後ろのキャラ名を取得する
        """
        if "@" in comment:
            name = Human.checkCommentNameInNameList("@",comment)
        elif "＠" in comment:
            name = Human.checkCommentNameInNameList("＠",comment)
        else:
            return "名前が無効です"

        if name != "名前が無効です":
            chara_name = Human.setCharName(name)
            return chara_name
        
        return "名前が無効です"
             
    
    
    def saveNikonamaUserIdToCharaName(self,NikonamaUserId, chara_name):
        """
        ユーザーIDとキャラ名を紐づけてjsonに保存する
        """
        # 既存のデータを読み込む
        try:
            with open('user_data.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}

        # ユーザーIDとキャラ名を紐づける
        data[NikonamaUserId] = chara_name

        # データをjsonに保存する
        with open('user_data.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)