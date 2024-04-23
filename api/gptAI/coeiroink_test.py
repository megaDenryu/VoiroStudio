import json

import requests

class CoeiroinkAPI:
    DEFAULT_SERVER = "http://127.0.0.1:50032"
    server = DEFAULT_SERVER

    # ステータスを取得する
    @staticmethod
    def get_status(print_error=False) -> str:
        try:
            response = requests.get(f"{CoeiroinkAPI.server}/")
            response.raise_for_status()
            return response.json()["status"]
        except Exception as err:
            if print_error:
                print(err)
            return None

    # 話者リストを取得する
    @staticmethod
    def get_speakers(print_error=False) -> {}:
        try:
            response = requests.get(f"{CoeiroinkAPI.server}/v1/speakers")
            response.raise_for_status()
            return response.json()
        except Exception as err:
            if print_error:
                print(err)
            return None

    # スタイルIDから話者情報を取得する
    @staticmethod
    def get_speaker_info(styleId: int, print_error=False) -> {}:
        try:
            post_params = {"styleId": styleId}
            response = requests.post(f"{CoeiroinkAPI.server}/v1/style_id_to_speaker_meta", params=post_params)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            if print_error:
                print(err)
            return None

    # テキストの読み上げ用データを取得する
    @staticmethod
    def estimate_prosody(text: str, print_error=False) -> {}:
        try:
            post_params = {"text": text}
            response = requests.post(f"{CoeiroinkAPI.server}/v1/estimate_prosody", data=json.dumps(post_params))
            response.raise_for_status()
            return response.json()
        except Exception as err:
            if print_error:
                print(err)
            return None

    # 音声データを生成する
    @staticmethod
    def synthesis(speaker: {}, text: str, prosody: {},
                  speedScale = 1, volumeScale = 1, pitchScale = 0, intonationScale = 1,
                  prePhonemeLength = 0.1, postPhonemeLength = 0.1, outputSamplingRate = 24000, print_error=False) -> bytes:
        post_params = {
            "speakerUuid": speaker["speakerUuid"],
            "styleId": speaker["styleId"],
            "text": text,
            "prosodyDetail": prosody["detail"],
            "speedScale": speedScale,
            "volumeScale": volumeScale,
            "pitchScale": pitchScale,
            "intonationScale": intonationScale,
            "prePhonemeLength": prePhonemeLength,
            "postPhonemeLength": postPhonemeLength,
            "outputSamplingRate": outputSamplingRate
        }
        try:
            response = requests.post(f"{CoeiroinkAPI.server}/v1/synthesis", data=json.dumps(post_params))
            response.raise_for_status()
            return response.content
        except Exception as err:
            if print_error:
                print(err)
            return None

    # 音声データを生成する
    @staticmethod
    def get_wave_data(styleId: int, text: str,
                      speedScale = 1, volumeScale = 1, pitchScale = 0, intonationScale = 1,
                      prePhonemeLength = 0.1, postPhonemeLength = 0.1, outputSamplingRate = 24000, print_error=False) -> bytes:

        speaker = CoeiroinkAPI.get_speaker_info(styleId)
        if speaker is None:
            return None
        
        prosody = CoeiroinkAPI.estimate_prosody(text)
        if prosody is None:
            return None
        
        return CoeiroinkAPI.synthesis(speaker, text, prosody,
                                      speedScale, volumeScale, pitchScale, intonationScale,
                                      prePhonemeLength, postPhonemeLength, outputSamplingRate, print_error)
    
if __name__ == "__main__":
    # テスト
    wav = CoeiroinkAPI.get_wave_data(1315987311, "こんにちは、私はAIです。")
    # 音声をファイルに保存
    with open("test.wav", "wb") as f:
        f.write(wav)