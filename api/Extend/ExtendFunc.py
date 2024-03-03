from pathlib import Path
import json
import os

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
            raise FileNotFoundError(f"'{target_folder}' フォルダが現在のファイルの先祖に見つかりませんでした。")
    
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
       

if __name__ == '__main__':
    if False:
        api_dir = ExtendFunc.findTargetDirFromParents(__file__, 'api')
        test_json_dir = api_dir / "CharSettingJson/test.json"
        test_list = ['a', 'b', 'd']
        ExtendFunc.saveListToJson(test_json_dir, test_list)
    else:
        test_json_dir = ExtendFunc.createTargetFilePathFromCommonRoot(__file__, "api/CharSettingJson/test.json")
        test_dict = {'a': 1, 'bc': 32, 'd': 3}
        ExtendFunc.saveDictToJson(test_json_dir, test_dict)

