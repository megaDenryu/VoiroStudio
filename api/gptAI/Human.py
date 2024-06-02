import sys
from pathlib import Path
import os
import json
import time
import re
from pprint import pprint

from api.Extend.ExtendFunc import ExtendFunc, TextConverter
from .gpt import ChatGPT
from .voiceroid_api import voicevox_human
from .voiceroid_api import Coeiroink

from ..images.image_manager.HumanPart import HumanPart
from starlette.websockets import WebSocket

try:
    from .voiceroid_api import cevio_human
except ImportError:
    print("cevio_human module could not be imported. Please ensure the required application is installed.")

try:
    from .voiceroid_api import AIVoiceHuman
except ImportError:
    print("AIVoiceHuman module could not be imported. Please ensure the required application is installed.")

class Human:
    def __init__(self,front_name:str ,voiceroid_dict, corresponding_websocket:WebSocket, prompt_setteing_num:str = "キャラ個別システム設定") -> None:
        """
        @param front_name: フロントで入力してウインドウに表示されてる名前
        @param voiceroid_dict: 使用してる合成音声の種類をカウントする辞書。{"cevio":0,"voicevox":0,"AIVOICE":0}。cevioやAIVOICEの起動管理に使用。
        """
        # debug用の変数
        self.voice_switch = True
        self.gpt_switch = True
        self.send_image_switch = True

        # 以下コンストラクタのメイン処理


        self.voice_mode = "wav出力"
        #フロントで入力してウインドウに表示されてる名前
        self.front_name:str = front_name
        #ボイスロイドの名前
        self.char_name = self.setCharName(front_name)
        print(f"char_name:{self.char_name}")
        if "" == self.char_name:
            #登録していないが持っている名前が入力された時の処理
            #AIVOICEから名前を取得する
            test_aivoice = AIVoiceHuman("test",0)

            # コンストラクタの処理はここで終わり
            
            return
        self.personal_id = 2
        # 体画像周りを準備する
        self.human_part = HumanPart(self.char_name)
        human_part_folder,self.body_parts_pathes_for_gpt = self.human_part.getHumanAllParts(self.char_name)
        data = {}
        data["body_parts_iamges"] = human_part_folder["body_parts_iamges"]
        data["init_image_info"] = human_part_folder["init_image_info"]
        data["front_name"] = self.front_name
        data["char_name"] = self.char_name
        self.image_data_for_client = data
        # dictを正規化する
        self.response_dict:dict = {
            self.char_name:"",
            "感情":"",
            "コード":"",
            "json返答":""
        }
        self.sentence = ""
        self.sentence_count = 0
        self.prompt_setting_num = prompt_setteing_num
        self.human_GPT:ChatGPT
        self.voice_system:str = self.start(prompt_setteing_num, voiceroid_dict)

        self.corresponding_websocket:WebSocket = corresponding_websocket

        
    
    def start(self, prompt_setteing_num:str = "キャラ個別システム設定", voiceroid_dict:dict[str,int] = {"cevio":0,"voicevox":0,"AIVOICE":0,"Coeiroink":0}):#voiceroid_dictはcevio,voicevox,AIVOICEの数をカウントする
        print(f"{self.char_name}のgpt起動開始")
        self.human_GPT = ChatGPT(self.char_name, prompt_setteing_num,self.gpt_switch, self.body_parts_pathes_for_gpt)
        print(f"{self.char_name}のgpt起動完了")
        #nameからcevioかvoicevoxかAIVOICEか判定
        if self.voice_switch:
            
            if "" != cevio_human.setCharName(self.char_name):
                tmp_cevio = cevio_human(self.char_name,voiceroid_dict["cevio"])
                print(f"{self.char_name}のcevio起動開始")
                self.human_Voice = tmp_cevio
                print(f"{self.char_name}のcevio起動完了")
                self.human_Voice.speak("起動完了")
                return "cevio"
            elif "" != voicevox_human.getCharNum(self.char_name):
                tmp_voicevox = voicevox_human(self.char_name,voiceroid_dict["voicevox"])
                print(f"{self.char_name}のvoicevox起動開始")
                self.human_Voice = tmp_voicevox
                print(f"{self.char_name}のvoicevox起動完了")
                self.human_Voice.speak("起動完了")
                return "voicevox"
            elif "" != AIVoiceHuman.setCharName(self.char_name):
                tmp_aivoice = AIVoiceHuman(self.char_name,voiceroid_dict["AIVOICE"])
                print(f"{self.char_name}のAIVOICE起動開始")
                self.human_Voice = tmp_aivoice
                print(f"{self.char_name}のAIVOICE起動完了")
                self.human_Voice.speak("起動完了")
                return "AIVOICE"
            elif "" != Coeiroink.getCharNum(self.char_name):
                tmp_coeiroink = Coeiroink(self.char_name,voiceroid_dict["Coeiroink"])
                print(f"{self.char_name}のcoeiroink起動開始")
                self.human_Voice = tmp_coeiroink
                print(f"{self.char_name}のcoeiroink起動完了")
                # self.human_Voice.speak("起動完了")
                return "Coeiroink"
            else:
                return "ボイロにいない名前が入力されたので起動に失敗しました。"
        else:
            print(f"ボイロ起動しない設定なので起動しません。ONにするにはHuman.voice_switchをTrueにしてください。")
            return "ボイロ起動しない設定なので起動しません。ONにするにはHuman.voice_switchをTrueにしてください。"
    
    def reStart(self):
        #gpt
        if self.gpt_switch:
            print(f"{self.char_name}のgpt再起動チェックをします")
            if hasattr(self,"human_GPT"):
                print(f"{self.char_name}のgptが既に起動してるので再起動します")
                self.human_GPT.reStart()
            else:
                print(f"{self.char_name}のgptが起動していないので起動します")
                self.human_GPT = ChatGPT(self.char_name)
            print(f"{self.char_name}のgpt起動完了")
        else:
            print(f"gpt起動しない設定なので起動しません。ONにするにはHuman.gpt_switchをTrueにしてください。")
        #self.human_Voiceの型がcevioかvoicevoxかで分岐
        if self.gpt_switch:
            if cevio_human == type(self.human_Voice) :
                print(f"{self.char_name}のcevio再起動チェックをします")
                if hasattr(self,"human_Voice"):
                    print(f"{self.char_name}のcevioが既に起動してるので再起動します")
                    self.human_Voice.reStart()
                else:
                    print(f"{self.char_name}のcevioが起動していないので起動します")
                    self.human_Voice = cevio_human(self.char_name,1)
                print(f"{self.char_name}のcevio起動完了")
        else:
            print(f"ボイロ起動しない設定なので起動しません。ONにするにはHuman.voice_switchをTrueにしてください。")
    
    def resetGPTPromptSetting(self, prompt_setting_num:str = "キャラ個別システム設定"):
        self.human_GPT.resetGPTPromptSetting(prompt_setting_num)

    def shutDown(self):
        del self.human_GPT
        if cevio_human == type(self.human_Voice):
            self.human_Voice.shutDown()
    
    def speak(self,str:str):
        self.human_Voice.speak(str)

    def outputWaveFile(self,str:str):
        str = str.replace(" ","").replace("　","")
        str = TextConverter.convertReadableJapanaeseSentense(str)
        if cevio_human == type(self.human_Voice):
            print("cevioでwav出力します")
            self.human_Voice.outputWaveFile(str)
        elif AIVoiceHuman == type(self.human_Voice):
            print("AIvoiceでwav出力します")
            self.human_Voice.outputWaveFile(str)
        elif voicevox_human == type(self.human_Voice):
            print("voicevoxでwav出力します")
            self.human_Voice.outputWaveFile(str)
        elif Coeiroink == type(self.human_Voice):
            print("coeiroinkでwav出力します")
            self.human_Voice.outputWaveFile(str)
        else:
            print("wav出力できるボイロが起動してないのでwav出力できませんでした。")

    def generate_text(self,str:str,gpt_version = "gpt-4-1106-preview"):
        return self.human_GPT.generate_text(str,gpt_version)
    
    def generate_text_simple(self,str:str,gpt_version = "gpt-4-1106-preview"):
        return self.human_GPT.generate_text_simple(str,gpt_version)
    
    def generate_text_simple_json_4(self,str:str,gpt_version = "gpt-4-1106-preview"):
        return self.human_GPT.generate_text_simple_json_4(str,gpt_version)

    def format_response(self,text:str):
        """
        gptから送られてきたjson文字列を辞書に代入する関数
        """
        try:
            tmp_dict:dict = json.loads(text)
            for key in self.response_dict.keys():
                if key in tmp_dict:
                    self.response_dict[key] = tmp_dict[key]
                else:
                    self.response_dict[key] = ""
            self.response_dict["json返答"] = "成功"
            self.saveResponse()
        except Exception as e:
            # textがjson形式でない時はエラーになるのでtextをそのまま全部会話の部分に入れる。
            self.response_dict[self.char_name] = text
            self.response_dict["json返答"] = "失敗"

    def appendSentence(self,input_sentence:str, inputer_name:str):
        if self.sentence_count == 0:
            self.sentence = f"{inputer_name}:{input_sentence}"
        else:
            self.sentence = f"{self.sentence}, {inputer_name}:{input_sentence}"
        self.sentence_count += 1
        return self.sentence,self.sentence_count
    def resetSentence(self):
        self.sentence = ""

    def execLastResponse(self):
        if "成功" == self.response_dict["json返答"]:
            print("json返答に成功してるので発声します")
            if "直接発声" == self.voice_mode:
                self.speak(self.response_dict[self.char_name])
            elif "wav出力" == self.voice_mode:
                self.outputWaveFile(self.response_dict[self.char_name])
            self.execGPTsCode(self.response_dict["コード"])
            # 反応がなければもう一度続きの反応を生成して声をかける処理を入れる
        else:
            print("json返答に失敗したので発声を中止します")

    def saveResponse(self):
        pass
    
    def execGPTsCode(self,code_text:str):
        """
        コードテキストを実行可能な形に整形
        """
        replace_words = [
            "```python\\n",
            "```"
        ]
        for word in replace_words:
            try:
                code_text.replace(word,"")
            except Exception as e:
                print("プログラムの形式がおかしいです")
        try:
            ret = eval(code_text)
            self.speak(ret)
        except Exception as e:
            print(e)
            try:
                exec(code_text)
            except Exception as e:
                print(e)
    
    @staticmethod
    def getNameList()->dict[str,str]:
        """
        キャラ名のリストを返す
        """
        # C:\Users\t-yamanaka\VoiroStudio\api\CharSettingJson\NameListForHuman.jsonを現在のC:\Users\t-yamanaka\VoiroStudio\api\gptAI\Human.pyからの相対パスで取得
        api_dir = Path(__file__).parent.parent
        name_list_path = api_dir / "CharSettingJson" / "NameListForHuman.json"

        with open(name_list_path, "r", encoding="utf-8") as f:
            name_list = json.load(f)
    
        return name_list

    @staticmethod
    def setCharName(name:str):
        """
        front_nameからchar_nameに変換する関数
        """
        name_list = Human.getNameList()
        
        try:
            return name_list[name]
        except Exception as e:
            print(f"{name}は対応するキャラがサーバーに登録されていません。")
            return name
    
    @staticmethod
    def pickFrontName(filename:str):
        """
        char_nameからfront_nameに変換する関数
        """
        name_list = Human.getNameList()
        for front_name_candidate in name_list.keys():
            if front_name_candidate in filename:
                return front_name_candidate
        return "名前が無効です"
    
    @staticmethod
    def checkCommentNameInNameList(atmark_type,comment:str):
        """
        コメントに含まれる名前がキャラ名リストに含まれているか確認する
        """
        name_list = Human.getNameList()
        for name in name_list:
            target = f"{atmark_type}{name}"
            if target in comment:
                return name
        return "名前が無効です"

    
    @staticmethod
    def convertDictKeyToCharName(dict:dict):
        """
        辞書のキーfront_nameからchar_nameに変換する
        """
        return_dict = {}
        for front_name,value in dict.items():
            return_dict[Human.setCharName(front_name)] = value
        return return_dict

    
    def getHumanImage(self):
        return self.image_data_for_client
    
    def saveHumanImageCombination(self, combination_data:dict, combination_name:str):
        self.human_part.saveHumanImageCombination(combination_data, combination_name,0)

    @staticmethod
    def parseSentenseList(sentense:str)->list[str]:
        """
        文章を分割してリストにする
        """
        sentence_list = re.split('[。、]', sentense)
        return sentence_list
    
    @staticmethod
    def extractSentence4low(response)->str:
        try:
            data = json.loads(response)
            if "status" in data and "speak" == data["status"] and "spoken_words" in data:
                return data["spoken_words"]
            else:
                return ""
        except json.JSONDecodeError:
            return response.split(":")[-1].split("：")[-1]
        




