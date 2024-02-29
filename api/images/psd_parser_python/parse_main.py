import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from parser2 import PSDParser
import converter2voiroidAIImage
from psd_tools import PSDImage
import os

class PsdParserMain:
    def __init__(self,folder:str,input:str):
        output = f"{folder}\\tmp_output2"
        os.makedirs(output, exist_ok=True)

        # コピー先のディレクトリの絶対パス。バックスラッシュは2つずつ書くこと。
        conv_in= output
        conv_out=f"{folder}\\Parts"
        os.makedirs(conv_out, exist_ok=True)



        mode = 1
        psd = PSDImage.open(input)
        psd_parser = PSDParser()
        if mode==0:
            psd_parser.save_layers(psd, output,0)
        if mode==1:
            for now_layer_counter,layer in enumerate(psd):
                psd_parser.save_layers(layer, output, now_layer_counter+1)



        # フォルダの正規化
        converter2voiroidAIImage.normalizeFolder(conv_in)
        # コピー元ディレクトリ内の最も深い階層にあるフォルダを取得する
        converter2voiroidAIImage.copyDeepestFolder(conv_in,conv_out)

if __name__ == "__main__":
    folder = f"C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\images\\ボイロキャラ素材\\フィーちゃん\\もちもちフィーちゃん_2"
    input  = f"C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\images\\ボイロキャラ素材\\フィーちゃん\\もちもちフィーちゃん_オリジナル\\もちもちフィーちゃん.psd"
    parser = PsdParserMain(folder,input)