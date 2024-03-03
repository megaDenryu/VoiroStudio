import sys
from pathlib import Path
import os
import random
sys.path.append('../..')
from api.gptAI.gpt import ChatGPT
from api.gptAI.voiceroid_api import cevio_human
from api.gptAI.Human import Human
from api.images.image_manager.HumanPart import HumanPart
from api.images.psd_parser_python.parse_main import PsdParserMain
from api.Extend.ExtendFunc import ExtendFunc

from enum import Enum

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from starlette.websockets import WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


from typing import Dict, List, Any

import mimetypes

from api.comment_reciver.comment_module import NicoNamaCommentReciever
from api.comment_reciver.NiconamaUserLinkVoiceroidModule import NiconamaUserLinkVoiceroidModule

from notifier import Notifier
import json
from pprint import pprint
import datetime
import traceback
from uuid import uuid4



app = FastAPI()
# プッシュ通知各種設定が定義されているインスタンス
notifier = Notifier()
# クライアントのidと対応するwsを格納する配列類
client_ids: list[str] = []
clients_ws:dict[str,WebSocket] = {}
#Humanクラスの生成されたインスタンスを登録する辞書を作成
human_dict:dict = {}
#Humanクラスの生成されたインスタンスをid順に登録する辞書を作成
human_id_dict = []
#使用してる合成音声の種類をカウントする辞書を作成
voiceroid_dict = {"cevio":0,"voicevox":0,"AIVOICE":0}
gpt_mode_dict = {}
#game_masterのインスタンスを生成
game_master_enable = False
human_queue_shuffle = False
yukarinet_enable = True
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
    print(f"{target=}")

    # ファイルが存在しない場合は404エラーを返す
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Content-Typeを取得
    content_type, encoding = mimetypes.guess_type(str(target))

    # ファイルを読み込み、Content-Typeとともにレスポンスとして返す
    return FileResponse(str(target), media_type=content_type)

    

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
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
                print(f"{human_ai.char_name=}")
                if "" != input_dict[human_ai.char_name]:
                    print(f"{input_dict[human_ai.char_name]=}")
                    # 文章をまず返答
                    json_data = json.dumps(message, ensure_ascii=False)
                    print(f"{json_data=}を送信します")
                    try:
                        await notifier.push(json_data)
                    except Exception as e:
                        print(e)
                        await websocket.send_json(json_data)
                    
                    
                    for sentence in Human.parseSentenseList(input_dict[human_ai.char_name]):
                        human_ai.outputWaveFile(sentence)
                        #wavデータを取得
                        wav_info = human_ai.human_Voice.output_wav_info_list
                        #バイナリーをjson形式で送信
                        print(f"{human_ai.char_name}のwavデータを送信します")
                        await websocket.send_json(json.dumps(wav_info))

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
                
                elif gpt_mode == "SimpleWait":

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
                    if status != "wait":
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
                        human_ai.resetSentence()
                
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


@app.websocket("/nikonama_comment_reciver/{room_id}/{front_name}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, front_name: str):
    await websocket.accept()
    char_name = Human.setCharName(front_name)
    print(f"{char_name}で{room_id}のニコ生コメント受信開始")
    nikonama_comment_reciever = NicoNamaCommentReciever(room_id)
    nulvm = NiconamaUserLinkVoiceroidModule()

    async for comment in nikonama_comment_reciever.get_comments():
        pprint(comment)
        if "user_id" in comment:
            user_id = comment["user_id"]
            if "@" in comment["comment"] or "＠" in comment["comment"]:
                print("ユーザーIDとキャラ名を紐づけます")
                char_name = nulvm.registerNikonamaUserIdToCharaName(comment["comment"],user_id)

            comment["char_name"] = nulvm.getCharaNameByNikonamaUser(user_id)
            
            

        
            
        await websocket.send_text(json.dumps(comment))

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
    #await notifier.connect(websocket)
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
    if response_mode == ResponseMode.noFrontName_needBodyParts:
        front_name = Human.pickFrontName(filename)
        #todo front_nameがない場合の処理
        if front_name == "名前が無効です":
            return {"message": "ファイル名が無効です。保存フォルダの推測に使うのでファイル名にキャラクター名を1つ含めてください"}
    # psdファイルが送られてくるので取得
    chara_name = Human.setCharName(front_name)
    # ファイルの保存先を指定
    api_dir = Path(__file__).parent.parent.parent / 'api'
    print(str(api_dir))
    folder_name = f"{filename.split('.')[0]}"
    folder = f"{str(api_dir)}\\images\\ボイロキャラ素材\\{chara_name}\\{folder_name}"

    # 保存先のフォルダが存在するか確認。存在する場合はフォルダ名を変更。ゆかり1,ゆかり2があればゆかり3を作成する感じ。
    file_counter = 0
    while os.path.exists(folder):
        file_counter = file_counter + 1
        folder_name = f"{filename.split('.')[0]}_{file_counter}"
        folder = f"{str(api_dir)}\\images\\ボイロキャラ素材\\{chara_name}\\{folder_name}"
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
        image_data_for_client = ImageData(
            body_parts_iamges = human_part_folder["body_parts_iamges"],
            init_image_info = human_part_folder["init_image_info"],
            front_name = front_name,
            char_name = chara_name
        )
        return image_data_for_client
    
    elif response_mode == ResponseMode.FrontName_noNeedBodyParts:
        return {"message": "psdファイルを保存しました。"}
    
    

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
                await notifier.push(msg)
                
            
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsエラーです:ws_combi_img_sender")
        # 切れたセッションの削除
        notifier.remove(websocket)

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
                
            
    # セッションが切れた場合
    except WebSocketDisconnect:
        print("wsを切断:ws_gpt_mode")



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

