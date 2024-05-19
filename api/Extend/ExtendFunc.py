from pathlib import Path
import json
import os
import typing
import Levenshtein
from pprint import pprint
from typing import TypeVar, TypedDict, get_type_hints, Dict, Any, Literal, get_origin
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from api.Extend.ExtendSet import Interval
T = TypeVar('T', bound=Dict)

class ExtendFunc:
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
                print("key",key)
                if TypeDict[key] == str:
                    corrected_data[key] = str(result[key])
                elif type(TypeDict[key]) == list[str]:
                    if result[key] in TypeDict[key]:
                        corrected_data[key] = result[key]
                    else:
                        corrected_data[key] = TypeDict[key][0]
                elif type(TypeDict[key]) == list[list[str]]:
                    for type_dict in TypeDict[key]:
                        if result[key] in type_dict:
                            corrected_data[key] = result[key]
                        else:
                            corrected_data[key] = type_dict[0]
                elif isinstance(TypeDict[key], Interval):
                    # 結果をfloatに変換
                    result[key] = float(result[key])
                    # 変換できたかチェックし、できなかった場合はstartに変換
                    if result[key] == float(result[key]):
                        if result[key] in TypeDict[key]:
                            corrected_data[key] = result[key]
                        else:
                            corrected_data[key] = TypeDict[key].start
                else:
                    print("key",type(TypeDict[key]))
            else:
                print("key",key)
                if TypeDict[key] == str:
                    corrected_data[key] = ""
                elif TypeDict[key] is Literal:
                    corrected_data[key] = TypeDict[key].__args__[0]
                elif type(TypeDict[key]) == list[str]:
                    corrected_data[key] = TypeDict[key][0]
                elif type(TypeDict[key]) == list[list[str]]:
                    corrected_data[key] = TypeDict[key][0][0]
                elif TypeDict[key] is Interval:
                    corrected_data[key] = TypeDict[key].start
        
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
        for key, value in replace_dict.items():
            target = target.replace(key, value)
        return target
    
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

if __name__ == '__main__':
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
            "入力成功度合い": "0.3"
        }
        corrected_data = ExtendFunc.correctDictToTypeDict(result, TypeDict)
        print(corrected_data)
    elif True:
        dict = {
            "赤ちゃんの発言": "babu-babu",
            "あなたの発言も踏まえた現在の全体状況": "あなたの発言も踏まえた現在の全体状況",
            "属性": "hoge",
            "huげ":"zunndamo"
        } 
        print(ExtendFunc.dictToStr(dict))
    
