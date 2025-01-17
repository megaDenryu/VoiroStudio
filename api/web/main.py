import asyncio
import os
import random
import sys
from pathlib import Path
sys.path.append('../..')
from api.comment_reciver.TwitchCommentReciever import TwitchBot, TwitchMessageUnit
from api.gptAI.gpt import ChatGPT
from api.gptAI.voiceroid_api import cevio_human
from api.gptAI.Human import Human
from api.gptAI.AgentManager import AgentEventManager, AgentManager, GPTAgent, InputReciever, LifeProcessBrain
from api.images.image_manager.HumanPart import HumanPart
from api.images.psd_parser_python.parse_main import PsdParserMain
from api.Extend.ExtendFunc import ExtendFunc, TimeExtend
from api.DataStore.JsonAccessor import JsonAccessor
from api.DataStore.AppSettingModule import AppSettingModule, PageMode
from api.Epic.Epic import Epic
from api.DataStore.Memo import Memo

from enum import Enum

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


from typing import Dict, List, Any, Literal

import mimetypes

from api.comment_reciver.comment_module import NicoNamaCommentReciever
from api.comment_reciver.newNikonamaCommentReciever import newNikonamaCommentReciever
from api.comment_reciver.NiconamaUserLinkVoiceroidModule import NiconamaUserLinkVoiceroidModule
from api.comment_reciver.YoutubeCommentReciever import YoutubeCommentReciever

from api.web.notifier import Notifier
import json
from pprint import pprint
import datetime
import traceback
from uuid import uuid4
import uvicorn

#フォルダーがあるか確認
HumanPart.initalCheck()

app = FastAPI()
# プッシュ通知各種設定が定義されているインスタンス
notifier = Notifier()
# クライアントのidと対応するwsを格納する配列類
client_ids: list[str] = []
clients_ws:dict[str,WebSocket] = {}
setting_module = AppSettingModule()
#Humanクラスの生成されたインスタンスを登録する辞書を作成
human_dict:dict[str,Human] = {}
#Humanクラスの生成されたインスタンスをid順に登録する辞書を作成
human_id_dict = []
#使用してる合成音声の種類をカウントする辞書を作成
voiceroid_dict = {"cevio":0,"voicevox":0,"AIVOICE":0,"Coeiroink":0}
gpt_mode_dict = {}
#game_masterのインスタンスを生成
game_master_enable = False
human_queue_shuffle = False
yukarinet_enable = True
nikonama_comment_reciever_list:dict[str,NicoNamaCommentReciever] = {}
new_nikonama_comment_reciever_list:dict[str,newNikonamaCommentReciever] = {}
YoutubeCommentReciever_list:dict[str,YoutubeCommentReciever] = {}
twitchBotList:dict[str,TwitchBot] = {}
epic = Epic()
gpt_agent_dict: dict[str,GPTAgent] = {}
input_reciever = InputReciever(epic ,gpt_agent_dict, gpt_mode_dict)
diary = Memo()


app_setting = JsonAccessor.loadAppSetting()
pprint(app_setting)

if game_master_enable:
    game_master = Human("game_master")
# print("アプリ起動完了")
# Websocket用のパス

@app.on_event("startup")
async def startup_event():
    print("Server is starting...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server is shutting down...")
    # ここに終了処理を書く
    # cevioを起動していたら終了させる
    cevio_shutdowned = False
    for name in human_dict.keys():
        human = human_dict[name]
        if cevio_shutdowned==False and human.voice_system == "cevio":
            try:
                #human.human_Voice.kill_cevio()
                #human.human_Voice.cevio.shutDown()
                shutdowned = True
            except Exception as e:
                print(e)
                print("cevioを終了できませんでした")
    print("cevioを終了しました")
    exit()
    

@app.websocket("/id_create")
async def create_id(websocket: WebSocket):
    await websocket.accept()
    id = str(uuid4())
    while id in client_ids:
        id = str(uuid4())
    client_ids.append(id)
    await websocket.send_text(id)


# この関数が @app.get("./") より上にあるので /app-ts/ はこっちで処理される
@app.get("/app-ts/{path_param:path}")
async def read_app_ts(path_param: str):
    app_ts_dir = Path(__file__).parent.parent.parent / 'app-ts/dist'
    print(str(app_ts_dir))

    print(f"{path_param=}")
    target = app_ts_dir / path_param
    if path_param == "":
        target = app_ts_dir / "index.html"
    elif path_param == "option":
        target = app_ts_dir / "option.html"
    print(f"{target=}")

    # ファイルが存在しない場合は404エラーを返す
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Content-Typeを取得
    content_type, encoding = mimetypes.guess_type(str(target))

    # ファイルを読み込み、Content-Typeとともにレスポンスとして返す
    return FileResponse(str(target), media_type=content_type)

@app.get("/{path_param:path}")
async def read_root(path_param: str):
    # appファイルのルートディレクトリを指定
    app_dir = Path(__file__).parent.parent.parent / 'app'
    print(str(app_dir))

    # パスを取得
    print(f"{path_param=}")
    target = app_dir / path_param
    if path_param == "":
        target = app_dir / "index.html"
    
    if path_param == "newHuman":
        target = app_dir / "index_Human2.html"

    if path_param == "MultiHuman":
        target = app_dir / "index_MultiHuman.html"
    
    if path_param == "settingPage":
        target = app_dir / "setting.html"

    print(f"{target=}")

    # ファイルが存在しない場合は404エラーを返す
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Content-Typeを取得
    content_type, encoding = mimetypes.guess_type(str(target))

    # ファイルを読み込み、Content-Typeとともにレスポンスとして返す
    return FileResponse(str(target), media_type=content_type)



@app.websocket("/ws/{client_id}")
async def websocket_endpoint2(websocket: WebSocket, client_id: str):
    print("リクエスト検知")
    #game_master.reStart()
    # クライアントとのコネクション確立
    await notifier.connect(websocket)
    clients_ws[client_id] = websocket

    try:
        while True:
            # クライアントからメッセージの受け取り
            datas = json.loads(await websocket.receive_text()) 
            message = datas["message"]
            recieve_gpt_mode_dict = Human.convertDictKeyToCharName(datas["gpt_mode"])
            for name in recieve_gpt_mode_dict.keys():
                gpt_mode_dict[name] = recieve_gpt_mode_dict[name]
            input = ""
            input_dict = {}
            json_data = json.dumps(message, ensure_ascii=False)
            #await notifier.push(json_data)
            inputer = ""
            for name,serif in message.items():
                if "選択中" in name:
                    pass
                else:
                    # フロントでのキャラ名で帰ってきてるので、Humanインスタンスのキャラ名に変換
                    char_name = Human.setCharName(name)
                    if char_name not in human_dict:
                        #サーバーだけを再起動したときにここを通るのでhuman_dictを作り直す
                        #name_dataに対応したHumanインスタンスを生成
                        prompt_setteing_num = "キャラ個別システム設定"
                        corresponding_websocket = clients_ws[client_id]
                        tmp_human = Human(name, voiceroid_dict, corresponding_websocket, prompt_setteing_num)
                        #使用してる合成音声の種類をカウント
                        print(f"{tmp_human.voice_system=}")
                        voiceroid_dict[tmp_human.voice_system] = voiceroid_dict[tmp_human.voice_system]+1
                        #humanインスタンスが完成したのでhuman_dictに登録
                        human_dict[tmp_human.char_name] = tmp_human


                    sentence = f"{char_name}:{serif} , "
                    input_dict[char_name] = serif
                    input = input + sentence
                    # インプットしたキャラの名前を取得
                    if "" != serif:
                        inputer = char_name
            print(f"input:{input}")

            #game_masterに状況を考えさせる
            if game_master_enable:
                #game_masterのインスタンスのgenerate_textを実行
                game_master.generate_text(input)
                # 感情パラメータと会話の取得
                game_master.format_response(game_master.response_dict["response"])
                print("game_masterの感情パラメータと会話の取得完了")
                message["game_master"] = game_master.response_dict
                # ブロードキャスト
                json_data = json.dumps(message, ensure_ascii=False)
                await notifier.push(json_data)

            #human_dictのキーをランダムな順番に並べ替えた配列を作成。userではないAIの名前リスト
            human_dict_keys = list(human_dict.keys())
            if True == human_queue_shuffle:
                random.shuffle(human_dict_keys)
            if inputer in human_dict_keys:
                human_dict_keys.remove(inputer)
            pprint(f"{human_dict_keys=}")

            #inputerの音声を生成
            for name in [inputer]:
                #gptには投げない
                print(f"ユーザー：{name}の返答を生成します")
                human_ai:Human = human_dict[name]
                print("yukarinetに投げます")
                print(f"{input_dict=}")
                await epic.appendMessageAndNotify(input_dict)
                print(f"{human_ai.char_name=}")
                if "" != input_dict[human_ai.char_name]:
                    print(f"{input_dict[human_ai.char_name]=}")
                    # # 文章をまず返答
                    # json_data = json.dumps(message, ensure_ascii=False)
                    # print(f"{json_data=}を送信します")
                    # try:
                    #     await notifier.push(json_data)
                    # except Exception as e:
                    #     print(e)
                    #     await websocket.send_json(json_data)
                    
                    
                    for sentence in Human.parseSentenseList(input_dict[human_ai.char_name]):
                        for reciever in nikonama_comment_reciever_list.values():
                            reciever.checkAndStopRecieve(sentence)
                            
                        human_ai.outputWaveFile(sentence)
                        #wavデータを取得
                        wav_info = human_ai.human_Voice.output_wav_info_list
                        #バイナリーをjson形式で送信
                        send_data = {
                            "sentence":{human_ai.front_name:sentence},
                            "wav_info":wav_info,
                            "chara_type":"player"
                        }
                        print(f"{human_ai.char_name}のwavデータを送信します")
                        # await websocket.send_json(json.dumps(wav_info))
                        await websocket.send_json(json.dumps(send_data))
                    # daiaryに保存
                    diary.insertTodayMemo(input_dict[human_ai.char_name])

            sentence_dict4sedn_gpt:str = json_data
            #human_dict_keysの順番にhuman_dictの値を取り出し、それぞれのインスタンスのgenerate_textを実行
            for ai_name in human_dict_keys:
                tmp_input = input
                print(f"{ai_name}の返答を生成します")
                human_ai:Human = human_dict[ai_name]
                #json返答エラー対策処理。２回まで自動で行うがそれ以上上手くいかなければ通す。
                human_ai.response_dict["json返答"] = ""
                error_count = 0
                gpt_mode = "none"#"test"
                pprint(gpt_mode_dict)
                print(f"{ai_name=}")
                if ai_name in gpt_mode_dict:
                    gpt_mode = gpt_mode_dict[ai_name]
                print(f"{gpt_mode=}")
                if gpt_mode == "high":
                    while "成功"!=human_ai.response_dict["json返答"]:
                        response = human_ai.generate_text(tmp_input)
                        # 感情パラメータと会話の取得
                        human_ai.format_response(response)
                        print("感情パラメータと会話の取得完了")
                        # 生成された返答をフロントエンドに送るための辞書に入れる
                        message[human_ai.front_name] = response
                        print("これをフロントに送るよ！")
                        json_data = json.dumps(message, ensure_ascii=False)
                        print(f"{json_data=}を送信します")
                        await notifier.push(json_data)
                        human_ai.execLastResponse()
                        tmp_input = "json形式で答えてね"
                        error_count = error_count + 1
                        if error_count == 2:
                            break
                    
                    if "成功" == human_ai.response_dict["json返答"]:
                        if "wav出力" == human_ai.voice_mode:
                            #wavデータを取得
                            wav_info = human_ai.human_Voice.output_wav_info_list
                            #バイナリーをjson形式で送信
                            await websocket.send_json(json.dumps(wav_info))
                
                elif gpt_mode == "SimpleWait4":

                    input_sentence,sentence_count = human_ai.appendSentence(input_dict[inputer])

                    if sentence_count <= 5 or len(input_sentence) < 77 :
                        continue

                    # prompt_setteing_num を確認し、prompt_setteing_numを1にする
                    if human_ai.human_GPT.prompt_setteing_num != 1:
                        human_ai.resetGPTPromptSetting(1)
                    #シンプルに実行したいので、inputerの文章だけを投げる
                    response_json = human_ai.generate_text_simple_json_4(input_sentence,"gpt-4-1106-preview")
                    #このモードの時はjsonなのでdictに変換
                    response_dict = json.loads(response_json)
                    status = response_dict["status"]
                    response = response_dict["spoken_words"]
                    
                    async def generateVoice(response):
                        # 生成された返答をフロントエンドに送るための辞書に入れる
                        message[human_ai.front_name] = response
                        json_data = json.dumps(message, ensure_ascii=False)
                        print(f"{json_data=}を送信します")
                        try:
                            await notifier.push(json_data)
                        except Exception as e:
                            print(e)
                            await websocket.send_json(json_data)
                        if "wav出力" == human_ai.voice_mode:
                            human_ai.outputWaveFile(response)
                            #wavデータを取得
                            wav_info = human_ai.human_Voice.output_wav_info_list
                            #バイナリーをjson形式で送信
                            print(f"{human_ai.char_name}のwavデータを送信します")
                            await websocket.send_json(json.dumps(wav_info))
                        pprint(response_dict)
                    if status != "wait":
                        await generateVoice(response)
                    human_ai.resetSentence()
                
                elif gpt_mode == "SimpleWait3.5":
                    print("SimpleWait3.5モードです")
                    # GPT3でwaitがあるモード
                    input_sentence,sentence_count = human_ai.appendSentence(input_dict[inputer],inputer)

                    if sentence_count <= random.randint(2,4) or len(input_sentence) < 10 :
                        continue

                    # prompt_setteing_num を確認し、prompt_setteing_numを1にする
                    if human_ai.human_GPT.prompt_setteing_num != 1:
                        human_ai.resetGPTPromptSetting(1)
                    #シンプルに実行したいので、inputerの文章だけを投げる
                    response_json = human_ai.generate_text_simple(input_sentence,"gpt-3.5-turbo")
                    #このモードの時はjsonなのでdictに変換
                    response = human_ai.human_GPT.filterResponse(response_json,human_ai.char_name)
                    print(f"{response=}")
                    human_ai.resetSentence()

                    # 生成された返答をフロントエンドに送るための辞書に入れる
                    message[human_ai.front_name] = response
                    json_data = json.dumps(message, ensure_ascii=False)
                    print(f"{json_data=}を送信します")
                    try:
                        await notifier.push(json_data)
                    except Exception as e:
                        print(e)
                        await websocket.send_json(json_data)
                    if "wav出力" == human_ai.voice_mode:
                        human_ai.outputWaveFile(response)
                        #wavデータを取得
                        wav_info = human_ai.human_Voice.output_wav_info_list
                        #バイナリーをjson形式で送信
                        print(f"{human_ai.char_name}のwavデータを送信します")
                        await websocket.send_json(json.dumps(wav_info))
                    
                    

                
                elif gpt_mode == "low":
                    input_sentence,sentence_count = human_ai.appendSentence(sentence_dict4sedn_gpt)#input_dict[inputer])

                    if human_ai.human_GPT.initSentenceSendingCount == 0:
                        human_ai.human_GPT.initSntenceSend(input_sentence)

                    if sentence_count <= 5 or len(input_sentence) < 77 :
                        continue
                    # prompt_setteing_num を確認し、prompt_setteing_numを0にする
                    if human_ai.human_GPT.prompt_setteing_num != 0:
                        human_ai.resetGPTPromptSetting("キャラ個別システム設定")

                    #シンプルに実行したいので、inputerの文章だけを投げる
                    response = human_ai.generate_text_simple(input_sentence,"gpt-3.5-turbo")
                    human_ai.format_response(response)
                    # 生成された返答をフロントエンドに送るための辞書に入れる
                    message[human_ai.front_name] = response
                    json_data = json.dumps(message, ensure_ascii=False)
                    print(f"{json_data=}を送信します")
                    try:
                        await notifier.push(json_data)
                    except Exception as e:
                        print(e)
                        await websocket.send_json(json_data)
                    if "wav出力" == human_ai.voice_mode:
                        extract_sentence = Human.extractSentence4low(response)
                        for sentence in Human.parseSentenseList(extract_sentence):
                            human_ai.outputWaveFile(sentence)
                            #wavデータを取得
                            wav_info = human_ai.human_Voice.output_wav_info_list
                            #バイナリーをjson形式で送信
                            print(f"{human_ai.char_name}のwavデータを送信します")
                            await human_ai.corresponding_websocket.send_json(json.dumps(wav_info))
                    human_ai.resetSentence()
                    sentence_dict4sedn_gpt = sentence_dict4sedn_gpt + response

                
                elif gpt_mode == "test":
                    # 今の時刻をh時m分s秒で取得
                    now = datetime.datetime.now().strftime('%H時%M分%S秒')
                    # nowから'を取り除く
                    now = now.replace("'", "")
                    response = f"これはgptAIの発話テストモードです:{now=}"
                    human_ai.format_response(response)
                    # 生成された返答をフロントエンドに送るための辞書に入れる
                    message[human_ai.front_name] = response
                    json_data = json.dumps(message, ensure_ascii=False)
                    print(f"{json_data=}を送信します")
                    try:
                        await notifier.push(json_data)
                    except Exception as e:
                        print(e)
                        await websocket.send_json(json_data)
                    if "wav出力" == human_ai.voice_mode:
                        human_ai.outputWaveFile(response)
                        #wavデータを取得
                        wav_info = human_ai.human_Voice.output_wav_info_list
                        #バイナリーをjson形式で送信
                        print(f"{human_ai.char_name}のwavデータを送信します")
                        try:
                            await human_ai.corresponding_websocket.send_json(json.dumps(wav_info))
                        except Exception as e:
                            print(e)
                            print("wav送信エラーです start")
                            print(f"{wav_info=}")
                            print("wav送信エラーです end")
                            #await websocket.send_json(json.dumps(wav_info))

                elif gpt_mode == "none":
                    pass

                    

            
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:ws")
        await notifier.connect(websocket)
        await notifier.push("切れたから再接続")
        #ONE.shutDown()
        # 切れたセッションの削除
        notifier.remove(websocket)


@app.websocket("/old_nikonama_comment_reciver/{room_id}/{front_name}")
async def old_nicowebsocket_endpoint(websocket: WebSocket, room_id: str, front_name: str):
    await websocket.accept()
    char_name = Human.setCharName(front_name)
    print(f"{char_name}で{room_id}のニコ生コメント受信開始")
    update_room_id_query = {
        "ニコ生コメントレシーバー設定": {
            "生放送URL":room_id
        }
    }
    JsonAccessor.updateAppSettingJson(update_room_id_query)
    end_keyword = app_setting["ニコ生コメントレシーバー設定"]["コメント受信停止キーワード"]
    nikonama_comment_reciever = NicoNamaCommentReciever(room_id,end_keyword)
    nikonama_comment_reciever_list[char_name] = nikonama_comment_reciever
    nulvm = NiconamaUserLinkVoiceroidModule()

    async for comment in nikonama_comment_reciever.get_comments():
        pprint(comment)
        if "user_id" in comment:
            user_id = comment["user_id"]
            if "@" in comment["comment"] or "＠" in comment["comment"]:
                print("ユーザーIDとキャラ名を紐づけます")
                char_name = nulvm.registerNikonamaUserIdToCharaName(comment["comment"],user_id)

            comment["char_name"] = nulvm.getCharaNameByNikonamaUser(user_id)
        
            if "/info 3" in comment["comment"]:
                comment["comment"] = comment["comment"].replace("/info 3","")
            
        await websocket.send_text(json.dumps(comment))

@app.post("/old_nikonama_comment_reciver_stop/{front_name}")
async def old_nikonama_comment_reciver_stop(front_name: str):
    char_name = Human.setCharName(front_name)
    if char_name in nikonama_comment_reciever_list:
        print(f"{front_name}のニコ生コメント受信停止")
        nikonama_comment_reciever = nikonama_comment_reciever_list[char_name]
        nikonama_comment_reciever.stopRecieve()
        return

@app.websocket("/nikonama_comment_reciver/{room_id}/{front_name}")
async def nikonama_comment_reciver_start(websocket: WebSocket, room_id: str, front_name: str):
    await websocket.accept()
    char_name = Human.setCharName(front_name)
    print(f"{char_name}で{room_id}のニコ生コメント受信開始")
    update_room_id_query = {
        "ニコ生コメントレシーバー設定": {
            "生放送URL":room_id
        }
    }
    JsonAccessor.updateAppSettingJson(update_room_id_query)
    end_keyword = app_setting["ニコ生コメントレシーバー設定"]["コメント受信停止キーワード"]
    ndgr_client = newNikonamaCommentReciever(room_id, end_keyword)
    new_nikonama_comment_reciever_list[char_name] = ndgr_client
    nulvm = NiconamaUserLinkVoiceroidModule()

    async for NDGRComment in ndgr_client.streamComments():
        # 生のユーザー ID が 0 より上だったら生のユーザー ID を、そうでなければ匿名化されたユーザー ID を表示する
        user_id = NDGRComment.raw_user_id if NDGRComment.raw_user_id > 0 else NDGRComment.hashed_user_id
        content = NDGRComment.content
        date = TimeExtend.convertDatetimeToString(NDGRComment.at)

        comment = {
            "user_id": user_id,
            "comment": content,
            "date": date,
        }

        ExtendFunc.ExtendPrint(comment)
        if "@" in comment["comment"] or "＠" in comment["comment"]:
            print("ユーザーIDとキャラ名を紐づけます")
            char_name = nulvm.registerNikonamaUserIdToCharaName(comment["comment"],user_id)
        comment["char_name"] = nulvm.getCharaNameByNikonamaUser(user_id)
        ExtendFunc.ExtendPrint(comment)
        await websocket.send_text(json.dumps(comment))

@app.post("/nikonama_comment_reciver_stop/{front_name}")
async def nikonama_comment_reciver_stop(front_name: str):
    char_name = Human.setCharName(front_name)
    if char_name in nikonama_comment_reciever_list:
        print(f"{front_name}のニコ生コメント受信停止")
        nikonama_comment_reciever = new_nikonama_comment_reciever_list[char_name]
        nikonama_comment_reciever.stopRecieve()
        return
    
@app.websocket("/YoutubeCommentReceiver/{video_id}/{front_name}")
async def getYoutubeComment(websocket: WebSocket, video_id: str, front_name: str):
    print("YoutubeCommentReceiver")
    await websocket.accept()
    char_name = Human.setCharName(front_name)

    try:
        while True:
            datas:dict = await websocket.receive_json()
            start_stop = datas["start_stop"]
            print(f"{front_name=} , {video_id=} , {start_stop=}")
            if start_stop == "start":
                nulvm = NiconamaUserLinkVoiceroidModule()
                print(f"{char_name}で{video_id}のYoutubeコメント受信開始")
                #コメント受信を開始
                ycr = YoutubeCommentReciever(video_id=video_id)
                YoutubeCommentReciever_list[char_name] = ycr
                async for comment in ycr.fetch_comments(ycr.video_id):
                    print(f"478:{comment=}") # {'author': 'ぴっぴ', 'datetime': '2024-04-20 16:48:47', 'message': 'はろー'}
                    author = comment["author"]
                    if "@" in comment["message"] or "＠" in comment["message"]:
                        print("authorとキャラ名を紐づけます")
                        char_name = nulvm.registerNikonamaUserIdToCharaName(comment["message"],author)

                    comment["char_name"] = nulvm.getCharaNameByNikonamaUser(author)
                    await websocket.send_text(json.dumps(comment))
            else:
                print(f"{char_name}で{video_id}のYoutubeコメント受信停止")
                if char_name in YoutubeCommentReciever_list:
                    YoutubeCommentReciever_list[char_name].stop()
                    del YoutubeCommentReciever_list[char_name]
                    await websocket.close()
    except WebSocketDisconnect:
        print(f"WebSocket disconnected unexpectedly for {char_name} and {video_id}")
        if char_name in YoutubeCommentReciever_list:
            YoutubeCommentReciever_list[char_name].stop()
            del YoutubeCommentReciever_list[char_name]
class TwitchCommentReceiver(BaseModel):
    video_id: str
    front_name: str

@app.post("/RunTwitchCommentReceiver")
async def runTwitchCommentReceiver(req:TwitchCommentReceiver):
    ExtendFunc.ExtendPrint("ツイッチ開始")
    ExtendFunc.ExtendPrint(req)
    video_id = req.video_id
    front_name = req.front_name
    char_name = Human.setCharName(front_name)
    print(f"{char_name}でTwitchコメント受信開始")
    TWTITCH_ACCESS_TOKEN = TwitchBot.getAccessToken()
    twitchBot = TwitchBot(video_id, TWTITCH_ACCESS_TOKEN)
    twitchBotList[char_name] = twitchBot
    twitchBot.run()
    # return {"message":"Twitchコメント受信開始"}

class StopTwitchCommentReceiver(BaseModel):
    front_name: str

@app.post("/StopTwitchCommentReceiver")
async def stopTwitchCommentReceiver(req:StopTwitchCommentReceiver):
    print("Twitchコメント受信停止")
    front_name = req.front_name
    chara_name = Human.setCharName(front_name)
    await twitchBotList[chara_name].stop()
    twitchBotList.pop(chara_name)
    return {"message":"Twitchコメント受信停止"}

@app.websocket("/TwitchCommentReceiver/{video_id}/{front_name}")
async def twitchCommentReceiver(websocket: WebSocket, video_id: str, front_name: str):
    ExtendFunc.ExtendPrint("TwitchCommentReceiver")
    await websocket.accept()
    char_name = Human.setCharName(front_name)
    message_queue:asyncio.Queue[TwitchMessageUnit] = twitchBotList[char_name].message_queue
    nulvm = NiconamaUserLinkVoiceroidModule()
    try:
        while True and char_name in twitchBotList:
            comment = {}
            messageUnit:TwitchMessageUnit = await message_queue.get()
            ExtendFunc.ExtendPrint(f"messageUnit:{messageUnit}")
            message = messageUnit.message
            listener = messageUnit.listner_name
            ExtendFunc.ExtendPrint(f"message:{message}")
            if "@" in message or "＠" in message:
                print("ユーザーIDとキャラ名を紐づけます")
                registered_char_name = nulvm.registerNikonamaUserIdToCharaName(message,listener)
            comment["char_name"] = nulvm.getCharaNameByNikonamaUser(listener)
            comment["comment"] = message
            ExtendFunc.ExtendPrint(comment)
            await websocket.send_text(json.dumps(comment))
            ExtendFunc.ExtendPrint("ツイッチ受信コメントをクライアントに送信完了")
        ExtendFunc.ExtendPrint("TwitchCommentReceiver終了")
    except WebSocketDisconnect:
        ExtendFunc.ExtendPrint(f"WebSocket が切断されました。 for {char_name} and {video_id}")



            


@app.websocket("/InputPokemon")
async def inputPokemon(websocket: WebSocket):
    # クライアントとのコネクション確立
    await notifier.connect(websocket)
    try:
        while True:
            # クライアントからメッセージの受け取り
            data = json.loads(await websocket.receive_text()) 
            # 双方向通信する場合
            #  await websocket.send_text(f"Message text was: {data}")
            # ブロードキャスト
            if type(data) == list:
                for d in data:
                    await notifier.push(f"Message text was: {d}")
            elif type(data) == dict:
                for key in data.keys():
                    await notifier.push(f"Message text was: {data[key]}")
            else:
                print(type(data))
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:InputPokemon")
        # 切れたセッションの削除
        notifier.remove(websocket)

#Websocket用のパス。ボイロ会話用Websocket用のパス。
@app.websocket("/InputGPT")
async def inputGPT(websocket: WebSocket):
    # クライアントとのコネクション確立
    await notifier.connect(websocket)
    tumugi = ChatGPT("つむぎ")
    try:
        while True:
            # クライアントからメッセージの受け取り
            data = json.loads(await websocket.receive_text()) 
            # 双方向通信する場合
            #  await websocket.send_text(f"Message text was: {data}")
            # ブロードキャスト
            if type(data) == list:
                for d in data:
                    await notifier.push(f"あなた: {d}")
                    response = tumugi.generate_text(d)
                    await notifier.push(f"つむぎ：{response}")
            elif type(data) == dict:
                for key in data.keys():
                    await notifier.push(f"あなた: {data[key]}")
                    response = tumugi.generate_text(data[key])
                    await notifier.push(f"つむぎ：{response}")
            elif type(data) == str:
                print("ここ")
                await notifier.push(f"あなた: {data}")
                response = tumugi.generate_text(data)
                await notifier.push(f"つむぎ：{response}")
            else:
                print(type(data))
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:InputGPT")
        # 切れたセッションの削除
        notifier.remove(websocket)

@app.websocket("/human/{client_id}")
async def human_pict(websocket: WebSocket, client_id: str):
     # クライアントとのコネクション確立
    print("humanコネクションします")
    await websocket.accept()
    print("humanコネクション完了！")
    try:
        while True:
            print("データ受け取り開始！")
            # クライアントからキャラクター名のメッセージの受け取り
            name_data = await websocket.receive_text()
            print("human:" + name_data)
            
            if Human.setCharName(name_data) == "":
                print("キャラ名が無効です")
                await websocket.send_json(json.dumps("キャラ名が無効です"))
                continue
            #キャラ立ち絵のパーツを全部送信する。エラーがあったらエラーを返す
            try:
                #name_dataに対応したHumanインスタンスを生成
                prompt_setteing_num = "キャラ個別システム設定"
                corresponding_websocket = clients_ws[client_id]
                tmp_human = Human(name_data, voiceroid_dict, corresponding_websocket, prompt_setteing_num)
                #使用してる合成音声の種類をカウント
                print(f"{tmp_human.voice_system=}")
                voiceroid_dict[tmp_human.voice_system] = voiceroid_dict[tmp_human.voice_system]+1
                #humanインスタンスが完成したのでhuman_dictに登録
                human_dict[tmp_human.char_name] = tmp_human
                #clientにキャラクターのパーツのフォルダの画像のpathを送信
                human_part_folder = tmp_human.image_data_for_client
                await websocket.send_json(json.dumps(human_part_folder))
            except Exception as e:
                print(e)
                traceback.print_exc()
                print("キャラ画像送信エラーです")
                await websocket.send_json(json.dumps("キャラ画像送信エラーです"))
    except WebSocketDisconnect:
        print("wsエラーです:human")
        # 切れたセッションの削除
        notifier.remove(websocket)


class Test(BaseModel):
    test_param: str

@app.post("/test")
async def test(req_body: Test):
    print(req_body.test_param)
    return {"message": "testレスポンス"}

class ResponseMode(str, Enum):
    noFrontName_needBodyParts = "noFrontName_needBodyParts"
    FrontName_needBodyParts = "FrontName_needBodyParts"
    FrontName_noNeedBodyParts = "FrontName_noNeedBodyParts"
    

class PsdFile(BaseModel):
    file: UploadFile
    filename: str
    response_mode: ResponseMode
    front_name: str

class ImageData(BaseModel):
    body_parts_iamges: Any
    init_image_info: Any
    front_name: str
    char_name: str


@app.post("/parserPsdFile")
async def parserPsdFile(
    file: UploadFile = File(...), 
    filename: str = Form(...), 
    response_mode: ResponseMode = Form(...), 
    front_name: str = Form(...)
):
    # file_contents = await req_body.file.read()
    # filename = req_body.filename
    # response_mode = req_body.response_mode
    # front_name = req_body.front_name
    file_contents = await file.read()
    print("ファイル受け取り完了")
    if response_mode == ResponseMode.noFrontName_needBodyParts:
        front_name = Human.pickFrontName(filename)
        #todo front_nameがない場合の処理
        if front_name == "名前が無効です":
            return {"message": "ファイル名が無効です。保存フォルダの推測に使うのでファイル名にキャラクター名を1つ含めてください"}
    # psdファイルが送られてくるので取得
    chara_name = Human.setCharName(front_name)
    # ファイルの保存先を指定
    api_dir = Path(__file__).parent.parent.parent / 'api'
    folder_name = f"{filename.split('.')[0]}"
    folder = str(HumanPart.getVoiroCharaImageFolderPath() / chara_name / folder_name)

    # 保存先のフォルダが存在するか確認。存在する場合はフォルダ名を変更。ゆかり1,ゆかり2があればゆかり3を作成する感じ。
    file_counter = 0
    while os.path.exists(folder):
        file_counter = file_counter + 1
        folder_name = f"{filename.split('.')[0]}_{file_counter}"
        folder = folder = str(HumanPart.getVoiroCharaImageFolderPath() / chara_name / folder_name)
    os.makedirs(folder)
    psd_file = f"{folder}\\{filename}"
    # ファイルの内容を保存
    with open(psd_file, 'wb') as f:
        f.write(file_contents)
    
    # psdファイルをパースして保存
    parser = PsdParserMain(folder,psd_file)
    # CharFilePath.jsonにファイル名を追加
    HumanPart.writeCharFilePathToNewPSDFileName(chara_name,folder_name)
    
    if response_mode == ResponseMode.noFrontName_needBodyParts or response_mode == ResponseMode.FrontName_needBodyParts:
        # パーツを取得
        human_part = HumanPart(chara_name)
        human_part_folder,body_parts_pathes_for_gpt = human_part.getHumanAllPartsFromPath(chara_name,folder)
        # image_data_for_client = ImageData(
        #     body_parts_iamges = human_part_folder["body_parts_iamges"],
        #     init_image_info = human_part_folder["init_image_info"],
        #     front_name = front_name,
        #     char_name = chara_name
        # )
        # return image_data_for_client
        image_data_for_client = {
            "body_parts_iamges": human_part_folder["body_parts_iamges"],
            "init_image_info": human_part_folder["init_image_info"],
            "front_name": front_name,
            "char_name": chara_name
        }
        return image_data_for_client
        
    
    elif response_mode == ResponseMode.FrontName_noNeedBodyParts:
        return {"message": "psdファイルを保存しました。"}
    


class PartsPath(BaseModel):
    folder_name: str
    file_name: str

OnomatopeiaMode = Literal["パク", "パチ", "ぴょこ"]
Status = Literal["開候補", "閉"]

class PatiSetting(BaseModel):
    chara_name: str
    front_name: str
    pati_setting: dict#Dict[OnomatopeiaMode, Dict[Status, List[PartsPath]]]
    now_onomatopoeia_action: dict#Dict[OnomatopeiaMode, List[PartsPath]]



@app.post("/pati_setting")
async def pati_setting(req: PatiSetting):
    chara_name = req.chara_name
    front_name = req.front_name
    pati_setting = req.pati_setting
    now_onomatopoeia_action = req.now_onomatopoeia_action
    
    try:
        human:Human = human_dict[chara_name]
        human.saveHumanImageCombination(pati_setting,"OnomatopeiaActionSetting")
        human.saveHumanImageCombination(now_onomatopoeia_action,"NowOnomatopoeiaActionSetting")
        return {"message": "オノマトペアクション設定の保存に成功しました"}
    except Exception as e:
        print(e)
        return {"message": "オノマトペアクション設定の保存でエラーが発生しました"}
    
    

@app.websocket("/img_combi_save")
async def ws_combi_img_reciver(websocket: WebSocket):
    # クライアントとのコネクション確立
    print("img_combi_saveコネクションします")
    await notifier.connect(websocket)
    try:
        while True:
            # クライアントからメッセージの受け取り
            data = json.loads(await websocket.receive_text())
            pprint(data)
            #受け取ったデータをjsonに保存する
            if type(data) == dict:
                #受け取ったデータをjsonに保存する
                json_data = data["combination_data"]
                human_name = data["chara_name"]
                combination_name = data["combination_name"]
                human:Human = human_dict[human_name]
                #jsonファイルを保存する
                print("jsonファイルを保存します")
                try:
                    human.saveHumanImageCombination(json_data,combination_name)
                    
                    msg = f"jsonファイルの保存に成功しました。"
                    
                except Exception as e:
                    print(e)
                    msg = f"jsonファイルの保存に失敗しました。{e=}"
                print(msg)
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:ws_combi_img_sender")
        # 切れたセッションの削除
        # notifier.remove(websocket)

@app.websocket("/gpt_mode")
async def ws_gpt_mode(websocket: WebSocket):
    # クライアントとのコネクション確立
    print("gpt_modeコネクションします")
    await websocket.accept()
    try:
        while True:
            # クライアントからメッセージの受け取り
            data = json.loads(await websocket.receive_text())
            recieve_gpt_mode_dict = Human.convertDictKeyToCharName(data)
            #受け取ったデータをjsonに保存する
            for name in recieve_gpt_mode_dict.keys():
                gpt_mode_dict[name] = recieve_gpt_mode_dict[name]
            msg = f"gpt_modeの変更に成功しました。{gpt_mode_dict=}"
            print(msg)
            if "individual_process0501dev" not in gpt_mode_dict.values():
                print("individual_process0501devがないので終了します")
                await input_reciever.stopObserveEpic()
                break
                
            
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsを切断:ws_gpt_mode")

@app.websocket("/gpt_routine_test/{front_name}")
async def ws_gpt_routine(websocket: WebSocket, front_name: str):
    # クライアントとのコネクション確立
    print("gpt_routineコネクションします")
    # await websocket.accept()
    # chara_name = Human.setCharName(front_name)
    # if chara_name not in human_dict:
    #     return
    # human = human_dict[chara_name]
    # human_gpt_manager = AgentManager(chara_name, epic)
    # while True:
    #     if gpt_mode_dict[chara_name] == "individual_process0501dev":
    #         start_time_second = TimeExtend()
    #         message_memory = human_gpt_manager.message_memory
    #         latest_message_time = human_gpt_manager.latest_message_time
    #         message = human_gpt_manager.joinMessageMemory(message_memory)
    #         think_agent_response = human_gpt_manager.think_agent.run(message)
    #         if human_gpt_manager.isThereDiffNumMemory(latest_message_time):
    #             continue
    #         serif_agent_response = await human_gpt_manager.serif_agent.run(think_agent_response)
    #         if human_gpt_manager.isThereDiffNumMemory(latest_message_time):
    #             continue
    #         serif_list = human_gpt_manager.serif_agent.getSerifList(serif_agent_response)
    #         for serif_unit in serif_agent_response:
    #             send_data = human_gpt_manager.createSendData(serif_unit, human)
    #             await websocket.send_json(send_data)
    #             # 区分音声の再生が完了したかメッセージを貰う
    #             end_play = await websocket.receive_json()
    #             # 区分音声の再生が完了した時点で次の音声を送る前にメモリが変わってるかチェックし、変わっていたら次の音声を送らない。
    #             if human_gpt_manager.isThereDiffNumMemory(latest_message_time):
    #                 human_gpt_manager.modifyMemory()
    #                 break
    #         else:
    #             # forが正常に終了した場合はelseが実行されて、メモリ解放処理を行う
    #             human_gpt_manager.message_memory = []

@app.websocket("/gpt_routine2/{front_name}")
async def ws_gpt_event_start2(websocket: WebSocket, front_name: str):
    # クライアントとのコネクション確立
    print("gpt_routine2コネクションします")
    await websocket.accept()
    chara_name = Human.setCharName(front_name)
    if chara_name not in human_dict:
        return
    human = human_dict[chara_name]
    
    
    
    agenet_event_manager = AgentEventManager(chara_name, gpt_mode_dict)
    agenet_manager = AgentManager(chara_name, epic, human_dict, websocket, input_reciever)
    gpt_agent = GPTAgent(agenet_manager, agenet_event_manager)
    gpt_agent_dict[chara_name] = gpt_agent

    pipe = asyncio.gather(
        input_reciever.runObserveEpic(),
        agenet_event_manager.setEventQueueArrow(input_reciever, agenet_manager.mic_input_check_agent),
        agenet_event_manager.setEventQueueArrow(agenet_manager.mic_input_check_agent, agenet_manager.speaker_distribute_agent),
        agenet_event_manager.setEventQueueArrowWithTimeOutByHandler(agenet_manager.speaker_distribute_agent, agenet_manager.think_agent),
        agenet_event_manager.setEventQueueArrow(agenet_manager.think_agent, agenet_manager.serif_agent),
        # agenet_event_manager.setEventQueueArrow(agenet_manager.think_agent, )
    )

    # pipeが完了したら通知
    await pipe
    ExtendFunc.ExtendPrint("gpt_routine終了")


@app.websocket("/gpt_routine/{front_name}")
async def ws_gpt_event_start(websocket: WebSocket, front_name: str):
    # クライアントとのコネクション確立
    print("gpt_routineコネクションします")
    await websocket.accept()
    chara_name = Human.setCharName(front_name)
    if chara_name not in human_dict:
        return
    human = human_dict[chara_name]
    
    
    
    agenet_event_manager = AgentEventManager(chara_name, gpt_mode_dict)
    agenet_manager = AgentManager(chara_name, epic, human_dict, websocket, input_reciever)
    gpt_agent = GPTAgent(agenet_manager, agenet_event_manager)
    gpt_agent_dict[chara_name] = gpt_agent

    # 意思決定のパイプラインを作成
    pipe = asyncio.gather(
        input_reciever.runObserveEpic(),
        agenet_event_manager.setEventQueueArrow(input_reciever, agenet_manager.mic_input_check_agent),
        agenet_event_manager.setEventQueueArrow(agenet_manager.mic_input_check_agent, agenet_manager.speaker_distribute_agent),
        agenet_event_manager.setEventQueueArrow(agenet_manager.speaker_distribute_agent, agenet_manager.non_thinking_serif_agent),
        # agenet_event_manager.setEventQueueArrowWithTimeOutByHandler(agenet_manager.speaker_distribute_agent, agenet_manager.think_agent),
        # agenet_event_manager.setEventQueueConfluenceArrow([agenet_manager.non_thinking_serif_agent, agenet_manager.think_agent], agenet_manager.serif_agent)
        # agenet_event_manager.setEventQueueArrow(agenet_manager.think_agent, )
    )

    # pipeが完了したら通知
    await pipe
    ExtendFunc.ExtendPrint("gpt_routine終了")

@app.websocket("/gpt_routine3/{front_name}")
async def wsGptGraphEventStart(websocket: WebSocket, front_name: str):
    # クライアントとのコネクション確立
    print("gpt_routineコネクションします")
    await websocket.accept()
    chara_name = Human.setCharName(front_name)
    if chara_name not in human_dict:
        return
    human = human_dict[chara_name]

    life_process_brain = LifeProcessBrain(chara_name, websocket)
    
    agenet_event_manager = AgentEventManager(chara_name, gpt_mode_dict)
    agenet_manager = AgentManager(chara_name, epic, human_dict, websocket, input_reciever)
    gpt_agent = GPTAgent(agenet_manager, agenet_event_manager)
    gpt_agent_dict[chara_name] = gpt_agent

    # 意思決定のパイプラインを作成
    # 目標の生成とタスクグラフの生成を行いたい。入力を受け取ると、目標を生成し、タスクグラフを生成する。これ以外に目標を生成する方法はあるのか？
    # 入力から目標を生成する過程はどうなっているのか？
    pipe = asyncio.gather(
        input_reciever.runObserveEpic(),
        agenet_event_manager.setEventQueueArrow(input_reciever, agenet_manager.mic_input_check_agent),
        agenet_event_manager.setEventQueueArrowToCreateTask(input_reciever, life_process_brain),
        agenet_event_manager.setEventQueueArrow(agenet_manager.mic_input_check_agent, agenet_manager.speaker_distribute_agent),
        agenet_event_manager.setEventQueueArrow(agenet_manager.speaker_distribute_agent, agenet_manager.non_thinking_serif_agent),
        # agenet_event_manager.setEventQueueArrowWithTimeOutByHandler(agenet_manager.speaker_distribute_agent, agenet_manager.think_agent),
        # agenet_event_manager.setEventQueueConfluenceArrow([agenet_manager.non_thinking_serif_agent, agenet_manager.think_agent], agenet_manager.serif_agent)
        # agenet_event_manager.setEventQueueArrow(agenet_manager.think_agent, )
    )

    # pipeが完了したら通知
    await pipe
    ExtendFunc.ExtendPrint("gpt_routine終了")



class Item(BaseModel):
    type: str
    data: str
@app.post("/ShortCut")
async def receive_data(item: Item):
    print("ShortCut")
    pprint(item)



# ブロードキャスト用のAPI
@app.get("/push/{message}")
async def push_to_connected_websockets(message: str):
    # ブロードキャスト
    print("ブロードキャスト")
    await notifier.push(f"! Push notification: {message} !")

# サーバ起動時の処理
@app.on_event("startup")
async def startup():
    # プッシュ通知の準備
    await notifier.generator.asend(None)

# 設定の状態を取得、管理、配信するAPI
@app.websocket("/settingStore/{client_id}/{setting_name}/{mode_name}")
async def settingStore(websocket: WebSocket, setting_name: str, mode_name:PageMode, client_id: str):
    print("settingStoreコネクションします")
    await websocket.accept()
    setting_module.addWs(setting_name, mode_name, client_id, websocket)
    try:
        while True:
            # クライアントからメッセージの受け取り
            data = await websocket.receive_json()
            pprint(data)
            #受け取ったデータをjsonに保存する
            if type(data) != dict:
                print("データがdict型ではありません")
                continue
            new_setting = setting_module.setSetting(setting_name, mode_name, data, {})
            await setting_module.notify(new_setting, setting_name)

    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:settingStore")






if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8020, lifespan="on")
