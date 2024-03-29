from api.Extend.ExtendFunc import ExtendFunc
import json

class JsonAccessor:
    def __init__(self, json_path):
        pass
    
    @staticmethod
    def loadAppSetting():
        # VoiroStudioReleaseVer\api\web\app_setting.jsonを取得
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/app_setting.json"
        app_setting = ExtendFunc.loadJsonToDict(path)
        return app_setting
    
    @staticmethod
    def saveAppSetting(app_setting):
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/app_setting.json"
        ExtendFunc.saveDictToJson(path, app_setting)
    
    @staticmethod
    def saveEndKeyWordsToJson(end_keywords):
        app_setting = JsonAccessor.loadAppSetting()
        app_setting["ニコ生コメントレシーバー設定"]["コメント受信停止キーワード"] = end_keywords
        JsonAccessor.saveAppSetting(app_setting)

    @staticmethod
    def loadNikonamaUserIdToCharaNameJson():
        try:
            path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/user_data.json"
            user_data = ExtendFunc.loadJsonToDict(path)
        except FileNotFoundError:
            user_data = {}
        return user_data
    
    @staticmethod
    def saveNikonamaUserIdToCharaNameJson(user_data):
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/user_data.json"
        ExtendFunc.saveDictToJson(path, user_data)