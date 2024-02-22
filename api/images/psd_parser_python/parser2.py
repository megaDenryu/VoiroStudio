import psd_tools
from psd_tools import compose

from PIL import Image, ImageDraw,ImageFilter
import os

import json

class PSDParser:
    def __init__(self):
        self.invalid_chars = ["\\","/",":","*","?","!","<",">","|"," ","　"]
        self.layer_counter_interval = 10
        self.error_layer_paths = []
    def save_layers(self,layer, path, now_layer_counter):
        if layer.kind == 'group':
            folder_name = self.validate_path(layer.name)
            folder_path = f"{path}\\{now_layer_counter * self.layer_counter_interval}_{folder_name}"
            os.makedirs(folder_path, exist_ok=True)
            child_layer_counter = 1
            for child in layer:
                self.save_layers(child, folder_path, child_layer_counter)
                child_layer_counter += 1
        elif layer.kind == 'pixel':
            layer_image = layer.topil()
            file_name = self.validate_path(layer.name)
            file_path = f"{path}\\{now_layer_counter * self.layer_counter_interval}_{file_name}.png"
            try:
                # 画像保存処理
                layer_image.save(file_path)
                #json保存処理
                layer_info = self.get_layer_info(layer,now_layer_counter)
                self.save_layer_info(layer_info, f"{path}\\{now_layer_counter * self.layer_counter_interval}_{file_name}.json")
            except:
                # 画像保存失敗時はエラー処理をする必要がある
                print(f"Error: {file_path}")

            

    def validate_path(self,path):
        for invalid_char in self.invalid_chars:
            path = path.replace(invalid_char,"")
        return path

    #layer情報取得関数
    def get_layer_info(self, layer,now_layer_counter):
        return {
            "name": f"{now_layer_counter}_{layer.name}.png",
            "x": layer.left,
            "y": layer.top,
            "width": layer.width,
            "height": layer.height
        }

    #layer情報保存関数
    def save_layer_info(self, layer_info, path):
        with open(path, 'w') as f:
            json.dump(layer_info, f)
    

# 以下メイン処理
if __name__ == "__main__":
    from psd_tools import PSDImage
    psd = PSDImage.open('C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\images\\ボイロキャラ素材\\IA\\kulori IA 立ち絵\\kulori IA 立ち絵_テスト\\kulori IA 立ち絵.psd')
    output = f"C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\images\\ボイロキャラ素材\\IA\\kulori IA 立ち絵\\kulori IA 立ち絵_テスト\\test_img"
    mode = 1
    psd_parser = PSDParser()
    if mode==0:
        psd_parser.save_layers(psd, output,0)
    if mode==1:
        for now_layer_counter,layer in enumerate(psd):
            psd_parser.save_layers(layer, output, now_layer_counter+1)