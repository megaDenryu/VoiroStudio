from pathlib import Path
import win32com.client
import time
import requests
import pyaudio
import json
from pprint import pprint
import datetime
import psutil
import os
import base64

#AI.VOICE Editor API用のライブラリ
import os
import clr
from typing import Dict, Any

from api.Extend.ExtendFunc import ExtendFunc

class cevio_human:
    def __init__(self,char_name:str,started_cevio_num:int) -> None:
        
        self.name = char_name 
        self.cevio_name = self.setCharName(char_name)
        #名前が設定されていない場合は起動しない
        if self.cevio_name != "":
            self.cevioStart(started_cevio_num)
            self.output_wav_info_list = []
    
    def settingParameter(self,talk_param_dict):
        """
        例:talk_param_dict = {"Volume":50 , "Speed":50 , "Tone":50 , "ToneScale":50 , "Alpha":50 }
        """
        # talk_parameterを設定
        for param, value in talk_param_dict.items():
            if param == "Volume":
                self.talker.Volume = value
            elif param == "Speed":
                self.talker.Speed = value
            elif param == "Tone":
                self.talker.Tone = value
            elif param == "ToneScale":
                self.talker.ToneScale = value
            elif param == "Alpha":
                self.talker.Alpha = value

    def settingEmotion(self,emotion_dict):
        """
        例:emotion_dict = {'嬉しい':0, '普通':100, '怒り':0, '哀しみ':0, '落ち着き':0}
        """
        # 感情設定
        component_array = self.talker.Components
        emotion_list = [component_array.At(i).Name for i in range(component_array.Length)]
        for emotion in emotion_list:
            component_array.ByName(emotion).Value = emotion_dict[emotion]
    def speak(self,content:str):
        """
        ２００文字以上だと切り詰められるので文節に区切って再生する
        """
        sentence_list = content.split("。")
        for text in sentence_list:
            print("cevioで喋ります")
            state = self.talker.Speak(text)
            state.Wait()
    def outputWaveFile(self,content:str):
        """
        ２００文字以上だと切り詰められるので文節に区切って再生する
        """
        sentence_list = content.split("。")
        print(sentence_list)
        #output_wav_info_listを初期化
        self.output_wav_info_list = []
        for index,text in enumerate(sentence_list):
            if text == "":
                continue
            else:
                print(f"cevioでwavを生成します:{index + 1}/{len(sentence_list)}")
                #output_wavフォルダがなければ作成
                os.makedirs("output_wav", exist_ok=True)
                wav_path = f"output_wav/cevio_audio_{self.cevio_name}_{index}.wav"
                state:bool = self.talker.OutputWaveToFile(text,wav_path)
                phoneme = self.talker.GetPhonemes(text) #音素
                phoneme_str = [[phoneme.at(x).Phoneme,phoneme.at(x).StartTime,phoneme.at(x).EndTime] for x in range(0,phoneme.Length)]
                phoneme_time = [phoneme.at(x).Phoneme for x in range(0,phoneme.Length)]
                wav_data = self.openWavFile(wav_path)   #wabのbinaryデータ
                wav_info = {
                    "path":wav_path,
                    "wav_data":wav_data,
                    "phoneme_time":phoneme_time,
                    "phoneme_str":phoneme_str,
                    "char_name":self.name,
                    "cevio_name":self.cevio_name
                }
                #pprint(f"{wav_info=}")
                self.output_wav_info_list.append(wav_info)

    def openWavFile(self,file_path):
        """
        wavファイルをバイナリー形式で開き、base64エンコードした文字列を返す
        """
        try:
            # ファイルをバイナリー形式で開く
            with open(file_path,mode="rb") as f:
                binary_data = f.read()
            # ファイル情報をjsonに文字列として入れるためにファイルのバイナリーデータをbase64エンコードする
            base64_data = base64.b64encode(binary_data)
            base64_data_str = base64_data.decode("utf-8")
            return base64_data_str
        except Exception as e:
            return ""
    @staticmethod
    def setCharName(name):
        api_dir = Path(__file__).parent.parent
        path = api_dir / "CharSettingJson" / "CevioNameForVoiceroidAPI.json"
        with open(path, "r", encoding="utf-8") as f:
            name_list:list[str] = json.load(f)
        #name_dictのキーにnameがあれば、その値を返す。なければ空文字を返す。
        if name in name_list:
            return name
        else:
            return ""
    def cevioStart(self,started_cevio_num:int):
        print("cevio起動開始")
        if 0 == started_cevio_num:
            #self.kill_cevio()
            pass
        print("cevioが起動しているか確認完了")
        self.cevio = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.ServiceControl2")


        print("cevioのインスタンス化完了")
        self.cevio.StartHost(False)
        print("cevio起動完了")
        self.talker = win32com.client.Dispatch("CeVIO.Talk.RemoteService2.Talker2V40")
        print("talkerのインスタンス化完了")
        self.talker.Cast = self.cevio_name
        print("キャラクターの設定完了")

    def kill_cevio(self):
        for proc in psutil.process_iter():
            try:
                processName = proc.name()
                if 'CeVIO' in processName:
                    target_pid = proc.pid
                    os.kill(target_pid, 9)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
    def shutDown(self):
        self.cevio.CloseHost(0)
    def reStart(self):
        print(f"時刻:{datetime.datetime.now()}")
        print("cevio再起動開始")
        #self.shutDown()
        #time.sleep(2)
        self.cevio.StartHost(False)
        self.talker.Cast = self.setCharName(self.name)
        #self.cevioStart()
        print("cevio再起動完了")
    
    def getAvailableCast(self):
        """
        利用可能なキャスト一覧を出力

        Returns:
            result (list): 利用可能なキャスト名

        Raises :
          CevioException : CeVIOが起動していない場合の例外
        """

        castlist = self.talker.AvailableCasts
        result = []
        for i in range(0,castlist.Length):
            result.append(castlist.At(i))
        return result
        
class voicevox_human:
    def __init__(self,name:str,started_voicevox_num:int) -> None:
        
        if "" != self.getCharNum(name):
            self.char_num = self.getCharNum(name)
            self.query_url = f"http://127.0.0.1:50021/audio_query" #f"http://localhost:50021/audio_query"だとlocalhostの名前解決に時間がかかるらしい
            self.synthesis_url = f"http://127.0.0.1:50021/synthesis" #f"http://localhost:50021/synthesis"だとlocalhostの名前解決に時間がかかるらしい
            self.char_name = name
        else:
            self.char_name = ""
            self.name = ""
    
    @staticmethod
    def getCharNum(name):
        """
        VOICEVOXとの通信で使う名前。
        front_nameとchar_nameのようなgptや画像管理で使うための名前ではない。
        """

        api_dir = Path(__file__).parent.parent
        path = api_dir / "CharSettingJson" / "VoiceVoxNameToNumber.json"
        with open(path, "r", encoding="utf-8") as f:
            name_dict = json.load(f)
        #name_listのキーにnameがあれば、その値を返す。なければ空文字を返す。
        if name in name_dict:
            return name_dict[name]
        else:
            return ""

    def getVoiceQuery(self, text: str) -> Dict[str, Any]:
        params = {
            'speaker': self.char_num,
            'text': text
        }
        pprint(params)
        query_dict:Dict[str, Any] = requests.post(self.query_url, params=params).json()
        return query_dict
    
    
    def getVoiceWav(self,query_dict:Dict[str, Any]):
        """
        getVoiceQuery()で取得したquery_dictを引数に使ってwavを生成する.
        """
        query_json = json.dumps(query_dict)
        wav = requests.post(self.synthesis_url, params={'speaker': self.char_num}, data=query_json)
        return wav
    
    def wav2base64(self,wav):
        binary_data = wav.content
        base64_data = base64.b64encode(binary_data)
        base64_data_str = base64_data.decode("utf-8")
        return base64_data_str

    def getLabData(self,query_dict:Dict[str,Any], pitchScale = None, speedScale = None, intonationScale = None):
        """
        参考URL:https://qiita.com/hajime_y/items/7a5b3be2eec561a6117d
        getVoiceQuery()で取得したquery_dictを引数に使ってlabdataを生成する.
        """
        if pitchScale is not None:
            query_dict["pitchScale"] = pitchScale
        if speedScale is not None:
            query_dict["speedScale"] = speedScale
        if intonationScale is not None:
            query_dict["intonationScale"] = intonationScale

        labdata=""
        phonome_str = []
        phonome_time = []
        now_length=0
        timescale = 10000000/float(query_dict["speedScale"])
        for phrase in query_dict["accent_phrases"]:
            for mora in phrase["moras"]:
                #moraの中には子音の情報と母音の情報が両方ある。子音はない場合もある。
                # 子音がある場合
                if mora["consonant_length"] is not None:
                    #labdata += str(int(now_length*timescale)) + " "
                    start = int(now_length*timescale) / 10000000
                    now_length += mora["consonant_length"]
                    #labdata += str(int(now_length*timescale)) + " " + mora["consonant"] + "\n"
                    end = int(now_length*timescale) / 10000000
                    phonome_str.append([mora["consonant"],start,end])
                    phonome_time.append(mora["consonant"])
                # 母音
                #labdata += str(int(now_length*timescale)) + " "
                start = int(now_length*timescale) / 10000000
                now_length += mora["vowel_length"]
                #labdata += str(int(now_length*timescale)) + " " + mora["vowel"] + "\n"
                end = int(now_length*timescale) / 10000000
                phonome_str.append([mora["vowel"],start,end])
                phonome_time.append(mora["vowel"])
            if phrase["pause_mora"] is not None:
                # ポーズの場合
                #labdata += str(int(now_length*timescale)) + " "
                start = int(now_length*timescale) / 10000000
                now_length += phrase["pause_mora"]["vowel_length"]
                #labdata += str(int(now_length*timescale)) + " " + "pau\n"
                end = int(now_length*timescale) / 10000000
                phonome_str.append(["pau",start,end])
                phonome_time.append("pau")
        return phonome_str,phonome_time#labdata
    
    def speak(self,text):
        query:Dict[str, Any] = self.getVoiceQuery(text)
        pprint(query)
        phonome_str,phonome_time = self.getLabData(query)
        pprint(phonome_str)
        wav = self.getVoiceWav(query)
        print(text)
        self.playWav_pyaudio(wav)
        #self.saveWav(wav)
        print("終わり")

    def saveWav(self,response_wav):
        with open("audio.wav", "wb") as f:
            f.write(response_wav.content)
    def playWav_pyaudio(self,response_wav):
        p = pyaudio.PyAudio()
        stream =  p.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=24000,
                         output=True)
        stream.write(response_wav.content)

        stream.stop_stream()
        stream.close()

        p.terminate()
    
    def outputWaveFile(self,content:str):
        """
        ２００文字以上だと切り詰められるので文節に区切って再生する
        """
        sentence_list = content.split("。")
        print(sentence_list)
        #output_wav_info_listを初期化
        self.output_wav_info_list = []
        for index,text in enumerate(sentence_list):
            if text == "":
                continue
            else:
                #output_wavフォルダがなければ作成
                os.makedirs("output_wav", exist_ok=True)
                print(f"voicevoxでwavを生成します:{index + 1}/{len(sentence_list)}")
                wav_path = f"output_wav/voicevox_audio_{self.char_name}_{index}.wav"
                query:Dict[str, Any] = self.getVoiceQuery(text)
                print("query取得完了")
                phoneme_str,phoneme_time = self.getLabData(query)
                print("lab_data取得完了")
                wav_data = self.wav2base64(self.getVoiceWav(query))
                print("wav_data取得完了")
                wav_info = {
                    "path":wav_path,
                    "wav_data":wav_data,
                    "phoneme_time":phoneme_time,
                    "phoneme_str":phoneme_str,
                    "char_name":self.char_name,
                }
                self.output_wav_info_list.append(wav_info)
    
    @staticmethod
    def createVoiceVoxNameToNumberDict():
        """
        まず
        curl -X 'GET' \
        'http://localhost:50021/speakers' \
        -H 'accept: application/json'
        を実行して、VOICEVOXのキャラクター名とキャラクター番号のjsonを取得する。
        次にVOICEVOXのキャラクター名とキャラクター番号の対応表を作成する。
        """
        import requests

        url = "http://localhost:50021/speakers"
        headers = {'accept': 'application/json'}
        response = requests.get(url, headers=headers)
        speaker_dict = response.json()
        save_dict = {}
        for speaker in speaker_dict:
            name = speaker["name"]
            styles = speaker["styles"]
            for style in styles:
                style_name = style["name"]
                style_num = style["id"]
                save_name = name + ":" +style_name
                save_dict[save_name] = style_num
        pprint(save_dict)
        api_dir = Path(__file__).parent.parent
        path = api_dir / "CharSettingJson" / "VoiceVoxNameToNumber.json"
        #pathにspeaker_dictを書き込む
        with open(path, "w", encoding="utf-8") as f:
            json.dump(save_dict,f,ensure_ascii=False, indent=4)





class AIVoiceHuman:
    def __init__(self,char_name:str,started_AIVoice_num:int) -> None:
        self.char_name = char_name
        self.aivoice_name = self.setCharName(char_name)
        self.start()
        print(self.updateCharName())
        
    def start(self):
        _editor_dir = os.environ['ProgramW6432'] + '\\AI\\AIVoice\\AIVoiceEditor\\'

        if not os.path.isfile(_editor_dir + 'AI.Talk.Editor.Api.dll'):
            print("A.I.VOICE Editor (v1.3.0以降) がインストールされていません。")
            exit()

        # pythonnet DLLの読み込み
        clr.AddReference(_editor_dir + "AI.Talk.Editor.Api")
        from AI.Talk.Editor.Api import TtsControl, HostStatus

        self.tts_control = TtsControl()

        # A.I.VOICE Editor APIの初期化
        host_name = self.tts_control.GetAvailableHostNames()[0]
        self.tts_control.Initialize(host_name)

        # A.I.VOICE Editorの起動
        if self.tts_control.Status == HostStatus.NotRunning:
            self.tts_control.StartHost()

        # A.I.VOICE Editorへ接続
        self.tts_control.Connect()
        host_version = self.tts_control.Version
        self.setVoiceChara()
        print(f"{host_name} (v{host_version}) へ接続しました。")

    def outputWaveFile(self,content:str):
        """
        ２００文字以上だと切り詰められるので文節に区切って再生する
        """
        sentence_list = content.split("。")
        print(sentence_list)
        #output_wav_info_listを初期化
        self.output_wav_info_list = []
        for index,text in enumerate(sentence_list):
            if text == "":
                continue
            else:
                print(f"AIVoiceでwavを生成します:{index + 1}/{len(sentence_list)}")
                wav_path = f"output_aivoice/aivoice_audio_{self.aivoice_name}_{index}"

                #tts_controlには毎回キャラクターを設定
                try:
                    self.setVoiceChara()
                except Exception as e:
                    #AIVoiceとの接続が切断されてるときがあるので、再接続する
                    print("キャラクターの設定に失敗しました")
                    print(e)
                    self.start()
                    self.setVoiceChara()
                # テキストを設定
                self.tts_control.Text = text

                # 音声、lab、を保存
                self.tts_control.SaveAudioToFile(f"{wav_path}.wav")



                # 送信するデータを作成する
                phoneme_str, phoneme_time = self.getPhonemes(f"{wav_path}.lab")
                wav_data = self.openWavFile(f"{wav_path}.wav")   #wabのbinaryデータ
                wav_info = {
                    "path":wav_path,
                    "wav_data":wav_data,
                    "phoneme_time":phoneme_time,
                    "phoneme_str":phoneme_str,
                    "char_name":self.char_name,
                    "aivoice_name":self.aivoice_name
                }
                #pprint(f"{wav_info=}")
                self.output_wav_info_list.append(wav_info)
    
    def openWavFile(self,file_path):
        """
        wavファイルをバイナリー形式で開き、base64エンコードした文字列を返す
        """
        try:
            # ファイルをバイナリー形式で開く
            with open(file_path,mode="rb") as f:
                binary_data = f.read()
            # ファイル情報をjsonに文字列として入れるためにファイルのバイナリーデータをbase64エンコードする
            base64_data = base64.b64encode(binary_data)
            base64_data_str = base64_data.decode("utf-8")
            return base64_data_str
        except Exception as e:
            return ""
    def getPhonemes(self,file_path)->tuple[list[list[str]],list[str]]:
        # 空のリストを作成
        phoneme_str:list[list[str]] = []
        phoneme_time:list[str] = [] 
        # ファイルを開く
        with open(file_path, 'r') as file:
            # 各行を読み込む
            for line in file:
                # 行をスペースで分割
                split_line = line.strip().split()
                format_split_line = [split_line[2],int(split_line[0]) / (10**7),int(split_line[1]) / (10**7)]
                time = split_line[2]
                # 結果をリストに追加
                phoneme_str.append(format_split_line)
                phoneme_time.append(time)

        return phoneme_str,phoneme_time
    
    def setVoiceChara(self):
        #ボイスを琴葉 葵に設定する
        self.tts_control.CurrentVoicePresetName=self.aivoice_name
    
    def convertPythonList(self,CsArr):
        list = []
        for i in CsArr:
            list.append(i)
        return list
    
    @staticmethod
    def setCharName(name:str)->str:
        """
        AIVOICEとの通信で使う名前。
        front_nameとchar_nameのようなgptや画像管理で使うための名前ではない。
        """

        path = ExtendFunc.createTargetFilePathFromCommonRoot(__file__, "api/CharSettingJson/AIVOICENameForVoiceroidAPI.json")
        name_dict:dict[str,str] = ExtendFunc.loadJsonToDict(path)
        #name_listのキーにnameがあれば、その値を返す。なければ空文字を返す。
        if name in name_dict:
            return name_dict[name]
        else:
            return ""
    
    def getAvailableVoicePresetNames(self)->tuple[list[str],list[str]]:
        voiceNames = self.convertPythonList(self.tts_control.VoiceNames) #利用可能なキャラクター名一覧を取得
        #[ '琴葉 茜', '琴葉 茜（蕾）', '琴葉 葵', '琴葉 葵（蕾）' ]

        voicePresetNames = self.convertPythonList(self.tts_control.VoicePresetNames) #標準ボイス、ユーザーボイス名一覧を取得
        # [ '琴葉 茜 - 新規', '琴葉 茜', '琴葉 茜（蕾）', '琴葉 葵', '琴葉 葵（蕾）' ]

        return voiceNames,voicePresetNames
    
    def updateCharName(self):
        """
        1.何らかのAIVOICEのボイロを起動したときに呼び出して新しいキャラが要れば更新する
        todo この関数を呼び出すタイミングを考える
        2.KnownNames.jsonに自分が持っているキャラがいない人はいつ呼び出すか決まっていない。
        """
        # 同じapi_dirにアクセスするので効率化のために先に取得しておく
        api_dir = ExtendFunc.getTargetDirFromParents(__file__, "api")
        
        # AIVOICEKnouwnNames.jsonを取得する
        AIVOICEKnouwnNames_path = api_dir / "CharSettingJson/AIVOICEKnownNames.json"
        knouwn_name_list:list[str] = ExtendFunc.loadJsonToList(AIVOICEKnouwnNames_path)
        
        # 利用可能なキャラクター名一覧を取得
        (voiceNames,now_voicePresetNames) = self.getAvailableVoicePresetNames()
        # 新しく追加されたボイスロイドの名前など、known_name_listにない名前をname_listに追加する
        necessity_update_knouwn_name_list = False
        for name in voiceNames:
            if name not in knouwn_name_list:
                knouwn_name_list.append(name)
                necessity_update_knouwn_name_list = True
        # AIVOICEKnouwnNames.jsonを更新する必要があれば更新する
        if necessity_update_knouwn_name_list:
            ExtendFunc.saveListToJson(AIVOICEKnouwnNames_path,knouwn_name_list)

        # 既に知っている名前に自分で追加したプリセットの名前を追加して使用可能な名前一覧を更新する
        new_name_list:list[str] = [] + knouwn_name_list
        for name in now_voicePresetNames:
            if name not in knouwn_name_list:
                new_name_list.append(name)
        # AIVOICENameForVoiceroidAPI.jsonを取得する
        AIVOICENameForVoiceroidAPI_path = api_dir / "CharSettingJson/AIVOICENameForVoiceroidAPI.json"
        old_name_list:list[str] = list(ExtendFunc.loadJsonToDict(AIVOICENameForVoiceroidAPI_path).values())
        
        #old_name_listとnew_name_listを比較して、違う名前があればchange_name_listに追加する
        change_name_list = []
        necessity_update_AIVOICEname_list = False
        set_old_name_list = set(old_name_list)
        set_new_name_list = set(new_name_list)
        #２つのsetが同じかどうかを比較する
        if set_old_name_list != set_new_name_list:
            new_name_dict:dict[str,str] = {}
            for name in new_name_list:
                # AIVOICEの名前は半角スペースが入っているので、それを取り除いてキーにする
                key_name = name.replace(" ","")
                new_name_dict[key_name] = name
            ExtendFunc.saveDictToJson(AIVOICENameForVoiceroidAPI_path,new_name_dict)
        
        return "update完了"


    def getVoiceQuery(self,text:str):
        pass
    
    def getVoiceWav(self,query):
        pass
    
    def speak(self,text):
        pass

    def saveWav(self,response_wav):
        pass

if __name__ == '__main__':
    if False:
        print("開始")
        one = cevio_human("おね",0)
        ia = cevio_human("ia",1)
        tudumi = cevio_human("つづみ",2)
        one.outputWaveFile("おはよう")
        ia.outputWaveFile("おねちゃんきょーもかみぼさぼさじゃーん")
        tudumi.outputWaveFile("ほんとね、といてあげるわ")

    elif False:
        tumugi = voicevox_human("春日部つむぎ",0)
        tumugi.speak("あーしはつむぎ,埼玉１のギャルの春日部つむぎだよ、よろしくねオタク君")

    elif False:
        aoi = AIVoiceHuman("琴葉葵",0)
        aoi.outputWaveFile("あーしは葵,埼玉１のギャルの琴葉葵だよ、よろしくねオタク君")
    elif True:
        print("開始")
        voicevox_human.createVoiceVoxNameToNumberDict()
        print("終了")