from pprint import pprint
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend
import json
import yaml

class JsonAccessor:
    def __init__(self, json_path):
        pass

    @staticmethod
    def extendJsonLoad(loadString:str):
        """
        json文字列を読み込み、辞書型に変換します。できない場合は何かしらのjsonにして返します
        """
        try:
            return json.loads(loadString)
        except json.JSONDecodeError:
            new_dict = {f"{TimeExtend()}":loadString, "エラー":"json形式でないため、文章のみを返します。"}
            ExtendFunc.ExtendPrint("new_dict",new_dict)
            JsonAccessor.saveLogJson("ErrorLog.json",new_dict)
            return new_dict
    
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
    def updateAppSettingJson(setting_value:dict):
        app_setting = JsonAccessor.loadAppSetting()
        pprint(app_setting)
        ExtendFunc.deepUpdateDict(app_setting, setting_value)
        pprint(app_setting)
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
        # print("openai_api_key:",openai_api_key)
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
    def loadAppSettingYamlAsString(yml_file_name:str)->str:
        """
        CharSetting.ymlを読み込み、その内容を文字列として返します。
        """
        yml_path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson" / yml_file_name
        with open(yml_path,encoding="UTF8") as f:
                content = f.read()
        return content
    
    @staticmethod
    def loadAppSettingYamlAsReplacedDict(yml_file_name:str, replace_dict:dict)->dict:
        """
        CharSetting.ymlを読み込み、その内容を辞書として返します。
        """
        content = JsonAccessor.loadAppSettingYamlAsString(yml_file_name)
        replaced_content = ExtendFunc.replaceBulkString(content, replace_dict)
        content_dict = yaml.safe_load(replaced_content)
        return content_dict
    
    @staticmethod
    def loadCoeiroinkNameToNumberJson():
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "CharSettingJson/CoeiroinkNameToNumber.json"
        coeiroink_name_to_number = ExtendFunc.loadJsonToDict(path)
        return coeiroink_name_to_number
    
    @staticmethod
    def saveCoeiroinkNameToNumberJson(coeiroink_name_to_number):
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "CharSettingJson/CoeiroinkNameToNumber.json"
        ExtendFunc.saveDictToJson(path, coeiroink_name_to_number)

    @staticmethod
    def loadGPTBehaviorYaml(chara_name:str = "一般"):
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "AppSettingJson/GPTBehavior.yml"
        with open(path,encoding="UTF8") as f:
            content = f.read()
        dict = yaml.safe_load(content)
        return dict[chara_name]
    
    @staticmethod
    def saveLogJson(file_name, input_dict):
        # 拡張子がついてるかチェックし、なければつける
        if not file_name.endswith(".json"):
            file_name += ".json"
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "LogJson" / file_name
        ExtendFunc.saveDictToJson(path, input_dict)

    @staticmethod
    def insertLogJsonToDict(file_name, input_dict):
        if  isinstance(input_dict, str):
            try:
                input_dict = json.loads(input_dict)
            except json.JSONDecodeError:
                input_dict = {"文章":input_dict, "エラー":"json形式でないため、文章のみ保存しました。"}
        now_time = TimeExtend()
        save_dict = {
            f"{now_time.date}":input_dict
        }
        pprint(save_dict)
        # 拡張子がついてるかチェックし、なければつける
        if not file_name.endswith(".json"):
            file_name += ".json"
        path = ExtendFunc.getTargetDirFromParents(__file__, "api") / "LogJson" / file_name
        dict = ExtendFunc.loadJsonToDict(path)
        dict.update(save_dict)
        pprint(dict)
        ExtendFunc.saveDictToJson(path, dict)

if __name__ == "__main__":
    pudate = {}
    pudate["ニコ生コメントレシーバー設定"] = {}
    pudate["ニコ生コメントレシーバー設定"]["生放送URL"] = "test"
    JsonAccessor.updateAppSettingJson(pudate)