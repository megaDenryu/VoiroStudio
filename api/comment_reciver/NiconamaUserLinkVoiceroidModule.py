from ..gptAI.Human import Human
from api.DataStore.JsonAccessor import JsonAccessor
import json


class NiconamaUserLinkVoiceroidModule:
    

    def __init__(self):
        self.user_data = self.loadNikonamaUserIdToCharaNameJson()
    
    def loadNikonamaUserIdToCharaNameJson(self):
        user_data = JsonAccessor.loadNikonamaUserIdToCharaNameJson()
        return user_data
    
    def getCharaNameByNikonamaUser(self,NikonamaUserId):
        """
        ユーザーIDからキャラ名を取得する
        """
        NikonamaUserId = str(NikonamaUserId)
        if NikonamaUserId in self.user_data:
            return self.user_data[NikonamaUserId].replace("*","")
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
        data = self.loadNikonamaUserIdToCharaNameJson()
        NikonamaUserId = str(NikonamaUserId)
        if NikonamaUserId in data and "*" in data[NikonamaUserId]:
            print("このユーザーはキャラを変更できません")
            return

        # ユーザーIDとキャラ名を紐づける
        data[NikonamaUserId] = chara_name

        # データをjsonに保存する
        JsonAccessor.saveNikonamaUserIdToCharaNameJson(data)