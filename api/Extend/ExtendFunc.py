from dataclasses import dataclass
from pathlib import Path
import json
import os
import random
import re
import typing
import Levenshtein
from pprint import pprint
from typing import TypeVar, TypedDict, get_type_hints, Dict, Any, Literal, get_origin
import sys
import unicodedata
from googletrans import translate
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendSet import Interval
T = TypeVar('T', bound=Dict)

class ExtendFunc:
    
    @staticmethod
    def ExtendPrint(*args, **kwargs):
        """
        拡張プリント関数
        """
        # 呼び出し箇所のファイルパスと行数を取得
        caller_frame = sys._getframe(1)
        caller_file = caller_frame.f_code.co_filename
        caller_line = caller_frame.f_lineno
        print(f"{caller_file}:{caller_line}")
        # dict型ならpprintで出力
        for arg in args:
            if isinstance(arg, dict):
                pprint(arg, **kwargs ,indent=4)
            else:
                print(arg)



    @staticmethod
    def deepUpdateDict(target: dict, update: dict) -> dict:
        """
        辞書を再帰的に更新します。

        Parameters:
        target (dict): 更新対象の辞書
        update (dict): 更新内容

        Returns:
        dict: 更新後の辞書
        """
        for key, value in update.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                ExtendFunc.deepUpdateDict(target[key], value)
            else:
                target[key] = value
        return target

    @staticmethod
    def getTargetDirFromParents(current_file: str, target_folder: str) -> Path:
        """
        現在のファイルから親ディレクトリを遡り、指定したフォルダ名を探します。

        Parameters:
        current_file (str): 現在のファイルのパス
        target_folder (str): 検索対象のフォルダ名

        Returns:
        Path: 対象フォルダへのパス
        """
        current_path = Path(current_file).resolve()
        while current_path.name != target_folder and current_path != current_path.parent:
            current_path = current_path.parent

        if current_path.name == target_folder:
            return current_path
        else:
            raise FileNotFoundError(f"{current_path}から{target_folder} フォルダが現在のファイルの先祖に見つかりませんでした。")
    
    @staticmethod
    def getCommnonAncestorPath(path1: str, path2: str) -> Path:
        """
        2つのパスの共通の祖先を取得します。

        Parameters:
        path1 (str): パス1(絶対パス)
        path2 (str): パス2(絶対パス)

        Returns:
        Path: 共通の祖先
        """
        #path1をPathオブジェクトに変換できるか確認
        if not Path(path1).is_absolute():
            raise ValueError(f"path1は絶対パスである必要があります。")
        
        #path2をPathオブジェクトに変換できるか確認
        if not Path(path2).is_absolute():
            raise ValueError(f"path2は絶対パスである必要があります。")


        #path1とpath2の共通の最大文字列を取得
        common_path = Path(os.path.commonpath([path1, path2]))
        return common_path
    
    @staticmethod
    def createTargetFilePathFromCommonRoot(current_file_path: str, target_file_relative_path_from_common_root: str) -> Path:
        """
        現在のファイルから親ディレクトリを遡り、指定したフォルダ名を探し、そのフォルダ内にある指定したファイルへのパスを取得します。

        Parameters:
        current_file (str): 現在のファイルのパス
        common_root_path (str): 探したいファイルと現在のファイルの共通の祖先のパス. 例: "api/CharSettingJson/test.json"であれば"api"がcurrent_file_pathとの共通の祖先となる
        target_file_relative_path_from_common_parent (str): 共通の祖先からの探したいファイルの相対パス

        Returns:
        Path: 対象ファイルへのパス
        """
        common_root_path: str = target_file_relative_path_from_common_root.split('/')[0]
        target_dir = ExtendFunc.getTargetDirFromParents(current_file_path, common_root_path).parent
        return target_dir / target_file_relative_path_from_common_root
    
    @staticmethod
    def saveListToJson(file_path: Path, content: list):
        """
        ファイルを保存します。

        Parameters:
        file_path (Path): 保存先のjsonファイルパス
        content (list): 保存する内容
        """
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
    
    @staticmethod
    def saveDictToJson(file_path: Path, content: dict):
        """
        ファイルを保存します。

        Parameters:
        file_path (Path): 保存先のjsonファイルパス
        content (dict): 保存する内容
        """
        with open(file_path, 'w', encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)

    @staticmethod
    def loadJsonToList(file_path: Path) -> list:
        """
        jsonファイルを読み込みます。

        Parameters:
        file_path (Path): 読み込むjsonファイルパス

        Returns:
        list: 読み込んだ内容
        """
        print("file_path",file_path)
        ret_list = []
        with open(file_path, 'r', encoding="utf-8") as f:
            ret_list = json.load(f)
        if not isinstance(ret_list, list):
            raise ValueError(f"{file_path} はリスト形式ではありません。")
        return ret_list
    
    @staticmethod
    def loadJsonToDict(file_path: Path) -> dict:
        """
        jsonファイルを読み込みます。

        Parameters:
        file_path (Path): 読み込むjsonファイルパス

        Returns:
        dict: 読み込んだ内容
        """
        ret_dict = {}
        with open(file_path, 'r', encoding="utf-8") as f:
            ret_dict = json.load(f)
        if not isinstance(ret_dict, dict):
            raise ValueError(f"{file_path} は辞書形式ではありません。")
        return ret_dict
    
    """
    json文字列とそうでない文字列が混在した文字列からjson文字列を抽出して辞書にして返します。
    """
    @staticmethod
    def extractjson(input_str):
        # JSON文字列を抽出する正規表現パターン
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, input_str, re.DOTALL)
        
        json_dicts = []
        for match in matches:
            try:
                # JSON文字列をPythonの辞書に変換
                json_dict = json.loads(match)
                json_dicts.append(json_dict)
            except json.JSONDecodeError:
                continue
        
        return json_dicts

    @staticmethod
    def closestBoolean(target:str, str_list: list) -> str:
        """
        与えられた文字列リストの中から、最も近い文字列を返します。

        Parameters:
        target (str): 比較対象の文字列
        str_list (list): 比較対象の文字列リスト

        Returns:
        str: 最も近い文字列
        """
        return min(str_list, key=lambda x: Levenshtein.distance(target, x))
    
    
    @staticmethod
    def correctDictToGeneric(result: Dict[str, Any], typed_dict_class):
        """
        resultが指定したTypedDictの型になるように矯正する
        """
        # if typed_dict_class != TypedDict:
        #     raise ValueError("TypedDict型以外はサポートしていません。")
        corrected_data = {}
        dict = get_type_hints(typed_dict_class)
        keys = list(dict.keys())
        for key in keys:
            if key in result:
                if dict[key] == str:
                    corrected_data[key] = str(result[key])
                elif get_origin(dict[key]) is Literal:
                    if result[key] in dict[key].__args__:
                        corrected_data[key] = result[key]
                    else:
                        corrected_data[key] = dict[key].__args__[0]
            else:
                if dict[key] == str:
                    corrected_data[key] = ""
                elif get_origin(dict[key]) is Literal:
                    corrected_data[key] = dict[key].__args__[0]
        
        ret = typed_dict_class(**corrected_data)
        return ret
    
    @staticmethod
    def correctDictToTypeDict(result: Dict[str, Any], TypeDict:dict):
        """
        resultが指定したTypeDictの型になるように矯正する
        """
        corrected_data = {}
        keys = list(TypeDict.keys())
        print("keys",keys)
        for key in keys:
            if key in result:                
                def correctData(data_want_convert,target_type):
                    """
                    data_want_convertをtarget_typeに変換する
                    data_want_convert: result[key]
                    target_type: TypeDict[key]
                    """
                    type_converted_data = None
                    if target_type == str:
                        type_converted_data = str(data_want_convert)
                    elif isinstance(target_type, list) == True:
                        if data_want_convert in target_type:
                            type_converted_data = data_want_convert
                        else:
                            type_converted_data = target_type[0]
                    elif type(target_type) == list[list[str]]:
                        for type_dict in target_type:
                            if data_want_convert in type_dict:
                                type_converted_data = data_want_convert
                            else:
                                type_converted_data = type_dict[0]
                    elif isinstance(target_type, Interval):
                        # 結果をfloatに変換
                        data_want_convert = float(data_want_convert)
                        # 変換できたかチェックし、できなかった場合はstartに変換
                        if data_want_convert == float(data_want_convert):
                            if data_want_convert in target_type:
                                type_converted_data = data_want_convert
                            else:
                                type_converted_data = target_type.start
                    elif isinstance(target_type, dict) == True:
                        dict_type = target_type
                        key_type = list(dict_type.keys())[0]
                        value_type = dict_type[key_type]
                        type_converted_data = {}
                        for result_key,result_val in data_want_convert.items():
                            corrected_result_key = correctData(result_key, key_type)
                            corrected_result_val = correctData(result_val, value_type)
                            type_converted_data[corrected_result_key] = corrected_result_val
                    
                    else:
                        print("key",type(target_type))

                    return type_converted_data

                print("key",key)
                corrected_data[key] = correctData(result[key], TypeDict[key])

            else:
                print("key",key, "がresultに存在しません")
                if TypeDict[key] == str:
                    corrected_data[key] = ""
                elif TypeDict[key] is Literal:
                    corrected_data[key] = TypeDict[key].__args__[0]
                elif type(TypeDict[key]) == list[str]:
                    corrected_data[key] = TypeDict[key][0]
                elif type(TypeDict[key]) == list[list[str]]:
                    corrected_data[key] = TypeDict[key][0][0]
                elif isinstance(TypeDict[key], Interval):
                    corrected_data[key] = TypeDict[key].start
        # ExtendFunc.ExtendPrint("corrected_data",corrected_data)
        return corrected_data
    
    @staticmethod
    def correctDictToJsonSchemaTypeDictRecursive(result: Dict[str, Any], TypeDict:dict)->dict:
        TypeDict = {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "default": ""},
                            "description": {"type": "string", "default": ""},
                            "dependencies": {"type": "array", "items": {"type": "string"}, "default": []},
                            "task_type": {"type": "Enum", "enum": ["task", "subtask"], "default": "task"},
                            "time": {"type": "Interval", "start": 0, "end": 100, "default": 0}
                        },
                        "required": ["id", "description", "dependencies"]
                    }
                }
            },
            "default": {}
        }

        result = {
            "tasks": [
                {
                "id": "task1",
                "description": "タスク1の説明",
                "dependencies": []
                },
                {
                "id": "task2",
                "description": "タスク2の説明",
                "dependencies": "task1"
                },
                {
                "id": "task3",
                "description": "タスク3の説明",
                "dependencies": ["task1"]
                },
                {
                "id": "task4",
                "description": "タスク4の説明",
                "dependencies": ["task2", "task3"]
                }
            ]
        }

        
        def correctData(data_want_convert,TypeDict):
            ret = {}
            target_type = TypeDict["type"]
            if data_want_convert is None:
                return TypeDict["default"]

            if target_type == "object":
                if isinstance(data_want_convert, dict):
                    for propertie in TypeDict["properties"].keys():
                        if propertie in data_want_convert:
                            ret[propertie] = correctData(data_want_convert[propertie], TypeDict["properties"][propertie])
                        else:
                            ret[propertie] = TypeDict["properties"][propertie]["default"]
                else:
                    ret = TypeDict["default"]
            elif target_type == "array":
                ret = []
                if isinstance(data_want_convert, list):
                    for item in data_want_convert:
                        ret.append(correctData(item, TypeDict["items"]))
                else:
                    ret = TypeDict["default"]
            elif target_type == "string":
                try:
                    ret = str(data_want_convert)
                except:
                    ret = TypeDict["default"]
            elif target_type == "int":
                try:
                    ret = int(data_want_convert)
                except:
                    ret = TypeDict["default"]
            elif target_type == "float":
                try:
                    ret = float(data_want_convert)
                except:
                    ret = TypeDict["default"]
            elif target_type == "Enum":
                if data_want_convert in TypeDict["enum"]:
                    ret = data_want_convert
                else:
                    ret = TypeDict["default"]
            elif target_type == "Interval":
                if isinstance(data_want_convert, int) or isinstance(data_want_convert, float):
                    I = Interval("[", TypeDict["start"], data_want_convert, "]")
                    if I.__contains__(data_want_convert):
                        ret = data_want_convert
                    else:
                        ret = TypeDict["default"]
                else:
                    ret = TypeDict["default"]
            return ret
        corrected_data = {}
        corrected_data = correctData(result, TypeDict)
        return corrected_data
        
            
            
            
        

    
    @staticmethod
    def replaceBulkString(target: str, replace_dict: Dict[str, str]) -> str:
        """
        文字列中の指定した文字列を一括で置換します。

        Parameters:
        target (str): 置換対象の文字列
        replace_dict (Dict[str, str]): 置換する文字列の辞書

        Returns:
        str: 置換後の文字列
        """
        try:
            if replace_dict is None:
                return target
            for key, value in replace_dict.items():
                target = target.replace(key, value)
            return target
        except Exception as e:
            print("target",target)
            print("replace_dict",replace_dict)
            raise e
    
    @staticmethod
    def replaceBulkStringRecursiveCollection(target: Any, replace_dict: Dict[str, str]) -> Any:
        """
        文字列中の指定した文字列を一括で置換します。

        Parameters:
        target (Any): 置換対象の文字列
        replace_dict (Dict[str, str]): 置換する文字列の辞書

        Returns:
        Any: 置換後の文字列
        """
        if isinstance(target, str):
            return ExtendFunc.replaceBulkString(target, replace_dict)
        elif isinstance(target, list):
            return [ExtendFunc.replaceBulkStringRecursiveCollection(item, replace_dict) for item in target]
        elif isinstance(target, dict):
            return {ExtendFunc.replaceBulkStringRecursiveCollection(key,replace_dict) : ExtendFunc.replaceBulkStringRecursiveCollection(value, replace_dict) for key, value in target.items()}
        else:
            return target
    
    @staticmethod
    def dictToStr(dict: dict) -> str:
        """
        辞書のキーと値を文字列に変換します。
        返還後の形式例
        
        """
        strnized_value = ""
        for key, value in dict.items():
            strnized_value += f"{key}:{value}\n"
        return strnized_value
    
import datetime
class TimeExtend:
    def __init__(self,date_string = "now") -> None:
        if date_string == "now":
            self.date = datetime.datetime.now()
        else:
            date_parts = date_string.split(".")
            date = datetime.datetime.strptime(date_parts[0], '%Y-%m-%d %H:%M:%S')
            if len(date_parts) > 1:
                microsecond = int(date_parts[1]) * 1000
                self.date = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute, date.second, microsecond)
            else:
                self.date = date
    def __str__(self) -> str:
        return str(self.date)
    def __lt__(self, other: "TimeExtend"):
        return self.toSecond() < other.toSecond()
    def __le__(self, other: "TimeExtend"):
        return self.toSecond() <= other.toSecond()
    def __gt__(self, other: "TimeExtend"):
        return self.toSecond() > other.toSecond()
    def __ge__(self, other: "TimeExtend"):
        return self.toSecond() >= other.toSecond()
    def __eq__(self, o: "TimeExtend") -> bool:
        return self.date == o.date
    def toSecond(self) -> float:
        """
        日付と時刻を秒数に変換します。
        """
        return self.date.year * 31536000 + self.date.month * 2592000 + self.date.day * 86400 + self.date.hour * 3600 + self.date.minute * 60 + self.date.second + self.date.microsecond / 1000000
    @staticmethod
    def nowSecond() -> int:
        """
        現在の秒数を取得します。

        Returns:
        int: 現在の秒数
        """
        return datetime.datetime.now().second
    
    @staticmethod
    def nowMinute() -> int:
        """
        現在の分数を取得します。

        Returns:
        int: 現在の分数
        """
        return datetime.datetime.now().minute
    
    @staticmethod
    def nowHour() -> int:
        """
        現在の時間を取得します。

        Returns:
        int: 現在の時間
        """
        return datetime.datetime.now().hour
    
    @staticmethod
    def nowTimeToSecond() -> int:
        """
        現在の時刻を秒数に変換します。
        例: 1時30分20秒の場合、1*3600 + 30*60 + 20 = 5420

        Returns:
        int: 現在の時刻の秒数
        """
        return TimeExtend.nowHour() * 3600 + TimeExtend.nowMinute() * 60 + TimeExtend.nowSecond()
    
    @staticmethod
    def nowDateTime() -> str:
        """
        現在の日付と時刻を取得します。

        Returns:
        str: 現在の時刻(例：2024-05-04 19:18:17.799629)
        """
        return str(datetime.datetime.now())
    @staticmethod
    def nowDateTimeDict() -> dict:
        """
        現在の日付と時刻を取得します。

        Returns:
        dict: 現在の時刻
        """
        return {
            "year": datetime.datetime.now().year,
            "month": datetime.datetime.now().month,
            "day": datetime.datetime.now().day,
            "hour": datetime.datetime.now().hour,
            "minute": datetime.datetime.now().minute,
            "second": datetime.datetime.now().second
        }
    
    @staticmethod
    def nowDate() -> str:
        """
        現在の日付を取得します。

        Returns:
        str: 現在の日付(例：2024-05-04)
        """
        return str(datetime.date.today())
    
    @staticmethod
    def DateTimeDictToSecond(dateTimeDict: dict) -> int:
        """
        日付と時刻の辞書を秒数に変換します。

        Parameters:
        dateTimeDict (dict): 日付と時刻の辞書

        Returns:
        int: 秒数
        """
        return dateTimeDict["year"] * 31536000 + dateTimeDict["month"] * 2592000 + dateTimeDict["day"] * 86400 + dateTimeDict["hour"] * 3600 + dateTimeDict["minute"] * 60 + dateTimeDict["second"]
    
    @staticmethod
    def nowDateTimeToSecond() -> int:
        """
        現在の日付と時刻を秒数に変換します。

        Returns:
        int: 秒数
        """
        return TimeExtend.DateTimeDictToSecond(TimeExtend.nowDateTimeDict())
    
    @staticmethod
    def diffTime(time:"TimeExtend")->float:
        """
        現在の時刻と指定した時刻の差を取得します。

        Parameters:
        time (int): 比較対象の時刻

        Returns:
        int: 現在の時刻と指定した時刻の差
        """
        now = TimeExtend()
        return now.toSecond() - time.toSecond()



class TextConverter:
    roman_japanese_categories = ['Lu', 'Ll', 'Lt', 'Lm', 'Lo','Nd']
    hira_kata_kanji_number_categories = ['Hiragana', 'Katakana', 'Han','Nd']
    hankaku_special_char = ["%", "!", "?", "(", ")", "[", "]", "{", "}", "<", ">", "=", "+", "-", "*", "/", "|", "&", "^", "~", "#", "@", ":", ";", ",", ".", "_", " ", "　"]
    zenkaku_special_char = ["％", "！", "？", "（", "）", "［", "］", "｛", "｝", "＜", "＞", "＝", "＋", "－", "＊", "／", "｜", "＆", "＾", "～", "＃", "＠", "：", "；", "、", "。", "＿", "　"]
    special_char_yomi = {
    "%": "ぱーせんと",
    "!": "びっくり",
    "?": "はてな",
    "(": "かっこ",
    ")": "かっことじ",
    "[": "だいかっこ",
    "]": "だいかっことじ",
    "{": "ちゅうかっこ",
    "}": "ちゅうかっことじ",
    "<": "しょうなり",
    ">": "だいなり",
    "=": "いこーる",
    "+": "ぷらす",
    "-": "まいなす",
    "*": "かける",
    "/": "わる",
    "|": "ばー",
    "&": "あんど",
    "^": "はっと",
    "~": "ちるだ",
    "#": "しゃーぷ",
    "@": "あっと",
    ":": "ころん",
    ";": "せみころん",
    ",": "てん",
    ".": "ぴりおど",
    "_": "あんだーばー",
    " ": " ",   # 半角スペース
    "　": "　", # 全角スペース
    "％": "ぱーせんと",
    "！": "びっくり",
    "？": "はてな",
    "（": "かっこ",
    "）": "かっことじ",
    "［": "だいかっこ",
    "］": "だいかっことじ",
    "｛": "ちゅうかっこ",
    "｝": "ちゅうかっことじ",
    "＜": "しょうなり",
    "＞": "だいなり",
    "＝": "いこーる",
    "＋": "ぷらす",
    "－": "まいなす",
    "＊": "かける",
    "／": "わる",
    "｜": "ばー",
    "＆": "あんど",
    "＾": "はっと",
    "～": "ちるだ",
    "＃": "しゃーぷ",
    "＠": "あっと",
    "：": "ころん",
    "；": "せみころん",
    "、": "てん",
    "。": "ぴりおど",
    "＿": "あんだーばー"
}

    @staticmethod
    def checkCharacterDetailType(char):
        if 'ぁ' <= char <= 'ん' or char == "ー":
            return "ひらがな"
        elif 'ァ' <= char <= 'ン':
            return "全角カタカナ"
        elif 'ｦ' <= char <= 'ﾟ':
            return "半角カタカナ"
        elif 'ａ' <= char <= 'ｚ' or 'Ａ' <= char <= 'Ｚ':
            return "全角英字"
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            return "半角英字"
        elif '０' <= char <= '９':
            return "全角数字"
        elif '0' <= char <= '9':
            return "半角数字"
        elif '一' <= char <= '龥':
            return "漢字"
        elif char in TextConverter.hankaku_special_char or char in TextConverter.zenkaku_special_char:
            return "特別記号"
        elif unicodedata.category(char).startswith('P'):
            return "記号"
        elif unicodedata.category(char).startswith('So'):
            return "絵文字"
        else:
            return "その他"
    
    @staticmethod
    def aggregatingType(detail_type:Literal["ひらがな","全角カタカナ","半角カタカナ","全角英字","半角英字","全角数字","半角数字","漢字","特別記号","記号","絵文字","その他"]):
        if detail_type in ["ひらがな","全角カタカナ","半角カタカナ","全角数字","半角数字","漢字"]:
            return "日本語"
        elif detail_type in ["全角英字","半角英字"]:
            return "英字"
        elif detail_type in ["特別記号"]:
            return "特別記号"
        elif detail_type in ["記号","絵文字"]:
            return "Unicode記号"
        elif detail_type in ["その他"]:
            return "その他"
    @staticmethod
    def checkCharacterType(chara:str):
        return TextConverter.aggregatingType(TextConverter.checkCharacterDetailType(chara))
            

    @staticmethod
    def convertReadableJapanaeseSentense(text):
        """
        ルビを振ります。
        """
        # 構造体のクラスを作成
        @dataclass
        class WordWithType:
            word: str
            word_type: Literal['日本語', '英字', '特別記号', 'Unicode記号', 'その他'] | None
        

        previous_char_type = None
        char_type_continuous = False
        split_text:list[WordWithType] = []
        contituos_word:list[str] = []
        char_type = None
        for char in text:
            # 文字の種類を取得
            char_type = TextConverter.checkCharacterType(char)
            if char_type == previous_char_type or char_type == "特別記号":
                if char_type != "特別記号":
                    previous_char_type = char_type
                contituos_word.append(char)
            else:
                # contituos_wordを連結した文字列にしてsplit_textに追加
                word = "".join(contituos_word)
                word_with_type = WordWithType(word, previous_char_type)
                split_text.append(word_with_type)
                # contituos_wordを初期化
                contituos_word = [char]
                previous_char_type = char_type
        else:
            if char_type == None:
                char_type = "日本語"
                contituos_word = ["あ"]
            word = "".join(contituos_word)
            word_with_type = WordWithType(word, char_type)
            split_text.append(word_with_type)
        ret_text_list:list[str] = []
        pprint(split_text)
        for element in split_text:
            if element.word_type == "英字":
                # 英字を翻訳
                ret_text_list.append(TextConverter.TranslateEngToJapanese(element.word))
            elif element.word_type == "日本語" or element.word in ["ー","々","〆","〤","〥","〦","〧","〨","〩","ヶ"]:
                ret_text_list.append(element.word)
            elif element.word_type == "特別記号":
                # 記号を読み仮名に変換
                ret_text_list.append(TextConverter.BulkConvertSpecialCharToYomi(element.word))
            elif element.word_type == "Unicode記号":
                ret_text_list.append(TextConverter.convertUnicodeOnlyTextToText(element.word))
            elif element.word_type == "その他":
                ret_text_list.append(TextConverter.TranslateAutoToJapanese(element.word))
                ret_text_list.append("まる。")
        return "".join(ret_text_list)
    
    @staticmethod
    def BulkConvertSpecialCharToYomi(text:str):
        """
        文字列中の特別記号を読み仮名に変換します。

        Parameters:
        text (str): 変換対象の文字列

        Returns:
        str: 変換後の文字列
        """
        for char in text:
            if char in TextConverter.hankaku_special_char or char in TextConverter.zenkaku_special_char:
                text = text.replace(char, TextConverter.special_char_yomi[char])
        return text

    @staticmethod
    def is_roman_or_japanese(character):
        try:
            # Unicodeカテゴリを取得
            print(character)
            category = unicodedata.category(character)
            print(category)
            # ローマ字または日本語のカテゴリに含まれているかチェック
            return category in TextConverter.roman_japanese_categories
        except ValueError:
            # Unicode名がない文字は無視（削除）
            return False
        
    @staticmethod
    def isNumber(character):
        try:
            # Unicodeカテゴリを取得
            category = unicodedata.category(character)
            # ローマ字または日本語のカテゴリに含まれているかチェック
            return category in ['Nd']
        except ValueError:
            # Unicode名がない文字は無視（削除）
            return False
        
    
    
    @staticmethod
    def convert_text(text):
        new_text = ""
        for char in text:
            if TextConverter.is_roman_or_japanese(char):
                new_text += char
                print(new_text)
            else:
                try:
                    # Unicodeの意味の文字列で変換
                    new_text += unicodedata.name(char)
                    print(new_text)
                except ValueError:
                    # ライブラリにない文字は削除
                    new_text += "w"
        return new_text
    
    @staticmethod
    def convertUnicodeOnlyTextToText(text):
        """
        ,,や？や絵文字だけの文字列を変換します。日本語やローマ字などが入っていればそのまま返します。
        """
        new_text = ""
        for char in text:
            if TextConverter.is_roman_or_japanese(char):
                ExtendFunc.ExtendPrint(new_text)
                return text
            else:
                try:
                    # Unicodeの意味の文字列で変換
                    new_text += (unicodedata.name(char))
                    ExtendFunc.ExtendPrint(new_text)
                except ValueError:
                    # ライブラリにない文字は削除
                    new_text += "w"
                    ExtendFunc.ExtendPrint(new_text)
        translate_text = TextConverter.TranslateEngToJapanese(new_text)
        ret = TextConverter.convertUnicodeOnlyTextToText(translate_text)
        return ret
    
    @staticmethod
    def TranslateEngToJapanese(word_to_translate):
        # 英単語を日本語に翻訳
        translated_word = translate(word_to_translate, to_language='ja', from_language='en')
        return translated_word
    
    @staticmethod
    def TranslateAutoToJapanese(word_to_translate):
        translated_word = translate(word_to_translate, to_language='ja')
        return translated_word # 出力: 例
    @staticmethod
    def translateEngWithJapanese(word_to_translate):
        """
        英語と日本語が混在した文章を翻訳します。
        まず文章を日本語が連続してる部分と英語が連続してる部分に分けた配列を作成し、
        英語部分を翻訳し、日本語部分と翻訳した英語部分を結合して返します。
        """
        
        
        # 翻訳後の文章を格納するリスト
        translated_words = []
        # 英語と日本語が連続している部分を格納するリスト
        continuous_words = []
        # 英語と日本語が連続している部分を判定するフラグ
        is_continuous = False
        # 英語と日本語が連続している部分を判定するための変数
        continuous_word = ""
        # 英語と日本語が連続している部分を判定
        for char in word_to_translate:
            # 文字が英語か日本語か数字かunicodeの記号か判定
            print(char)
        
        # 英語を翻訳
       
        # 翻訳後の文章を結合

class RandomExtend:
    @staticmethod
    def random0to1():
        return random.random()
       




if __name__ == '__main__':
    if True:
        # text = "ل  تستطيع  مساعدتي  من  فضلك؟"
        text = "うおーー"
        bool = TextConverter.convertReadableJapanaeseSentense(text)
        print(bool)
        l = ["ad","ｄｗだ"]
        #リストを連結して文字列にする
        print("".join(l))

        
    if False:
        text = "translate to Japanese とか これなんか多分 英語を維持するんだよね"
        text  = TextConverter.translateEngWithJapanese(text)
        print(text)

    if False:
        """
        TextConverterのテスト
        """
        input_text = "ﾠ"
        converted_text = TextConverter.convertUnicodeOnlyTextToText(input_text)
        length = len(converted_text)
        ExtendFunc.ExtendPrint(converted_text,length)  # 出力: Hello, 世界WHITE SMILING FACE!

    if False:
        api_dir = ExtendFunc.findTargetDirFromParents(__file__, 'api')
        test_json_dir = api_dir / "CharSettingJson/test.json"
        test_list = ['a', 'b', 'd']
        ExtendFunc.saveListToJson(test_json_dir, test_list)
    elif False:
        test_json_dir = ExtendFunc.createTargetFilePathFromCommonRoot(__file__, "api/CharSettingJson/test.json")
        test_dict = {'a': 1, 'bc': 32, 'd': 3}
        ExtendFunc.saveDictToJson(test_json_dir, test_dict)
    elif False:
        print(TimeExtend.nowSecond())
    elif False:
        TypeDict = {
            f"赤ちゃんの発言": str,
            "あなたの発言も踏まえた現在の全体状況": str,
            "属性": ['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ']
            }
        
        result = {
            "赤ちゃんの発言": "babu-babu",
            "あなたの発言も踏まえた現在の全体状況": "あなたの発言も踏まえた現在の全体状況",
            "属性": "hoge",
            "huげ":"zunndamo"
        }
        
        corrected_data = ExtendFunc.correctDictToTypeDict(result, TypeDict)
        pprint(corrected_data, indent=4)
    elif False:
        time = TimeExtend("2024-05-04 19:18:17")
        time2 = TimeExtend("2024-05-04 19:18:17")
        print(time)
        print(time2.toSecond())
        print(time <= time2)
    elif False:
        TypeDict = {
            "入力成功度合い":Interval("[",0,1,"]")
        }
        result = {
            "入力成功度合い": "1.1"
        }
        corrected_data = ExtendFunc.correctDictToTypeDict(result, TypeDict)
        print(corrected_data)
    elif False:
        TypeDict = {
            "以前と今を合わせた周囲の状況の要約": str,
            "どのキャラがどのキャラに話しかけているか？または独り言か？": str,
            "他のキャラの会話ステータス": {str:['質問', '愚痴', 'ボケ', 'ツッコミ', 'ジョーク', '励まし', '慰め', '共感', '否定', '肯定', '感嘆表現', '愛情表現']},
            "ロール": ['アシスタント', 'キャラクターなりきり'],
            "あなたの属性": ['赤ちゃん', '大工', '彼女', '看護師', '嫁', '先生', '同僚', '先輩', '上司', 'ママ', 'パパ'],
            "{{gptキャラ}}のこれからの感情": ['喜', '怒', '悲', '楽', '好き', '嫌い', '疲れ', '混乱', '疑問', 'ツンツン', 'デレデレ', '否定', '肯定', '催眠'],
            "{{gptキャラ}}のこれからの会話ステータス": ['傾聴', '質問', '教える', 'ボケる', '突っ込む', '嘲笑', '感嘆表現', '愛憎表現', '続きを言う'],
            "今まで起きたことの要約": str,
            "{{gptキャラ}}の次の行動を見据えた心内セリフと思考": str
            }
        result = {
                "以前と今を合わせた周囲の状況の要約": "プレイヤーキャラが考え事をしていて独り言を言っている中、{{gptキャラ}}がボケて「ぴよぴよ」と発言。プレイヤーキャラが「びよーん」と返答した。",
                "どのキャラがどのキャラに話しかけているか？または独り言か？": "プレイヤーキャラが独り言を言っている中、{{gptキャラ}}がボケた。その後、プレイヤーキャラが{{gptキャラ}}に「びよーん」と返答。",
                "他のキャラの会話ステータス": {
                    "プレイヤーキャラ": "ボケ",
                    "{{gptキャラ}}": "はげしいボケ"
                },
                "ロール": "キャラクターなりきり",
                "あなたの属性": "年下の女友達",
                "{{gptキャラ}}のこれからの感情": "楽",
                "{{gptキャラ}}のこれからの会話ステータス": "続きを言う",
                "今まで起きたことの要約": "プレイヤーキャラが独り言を言っていたところに、{{gptキャラ}}がボケて「ぴよぴよ」と言った。それに対してプレイヤーキャラが「びよーん」と返した。",
                "{{gptキャラ}}の次の行動を見据えた心内セリフと思考": "プレイヤーキャラが楽しんでいるみたいだから、もっと楽しませるために次もボケてみよう。『ぴよぴよ』に続けてもっと可愛く楽しいことを言ってみよう。"
            }

        corrected_data = ExtendFunc.correctDictToTypeDict(result, TypeDict)
        pprint(corrected_data)
    elif False:
        dicta = {
            "赤ちゃんの発言": "babu-babu",
            "あなたの発言も踏まえた現在の全体状況": "あなたの発言も踏まえた現在の全体状況",
            "属性": "hoge",
            "huげ":"zunndamo"
        } 
        print(ExtendFunc.dictToStr(dicta))
    elif True:

        ret = ExtendFunc.correctDictToJsonSchemaTypeDictRecursive({},{})
        ExtendFunc.ExtendPrint(ret)
    
