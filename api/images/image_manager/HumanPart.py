from __future__ import annotations # annotationsを有効にする
from typing import TYPE_CHECKING
import sys
import json
from pathlib import Path
import os
import base64
from pprint import pprint
import re
from collections import OrderedDict
from api.Extend.ExtendFunc import ExtendFunc

if TYPE_CHECKING:
    from api.gptAI.Human import Human

class HumanPart:
    def __init__(self,chara_name) -> None:
        self.name = chara_name #キャラの名前。フロントネームからキャラネームに変換済みの物を入れる。
        self.emotion_list = [
            "普通",
            "嬉しい",
            "がびーん",
            "涙目",
            "怖い",
            "怒り",
            "悲しい",
            "恥ずかしい",
            "楽しい"
        ]
        self.api_dir = ExtendFunc.getTargetDirFromParents(__file__,"api")
    
    def setCharFilePath(self,name,psd_num):
        
        char_file_path = self.api_dir / "CharSettingJson" / "CharFilePath.json"
        print("char_file_path",char_file_path)
        with open(char_file_path, 'r', encoding='utf-8') as f:
            name_list = json.load(f)
        file_path = f"{name}/{name_list[name][psd_num]}"
        print("file_path",file_path)
        return file_path
    
    @staticmethod
    def writeCharFilePathToNewPSDFileName(chara_name,folder_name):
        CharFilePath_path = ExtendFunc.createTargetFilePathFromCommonRoot(__file__, "api/CharSettingJson/CharFilePath.json")
        CharFilePathDict:dict[str,list[str]] = ExtendFunc.loadJsonToDict(CharFilePath_path)
        if chara_name in CharFilePathDict:
            CharFilePathDict[chara_name].insert(0,folder_name)
        else:
            CharFilePathDict[chara_name] = [folder_name]
        ExtendFunc.saveDictToJson(CharFilePath_path,CharFilePathDict)

    def getHumanAllParts(self, human_char_name:str, psd_num = 0):
        #入力名からキャラの正式名を取得
        char_file_path = self.setCharFilePath(human_char_name,psd_num)
        #キャラの正式名からキャラの体パーツフォルダの画像のpathを取得
        path_str = f"../images/ボイロキャラ素材/{char_file_path}"
        return self.getHumanAllPartsFromPath(human_char_name,path_str)
    
    def getHumanAllPartsFromPath(self, human_char_name:str, path_str:str):
        #キャラの体パーツフォルダの画像を全て辞書形式で取得
        data_for_client = {}
        data_for_client["body_parts_iamges"],body_parts_pathes_for_gpt = self.recursive_file_check(f"{path_str}/parts")
        self.saveImageInfo(body_parts_pathes_for_gpt,path_str)
        data_for_client["init_image_info"] = self.getInitImageInfo(path_str)
        return data_for_client,body_parts_pathes_for_gpt

    def openFile(self,file_path):
        # ファイルをバイナリー形式で開く
        with open(file_path,mode="rb") as f:
            binary_data = f.read()
        # ファイル情報をjsonに文字列として入れるためにファイルのバイナリーデータをbase64エンコードする
        binary_data_b64 = base64.encodebytes(binary_data)
        return binary_data_b64.decode()
        #return file_path
    
    def openJsonFile(self,file_path):
        # jsonファイルを開いて、辞書型に変換する
        with open(file_path,encoding="UTF8") as f:
            json_data = json.load(f)
        return json_data
    
    def saveJsonFile(self,file_path,json_data):
        """
        file_pathがあれば上書き、なければ新規作成
        """
        #file_pathがない場合
        if not os.path.exists(file_path):
            #ディレクトリがなければ作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, mode="w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
        else:
            #file_pathがある場合上書きする
            with open(file_path,mode="w",encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)


    def recursive_file_check(self,path_str:str) -> tuple[dict, dict]:
        path = Path(path_str)
        file_names:list[str] = os.listdir(path)
        dict = {}
        filepath_dict = {} #gptにファイル構造を渡すために全てのパスを文字列で取得
        for file_name in file_names:
            #print(file_name)
            file_path = f"{path_str}/{file_name}"
            if os.path.isdir(file_path):
                # directoryだったら中のファイルに対して再帰的にこの関数を実行
                data,pathes = self.recursive_file_check(file_path)
                dict[file_path.split("/")[-1]] = data
                filepath_dict[file_path.split("/")[-1]] = pathes
            else:
                # fileだったら処理
                key = file_path.split("/")[-1].split(".")[0]
                if key not in dict.keys():
                    dict[key] = {}
                if file_path.endswith(".png") or file_path.endswith(".jpg"):
                    data = self.openFile(file_path)
                    pathes = "gazou"
                    dict[key]["img"] = data
                    filepath_dict[file_path.split("/")[-1]] = pathes
                elif file_path.endswith(".json"):
                    data = self.openJsonFile(file_path)
                    pathes = "json"
                    dict[key]["json"] = data
                    filepath_dict[file_path.split("/")[-1]] = pathes
                else:
                    print("pngでもjsonでもないファイルがありました。")
                    print(f"{file_path=}")
        return dict, filepath_dict
    
    def getInitImageInfo(self,path_str:str)->list[str]:
        """
        pathからキャラpsdの初期状態をインポートする
        """
        init_image_info:list[str] = []
        path_str = f"{path_str}/init_image_info.json"
        path = Path(path_str)
        #jsonファイルを開く
        try:
            with open(path_str,encoding="UTF8") as f:
                init_image_info = json.load(f)
                #jsonファイルの中身を確認
            pprint(init_image_info)
            return init_image_info
        except Exception as e:
            print(e)
            print(f"init_image_info.jsonが見つかりませんでした。path:{path}")
            return init_image_info
        
    def saveImageInfo(self,info_dict:dict,path_str:str):
        save_switch = False
        # もしinit_image_info.jsonがなかったら作成する
        if not os.path.exists(f"{path_str}/init_image_info.json"):
            save_switch = True
        if True == save_switch :
            init_dict = {}
            for key in info_dict.keys():
                part_image_dict = info_dict[key]
                #part_image_dictのキー配列の最初の要素を取得。hoge.pngやhoge.jsonのhogeの部分を取得。
                mode_human_part_manager = "HumanPartManager2"
                if mode_human_part_manager == "iHumanPartManager":
                    #iHumanPartManager用の処理
                    init_dict[key] = list(part_image_dict.keys())[0].split(".")[0]
                elif mode_human_part_manager == "HumanPartManager2":
                    #HumanPartManager2用の処理
                    init_dict[key] = self.allPartNameDict(part_image_dict)
                
                

            # そのままinfo_dictをinit_image_info.jsonに保存するとキー名に対して昇順にならないので、昇順に並び変える
            ordereddictdata = OrderedDict({k: v for k, v in sorted(info_dict.items(), key=lambda item: int(re.split('_', item[0])[0]))})
            init_ordereddictdata = OrderedDict({k: v for k, v in sorted(init_dict.items(), key=lambda item: int(re.split('_', item[0])[0]))})
            save_data = {
                "init":init_ordereddictdata,
                "all_data":ordereddictdata
            }

            with open(f"{path_str}/init_image_info.json",mode="w",encoding="utf-8") as f:
                json.dump(save_data,f,indent=4,ensure_ascii=False)
    
    def allPartNameDict(self,part_image_dict:dict):
        """
        part_image_dictのキー配列の最初の要素を取得。hoge.pngやhoge.jsonのhogeの部分を取得。
        """
        return_dict = {}
        all_part_name_list = part_image_dict.keys()
        for part_name in all_part_name_list:
            part_name = part_name.split(".")[0]
            return_dict[part_name] = "off"

        return return_dict
        
    def saveHumanImageCombination(self,combination_data,combination_name,psd_num):
        """
        init_image_info.jsonの中にcombination_nameのキーでcombination_dataを保存する
        """
        char_file_path = self.setCharFilePath(self.name,psd_num)
        path_str = f"../images/ボイロキャラ素材/{char_file_path}"
        init_image_info = self.getInitImageInfo(path_str)
        init_image_info[combination_name] = combination_data
        self.saveJsonFile(f"{path_str}/init_image_info.json",init_image_info)


#h = HumanPart()
#h.getHumanAllParts("おね")