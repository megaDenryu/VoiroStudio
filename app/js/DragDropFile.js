/**
 * お部屋の要素を取得する
 * 要素にイベントリスナーをオブジェクトを設定する
 * ファイルを開く
 * サーバーにファイルを送信する
 * 
 * 「要素にドラッグドロップでファイルを受け付けて、ファイルを検査して一致するファイルを取得する」
 */

class DragDropFile{

    /** @type {Element}*/ human_tab
    /** @type {Element}*/ human_window
    /** @type {HTMLElement}*/ human_name
    /** @type {Element}*/ human_images
    /** @type {string}*/ target_voiceroid_front_name

    /** 
     * @param {Element} human_tab */
    constructor(human_tab){
        this.human_tab = human_tab;
        this.human_window = this.human_tab.getElementsByClassName("human_window")[0];
        this.human_name = /** @type {HTMLElement}*/ (this.human_tab.getElementsByClassName("human_name")[0]);
        this.human_images = this.human_tab.getElementsByClassName("human_images")[0];
        this.target_voiceroid_front_name = "????";
        human_tab.addEventListener("click", this);
        human_tab.addEventListener("drop", this);
        human_tab.addEventListener("dragover", this);

    }

    handleEvent(/** @type {DragEvent}*/event){
        //これがないと、ドラッグドロップができない
        event.preventDefault();

        if(event.type == "click"){
            console.log("ファイルがドラッグされています。")
            //POST確認
            fetch(`http://localhost:${port}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({test_param: "testだよ茜ちゃん"})
            }).then(response => response.json())
            .then(data => {
                console.log(data);
            })
        } else if(event.type == "drop"){
            console.log("ファイルがドロップされました。")
            // ドロップされたファイルを取得する
            const files = event.dataTransfer?.files;

            if (files == undefined) {
                console.log("ファイルがありません。フォルダーは受け付けません。");
                return;
            }

            const response_mode = this.decideResponseMode()
            

            if (files.length == 1) {
                // ファイルが1つだけなら、ファイル名がどのボイロでも、今のウインドウの子のフォルダーに保存する
                const file = files[0];
                if (file.name.endsWith('.psd')) {
                    console.log("psdファイルです。サーバーに送ります。")

                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('filename', file.name);
                    formData.append("response_mode", response_mode)
                    formData.append("front_name", this.target_voiceroid_front_name)

                    console.log(`response_mode: ${response_mode}`)

                    if (response_mode == "FrontName_needBodyParts") {
                        console.log("front_nameがあり、かつ、画像が表示されてないなら、サーバーはBodyPartsを返す")
                        fetch(`http://localhost:${port}/parserPsdFile}`, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            //JavaScriptでは、オブジェクトからデータを抽出して新しい変数に格納するために、以下のようにデストラクチャリング（Destructuring）という機能を使用することができます。
                            const { body_parts_iamges, init_image_info, front_name, char_name } = data;
                            // これで、dataから各データが新しい変数に格納されます。
                            // body_parts_iamges, init_image_info, front_name, char_nameという名前の変数が作成され、それぞれに対応するデータが格納されます

                            /**
                             * @type {BodyParts}
                             */
                            const body_parts = {
                                "front_name": front_name,
                                "char_name": char_name,
                                "body_parts_iamges": body_parts_iamges,
                                "init_image_info": init_image_info
                            }
                            
                            // registerHumanName(front_name,this.human_tab,this.human_name)
                            humans_list[body_parts["char_name"]] = new HumanBodyManager2(body_parts,this.human_window)
                            front2chara_name[body_parts["front_name"]] = body_parts["char_name"]
                        })
                        .catch(error => console.error(error));
                    } else if (response_mode == "FrontName_noNeedBodyParts") {
                        console.log("front_nameがあり、かつ、画像が表示されているなら、サーバーは何も返さない")
                        fetch(`http://localhost:${port}/parserPsdFile`, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            //JavaScriptでは、オブジェクトからデータを抽出して新しい変数に格納するために、以下のようにデストラクチャリング（Destructuring）という機能を使用することができます。
                            const { body_parts_iamges, init_image_info, front_name, char_name } = data;
                            
                        })
                        .catch(error => console.error(error));
                    } else if (response_mode == "noFrontName_needBodyParts") {
                        console.log("front_nameが空文字列なら、サーバーはファイル名からchar_nameを推測してBodyPartsを返す")
                        fetch(`http://localhost:${port}/parserPsdFile`, {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log(data)
                            const { body_parts_iamges, init_image_info, front_name, char_name } = data;
                            // これで、dataから各データが新しい変数に格納されます。
                            // body_parts_images, init_image_info, front_name, char_nameという名前の変数が作成され、それぞれに対応するデータが格納されます

                            /**
                             * @type {BodyParts}
                             */
                            const body_parts = {
                                "front_name": front_name,
                                "char_name": char_name,
                                "body_parts_iamges": body_parts_iamges,
                                "init_image_info": init_image_info
                            }

                            registerHumanName(front_name,this.human_tab,this.human_name)
                            humans_list[body_parts["char_name"]] = new HumanBodyManager2(body_parts,this.human_window)
                            front2chara_name[body_parts["front_name"]] = body_parts["char_name"]
                        })
                        .catch(error => console.error(error));
                    }
                } else if (file.type == "image/png" || file.type == "image/jpeg" || file.type == "image/gif") {
                    console.log("画像ファイルです。")
                } else {
                    console.log("ファイルが適切な形式ではありません。");
                }


            } else if (files.length > 1) {
                // ファイルが複数なら、ファイル名がどのボイロでも、今のウインドウの子のフォルダーに保存する

                // ファイルの検査。フォルダならdrop_enable=falseにする
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    this.checkFileType(file);
                }
            }

            // ファイルの検査。psdか画像ならdrop_enable=trueにする

        }
    }

    /**
     * 
     * @returns {string}
     */
    getFrontname(){
        return this.target_voiceroid_front_name;
    }

    setFrontname(/** @type {string}*/frontname){
        this.target_voiceroid_front_name = frontname;
    }

    checkFileType(/** @type {File}*/file){
        const file_type = file.type;
        if (file_type == "image/png" || file_type == "image/jpeg" || file_type == "image/gif") {
            return true;
        } else {
            return false;
        }
    }

    

    /**
     * front_nameが空文字列なら、サーバーはファイル名からchar_nameを推測してBodyPartsを返す
     * front_nameがあり、かつ、画像が表示されてないなら、サーバーはBodyPartsを返す
     * front_nameがあり、かつ、画像が表示されているなら、サーバーは何も返さない
     * @returns {"noFrontName_needBodyParts"|"FrontName_needBodyParts"|"FrontName_noNeedBodyParts"}
     */
    decideResponseMode(){

        if (this.target_voiceroid_front_name == "????") {
            return "noFrontName_needBodyParts"
        } else {
            //このhuman_tab内に画像があるかどうかを調べる
            const human_image_list = this.human_images.getElementsByClassName("human_image");
            if (human_image_list.length > 0) {
                return "FrontName_noNeedBodyParts"
            } else {
                return "FrontName_needBodyParts"
            }
        }
    }



}

class DragDropEventObject{

    /**
     * ドラッグアンドドロップされたときの制御
     * ドラッグオーバーされたら、ファイルを検査する。psdか画像ならdropを許可する。
     * ドロップされたら、ファイルを取得する。
     */
    constructor(){

        document.addEventListener("dragover", e => {}); 
    }

    /**
     * 
     * @param {DragEvent} event 
     */
    
}