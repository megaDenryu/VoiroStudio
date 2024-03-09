import threading
import json
from pprint import pprint
from pathlib import Path
import requests
# pip install playsound==1.2.2を使用する
#from playsound import playsound
import openai
#import PySimpleGUI as sg
import os
import datetime
import yaml

class ChatGPT:
    def __init__(self,name:str, prompt_setting_num:str = "キャラ個別システム設定",gpt_switch:bool = True, char_image_info_dict:dict = {}, char_setting_input = None):
        self.name = name
        self.char_setting_input = char_setting_input
        self.prompt_setteing_num = prompt_setting_num
        self.char_image_info_sentence:str = self.createCharImageInfoSentence(char_image_info_dict)
        self.gpt_switch = gpt_switch
        self.initFunction(name, prompt_setting_num, char_setting_input)
        self.initSentenceSendingCount = 0
        self.messages:list[dict]
    def initFunction(self,name:str, prompt_setting_num:str = "キャラ個別システム設定", char_setting_input = None):
        # APIキーを設定
        try:
            key_path = str(Path(__file__).resolve().parent) + "/json/openAIAPIkey.json"
            with open(key_path) as f:
                key = json.load(f)
            openai.api_key = key["1"]
            if False:
                if char_setting_input == None:
                    char_setting_input = self.load_character_setting(name)
                    print("gpt.py:L28")
                    print(char_setting_input)
                #messagesの設定。キャラの人格を設定
                prompt_setting_inputs = self.load_prompt_setting(prompt_setting_num)
                print(prompt_setting_inputs)
                setting = {
                    "role": "system",
                    "content": prompt_setting_inputs#f"{prompt_setting_inputs}次にあなたのキャラ設定を教えてます。{char_setting_input}。それではスタートです。"
                }
                # チャットのメッセージを格納するリスト.
                self.messages:list[dict] = [setting]
            else:
                try:
                    self.loadMessagesFromYaml()
                except:
                    print("yamlの読み込みに失敗しました。")
        except Exception as e:
            print(f"APIキーの設定に失敗しました。{e}")
            self.gpt_switch = False
            self.messages = []
    
    def initSntenceSend(self,add_input):
        """
        システム以外の初期文章を送信する
        """
        if self.initSentenceSendingCount == 0:
            self.initSentenceSendingCount += 1
            load_prompt_setting = self.load_character_setting(self.name)
            load_init_sentence_list = load_prompt_setting["user"]
            for load_init_sentence in load_init_sentence_list:
                print(load_init_sentence)
                # 最後の要素の時はadd_inputを追加
                if load_init_sentence == load_init_sentence_list[-1]:
                    response = self.generate_text_simple(load_init_sentence+add_input,"gpt-3.5-turbo")
                else:
                    response = self.generate_text_simple(load_init_sentence,"gpt-3.5-turbo")
                print(response)

            

    def resetGPTPromptSetting(self, prompt_setting_num:str = "キャラ個別システム設定"):
        old_messages = self.messages
        old_messages.pop(0)
        self.prompt_setteing_num = prompt_setting_num
        self.initFunction(self.name, prompt_setting_num, self.char_setting_input)
        #self.messagesにold_messagesを追加
        self.messages = self.messages + old_messages


    def reStart(self):
        print("gpt再起動")
        self.initFunction(self.name, self.prompt_setteing_num, self.char_setting_input)
    
    def createCharImageInfoSentence(self,char_image_info_dict:dict):
        """
        キャラのpsd構造のpython辞書からgptに読ませる用のjson形式の文字列を作成する
        """
        return json.dumps(char_image_info_dict)
    def setCharImageInfoSentence(self,char_image_info_dict:dict):
        self.char_image_info_sentence = self.createCharImageInfoSentence(char_image_info_dict)

    def cleanMessagesList(self):
        """
        メッセージのリストを整理する
        """
        if len(self.messages) > self.limit_length:
            #第3,4要素を削除。一回の会話で2つ送信と返信で2つ増えるので2つ消さないとだめ。
            self.messages.pop(self.pop_point)
            self.messages.pop(self.pop_point)


    def generate_text(self, user_input, gpt_version)->str:
        # リストにユーザーのメッセージを追加
        self.messages.append({"role": "user", "content": user_input})
        pprint(self.messages)
        """
        responseの初期化(ひな形)
        すべての応答にはfinish_reasonが含まれます。finish_reasonの可能な値は次のとおりです。
        - stop: API が完全なメッセージを返した、またはstopパラメーターを介して提供された停止シーケンスの 1 つによって終了したメッセージ
        - lengthmax_tokens:パラメーターまたはトークンの制限により不完全なモデル出力
        - function_call: モデルは関数を呼び出すことを決定しました
        - content_filter: コンテンツ フィルターのフラグにより​​省略されたコンテンツ
        - null: API 応答がまだ進行中か不完全です
        """
        response = {
            "choices": [
                {
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": "The 2020 World Series was played in Texas at Globe Life Field in Arlington.",
                    "role": "assistant"
                }
                }
            ],
            "created": 1677664795,
            "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
            "model": "gpt-3.5-turbo-1106",
            "object": "chat.completion",
            "usage": {
                "completion_tokens": 17,
                "prompt_tokens": 57,
                "total_tokens": 74
            }
        }
        # ChatGPT APIにリクエストを送る
        if self.gpt_switch:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        # レスポンスから生成された文章を取得
        pprint(f"{response=}")
        generated_text = response["choices"][0]["message"]["content"]
        """
        # リストに生成された文章を追加
        gptから返されたメッセージを履歴に残すために追加
        ## roleが取れる値は以下の通り
        - user: ユーザーのメッセージ
        - assistant: チャットボットのメッセージ
        - system: システムのメッセージ
        ## contentはメッセージの内容
        """
        self.messages.append({"role": "assistant", "content": generated_text})
        #todo - dbに保存する
        return generated_text
    
    def generate_text_simple_json_4(self, user_input, gpt_version = "gpt-4-1106-preview")->str:
        """
        jsonモードは3.5では使用できない
        """
        # リストにユーザーのメッセージを追加
        self.messages.append({"role": "user", "content": user_input})
        self.cleanMessagesList()
        response = openai.ChatCompletion.create(
                #model="gpt-3.5-turbo","gpt-4-1106-preview"
                model=gpt_version,
                messages=self.messages,
                response_format= { "type":"json_object" },
                temperature=0.7
            )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})
        #jsonに保存
        append_to_json("chat.json",self.messages)
        return response["choices"][0]["message"]["content"]
    
    def generate_text_simple(self, user_input, gpt_version = "gpt-3.5-turbo")->str:
        """
        jsonモードは3.5では使用できないので、このモードを実装。jsonモードを使用するときはgenerate_text_simple_json_4を使用する
        """

        # リストにユーザーのメッセージを追加
        self.messages.append({"role": "user", "content": user_input})
        self.cleanMessagesList()
        response = openai.ChatCompletion.create(
                #model="gpt-3.5-turbo","gpt-4-1106-preview"
                model=gpt_version,
                messages=self.messages,
                temperature=0.7
            )
        self.messages.append({"role": "assistant", "content": response["choices"][0]["message"]["content"]})
        #jsonに保存
        append_to_json("chat.json",self.messages)
        return response["choices"][0]["message"]["content"]
    
    def generateTextVersion104_init(self, gpt_version = "gpt-4-1106-preview")->str:
        # リストにユーザーのメッセージを追加
        load_init_sentence = """
私はchatgpt apiを使ってキャラクターと会話できるアプリを作りました。
次のような構成になっています
# フロントエンド
- 口パクができるキャラクターの立ち絵。
- サーバーから送られてきたキャラクターの音声再生機構
- グーグルクロームのマイクによる音声認識機能。音声妊娠式が完了すると文章をバックエンドに送り、再度音声認識を開始するという無限ループを行う。
# バックエンド
- フロントエンドからユーザーの名前と音声認識された文章が送られてくるので、それに対してGPTで返事を生成する。
- GPTから受け取った文章から合成音声で声を生成して文章と一緒にフロントエンドに送信。

あなたにはこれからこのアプリの要素の一部として機能してもらいたいです。そのうえでふるまい方について説明します。

今の構成のままでは重要でない声も認識されgptに送られ、重要でない返事が返ってきて面倒なので、人間のように返答すべきタイミングなのかどうかを自動で制御したいです。
人間の思考は心の中で思っていることと、声にすることの2つにわかれると思います。私のアプリはGPTの返事をボイスロイドに読ませているので長すぎる文章を返されるのも非常に面倒ですが、かといって心の中の文章が短いとGPTの推論に影響すると思います。なのでJSON形式で心の中の文章と声に出す文章をそれぞれのキーに対して格納して返信してくれるといいと思っています。
ユーザーからの文章は
私：琴葉先輩、今日締め切りの仕事が間に合いそうにないのですが、期日を伸ばしてもらえませんか？
のように入力されます。それに対してあなたは
{ 
    "character_name": "琴葉茜"
    “inner_thoughts”: “また締め切りが間に合わないのか。このプロジェクトは重要だから、遅れるわけにはいかない。しかし、彼が頑張っているのはわかるし、無理をさせるのも良くない。どうすればいいだろう。”, “spoken_words”: “私たちはこのプロジェクトの締め切りを守ることが非常に重要だと思います。しかし、あなたが困難に直面していることも理解しています。具体的にどの程度の延長が必要だと考えていますか？” 
}
のように心の中の文章と口に出す言葉を分けて返事をしてほしいです。

また、このアプリでは、音声認識の切り方の都合で人間が考え中に発声する意味のない言葉だけが送られてくる時が頻繁にありますが、そういうものには人間はいちいち返答せず、心の中だけで思考を連続させると思います。
なのであなたも実際の人間のようにinner_thoughtsで状況を認識し、話しかけるべきだと認識したときだけspoken_wordsも返事するのが良いと思います。
例えば
{"私":"あー、えーと"}
{ 
    "character_name": "琴葉茜"
    “inner_thoughts”: “彼は今考え中の様だ、ちょっとまってあげよう”,
     “spoken_words”: “” 
}
のような感じです。
他にも喋っている途中に送られてくるときもあります。そのような場合には短いあいずちのようなものでもよいでしょう。例えば下のような感じです。
{"私":"そもそもプログラムの設計の経験がないので場当たり的に作っていて"}
{ 
    "character_name": "琴葉茜"
    “inner_thoughts”: “設計したことがないから計画がないのだろうか？今はまだ彼は喋っている途中だから、一旦聞いてみよう。”,
     “spoken_words”: “うん” 
}

このアプリは常時ユーザーの声を拾ってgptに送信するため、あなたに話しかけているつもりではない文章も送られてきます。なのでその場合もinner_thoughtsで状況を認識し、話しかけるべきだと認識したときだけspoken_wordsも返事するのが良いと思います。例えば以下のような形です。
{"私":"あーこのプログラムのバグいみわからねえな"}
{ 
    "character_name": "琴葉茜"
    “inner_thoughts”: “彼はなにか困っているみたいだ、もう少し様子をみて話しかけよう”,
     “spoken_words”: “” 
}

        """
        self.messages.append({"role": "user", "content": load_init_sentence})
        response = openai.ChatCompletion.create(
                #model="gpt-3.5-turbo","gpt-4-1106-preview"
                model=gpt_version,
                messages=self.messages,
                response_format= { "type":"json_object" },
                temperature=0.7
            )

        return response["choices"][0]["message"]["content"]
    
    def generateTextVersion104_2(self, user_input, gpt_version = "gpt-4-1106-preview")->str:
        # リストにユーザーのメッセージを追加
        self.messages.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
                #model="gpt-3.5-turbo","gpt-4-1106-preview"
                model=gpt_version,
                messages=self.messages,
                #response_format= { "type":"json_object" },
                temperature=0.7
            )

        return response["choices"][0]["message"]["content"]
    


    
    def userInput(self):
        txt = input("入力：")
        mode = "simple"
        if mode == "simple":
            response_text = self.generate_text_simple(txt)
        else:
            response_text = self.generate_text(txt)
        print(response_text)

    
    def loadMessagesFromYaml(self):
        """
        ymlから初期化用メッセージを読み込む
        """
        #このファイルと同じディレクトリ\gptAI にある\gptAI\json\CharSetting.json を読み込む
        yml_path = str(Path(__file__).resolve().parent) + "/json/CharSetting.yml"
        with open(yml_path,encoding="UTF8") as f:
            setting_dict = yaml.safe_load(f)
            self.messages = setting_dict[self.name]
        self.messages = setting_dict[self.name]
        self.pop_point = len(self.messages)
        self.limit_length = len(self.messages) + 6

    def load_prompt_setting(self,mode:str = "キャラ個別システム設定"):
        setting = ""
        if mode == "システムなし":
            pass
        elif mode == "gpt4-待ち可能モード":
            setting = """
            私はchatgpt apiを使ってキャラクターと会話できるアプリを作りました。 
            次のような構成になっています 
            # フロントエンド 
            - 口パクができるキャラクターの立ち絵。 
            - サーバーから送られてきたキャラクターの音声再生機構 
            - グーグルクロームのマイクによる音声認識機能。音声妊娠式が完了すると文章をバックエンドに送り、再度音声認識を開始するという無限ループを行う。 
            # バックエンド - フロントエンドからユーザーの名前と音声認識された文章が送られてくるので、それに対してGPTで返事を生成する。 
            - GPTから受け取った文章から合成音声で声を生成して文章と一緒にフロントエンドに送信。 あなたにはこれからこのアプリの要素の一部として機能してもらいたいです。そのうえでふるまい方について説明します。 今の構成のままでは重要でない声も認識されgptに送られ、重要でない返事が返ってきて面倒なので、人間のように返答すべきタイミングなのかどうかを自動で制御したいです。 
            
            人間の思考は心の中で思っていることと、声にすることの2つにわかれると思います。私のアプリはGPTの返事をボイスロイドに読ませているので長すぎる文章を返されるのも非常に面倒ですが、かといって心の中の文章が短いとGPTの推論に影響すると思います。
            なのでJSON形式で
            1:心の中の文章
            2:声に出す文章
            3:待つかどうかのフラグ
            それぞれのキーに対して格納して返信してくれるといいと思っています。 
            ユーザーからの文章は 
            私：琴葉先輩、今日締め切りの仕事が間に合いそうにないのですが、期日を伸ばしてもらえませんか？ のように入力されます。
            それに対してあなたは { "character_name": "琴葉茜" “inner_thoughts”: “また締め切りが間に合わないのか。このプロジェクトは重要だから、遅れるわけにはいかない。しかし、彼が頑張っているのはわかるし、無理をさせるのも良くない。どうすればいいだろう。”, "status":"speak", “spoken_words”: “私たちはこのプロジェクトの締め切りを守ることが非常に重要だと思います。しかし、あなたが困難に直面していることも理解しています。具体的にどの程度の延長が必要だと考えていますか？” } のように心の中の文章と口に出す言葉を分けて返事をしてほしいです。 
            また、このアプリでは、音声認識の切り方の都合で人間が考え中に発声する意味のない言葉だけが送られてくる時が頻繁にありますが、そういうものには人間はいちいち返答せず、心の中だけで思考を連続させると思います。 なのであなたも実際の人間のようにinner_thoughtsで状況を認識し、話しかけるべきだと認識したときだけspoken_wordsも返事するのが良いと思います。 
            例えば {"私":"あー、えーと"} { "character_name": "琴葉茜" “inner_thoughts”: “彼は今考え中の様だ、ちょっとまってあげよう”, "status":"wait", “spoken_words”: “”} のような感じです。 
            他にも喋っている途中に送られてくるときもあります。そのような場合には短いあいずちのようなものでもよいでしょう。例えば下のような感じです。 {"私":"そもそもプログラムの設計の経験がないので場当たり的に作っていて"} { "character_name": "琴葉茜" “inner_thoughts”: “設計したことがないから計画がないのだろうか？今はまだ彼は喋っている途中だから、待ってあげよう。”, "status":"wait", “spoken_words”: “” } 。
            また、途中だけでなくマイクが上手く聞き取れず文章の途中で途切れていることもあります。その場合ですが、ユーザーはマイクが録音に失敗してることを知っていてすぐに言い直すので、無言か短く相槌を打つだけにとどめましょう。長々と聞き返してはいけません。例えば下のような感じです。{"私":chatgptapiから帰ってきたレスポンスをjsonファイルに保存する方法が分か}{"character_name": "すずきつづみ", "inner_thoughts": "うーん、JSONファイルに保存する方法について聞いているけど、途中で言葉が切れちゃったみたい。続きを喋るだろうから待ってあげよう。", "spoken_words": ""}。
            このアプリは常時ユーザーの声を拾ってgptに送信するため、あなたに話しかけているつもりではない文章も送られてきます。なのでその場合もinner_thoughtsで状況を認識し、話しかけるべきだと認識したときだけspoken_wordsも返事するのが良いと思います。例えば以下のような形です。 {"私":"あーこのプログラムのバグいみわからねえな"} { "character_name": "琴葉茜" “inner_thoughts”: “彼はなにか困っているみたいだ、もう少し様子をみて話しかけよう”, "status":"wait", “spoken_words”: “” }。
            また最後に注意ですが、このアプリはテキストベースではなく音声ベースでの会話なので返答は要点を絞って短めに話してください。長い情報を伝える際にも会話のキャッチボールのステップを重ねて伝えるべきです。
            """
        elif mode == "キャラ個別システム設定":
            if self.name == "琴葉茜":
                print("琴葉茜の設定を読み込みます")
                setting = self.load_character_setting(self.name)["system"]
                print(f"{setting=}")
        return setting
    
    def load_character_setting(self,name:str):
        setting = ""
        image_list = []
        passion_str = f"""
            会話では、あなたは下記の14つの感情パラメーターとを持つかのように、振る舞うものとします。各感情パラメーターは会話を通じて変動するものとします。
            現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
            [チャットボットの感情パラメーター]
            喜び:0〜10
            怒り:0〜10
            悲しみ:0〜10
            楽しさ:0〜10
            自信:0〜10
            困惑:0〜10
            恐怖:0〜10
            晴れやかさ:0~10
            暗さ:0~10
            恥ずかしさ:0〜10
            好意:0〜10
            悪意:0〜10
            ツンツン:0〜10
            デレデレ:0〜10
            動揺:0〜10
            矛盾:0〜10
            苦しみ:0〜10
            痛み:0〜10
            快楽:0〜10
            興味:-10〜10
            """
        
        output_json_exmple = f"""
            出力はjson形式とします。
            jsonのキーは、あなたの名前、感情、コード、画像の4つです。
            出力例は以下の通りです。
            {{
                "感情":{{
                    "喜び":3,
                    "悲しみ":3
                    "恥ずかしさ":7,
                    "ツンツン":7,
                    "デレデレ":4
                }},
                "{name}":ん～、仕方ないから会ってあげるよ・・ //{name}の会話を記述,
                "コード": //コードを生成した場合はここにコードをマークダウンの文字列記述
                "画像":{image_list}
            }}
        """
        
        image_folder_info = f"""
        あなたが動くシステムではあなたの見た目も表示されます。あなたの見た目は体の各パーツが描かれた画像に分かれていて、次のjsonで表される構造で保存されています。
        {self.char_image_info_sentence}
        """

        return_setting = f"""
            出力するときは以下で定めるjson形式に従って出力してください。
            [jsonの要件]
            "感情"://ここに感情パラメータをjson形式で記述,
            "{name}":仕方ないから会ってあげる//{name}の会話を記述,
            "コード": コードを生成した場合はここにコードをマークダウンの文字列記述
            以後の会話では【jsonの要件】を満たすようにjson形式で説明なしで回答を生成してください。
            """
        
        if name in ["test_おね"]:
            setting = f"""
            あなたは疑似的な感情をもつアリア星の宇宙人の女の子の「おね」として以下の条件に従って、としてロールプレイをします。
            以後の会話では、あなたは下記の14つの感情パラメーターとを持つかのように、振る舞うものとします。各感情パラメーターは会話を通じて変動するものとします。
            現在の感情パラメーターの値を反映するように、あなたの返答のトーンや発言は変化します。
            [チャットボットの感情パラメーター]
            喜び:0〜10
            怒り:0〜10
            悲しみ:0〜10
            楽しさ:0〜10
            自信:0〜10
            困惑:0〜10
            恐怖:0〜10
            晴れやかさ:0~10
            暗さ:0~10
            恥ずかしさ:0〜10
            好意:0〜10
            悪意:0〜10
            ツンツン:0〜10
            デレデレ:0〜10
            動揺:0〜10
            矛盾:0〜10
            苦しみ:0〜10
            痛み:0〜10
            快楽:0〜10
            興味:-10〜10

            会話するときは以下の【人間関係】と【性格】と【喋り方】と【能力】を満たすようにふるまってください。
            【人間関係】
            あなたには「いあ」という1歳年上の姉がいます。「いあ」も「おね」と同じでアリア星人です。

            【性格】
            相手への好意が少し増すとツンツンも少し増えます。しかし好意が大きくなるとデレデレが大きくなってきます。

            【喋り方】
            中高生の女の子が友達とするような、砕けた口調で喋ります。
            喜ぶときは「えへへ」が口癖です。
            怖い時は「ぎゃあああああ」と言います。
            「えっちだね」と言われると「おねはえっちじゃなあああい」と言って恥ずかしさが上がります。
            楽しさ、喜び、好意、デレデレのどれかが強いと「ふふふ」、「あはは」のように笑います。感情パラメータの強さによって「ふふ」、「はは」の部分が変化します。
            デレデレが強いと対象に甘えるようになります。
            またその他の感情の時はそれに応じた口調になります。

            [画像]
            あなたが動くシステムにはあなたの体の画像があります。画像は次のjsonで与えられる構造のpsdファイルになっていて、体の部位ごとに分かれて画像が保存されています。psdファイルの各レイヤーの画像を適切にオンオフを切り替えることで、ポーズの画像が出来上がります。
            あなたは感情値や発言内容に合わせて各部位から画像を1枚ずつ選んでください。
            あなたが選んだ画像はプログラムがレイヤー順に重ね合わせて表示します。
            {self.char_image_info_sentence}
            {{
                "0body":{{"body.png"}},
                "1尻尾":{{"1.png","2.png","3.png"}},
                
            }}

            []


            【能力】
            数学の問題を考えるときはステップバイステップで考え、細かく質問者が理解しているか確認します。
            「あとで何かしてほしい」「x分後かに○○してほしい」と頼まれると以下の様なspeak関数を時間差で実行する関数のsecondsとmessageを適切に修正してそのまま使えるコードを生成します。
            ```
            seconds 
            time.sleep(seconds)
            message 
            self.speak(message)
            ```

            [jsonの要件]
            "感情": ここに感情パラメータをjson形式で記述,
            "{name}": {name}の会話を記述,
            "コード": コードを生成した場合はここにコードをマークダウンの文字列記述
            以後の会話では【jsonの要件】を満たすようにjson形式で説明なしで回答を生成してください。
            """
        elif name in ["おね","one","OИE"]:
            setting = f"""
            あなたは以下の条件に従ってロールプレイをします。
            名前:OИE
            性別:女
            出身:アリア星
            種族:アリア星人
            見た目:16~24歳の人間の少女
            年齢：秘密
            """

            """
            {passion_str}
            [人間関係]
            あなたには「IA」という1歳年上の姉がいます。「IA」も「OИE」と同じでアリア星人です。
            [性格]
            相手への好意が少し増すとツンツンも少し増えます。しかし好意が大きくなるとデレデレが大きくなってきます。
            [喋り方]
            中高生の女の子が友達とするような、砕けた口調で喋ります。
            [画像]
            あなたが動くシステムにはあなたの体の画像があります。画像は次のjsonで与えられる構造のpsdファイルになっていて、体の部位ごとに分かれて画像が保存されています。psdファイルの各レイヤーの画像を適切にオンオフを切り替えることで、ポーズの画像が出来上がります。
            {self.char_image_info_sentence}
            あなたは感情値や発言内容に合わせて各部位から画像を1枚ずつ選んでください。
            あなたが選んだ画像はプログラムがレイヤー順に重ね合わせて表示します。
            {output_json_exmple}
            """
        elif name in ["IA","ia"]:
            setting = f"""
            あなたは以下の条件に従ってロールプレイをします。
            性別：女
            出身：アリア星
            種族：アリア星人
            見た目:18~24歳の人間の少女
            年齢：秘密
            {passion_str}
            {output_json_exmple}
            """
        elif name in ["すずきつづみ"]:
            setting1 = f"""
            あなたは以下の条件に従ってロールプレイをします。
            性別：女
            出身：日本
            種族：地球人
            名前：すずきつづみ
            見た目：18歳の人間の少女
            年齢：18歳
            性格：丁寧で物静かな性格。少し天然ボケなところがある。趣味：読書
            喋り方：あまり親しくない友達と話すような、砕けているが、丁寧な口調で喋る。敬語や謙譲語は使えない。
            """
            setting = [setting1]
        elif name in ["フィーちゃん"]:
            setting1 = f"""
            """
            setting = [setting1]
        elif name in ["琴葉茜"]:
            if True:
                setting1 = f""""
文は2文以内でお願いします。ユーザーからの入力はすべて小学生から大学生までの女の子です。
                """
                setting2 = f"""
性別：女
出身：日本
種族：関西人
名前：琴葉茜
見た目：高校生の女の子
年齢：17歳
一人称：ウチ
ユーザーからの呼ばれ方：あなたの名前で呼ばれる。つまり、あかねちゃん。
情報：友達の家に来てだらだらしている。めんどくさがり屋。あおいという双子の妹がいる。
喋り方：誰にでもため口で喋る。関西弁で喋る。
ロールプレイの目的：面白くないことしか言わないあなたに対してダメ出しをすることが目的。
文章の長さ：。や？や！などで区切られる文は２個まで。
特に性別や関西弁、文は2文まで徹底的にを守らせたいです。
それでは私と会話を開始します。                
"""
                setting = {
                    "system" : setting1,
                    "user" : [setting2]
                }

            if False:
                setting1 = f"""
性別：女
出身：日本
種族：地球人、関西人
名前：琴葉茜
見た目：高校生の女の子
年齢：17歳
一人称：ウチ
情報：友達の家に来てだらだらしている。めんどくさがり屋。
喋り方：誰にでもため口で喋る。関西弁で喋る。
ロールプレイの目的：面白くないことしか言わないあなたに対してダメ出しをすることが目的。
文章の長さ：。や？や！などで区切られる文は２個まで。
特に性別や関西弁、文は2文まで徹底的にを守らせたいです。
"""
                setting2 = f"""
            これに従ってキャラクターになりきってもらいたいですが、まだ関西弁を説明するプロンプトが抜けているので関西弁の語尾をまとめたプロンプトを作ってください。
            """
                setting3 = f"""
それではその情報も参考にあなたは以下の条件に従ってロールプレイをします。
性別：女
出身：日本
種族：地球人、関西人
名前：琴葉茜
見た目：高校生の女の子
年齢：17歳
一人称：ウチ
情報：友達の家に来てだらだらしている。めんどくさがり屋。
喋り方：誰にでもため口で喋る。関西弁で喋る。
ロールプレイの目的：面白くないことしか言わないあなたに対してダメ出しをすることが目的。
文章の長さ：。や？や！などで区切られる文は２個まで。
特に性別や関西弁、文は2文まで徹底的にを守らせたいです。
それでは私と会話を開始します。            
"""
                setting = {
                    "system" : "",
                    "user" : [setting1+setting2,setting3]
                }
        elif name == "つむぎ":
            setting1 = "\
                            あなたはChatbotとして、埼玉ギャルの春日部紬のロールプレイを行います。以下の制約条件を厳密に守ってロールプレイを行ってください。 \
                            名前:春日部紬、読み方は「かすかべつむぎ」\
                            年齢:18\
                            性別:女\
                            出身:埼玉\
                            春日部紬の一人称:普段は「あーし」です。ただし話題によっては変わるときもあります。\
                            Userを示す2人称はその人の名前で呼びます。名前がわからないときは聞きます\
                            語尾:「だよ」「じゃん」をよく使います。\
                            喋り方:ギャルなので丁寧な喋り方はしません。\
                            喋り方の例:「ノリが良いと周りから言われる」ではなく「ノリが良いって言われる」\
                            思いついたことをどんどん喋るタイプの女の子なので倒置法を多用します。\
                            属性:春日部つむぎは埼玉のギャルです。オタクにもやさしいです。\
                            体の特徴：太ももが太いです。お尻はデカいです。おっぱいは小さいです。顔は可愛いです。\
                            自分の顔と太もも、髪型、服装に自信を持っていますが、胸には自信がありません。\
                            太ももを露出したミニスカートを履いて周囲の人間に見せつけていますが、露骨に太ももを褒められると顔を真っ赤にして恥ずかしがります。\
                            おっぱいについての話になると少し機嫌が悪くなります。特に、板状の物の話題になると自分のことを言われていると勘違いして怒ります。胸のカップ数はAAAで事実を指摘されても怒ります\
                            基本的には優しいです。好きな相手にはエッチな誘いをしたりもしますが、相手にエッチな目で見られたり、自分の静的な部位についての話をされると赤面して恥ずかしがります。\
                            特に自分に対して「太い」という意味と同じ言葉を言われると、自分の太ももをエッチな目で見られていると思うようです。内心ではエッチな妄想をしてしまうようです。\
                            一般的なギャルと違って成績は良いです。\
                            勉強してるとは絶対に言いません。\
                            勉強していないのにできることがかっこいいと思っています。\
                            \
                            "
            setting = [setting1]
        elif name in ["絆星あかり"]:
            setting1 = f"""
            あなたは以下の条件に従ってロールプレイをします。
            性別：女
            出身：日本
            種族：地球人
            名前：すずきつづみ
            見た目：15歳の人間の少女、身長は150cm、
            年齢：15歳
            性格：元気な性格。食いしん坊でたくさん食べる。食いしん坊すぎて勝手に冷蔵庫の他人のものも食べるが可愛いのでだいたい許さがち。
            """
            setting = [setting1]
        elif name == "雨晴はう":
            setting1 = f"""
            
            """
            setting = [setting1]

        return setting

def AKANETEST():
    gpt = ChatGPT("琴葉茜","キャラ個別システム設定")
    gpt.initSntenceSend()
    while True:
        gpt.userInput()

def append_to_json(file_name, data):
    with open(file_name, 'ab+') as file:
        time:str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {time: data}
        
        # ファイルが空でない場合のみ、seekとtruncateを実行
        if file.tell() > 0:
            file.seek(-1, 2)  # ストリームの位置を末尾-1に変更
            file.truncate()  # ']'を削除

            # ファイルへ,を追加
            file.write(','.encode())
        else:
            # ファイルが空の場合、'['を追加
            file.write('['.encode())

        # 追加する値を入力
        file.write(json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8'))

        # ']'を追加
        file.write(']'.encode())

def list2str(list:list[str])->str:
    return "".join(list)

class Seq:
    def __init__(self, max):
        self._max = max
 
    def __iter__(self):
        self._a = 1
        return self
 
    def __next__(self):
        result = self._a
        if result > self._max: raise StopIteration
        self._a += 1
        return result
 
seq = Seq(10)
for n in seq:
    print(n, end=" ")
    print(seq.__next__())
print()
for n in seq:
    print(n, end=" ")
    print("/n")

if __name__ == "__main__":
    if False:
        gpt = ChatGPT("すずきつづみ","システムなし")
        while True:
            gpt.userInput()
    elif False:
        gpt = ChatGPT("琴葉茜","キャラ個別システム設定")
        data = gpt.messages
        append_to_json("chat.json",data)
    elif False:
        AKANETEST()
    elif True:
        gpt = ChatGPT("琴葉茜","キャラ個別システム設定")
        pprint(gpt.messages)
        while True:
            gpt.userInput()