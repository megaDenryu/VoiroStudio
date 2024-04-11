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

    @staticmethod
    def loadOpenAIAPIKey():
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/openai_api_key.json"
        #もしファイルが存在しない場合はファイルを作成
        if not path.exists():
            with open(path, mode='w') as f:
                json.dump({"openai_api_key":""}, f, indent=4)
        openai_api_key = ExtendFunc.loadJsonToDict(path)["openai_api_key"]
        print("openai_api_key:",openai_api_key)
        return openai_api_key
    
    @staticmethod
    def loadCharSettingYamlAsString()->str:
        """
        CharSetting.ymlを読み込み、その内容を文字列として返します。
        """
        yml_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/CharSetting.yml"
        with open(yml_path,encoding="UTF8") as f:
                content = f.read()
        return content
    
    @staticmethod
    def loadCoeiroinkNameToNumberJson():
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "CharSettingJson/CoeiroinkNameToNumber.json"
        coeiroink_name_to_number = ExtendFunc.loadJsonToDict(path)
        return coeiroink_name_to_number
    
    @staticmethod
    def saveCoeiroinkNameToNumberJson(coeiroink_name_to_number):
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "CharSettingJson/CoeiroinkNameToNumber.json"
        ExtendFunc.saveDictToJson(path, coeiroink_name_to_number)