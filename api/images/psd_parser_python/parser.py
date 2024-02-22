import psd_tools
from psd_tools import compose
from psd_tools import PSDImage
from PIL import Image, ImageDraw,ImageFilter
import os

def main():

    mode = "main"

    #このファイルが存在するディレクトリパスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    #current_dir = "api/images/psd_parser_python"
    psd_file_name = 'kuloriIA立ち絵.psd'#"あかねちゃんver1.31（標準）.psd"

    #psd_file_path = "C:\\Users\\pokr301qup\\python_dev\\poke-fastapi-websockets\\api\\images\\ボイロキャラ素材\\すずきつづみ\\kulori すずきつづみ立ち絵\\kulori すずきつづみ立ち絵\\kulori つづみ立ち絵.psd"
    #psd_file_name = "ONE_1202.psd"
    #'api/images/psd_parser_python/ONE_1202.psd'
    psd = PSDImage.open(f'{current_dir}/{psd_file_name}')

    parser_project = ParserProject(psd,current_dir,psd_file_name)
    if mode == "main":
        parser_project.mainProcess()
    elif mode == "test":
        parser_project.showFileStructure()


class ParserProject:
    def __init__(self,psd:PSDImage,current_dir,psd_file_name):
        #psdファイルのパスなど
        self.psd = psd
        self.current_dir = current_dir
        self.psd_file_name = psd_file_name
        self.parts_folder_name = psd_file_name.replace(".psd","")

        #無効な文字の配列
        self.invalid_chars = ["\\","/",":","*","?","\"","<",">","|"," "]

        #カウンター
        self.psd_pixel_layer_size = 0
        self.psd_group_layer_size = 0

        # imagemagickを使うかどうか
        self.use_imagemagick = True

    def mainProcess(self):
        # 全てのGroupを可視化し、全てのPixelLayerを不可視化する
        for layer in self.psd:
            self.recursiveLayerVisible(layer)
        
        if self.use_imagemagick:
            #imagemagickを使う場合はさらにレイヤーもすべて不可視化する
            for layer in self.psd:
                layer.visible = False

        # psdファイルのサイズを取得し、カウンターを初期化する
        self.psd_pixel_layer_size = self.pixel_counter
        self.pixel_counter = 0
        self.psd_group_layer_size = self.group_counter
        self.group_counter = 0

        # psdファイル名から.psdをを抜いた名前でパーツ画像を保存するフォルダを作成する
        os.makedirs(f'{self.current_dir}/{self.parts_folder_name}', exist_ok=True)

        # psdファイルの全てのPixelLayerを一つずつ可視化し、pngとして保存する
        for num_layer,layer in enumerate(self.psd):
            if self.use_imagemagick:
                #imagemagickを使う場合は最初に各レイヤーを一つずつ可視化する
                layer.visible = True

            if layer.is_group():
                self.recursiveSaveLayer(layer,num_layer,f'{self.current_dir}/{self.parts_folder_name}')
            elif layer.kind == 'pixel':
                #無効な文字を削除して、保管するフォルダ名にする
                folder_name = layer.name
                for invalid_char in self.invalid_chars:
                    folder_name = folder_name.replace(invalid_char,"")                
                # 保管フォルダのパスを作成する
                path_name = f'{self.current_dir}/{self.parts_folder_name}/{num_layer}{folder_name}'
                # 保管フォルダを作成する
                os.makedirs(path_name, exist_ok=True)
                self.recursiveSaveLayer(layer,num_layer,path_name)
            else:
                print("例外========================:",layer)
            
            if self.use_imagemagick:
                #imagemagickを使う場合はこのループの最後にこのレイヤーを不可視化する
                layer.visible = False
   
    def recursiveLayerVisible(self,layer):
        """
        現在LayerがGroupならば、可視化し、再帰的に子レイヤーを処理する
        現在LayerがPixelLayerならば、不可視化する
        @param layer:psd_tools.api.layers.Layer
        """
        if layer.is_group():
            self.groupLayerCounter()
            if self.use_imagemagick:
            #imagemagickを使う場合は全てのレイヤーを不可視化する
                layer.visible = False
            else:
                layer.visible = True
            for child in layer:
                self.recursiveLayerVisible(child)
        else:
            self.pixelLayerCounter()
            layer.visible = False

    def recursiveSaveLayer(self,layer,num_layer,parent_name):
        """
        recursiveLayerVisible()を実行して、
        - グループを全て可視化し、
        - PixelLayerを全て不可視化
        した後に実行すること。

        現在LayerがGroupならば、フォルダを作成し、再帰的に子レイヤーを処理する
        現在LayerがPixelLayerならば、画像を保存する
        @param layer:psd_tools.api.layers.Layer
        @param num_layer:現在のレイヤーの番号。フォルダ名、ファイル名に使用する
        """

        #フォルダ名、ファイル名に使用する名前を作成する。無効な文字を削除して、補完するフォルダ名にする
        folder_file_name = layer.name
        for invalid_char in self.invalid_chars:
            folder_file_name = folder_file_name.replace(invalid_char,"")

        #pathを作成する
        path_name = f'{parent_name}/{num_layer}_{folder_file_name}'
        
        #layerの種類で処理を分ける
        if layer.is_group():
            #現在layerがグループなら、フォルダを作成
            os.makedirs(path_name, exist_ok=True)
            print(f"フォルダー {self.groupLayerCounter()}/{self.psd_group_layer_size} : ****{path_name}****")
            #再帰的に子レイヤーを処理する
            if self.use_imagemagick:
                layer.visible = True
            for child_num,child in enumerate(layer):
                self.recursiveSaveLayer(child,child_num,path_name)
            if self.use_imagemagick:
                layer.visible = False
        elif layer.kind == 'pixel':
            #現在layerがpixelなら、visibleをTrueにして、getPartsImage(self.psd)で画像を保存する
            layer.visible = True
            if self.use_imagemagick:
                #imagemagickを使う場合はまずこのpsdを保存する
                self.psd.save(f"tmp4convert.psd")
                #imagemagickを使って、psdをpngに変換する
                #os.system(f"magick convert -strip -dispose Background tmp4convert.psd[0] {path_name}.png")
                os.system(f"magick convert -background none -flatten tmp4convert.psd {path_name}.png")
                #os.system(f"magick convert -strip tmp4convert.psd[1-] -layers merge {path_name}.png")
                exported_file_name = f"{path_name}.png"
            else:
                exported_file_name = self.getPartsImage(self.psd,path_name)
            print(f"    {self.pixelLayerCounter()}/{self.psd_pixel_layer_size} : ---------------------{exported_file_name}-------------------------")
            #visibleをFalseに戻す
            layer.visible = False
        else:
            print("例外========================:",layer)
    
    def allRawImageExportAndRename(self):
        """
        1:psdファイル内の画像を番号順でpngファイルに変換
        """

    @staticmethod
    def getPartsImage(psd:PSDImage,name):
        """
        param layer:psd_tools.api.layers.Layer
        param name:保存するファイル名.'api/images/psd_parser_python/ONE_1202_全身.png'など。拡張子はpngであること。
        """
        #psd.composite()で、レイヤーを合成する。背景は透明にするために、パーツに使われてない色にする。今は緑色。
        r = 0.0
        g = 1.0
        b = 0.0
        all_image = psd.composite(color=(r,g,b),alpha=1.0,layer_filter=lambda layer: layer.is_visible())
        #背景を透明にするために画像にアルファチャンネルを追加する
        all_image.putalpha(255)
        #一度画像を保存する
        #all_image.save(f"{name}_opaque.png")
        # 設定した背景色を抜いて保存する。https://qiita.com/Kent-747/items/e3a678c110cd7be35add を参照した。
        #all_image = Image.open(name)
        all_image.convert("RGBA")
        datas = all_image.getdata()
        newData = []
        for item in datas:
            if item[0] == int(255*r) and item[1] == int(255*g) and item[2] == int(255*b):
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        all_image.putdata(newData)

        try:
            all_image.save(f"{name}.png",'PNG')
            return f"{name}.png"
        except Exception as e:
            return f"{name}.pngが保存できませんでした。{e}"

    def showFileStructure(self):
        """
        ファイル構造を表示する
        """
        for layer in self.psd:
            self.recursiveFileStructure(layer)
    
    def recursiveFileStructure(self,layer):
        """
        再帰的にファイル構造を表示する
        @param layer:psd_tools.api.layers.Layer
        """
        
        if layer.is_group():
            print(f"{self.groupLayerCounter()}****************group : {layer} ****************")
            for child in layer:
                self.recursiveFileStructure(child)
        elif layer.kind == 'pixel':
            print(f"画像{layer}------------{self.pixelLayerCounter()}")
        else:
            print("例外========================:",layer)
    def pixelLayerCounter(self):
        """
        このメソッドを呼び出した回数を表示する
        """
        #counterが存在しない場合は、作成する
        if not hasattr(self,"pixel_counter"):
            self.pixel_counter = 0
        self.pixel_counter += 1
        return self.pixel_counter
    def groupLayerCounter(self):
        """
        このメソッドを呼び出した回数を表示する
        """
        #counterが存在しない場合は、作成する
        if not hasattr(self,"group_counter"):
            self.group_counter = 0
        self.group_counter += 1
        return self.group_counter
#再帰的にレイヤーを取得
"""
param layer:psd_tools.api.layers.Layer
param visible:レイヤーの可視性.デフォルトは"no"で、可視性を変更しない
              trueで全て可視化、falseで全て不可視化
"""


def getLayers(layer,visible = "no"):
    if visible != "no":
        layer.visible = visible
    if layer.is_group():
        print(f"****************group : {layer} ****************")
        for child in layer:
            getLayers(child,visible)
    else:
        print(layer)
    
def get_parts_image(psd):
    all_image = psd.composite(color=(1.0,0.0,0.0),alpha=1.0,layer_filter=lambda layer: layer.is_visible())
    all_image.putalpha(255)
    all_image.save('api/images/psd_parser_python/ONE_1202_全身.png')
    #all_image.putalpha(128)
    # 背景を白抜きして保存する。https://qiita.com/Kent-747/items/e3a678c110cd7be35addを参照した。
    all1_image = Image.open('api/images/psd_parser_python/ONE_1202_全身.png')
    all1_image.convert("RGBA")
    datas = all1_image.getdata()
    print(datas)
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 0 and item[2] == 0:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    all1_image.putdata(newData)

    all1_image.save('api/images/psd_parser_python/ONE_1202_全身1.png','PNG')
    print("---------------------------------------------------")

    # 見えなくなっているレイヤーを見えるようにして画像を保存する
    #print(parser.layer_list)
    #parser.psd.compose(parser.layer_list).save('api/images/psd_parser_python/ONE_1202_visible.png')
    
        

class Parser:
    def __init__(self,psd):
        self.psd = psd
        self.layer_list = []

    #一番大きいレイヤーを取得

    #このレイヤーに一つだけマスクする

    #再帰的にレイヤーを取得
    def get_layers(self,layer,visible = "no"):
        if visible != "no":
            layer.visible = visible
        if layer.is_group():
            print(f"****************group : {layer} ****************")
            for child in layer:
                self.get_layers(child,visible)
        else:
            print(layer)
            self.layer_list.append(layer)

    def clip(self,layer):
        layer.clipping = True
        print(layer.clip_layers)



def parse_psd(psd):
    for layer in psd:
        #layer.nameのフォルダを作成
        if layer.is_group():
            path = 'api/images/psd_parser_python/image/' + layer.name
            os.makedirs(path, exist_ok=True)
            for child in layer:
                #レイヤーの名前を取得
                image_name = child.name
                # 名前に*が含まれている場合は*を削除
                if "*" in image_name:
                    image_name = image_name.replace("*", "")
                print(image_name)
                #レイヤーの画像を取得、保存。例外処理
                try:
                     child.composite().save(path + "/" + image_name + ".png")
                except:
                    print("例外処理")
        else:
            layer_name = layer.name
            # 名前に*が含まれている場合は*を削除
            if "*" in layer_name:
                layer_name = layer_name.replace("*", "")
            print(layer_name)
            #レイヤーの画像を取得、保存
            try:
                layer.composite().save('api/images/psd_parser_python/image/' + layer_name + ".png")
            except:
                print("例外処理")
    
       


#レイヤーの名前を取得
def get_layer_name(layer):
    if layer.is_group():
        return layer.name
    else:
        return layer.name
#レイヤーの画像を取得
def get_layer_image(layer):
    if layer.is_group():
        return None
    else:
        return layer.composite()



main()





