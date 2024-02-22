import requests
import json
import time
import re
#import simpleaudio

def audio_query(text, speaker, max_retry):
    # 音声合成用のクエリを作成する
    query_payload = {"text": text, "speaker": speaker}
    for query_i in range(max_retry):
        r = requests.post("http://localhost:50021/audio_query", 
                        params=query_payload, timeout=(10.0, 300.0))
        if r.status_code == 200:
            query_data = r.json()
            break
        time.sleep(1)
    else:
        raise ConnectionError("リトライ回数が上限に到達しました。 audio_query : ", "/", text[:30], r.text)
    return query_data
def synthesis(speaker, query_data,max_retry):
    synth_payload = {"speaker": speaker}
    for synth_i in range(max_retry):
        r = requests.post("http://localhost:50021/synthesis", params=synth_payload, 
                          data=json.dumps(query_data), timeout=(10.0, 300.0))
        if r.status_code == 200:
            #音声ファイルを返す
            return r.content
        time.sleep(1)
    else:
        raise ConnectionError("音声エラー：リトライ回数が上限に到達しました。 synthesis : ", r)


def text_to_speech(texts, speaker=8, max_retry=20):
    if texts==False:
        texts="ちょっと、通信状態悪いかも？"
    texts=re.split("(?<=！|。|？)",texts)
    play_obj=None
    for text in texts:
        # audio_query
        query_data = audio_query(text,speaker,max_retry)
        # synthesis
        voice_data=synthesis(speaker,query_data,max_retry)
        #音声の再生
        with open("audio.wav", "wb") as f:
            f.write(voice_data)

        """
        if play_obj != None and play_obj.is_playing():
            play_obj.wait_done()
        wave_obj=simpleaudio.WaveObject(voice_data,1,2,24000)
        play_obj=wave_obj.play()
        """
        
if __name__ == "__main__": 
    text_to_speech("あーし、ホロライブの「あずきダンス」大好きなんだよ！最高にハッピーで元気な曲だし、いつも気分を上げてくれるんだ。憂鬱な時や、 楽しい時間を過ごしたい時に聴くのが大好きな曲なんだ。歌詞がキャッチーで、ビートが元気づけるから、踊りたくなるよね！きっと、気合いを入れる時に最適な曲だよ！")