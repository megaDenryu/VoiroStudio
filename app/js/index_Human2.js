///@ts-check

/**
 * 
 * @param {HTMLElement} human_tab_elm 
 */
function addClickEvent2Tab(human_tab_elm){
    // タブに対してクリックイベントを適用
    const tabs = human_tab_elm.getElementsByClassName('tab');
    human_tab_elm.addEventListener('click', tabSwitch, false);
    for(let i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener('click', tabSwitch, false);
    }
    // タブ識別用にdata属性を追加
    const num = message_box_manager.message_box_list.length;
    human_tab_elm.setAttribute('data-tab_num', num);
    //メッセージボックスのサイズが変更された時のイベントを追加
    var message_box_elm = human_tab_elm.getElementsByClassName("messageText")[0];
    const front_name = human_tab_elm.getElementsByClassName("human_name")[0].innerText
    var message_box = new MessageBox(message_box_elm,message_box_manager,num,human_tab_elm);
}

class VoiceRecognitioManager {
    static instance = null;

    constructor(){
        //音声認識
        this.user_number = 0;
        this.recognition = new webkitSpeechRecognition();
        this.recognition.lang = 'ja-JP';  // 言語を日本語に設定
        this.recognition.onresult = this.convertToHiragana;  // 結果が返ってきたらconvertToHiraganaを実行
        this.restartEventOnEnd()
        /*this.recognition.onend = () => {
            this.recognition.start();  // 音声認識が終了したときに再開する
        };*/
    }

    static singlton(){
        if(!VoiceRecognitioManager.instance){
            VoiceRecognitioManager.instance = new VoiceRecognitioManager();
        }
        return VoiceRecognitioManager.instance;
    }

    start(){
        this.restartEventOnEnd();
        this.recognition.start();  // 音声認識を開始
        console.log("音声認識を開始");
    }

    stop(){
        this.recognition.stop();  // 音声認識を停止
    }

    deleteEventOnEnd(){
        this.recognition.onend = () => {
            console.log("音声認識を停止");
        };
    }
    restartEventOnEnd(){
        this.recognition.onend = () => {
            this.recognition.start();  // 音声認識が終了したときに再開する
            let now = new Date();
            console.log("音声認識を再開", "現在時刻:", now.toISOString());
        };
    }

    

    convertToHiragana(event,self){
        console.log("音声認識イベント発生");
        const text = event.results[0][0].transcript;  // 音声認識の結果を取得
        // 音声認識の結果をひらがなに変換するAPIにリクエストを送る
        var speak_debug = true;
        if (speak_debug && 1 == VoiceRecognitioManager.singlton().user_number){
            let now = new Date();
            console.log("音声認識結果を表示", "現在時刻:", now.toISOString(),text);
            //userのキャラの名前を取得
            var user_elem = document.getElementsByClassName("tab user")[0];
            var user_char_name = user_elem.parentElement.getElementsByClassName("human_name")[0].innerText;
            //user_char_nameのmessage_boxを取得
            var message_box = message_box_manager.message_box_dict.get(user_char_name);
            //message_boxにtextを追加
            message_box.sendMessage(text);

            /*
            var input_dict = {};
            input_dict[user_char_name] = text;
            ws.send(JSON.stringify(input_dict));
            */
        } else {
            fetch('https://api.example.com/convert_to_hiragana', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(response => response.json())
            .then(data => {
                const hiragana = data.hiragana;  // 変換後のひらがなを取得
                console.log(hiragana);
            })
            .catch(error => console.error('Error:', error));
            return 0;
        }
    }
}


/**
 * 
 * タブをクリックすると実行する関数。+なら人間を追加。名前ならそこをアクティブにする。
 * @param {Event} event
 * @message_box_manager {MessageBoxManager} message_box_manager
 * @this {HTMLElement}
 * @return {void} 
 */
function tabSwitch(event){
    if (this.innerText == "+") {
        var humans_space = document.getElementsByClassName('humans_space')[0]
        //追加タブを追加
        var tab = humans_space.querySelector(".init_tab")
        var clone = tab.cloneNode(true)
        clone.classList.remove("init_tab");
        clone.classList.add("tab")
        clone.getElementsByClassName('human_name')[0].innerText = "????"
        humans_space.append(clone);
        addClickEvent2Tab(clone);
        drag_drop_file_event_list.push(new DragDropFile(clone));
        
        //changeMargin()
    }else if(this.innerText == "x") {
        //削除ボタンが押された人のタブを削除
        delete_target_element = this.parentNode.parentNode
        delete_target_element.remove()
        //changeMargin()
        //別のタブにアクティブを移す処理

        //ニコ生コメント受信を停止する。nikonama_comment_reciver_stopにfront_nameをfetchで送信する。
        const front_name = delete_target_element.getElementsByClassName("human_name")[0].innerText;
        fetch(`http://${localhost}:${port}/nikonama_comment_reciver_stop/${front_name}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ front_name: front_name })
        })
        const char_name = front2chara_name[front_name]
        //設定タブを開いてるならエレメントを削除し、setting_infoからも削除
        console.log("設定タブを開いてるならエレメントを削除し、setting_infoからも削除")
        if (char_name in setting_info) {
            console.log(char_name+"setteng_infoにあるので削除")
            setting_info[char_name].ELM_accordion.remove();
            delete setting_info[char_name];
            
        }
        
        //このタブのキャラのデータを削除
        if (char_name in humans_list) {
            delete humans_list[char_name];
        }
        
        //message_box_managerからも削除
        message_box_manager.message_box_dict.delete(front_name);

    }
    else if (this.className.includes("human_name") && !this.className.includes("input_now")) {
        //iosの自動再生制限対策でid=audioのaudioタグを再生する
        /*var audio = document.getElementById('audio');
        audio.volume = 0;
        audio.play();*/
        //キャラの名前を選択できるようにプルダウンかinputを追加
        this.classList.add('input_now')
        let ELM_human_name = this;
        let human_tab = /** @type {Element}*/(ELM_human_name.parentNode.parentNode)
        //this.innerText = ""
        let input = document.createElement("input")
        input.type = "text"
        input.enterKeyHint = "enter"
        //pc版
        input.addEventListener("keydown", function(event) 
        {
            console.log(this)
            if (event.key === "Enter") {
                //removeInputCharaNameイベントを解除する
                input.removeEventListener("blur", removeInputCharaName.bind(input));
                const human_name = input.value;
                registerHumanName(human_name, human_tab, ELM_human_name)
                sendHumanName(human_name)
                input.remove();
            }
        });
        //フォーカスが外れたときにinputを削除
        input.addEventListener("blur", removeInputCharaName.bind(input));
        ELM_human_name.appendChild(input);
        input.focus();
    }
    else if (this.innerText == "npc") {
        //npcの場合、userに変更され、他のuserはnpcに変更される
        
        //他のuserがあれば、npcに変更
        var user_elms = document.getElementsByClassName("tab user");
        if (user_elms.length > 0){
            user = user_elms[0];
            user.innerText = "npc";
            user.classList.remove("user");
            user.classList.add("npc");
            VoiceRecognitioManager.singlton().deleteEventOnEnd();
        }
        
        //自分はuserに変更
        this.innerText = "user";
        this.classList.remove("npc");
        this.classList.add("user");
        //音声認識を開始
        var vrm = VoiceRecognitioManager.singlton()
        vrm.user_number = 1;
        vrm.start();

        
    }
    else if (this.innerText == "user") {
        //音声認識を停止
        const vrm = VoiceRecognitioManager.singlton()
        vrm.deleteEventOnEnd();
        //自分はnpcに変更
        this.innerText = "npc";
        //classも変更
        this.classList.remove("user");
        this.classList.add("npc");
        vrm.user_number = 0;   
    }
    else if (this.innerText == "設定") {
        event.target.classList.add("setting_now")
        //設定画面を表示
        const front_name = this.parentNode.getElementsByClassName("human_name")[0].innerText
        const char_name = front2chara_name[front_name]
        if (char_name in setting_info) {
            console.log(char_name+"setteng_infoにある")
            if (setting_info[char_name].ELM_accordion.classList.contains("vissible")){
                console.log("vissibleを削除",setting_info[char_name].ELM_accordion)
                setting_info[char_name].ELM_accordion.classList.remove("vissible")
                setting_info[char_name].ELM_accordion.classList.add("non_vissible")

            }else{
                console.log("vissibleを追加",setting_info[char_name].ELM_accordion)
                setting_info[char_name].ELM_accordion.classList.remove("non_vissible")
                setting_info[char_name].ELM_accordion.classList.add("vissible")
            }
        } else {
            console.log(char_name+"setteng_infoにない")
            chara_human_body_manager = humans_list[char_name]
            var vas = new VoiroAISetting(chara_human_body_manager);
            humans_list[char_name].BindVoiroAISetting(vas);
            setting_info[char_name] = vas;
            setting_info[char_name].ELM_accordion.classList.add("vissible")



        }
        
    } else if (this.className.includes("gpt_setting")) {
        //gptの設定画アコーディオンを表示

    }
    else {
        //キャラ名の場合

    }
    //アクティブにする
    var active = document.getElementsByClassName('is-active')[0];
    if (active) {
    active.classList.remove('is-active');
    }
    this.classList.add('is-active');
    
}

/**
 * @param {string} human_name
 * @param {Element} human_tab
 * @param {HTMLElement} ELM_human_name
 */
function registerHumanName(human_name, human_tab, ELM_human_name) {
    let human_window = human_tab.getElementsByClassName("human_window")[0]
    //画像が送られてきたときに画像を配置して制御するためにhuman_windowにキャラの名前のタグを付ける。
    human_window.classList.add(`${human_name}`)
    //名前を格納
    ELM_human_name.innerText = human_name;
    ELM_human_name.classList.remove("input_now")
    
    //messageBoxにhuman_nameを格納
    //今のhuman_tabの番号を取得
    const tab_num = human_tab.getAttribute('data-tab_num');
    message_box_manager.linkHumanNameAndNum(human_name,tab_num)
}

function removeInputCharaName(event) {
    //thisはinputがbindされている
    console.log("blur")
    parent_elem = this.parentNode
    parent_elem.classList.remove("input_now")
    console.log(this)
    this.remove();
}

class MessageBoxManager {

    /** @type {MessageBox[]} メッセージボックスのリスト*/ 
    message_box_list

    /** @type {ExtendedMap< string, MessageBox>}  メッセージボックスの辞書。キーはキャラのfront_name、値はメッセージボックスのインスタンス。*/
    message_box_dict

    /** @type {number} 監視しているメッセージボックスの番号を格納。-1なら監視していない。*/
    observe_target_num

    /** @type {ResizeObserver} 監視対象のメッセージボックスの高さが変更されたときに、他のメッセージボックスの高さも変更するためのオブジェクト。*/
    resizeObserver

    /** @type {ExtendedMap<string, string>} キャラのgptモードの状態を格納する辞書。キーはキャラのfront_name、値はgptモードの状態。*/
    Map_all_char_gpt_mode_status

    constructor() {
        this.message_box_list = [];
        this.message_box_dict = new ExtendedMap();
        this.observe_target_num = -1;
        this.resizeObserver = new ResizeObserver((entries) => {
            this.setHeight(entries[0].target.style.height , this);
        });
        this.Map_all_char_gpt_mode_status = new ExtendedMap();
    }

    setMessageBox(message_box) {
        this.message_box_list.push(message_box);
        var assign_number = this.message_box_list.length - 1;
        return assign_number;
    }

    //１つのメッセージボックスの大きさが変更されたときに、他のメッセージボックスの大きさも変更する関数
    setHeight(height, changed_message_box) {
        var self = this;
        //他のmessage_boxの高さも変更する
        console.log("message_box_list=",this.message_box_list);
        for (let i=0;i<this.message_box_list.length;i++){
            if (this.observe_target_num != i){
                this.message_box_list[i].message_box_elm.style.height = height;
            }
        }

    }

    /**
     * キャラのフロントネームとメッセージボックスを紐づける
     * @param {string} front_name 
     * @param {number} tab_num 
     */
    linkHumanNameAndNum(front_name,tab_num) {
        const message_box = this.message_box_list[tab_num];
        this.message_box_dict.set(front_name,message_box);
        message_box.front_name = front_name;
        message_box.setGptMode("off");
        const gpt_mode_name_list = ["off","individual_process0501dev","SimpleWait4","SimpleWait3.5","low","high","test"];
        message_box.gpt_setting_button_manager_model = new GPTSettingButtonManagerModel(front_name, message_box, gpt_mode_name_list)
    }

    /**
     * @param {string} front_name 
     * @param {string} gpt_mode 
     */
    setGptMode2AllStatus(front_name,gpt_mode) {
        this.Map_all_char_gpt_mode_status.set(front_name, gpt_mode);
    }

    getAllGptModeByDict() {
        const gpt_mode_dict = {};
        for (let [key, value] of this.Map_all_char_gpt_mode_status) {
            gpt_mode_dict[key] = value;
        }
        return gpt_mode_dict;
    }

    /**
     * @param {string} front_name
     * @return {MessageBox | null}
     * */
    getMessageBoxByFrontName(front_name) {
        //front_nameがfront2chara_nameにない場合はnullを返す
        if (front_name in front2chara_name) {
            return this.message_box_dict.get(front_name);
        } else {
            return null;
        }
    }

    getMessageBoxByCharName(char_name) {
        const front_name = chara_name2front_name(char_name);
        if (front_name == "no_front_name") {
            return null;
        }
        return this.message_box_dict.get(front_name);
    }

}


class MessageBox {
    //message_box単体のクラス

    /** @type {string}*/ gpt_mode
    /** @type {GPTSettingButtonManagerModel}*/ gpt_setting_button_manager_model;
    /** @type {HumanTab}*/ human_window;
    
    /**
     * 
     * @param {HTMLElement} message_box_elm 
     * @param {MessageBoxManager} message_box_manager 
     * @param {number} manage_num 
     * @param {HTMLElement} human_tab_elm
     */
    constructor(message_box_elm, message_box_manager, manage_num, human_tab_elm) {
        this.char_name = "";
        this.front_name = "";
        this.gpt_mode = "";
        this.message_box_elm = message_box_elm;
        this.parent_ELM_input_area = this.message_box_elm.closest(".input_area");
        this.ELM_send_button = this.parent_ELM_input_area.getElementsByClassName("send_button")[0];
        this.ELM_delete_button = this.parent_ELM_input_area.getElementsByClassName("delete_button")[0];
        this.message_box_manager = message_box_manager;
        this.human_window = new HumanTab(human_tab_elm, this.front_name);
        //メッセージボックスマネージャーにこのメッセージボックスを登録
        this.manage_num = this.message_box_manager.setMessageBox(this)
        if(manage_num != this.manage_num) {
            alert("message_box_managerに登録された番号と、message_boxの番号が一致しません。")
        }
        //メッセージボックスの高さが変更されたときに、他のメッセージボックスの高さも変更するようにする
        this.message_box_elm.addEventListener('mousedown', this.startObsereve.bind(this));
        this.message_box_elm.addEventListener('mouseup', this.endObsereve.bind(this));
        this.ELM_send_button.onclick = this.execContentInputMessage.bind(this);
    }
    startObsereve() {
        this.message_box_manager.observe_target_num = this.manage_num;
        this.message_box_manager.resizeObserver.observe(this.message_box_elm);
    }
    endObsereve() {
        this.message_box_manager.observe_target_num = -1;
        this.message_box_manager.resizeObserver.unobserve(this.message_box_elm);
    }
    execContentInputMessage() {
        const front_name = this.front_name;
        const message = this.message_box_elm.value;
        //messageに「コメビュモード:{room_id}」と入力されている場合
        if (message.includes("コメビュモード:")) {
            //コメビュモードに入る
            const room_id = message.split(":")[1];
            //websocketを開く
            this.ws_nikonama_comment_reciver = new WebSocket(`ws://${localhost}:${port}/nikonama_comment_reciver/${room_id}/${front_name}`);
            this.ws_nikonama_comment_reciver.onmessage = this.receiveNikoNamaComment.bind(this);
            //メッセージボックスの中身を削除
            this.message_box_elm.value = "";
            //focusを戻す
            this.message_box_elm.focus();
        } else if (message.includes("https://live.nicovideo.jp/watch/")) {
            //コメビュモードに入る
            const room_id = message.split("https://live.nicovideo.jp/watch/")[1];
            //websocketを開く
            this.ws_nikonama_comment_reciver = new WebSocket(`ws://${localhost}:${port}/nikonama_comment_reciver/${room_id}/${front_name}`);
            this.ws_nikonama_comment_reciver.onmessage = this.receiveNikoNamaComment.bind(this);
            //メッセージボックスの中身を削除
            this.message_box_elm.value = "";
            //focusを戻す
            this.message_box_elm.focus();
        } else if (message.includes("https://www.youtube.com/watch?v=")) {
            //youtubeのコメントを受信する
            const video_id = message.split("https://www.youtube.com/watch?v=")[1];
            console.log(video_id)
            //websocketを開く
            this.ws_youtube_comment_reciver = new ExtendedWebSocket(`ws://${localhost}:${port}/YoutubeCommentReceiver/${video_id}/${front_name}`);
            this.ws_youtube_comment_reciver.onmessage = this.receiveYoutubeLiveComment.bind(this);
            //接続を完了するまで待つ
            this.ws_youtube_comment_reciver.onopen = () => {
                //開始メッセージを送信
                // @ts-ignore
                this.ws_youtube_comment_reciver.sendJson({ "start_stop": "start" });
            }

            //メッセージボックスの中身を削除
            this.message_box_elm.value = "";
            //focusを戻す
            this.message_box_elm.focus();
        } else if (message.includes("ようつべコメント停止:")) {
            console.log("コメント受信停止します")
            if (this.ws_youtube_comment_reciver) {
                console.log("コメント受信停止を送信")
                this.ws_youtube_comment_reciver.sendJson({ "start_stop": "stop" });
            }
        }
        else if (message.includes("背景オン:") || message.includes("GBmode:") || message.includes("MBmode:") || message.includes("BBmode:")) {
            this.human_window.changeBackgroundMode(message);
        }
        else {
            //メッセージを送信する
            const message = this.message_box_elm.value;
            this.sendMessage(message)
        }

        //メッセージボックスの中身を削除
        this.message_box_elm.value = "";
        //focusを戻す
        this.message_box_elm.focus();

    }
    receiveNikoNamaComment(event) {
        const message = JSON.parse(event.data);
        const char_name = message["char_name"];
        const comment = message["comment"];
        console.log("char_name=",char_name,"comment=",comment)
        if (char_name == this.char_name) {
            this.sendMessage(comment);
        } else {
            let message_box = message_box_manager.getMessageBoxByCharName(char_name)
            if (message_box == null) {
                this.sendMessage(comment);
            } else {
                message_box.sendMessage(comment);
            }

        }
    }

    receiveYoutubeLiveComment(event) {
        const message = JSON.parse(event.data);
        const char_name = message["char_name"];
        const comment = message["message"];
        console.log("char_name=",char_name,"comment=",comment)
        if (char_name == this.char_name) {
            this.sendMessage(comment);
        } else {
            let message_box = message_box_manager.getMessageBoxByCharName(char_name)
            if (message_box == null) {
                this.sendMessage(comment);
            } else {
                message_box.sendMessage(comment);
            }

        }
    
    }

    /**
     * @param {string} gpt_mode 
     */
    setGptMode(gpt_mode) {
        this.gpt_mode = gpt_mode;
        this.message_box_manager.setGptMode2AllStatus(this.front_name,gpt_mode);
    }

    sendMessage(message) {
        //メッセージを送信する
        const message_dict = {}
        message_dict[this.front_name] = message;
        const send_data = {
            "message" : message_dict,
            "gpt_mode" : this.message_box_manager.getAllGptModeByDict()
        }
        ws.send(JSON.stringify(send_data));
    }
}

class HumanTab {

    // モードとクラス名の対応を定義
    bg_modes = {
        "背景オン:": { display: "block", className: "" },
        "GBmode:": { display: "none", className: "green_back" },
        "MBmode:": { display: "none", className: "maze_back" },
        "BBmode:": { display: "none", className: "blue_back" },
        // 新しいモードを追加する場合はここに追記
    };

    /**
     * 
     * @param {HTMLElement} human_tab_elm 
     * @param {string} front_name 
     */
    constructor(human_tab_elm,front_name) {
        this.human_tab_elm = human_tab_elm;
        this.human_window_elm = human_tab_elm.getElementsByClassName("human_window")[0];
        this.front_name = front_name;
    }

    /**
     *  @param {"背景オン:"|"GBmode:"|"MBmode:"|"BBmode:"} mode_key
     */
    changeBackgroundMode(mode_key) {
        let ELM_human_tab = this.human_window_elm.closest(".human_tab");
        let ELM_bg_image = ELM_human_tab.getElementsByClassName("bg_images")[0];
        const ELM_human = ELM_human_tab.getElementsByClassName("human")[0];

        // 全ての可能な背景クラスを削除
        ELM_human.classList.remove("green_back", "maze_back", "blue_back");

        const mode = this.bg_modes[mode_key];

        if (mode) {
            // ELM_bg_imageの表示状態を更新
            ELM_bg_image.style.display = mode.display;

            // 必要ならクラス名を追加
            if (mode.className) {
                ELM_human.classList.add(mode.className);
            }
        }
    }

}

function getMessageBoxByCharName(char_name) {
    return message_box_manager.message_box_dict.get(char_name);
}

//キャラ名を送信するときのイベント関数
function sendMessage(event) {
    event.preventDefault()
    var human_tabs = document.getElementsByClassName("human_tab")
    inputs_dict = {}
    for (let i=0;i<human_tabs.length;i++){
        human_name = human_tabs[i].getElementsByClassName("human_name")[0].innerText
        input_elem = human_tabs[i].getElementsByClassName("messageText")[0]
        inputs_dict[human_name] = input_elem.value
        input_elem.value = ""
    }
    inputs_json = JSON.stringify(inputs_dict)
    ws.send(inputs_json)

    //sendを押したキャラタブのmessageTextにフォーカスを移す。
    ELM_input_area = event.target.closest(".input_area")
    ELM_messageText = ELM_input_area.getElementsByClassName("messageText")[0]
    ELM_messageText.focus()

    
}

/**
 * @typedef {Object} ImageInfo
 * @property {string} element - キャンバス要素の識別子
 * @property {string} img - 画像のデータ（Base64形式）
 * @property {Object} json - 画像のメタデータ
 * @property {string} json.name - 画像の名前
 * @property {number} json.x - 画像のx座標
 * @property {number} json.y - 画像のy座標
 * @property {number} json.width - 画像の幅
 * @property {number} json.height - 画像の高さ
 * @property {number} json.z_index - 画像のz_index
 * @property {string} json.口 - 口パクの文字
 */

/**
 * @typedef {Record<string, Record<string, string>>} AllData
 * @typedef {Record<string, Record<string, string>>} InitData
 */

/**
 * @typedef {Object} InitImageInfo
 * @property {Record<string, InitData>} [property] - 動的に追加されるプロパティ
 * @property {Record<"パク"|"パチ"|"ぴょこ",Record<"開候補"|"閉",PartsPath[]>>} OnomatopeiaActionSetting
 */

/**
 * @typedef {Object} BodyParts
 * @property {Record<string, ImageInfo>} body_parts_iamges - 体のパーツの画像のurlを格納した辞書
 * @property {InitImageInfo} init_image_info - キャラの画像の初期情報を格納した辞書
 * @property {string} front_name - フロントエンドでのキャラの名前
 * @property {string} char_name - キャラの名前
 */

//キャラ名を受信するときのイベント関数
function receiveMessage(event) {
    if(false){
        //
        no_image_human = document.getElementsByClassName("no_image_human")
        human_image = no_image_human[1].document.getElementsByClassName("human_image")
        var blob = event.data;
        var url = URL.createObjectURL(blob)
        var img = document.createElement("img");
        image_human.src = url;
        no_image_human[1].classList.remove("no_image_human")
    }
    else{
        //ここで行う処理の内容は、apiから受信したキャラ画像を表示する処理
        no_image_human = document.getElementsByClassName("no_image_human")
        
        
        /**
         * @type {BodyParts}
         */
        var body_parts = JSON.parse(JSON.parse(event.data));
        console.log(body_parts)
        console.log(body_parts.char_name,body_parts["char_name"])
        if ("実験" == body_parts["char_name"]){
            //ONEのインスタンスの作成と画像の表示を開始
            humans_list.ONE_chan = new HumanBodyManager(body_parts)
        } else {
            console.log("human_listに追加:"+body_parts["char_name"])
            
            if (true){
                try{
                    humans_list[body_parts["char_name"]] = new HumanBodyManager2(body_parts)
                } catch (e) {
                    console.log(e)
                    console.log("human_listに追加失敗:"+body_parts["char_name"])
                }
                    
            }
            else{
                humans_list[body_parts["char_name"]] = new iHumanBodyManager(body_parts)
            }
            front2chara_name[body_parts["front_name"]] = body_parts["char_name"]
            console.log("front2chara_name=",front2chara_name)
        }
    }
}

/**
 * @typedef {Object} WavInfo
 * @property {string} path - wavファイルのパス
 * @property {string} wav_data - wavファイルのデータ（Base64形式）
 * @property {string} phoneme_time - 音素の開始時間と終了時間の情報
 * @property {string} phoneme_str - 音素の情報
 * @property {string} char_name - キャラの名前
 * @property {string} voice_system_name - 音声合成のシステムの名前
 */

//gptで生成された会話データを受信したときのイベント関数
async function receiveConversationData(event) {
    // console.log(typeof(event.data))
    // alert(event.data)
    var human_tab = document.getElementsByClassName('human_tab');
    let obj = JSON.parse(JSON.parse(event.data));
    console.log("メッセージを受信")
    console.log(obj)
    var audio_group = document.getElementsByClassName("audio_group")[0]
    if ("chara_type" in obj && obj["chara_type"] == "gpt") {
        //文章を表示
        const /**@type {Record<String,string>} */ sentence = obj["sentence"];
        const textPromise = execText(sentence,human_tab)

        //音声を再生
        const /**@type {WavInfo[]} */ wav_info  = obj["wav_info"];
        const audioPromise = execAudioList(wav_info,audio_group)

        // 両方の処理が終わるのを待つ
        await Promise.all([textPromise, audioPromise]);

        //gptからの音声だった場合は終了を通知。
        const front_name = getNthKeyFromObject(sentence, 0)
        const message_box = message_box_manager.getMessageBoxByFrontName(front_name);
        if (message_box) {
            const human_gpt_routine_ws = message_box.gpt_setting_button_manager_model.human_gpt_routine_ws_dict[front_name];
            human_gpt_routine_ws.sendJson({ "gpt_voice_complete": "complete" });
        }
        
    } else if("chara_type" in obj && obj["chara_type"] == "player") {
        //文章を表示
        const /**@type {Record<String,string>} */ sentence = obj["sentence"];
        const textPromise = execText(sentence,human_tab)

        //音声を再生
        const /**@type {WavInfo[]} */ wav_info  = obj["wav_info"];
        const audioPromise = execAudioList(wav_info,audio_group)

        // 両方の処理が終わるのを待つ
        await Promise.all([textPromise, audioPromise]);
    } else {
        if (0 in obj && "wav_data" in obj[0]) {
            //wavファイルが送られてきたときの処理。
            //複数のwavファイルが送られてくるのでaudio_groupに追加していく。
            await execAudioList(obj,audio_group)
        }
        else {
            await execText(obj,human_tab)
        }
    }
    

}

/**
 * //テキストが送られてきたときの処理
 * @param {Record<string,string>} obj
 * @param {HTMLCollectionOf<Element>} human_tab
 */
async function execText(obj,human_tab) {
    console.log(obj)
    for(let i=1; i<human_tab.length;i++){
        //human_tabの中のhuman_nameを取得
        let message = document.createElement('li')
        //human_nameを取得
        let name = human_tab[i].getElementsByClassName("human_name")[0].innerText
        //message_colを取得
        let message_col = human_tab[i].getElementsByClassName("message_col")[0]

        let str = ""
        //messageを作成
        if(obj.hasOwnProperty(name)){
            if(typeof obj[name] == "object"){
                console.log("上を通った")
                for(let key in obj[name]){
                    if (key == "感情"){
                        str = `${key}:${JSON.stringify(obj[name][key])}\n\n`
                    }else{
                        str = `${key}:${obj[name][key]}\n\n`
                    }
                    
                    let content = document.createTextNode(str)
                    message.appendChild(content)
                }
            }else{
                console.log("下を通った")
                console.log("obj[name]=",obj[name])
                let content = document.createTextNode(obj[name])
                message.appendChild(content)
            }
            
        
            //class = "subtitle"を取得してinnerTextをmessageに変更
            let subtitle = human_tab[i].getElementsByClassName("subtitle")[0]
            subtitle.innerText = obj[name]
            console.log("subtitle.innerText=",subtitle.innerText)

            //class = "message"を追加
            message.classList.add("message")
            message_col.appendChild(message)
            
            //mode_integrateのmessage_colにも追加
            let message_col_integrate = document.getElementsByClassName("message_col mode_integrate")[0]
            let message_integrate = message.cloneNode(true)
            message_integrate.classList.add("message_integrate")
            //message_integrateに番号情報を追加。後で位置の再調整に使う。
            message_integrate.setAttribute("data-tab_num",i)
            //message_integrateの横のmarginに使う値
            const base_margin = 6
            //message_integrateの横位置を調整
            message_integrate.style.marginLeft = `${100 / (human_tab.length-1) * (i-1) + base_margin / (human_tab.length-1)}%`
            //message_integrateのwidthを調整
            message_integrate.style.width = `${100 / (human_tab.length-1) - base_margin / (human_tab.length-1) * 2}%`

            message_col_integrate.appendChild(message_integrate)
            //一番下にスクロール
            message_col.scrollTop = message_col.scrollHeight;
            message_col_integrate.scrollTop = message_col_integrate.scrollHeight;
        }

        
        //humans_list.ONE_chan.changeTail()
    }
}



/**
 * @param {WavInfo[]} obj 
 * @param {Element} audio_group 
 */
async function execAudioList(obj,audio_group) {
    console.log(obj)
        
    for await(let item of obj){
        console.log("audio準備開始")
        audio_group = await execAudio(item,audio_group);
        console.log(item["char_name"]+`音源再生終了`)
    }
    console.log("全て再生終了")
}


/**
 * 
 * @param {WavInfo} obj 
 * @param {Element} audio_group 
 * @param {Number} maxAudioElements 
 * @returns 
 */
async function execAudio(obj,audio_group, maxAudioElements = 100) {
    //wavファイルをバイナリー形式で開き、base64エンコードした文字列を取得
    var wav_binary = obj["wav_data"]
    //wavファイルをbase64エンコードした文字列をaudioタグのsrcに設定
    var lab_data = obj["phoneme_str"];
    const voice_system_name = obj["voice_system_name"];
    console.log("lab_data=",lab_data)
    var audio = document.createElement('audio');
    audio.src = `data:audio/wav;base64,${wav_binary}`;
    //audioタグを追加
    audio_group.appendChild(audio);

    // audio_group内のaudioエレメントが上限を超えたら、最初のエレメントを削除
    while (audio_group.childElementCount > maxAudioElements) {
        audio_group.removeChild(audio_group.firstElementChild);
    }

    audio.load();
    await new Promise(resolve => audio.onloadedmetadata = resolve);
    //audioの長さを取得
    const time_length = audio.duration * 1000;
    //labdataの最後の要素の終了時間を取得
    const last_end_time = lab_data[lab_data.length-1][2] * 1000;
    let ratio = 1;
    if (voice_system_name == "Coeiroink") {
        ratio = time_length / last_end_time;
    }
    console.log(time_length,last_end_time,ratio)

    //audioを再生して口パクもする。
    var lab_pos = 0;
    console.log("audioタグを再生")
    await new Promise((resolve) => {
        audio.onended = resolve;
        audio.play().then(() => {
            var intervalId = setInterval(() => {
                var current_time = audio.currentTime * 1000;
                // console.log("current_time="+current_time, "lab_pos="+lab_pos);
                
                if (lab_data[lab_pos] !== undefined) {
                    var start_time = lab_data[lab_pos][1] * 1000 * ratio;
                    var end_time = lab_data[lab_pos][2] * 1000 * ratio;
                } else {
                    console.error('Invalid lab_pos:', lab_data, "lab_pos="+lab_pos);
                    // ここで適切なエラーハンドリングを行います
                }
                // console.log("start_time,end_time="+[start_time,end_time]);

                if (start_time <= current_time && current_time <= end_time ) {
                    // console.log("通ってる",obj["char_name"],lab_data[lab_pos][0]);
                    try{
                        humans_list[obj["char_name"]].changeLipImage(obj["char_name"],lab_data[lab_pos][0]);
                    } catch (e) {
                        console.log(e)
                        console.log(("口画像が設定されていない"))
                    }
                    lab_pos += 1;
                }

                if (current_time > end_time) {
                    lab_pos += 1;
                }

                if (lab_pos >= lab_data.length) {
                    //終わったら口パクを終了して口を閉じる
                    try{
                        humans_list[obj["char_name"]].changeLipImage(obj["char_name"],"end");
                    } catch (e) {
                        console.log(e)
                        console.log(("口画像が設定されていない"))
                    }
                    clearInterval(intervalId);
                }

                if (audio.ended) {
                    clearInterval(intervalId);
                }
            }, 10); // 100ミリ秒ごとに更新
        });
    });
    return audio_group;
}

async function async_receiveConversationData(event){
    await receiveConversationData(event);
}

/**
 * グローバルなイベントキューからイベントを取り出して処理する
 * 処理が終わったら再帰的に自身を呼び出す
 * ただし、処理中は次のイベントを処理しない
 **/
async function processMessages() {
    console.log("メッセージからprocessMessages()を呼び出しました、isProcessing=",isProcessing)
    if (isProcessing || messageQueue.length === 0) {
        // 処理中 or キューが空なら何もしない
        console.log("処理中 or キューが空なので何もしない")
        return;
    }
    // 処理を実行するので処理中フラグを立てる
    isProcessing = true;
    // キューからイベントを取り出して処理する
    var new_event = messageQueue.shift();
    await receiveConversationData(new_event);
    isProcessing = false;
    console.log("次のprocessMessages()を呼び出します")
    processMessages();
}            




function sendHumanName(human_name) {
    if (human_ws.readyState !== WebSocket.OPEN) {
        humanWsOpen();
        human_ws.onopen = function(e) {
            human_ws.send(human_name);
        };
    }
    human_ws.send(human_name);
}

function clearText(button) {
    text = button.parentNode.parentNode.getElementsByClassName("messageText")[0]
    text.value = ""
}



function changeMargin(){
    //todo 今は停止中。もっと良さそうな方法があれば使う。

    //Partyマージンを変更
    Party = document.getElementsByClassName("Party")[0]
    human_tabs = Party.getElementsByClassName("human_tab")
    margin = 25 / (human_tabs.length-1)
    Party.style.marginLeft = `${margin}%`;
    Party.style.marginRight = `${margin}%`;
    //もしclass = "message"があるならそのwidthをtab数に応じて変更
    messages = document.getElementsByClassName("message")
    for (let i=0;i<messages.length;i++){
        messages[i].style.width = `${95-human_tabs.length*2.5}%`
    }
    
    
}

//体パーツの画像をクリックして、画像を変更する処理を実装する
//body_partsの画像をクリックしたときの処理
function changeBodyParts(button){

}

/** 現状使わないが、canvasの勉強のため残す*/
function canvas_process(human_tab){
    //canvasの処理
    console.log("canvasの処理開始")
    var canvas = human_tab.getElementsByClassName('canvas')[0];
    //canvasを枠の大きさに合わせる
    const human_elem = human_tab.getElementsByClassName("human")[0] 
    canvas.width = human_elem.offsetWidth;
    canvas.height = human_elem.offsetHeight;
    //canvas.style.background = "red";
    //canvasにbg_imageを描画
    var ctx = canvas.getContext('2d');
    var img = new Image();
    img.src = "./images/その他画像/nc268704.jpg";
    //位置を真ん中にし、画像の比率はそのままに枠に合わせる
    img.onload = function(){
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);
    }

    //var ctx = canvas.getC
    console.log("canvasの処理終了")
}

class PsdManager{
    constructor(psd){
        this.psd = psd
        this.layers = psd.children
        this.layers_name = []
        this.layers.forEach(layer => {
            this.layers_name.push(layer.name)
        });
        this.layers_name.forEach(layer_name => {
            console.log(layer_name)
        });
    }
}

class DragDropObjectStatus{
    /**
     * 
     * @param {*} human_images_elem 
     * @param {HumanBodyManager2} humanBodyManager 
     */
    constructor(human_images_elem,humanBodyManager){
        //プロパティには各画像の状態などを格納する
        this.human_images_elem = human_images_elem;
        this.humanBodyManager = humanBodyManager;
        this.bg_image = human_images_elem.parentNode.getElementsByClassName("bg_image")[0]
        this.human_window = human_images_elem.parentNode
        this.human_image_elems = human_images_elem.getElementsByClassName("human_image");
        this.search_canvas_elem = human_images_elem.parentNode.getElementsByClassName("search_canvas")[0];
        this.mouse_down = false;
        this.mouse_down_pos_x = 0;
        this.mouse_down_pos_y = 0;
        this.img_scale = 1;

        var oprator_canvas = this.human_images_elem.getElementsByClassName("operator_canvas")[0];
        oprator_canvas.dataset.scale = this.img_scale;
    }
    handleEvent(event){
        switch(event.type){
            case "mousedown":
                this.mouseDown(event);
                break;
            case "touchstart":
                this.mouseDown(event);
                break;
            case "mouseup":
                this.mouseUp(event);
                break;
            case "mousemove":
                this.mouseMove(event);
                break;
            case "wheel":
                this.mouseWheel(event);
                break;
        }
    }
    
    mouseDown(e){
        console.log("mouseDown")
        //クラス名に .drag を追加
        e.target.classList.add("drag");
        //タッチデイベントとマウスのイベントの差異を吸収
        if(e.type === "mousedown") {
            var event = e;
        } else {
            var event = e;//.changedTouches[0];
        }

        //要素内でのマウスをクリックした場所の相対座標を取得。
        this.mouse_down_pos_x = event.pageX;
        this.mouse_down_pos_y = event.pageY;
        this.canvas_offsetLeft = e.target.offsetLeft;
        this.canvas_offsetTop = e.target.offsetTop;
        //console.log("mouse_down_pos_x="+[this.mouse_down_pos_x,event.pageX,e.target.offsetLeft])
        //console.log("mouse_down_pos_y="+[this.mouse_down_pos_y,event.pageY,e.target.offsetTop])

        //右クリックなら点を描画
        if (event.button == 2){
            console.log("右クリック")
            var oprator_canvas = e.target.parentNode.getElementsByClassName("operator_canvas")[0]
            var canvas_rect = oprator_canvas.getBoundingClientRect()
            var x_on_canvas = e.pageX - canvas_rect.left;
            var y_on_canvas = e.pageY - canvas_rect.top;
            console.log("canvas_rect.left,canvas_rect.top="+[canvas_rect.left,canvas_rect.top])
            drawFillRectInOpratorCanvas(
                x_on_canvas / this.img_scale,
                y_on_canvas / this.img_scale,
                10,10,"green"
                )
        }
        
    }

    /**
     * 
     * @param {Event} e 
     */
    mouseMove(e) {
        //ドラッグしている要素を取得
        //e.targetのクラスネームにdragがあるかどうかで処理を分岐させる
        if (e.target.classList.contains("drag")){
            var drag = e.target;
            //同様にマウスとタッチの差異を吸収
            if(e.type === "mousemove") {
                var event = e;
            } else {
                var event = e.changedTouches[0];
            }

            //フリックしたときに画面を動かさないようにデフォルト動作を抑制
            e.preventDefault();
            //マウスが動いた場所に要素を動かす
            for (let i=0;i<this.human_image_elems.length;i++){
                this.human_image_elems[i].style.left = addPixelValues(this.canvas_offsetLeft, event.pageX - this.mouse_down_pos_x + "px");
                this.human_image_elems[i].style.top = addPixelValues(this.canvas_offsetTop, event.pageY - this.mouse_down_pos_y + "px");
            }
        }
    }

    //マウスボタンが上がったら発火
    mouseUp(e) {
        console.log("mouseUp")
        if (e.target.classList.contains("drag")){
            var drag = e.target;

            //クラス名 .drag も消す
            drag.classList.remove("drag");
        }
    }
    //ホイールイベント:画像の拡大縮小
    mouseWheel(e){
        if (e.target.classList.contains("drag")){
            //ホイールの回転量を取得
            var wheel = e.deltaY;
            //ホイールの回転量に応じて画像の拡大縮小
            var delta_ratio = 0;
            if(wheel > 0){
                delta_ratio = -0.1;
            }else{
                delta_ratio = 0.1;
            }
            this.img_scale = this.img_scale + delta_ratio
            //opratpr_canvasのdata属性にscaleを保存
            var oprator_canvas = this.human_images_elem.getElementsByClassName("operator_canvas")[0];
            oprator_canvas.dataset.scale = this.img_scale;

            //console.log("img_scale:"+this.img_scale);
            //全ての画像のサイズは同じなので拡大縮小をする
            var height = 65 * this.img_scale;
            //console.log(`${height}vh`);
            //console.log(this.human_image_elems[0].style.height);
            //拡大縮小の中心を、クリックしたときの座標のbg_imageからの相対座標として、画像のtop,leftを変更する

            //背景画像の左上角の位置を取得。しかしGBmodeでは画像が消滅してうまく取得できてない可能性がある
            // var bg_image_rect = this.bg_image.getBoundingClientRect()
            var human_window_rect = this.human_window.getBoundingClientRect()
            //マウスの絶対位置から背景画像の左上角の位置を引くことで、背景画像に対するマウスの相対位置を計算
            var P_x = parseFloat(e.pageX,10) - parseFloat(human_window_rect.left,10)
            var P_y = parseFloat(e.pageY,10) - parseFloat(human_window_rect.top,10)
            var t = this.img_scale / (this.img_scale - delta_ratio)
            var old_top = parseFloat(this.human_image_elems[0].style.top,10)
            var old_left = parseFloat(this.human_image_elems[0].style.left,10)
            var new_left = P_x + t * (old_left - P_x) + "px";
            var new_top = P_y + t * (old_top - P_y) + "px";
            //console.log("new_left,new_top="+[new_left,new_top])
            for (let i=0;i<this.human_image_elems.length;i++){
                //画像のサイズを変更
                this.human_image_elems[i].style.height = `${height}vh`
                //画像の位置を変更
                this.human_image_elems[i].style.top = new_top;
                this.human_image_elems[i].style.left = new_left;
            }
            this.search_canvas_elem.style.height = `${height}vh`

            //mouseUpとmouseDownを発火させる
            this.mouseUp(e);
            this.mouseDown(e);
            

        }

    }
}

function addPixelValues(px1, px2) {
    var num1 = parseInt(px1, 10);
    var num2 = parseInt(px2, 10);
    var sum = num1 + num2;
    return sum + "px";
}

/**
 * 
 * @param {Element} human_images_elem 
 * @param {HumanBodyManager2} humanBodyManager
 */
function addMoveImageEvent(human_images_elem,humanBodyManager){
    //1個のdrag_and_dropクラスを動かせるようにする
    console.log("dragオブジェクトを準備する",human_images_elem);
    const drag_drop_object_status = new DragDropObjectStatus(human_images_elem,humanBodyManager);
    let oprator_canvas_elem = human_images_elem.getElementsByClassName("operator_canvas")[0]
    oprator_canvas_elem.addEventListener("mousedown",drag_drop_object_status);
    oprator_canvas_elem.addEventListener("touchstart",drag_drop_object_status);
    oprator_canvas_elem.addEventListener("mouseup",drag_drop_object_status);
    oprator_canvas_elem.addEventListener("mousemove",drag_drop_object_status);
    oprator_canvas_elem.addEventListener("wheel",drag_drop_object_status);
}


/**
 * Mapクラスを拡張して、追加のメソッドを提供します。
 * @extends {Map}
 * @template T1, T2
 */
class ExtendedMap extends Map {
    getNthKey(n) {
        let i = 0;
        for (let key of this.keys()) {
            if (i === n) {
                return key;
            }
            i++;
        }
    }

    getNthValue(n) {
        let i = 0;
        for (let value of this.values()) {
            if (i === n) {
                return value;
            }
            i++;
        }
    }

    sort(compareFn) {
        let entries = Array.from(this.entries());
        entries.sort(compareFn);
        this.clear();
        for (let [key, value] of entries) {
            this.set(key, value);
        }
    }

    comvert2keysArray() {
        let keys = Array.from(this.keys());
        console.log(keys);
        return keys;
    }
}

function getNthValueFromObject(dict,n){
    return Object.values(dict)[n]
}

function getNthKeyFromObject(dict,n){
    return Object.keys(dict)[n]
}

function deepFreeze(object) {
    // プロパティの値がオブジェクトである場合、再帰的に凍結
    for (let key in object) {
        if (typeof object[key] === 'object' && object[key] !== null) {
            deepFreeze(object[key]);
        }
    }

    // オブジェクト自体を凍結
    return Object.freeze(object);
}

function deepCopy(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * @typedef {Object} ZIndexRange
 * @property {number} start - 開始インデックス
 * @property {number} end - 終了インデックス
 */

/**
 * @typedef {Object} PartInfo
 * @property {number} z_index - zインデックス
 * @property {ZIndexRange} z_index_range - zインデックスの範囲
 * @property {ExtendedMap<string, ImageInfo>} imgs - 画像データ
 * @property {Record<string, "on"|"off">} now_imgs_status - 現在の画像ステータス
 * @property {string} mode_radio_duplicate - モードラジオの重複
 * @property {string} name - 名前
 * @property {ExtendedMap<string,HTMLCanvasElement>} body_img_elemnt_map - 体の画像要素のマップ
 * @property {any} duplicate_element - 重複要素
 */

/** 
 * PartInfoの拡張
 * @typedef {ExtendedMap<string,any>} MapPartInfo 
 */

/**
 * @typedef {Object} PartsPath
 * @property {string} folder_name
 * @property {string} file_name
 */


/**
     * iHumnaBodyManagerでは一つのレイヤーで一つの画像を表示していたが、
     * こちらでは一つのレイヤーで複数の画像を表示できるようにする。
     * @class 
     * @property {boolean} debug - デバッグモードかどうか
     * @property {string} front_name - フロントエンドでのキャラの名前
     * @property {string} char_name - キャラの名前
     * @property {ExtendedMap} body_parts_images - 体のパーツの画像のurlを格納した辞書
     * @property {ExtendedMap} body_parts_is_visible - 体のパーツのどれをvisible = tue　にするかを管理するオブジェクト
     * @property {ExtendedMap} body_parts_canvas - 体のパーツのcanvasを格納した辞書
     * 
     * @property {object} mouse_images - 口パクの画像を格納した辞書
     * @property {string} mouse_folder_name - 口パクの画像が格納されているフォルダの名前
     * 
     * @property {object} chara_canvas_init_data - キャラのcanvasの初期値を格納した辞書
     * @param {object} body_parts - 体のパーツの画像のurlを格納した辞書
     **/
class HumanBodyManager2 {

    /** @type {ExtendedMap<string,PartInfo>} */
    body_parts_info

    /** @type {InitData} */
    init_image_info

    /**@type {ExtendedMap<string,Record<string,ImageInfo>>} */
    body_parts_images

    /**@type {string} */
    mouse_folder_name

    /**@type {ExtendedMap<string, string>} */
    mouse_images = new ExtendedMap();

    /**@type {string} */
    patipati_folder_name

    /**@type {ExtendedMap<string, string>} */
    patipati_images = new ExtendedMap();

    /**@type {string} */
    pyokopyoko_folder_name

    /**@type {ExtendedMap<string, string>} */
    pyokopyoko_images = new ExtendedMap();

    /**@type {Record<string,string>}*/
    setting

    /**@type {"口"|"パクパク"|"無し"} */
    lip_sync_mode = "無し"

    /** @type {Record<"パク"|"パチ"|"ぴょこ",Record<"開候補"|"閉",PartsPath[]>>} */
    onomatopoeia_action_setting = {
        "パク":{"開候補":[],"閉":[]},
        "パチ":{"開候補":[],"閉":[]},
        "ぴょこ":{"開候補":[],"閉":[]}
    }

    /** @type {Record<"パク"|"パチ"|"ぴょこ",PartsPath[]>} */
    now_onomatopoeia_action = {
        "パク":[],
        "パチ":[],
        "ぴょこ":[]
    }

    /**@type {ExtendedMap<string, ExtendedMap<string, InitData>>} */
    pose_patterns;


    /**
     * @param {BodyParts} body_parts - パラメータ1の説明
     * @param {Element|null} human_window - パラメータ2の説明
     */
    constructor(body_parts,human_window = null){
        /**@type {boolean} */
        this.debug = false;
        
        /**@type {string} */
        this.front_name = body_parts.front_name;

        /**@type {string} */
        this.char_name = body_parts["char_name"];

        console.log(body_parts)
        
        this.body_parts_images = new ExtendedMap(Object.entries(body_parts["body_parts_iamges"]));
        console.log(this.body_parts_images)

        //body_parts["init_image_info"]["init"]がないエラーがあるので、エラーキャッチを実装
        try{
            if ("init_image_info" in body_parts){
                this.pose_patterns = /** @type {ExtendedMap<string, ExtendedMap<string, InitData>>} */ this.setPosePatternFromInitImageInfo(body_parts["init_image_info"]);
                if ("setting" in body_parts["init_image_info"]) {
                    this.setting = /** @type {Record<string,Record<string,string>>} */ (body_parts["init_image_info"]["setting"]);
                    this.initializeMouseMoveSetting();
                }
                if ("OnomatopeiaActionSetting" in body_parts["init_image_info"]) {
                    this.onomatopoeia_action_setting = deepCopy(body_parts["init_image_info"]["OnomatopeiaActionSetting"]);
                    
                } 
                if ("NowOnomatopoeiaActionSetting" in body_parts["init_image_info"]) {
                    // debugger;
                    this.now_onomatopoeia_action = deepCopy(body_parts["init_image_info"]["NowOnomatopoeiaActionSetting"]);
                    console.log(this.now_onomatopoeia_action)
                }
                if ("init" in body_parts["init_image_info"]){
                    this.init_image_info = /** @type {Record<string, Record<string, string>>} */ (body_parts["init_image_info"]["init"]);
                    console.log(this.init_image_info)
                }else{
                    throw new Error("body_parts[\"init_image_info\"]はあるが、body_parts[\"init_image_info\"][\"init\"]がありません。")
                }
            }else{
                throw new Error("body_parts[\"init_image_info\"]がありません。")
            }
        }catch(/** @type {any} */ e){
            console.log(e.message);
            this.init_image_info = {};
        }

        //各体パーツの画像の情報を格納したオブジェクトを作成
        this.body_parts_info = new ExtendedMap();
        let z_index_counter_start = 0;
        let z_index_counter_end = -1;

        //パクパクなどをまとめて格納するためのオブジェクトを初期化
        /** @type {ExtendedMap<string,ExtendedMap<string,string[]>>} */
        this.pakupaku_info = new ExtendedMap();
        const pakupaku_list = ["口","パクパク","パチパチ","ぴょこぴょこ"]
        this.pakupaku_folder_names = new ExtendedMap();
        for (let pakupaku of pakupaku_list){
            this.pakupaku_info.set(pakupaku,new ExtendedMap());            
        }

        //体パーツの画像の情報を格納したオブジェクトを作成
        for (let key_part_name of this.body_parts_images.keys()) {
            //key_part_nameの文字列に口が含まれていたら、それを特別なプロパティに格納。promiseで行う。

            const part_info = /** @type {Record<string, ImageInfo>} */ (this.body_parts_images.get(key_part_name));
            
            //体パーツのjsonファイルがある場合、口の情報を取得する
            for (let [part_img_name,part_img_info] of Object.entries(part_info))
            {
                const part_json = part_img_info["json"];
                // for (let pakupaku of pakupaku_list){
                //     if (pakupaku in part_json){
                //         this.pakupaku_folder_names.set(pakupaku,key_part_name);
                //         const pakupaku_param = part_json[pakupaku];
                //         this.pakupaku_info.get(pakupaku).set(pakupaku_param,part_img_name);
                //     }
                // }
                for (let pakupaku of pakupaku_list){
                    if (pakupaku in part_json){
                        // this.pakupaku_folder_names.set(pakupaku,key_part_name);
                        const pakupaku_param = part_json[pakupaku];
                        this.pakupaku_info.get(pakupaku).set(pakupaku_param,[key_part_name,part_img_name]);
                    }
                }


                // if ("口" in part_json){
                //     this.mouse_folder_name = key_part_name;
                //     const phoneme = part_json["口"];
                //     this.mouse_images.set(phoneme,part_img_name);
                // }

                // if ("パチパチ" in part_json){
                //     this.patipati_folder_name = key_part_name;
                //     const patipati_param = part_json["パチパチ"];
                //     this.patipati_images.set(patipati_param, part_img_name);
                // }

                // if ("ぴょこぴょこ" in part_json){
                //     this.pyokopyoko_folder_name = key_part_name;
                //     const pyokopyoko_param = part_json["ぴょこぴょこ"];
                //     this.pyokopyoko_images.set(pyokopyoko_param, part_img_name);
                // }
            }
            
            
            if (key_part_name == "front_name" || key_part_name == "char_name") {
                continue;
            } else {
                console.log(key_part_name,this.body_parts_images,this.body_parts_images.get(key_part_name))
                z_index_counter_start = z_index_counter_end + 1;
                z_index_counter_end = z_index_counter_start + Object.keys(this.body_parts_images.get(key_part_name)).length - 1;
                

                /** @type {PartInfo} */
                const partInfo = {
                    "z_index": (key_part_name.match(/\d+/))[0],//todo もう使わないので消す。一応確認する。
                    "z_index_range": {"start": z_index_counter_start, "end": z_index_counter_end},
                    "imgs": new ExtendedMap(Object.entries(this.body_parts_images.get(key_part_name)).sort(
                        (a, b) => {
                            const keyA = parseInt(a[0].split('_')[0]);
                            const keyB = parseInt(b[0].split('_')[0]);
                            console.log(keyA, keyB);
                            return keyA - keyB;
                        }
                    )),
                    "now_imgs_status": deepCopy(this.pose_patterns.get("init").get(key_part_name)),
                    "mode_radio_duplicate": "radio",
                    "name": key_part_name,
                    "body_img_elemnt_map": new ExtendedMap(),
                    "duplicate_element": null //'<div class="duplicate_mode"></div>'
                };

                this.body_parts_info.set(key_part_name, partInfo); 
            }
        }
        this.body_parts_info.sort(
            (/** @type {string[]} */ a, /** @type {string[]} */ b) => {
                const keyA = parseInt(a[0].split('_')[0]);
                const keyB = parseInt(b[0].split('_')[0]);
                return keyA - keyB;
            });

        //canvasの初期値を格納した辞書を作成。使うデータはbody_partsの中の最初の画像のデータ。
        this.chara_canvas_init_data = this.setCharaCanvasInitData();
        
        //名前入力時点でhuman_windowのelementにnameも追加されてるのでそれを取得する。
        this.human_window = human_window || document.getElementsByClassName(`${this.front_name}`)[0];
        this.human_images = this.human_window.getElementsByClassName("human_images")[0];
        let promise_setBodyParts2Elm = new Promise((resolve,reject) => {
            //search_canvasでのモード
            this.setBodyParts2Elm();
            // @ts-ignore
            resolve();
        })
        promise_setBodyParts2Elm.then(() => {
            console.log(`${this.front_name}インスタンスを生成しました。`);
            console.log(this.human_window);

            this.human_window = document.getElementsByClassName(`${this.front_name}`)[0];
            this.human_images = this.human_window.getElementsByClassName("human_images")[0];
            //画像をドラッグで動かせるようにする
            addMoveImageEvent(this.human_images,this);
        })

        // this.PatiPatiProcess("パチパチ");
        // this.PyokoPyokoProcess("ぴょこぴょこ");

        this.PatiPatiProcess2("パチ");
        this.PyokoPyokoProcess2("ぴょこ");


    }

    setCharaCanvasInitData(){
        const [max_width,max_height] = this.getMaxSizeOfBodyParts(this.body_parts_images);

        const chara_canvas_init_data = {
            "width":max_width,
            "height":max_height,
            "top":0,
            "left":0,
        };
        return chara_canvas_init_data;
    }

    /**
     * 
     * @param {ExtendedMap<string,Record<string,ImageInfo>>} body_parts_images 
     * @returns 
     */
    getMaxSizeOfBodyParts(body_parts_images){
        let max_width = 0;
        let max_height = 0;
        let /** @type {string}*/ key_part_name; 
        let /** @type {Record<string,ImageInfo>}*/ part_info = {};
        for ([key_part_name,part_info] of body_parts_images.entries()){
            let /** @type {string}*/ part_img_name;
            let /** @type {ImageInfo}*/ part_img_info;
            for ([part_img_name,part_img_info] of Object.entries(part_info)){
                const width = part_img_info["json"]["width"] + part_img_info["json"]["x"];
                const height = part_img_info["json"]["height"] + part_img_info["json"]["y"];
                if (width > max_width){
                    max_width = width;
                }
                if (height > max_height){
                    max_height = height;
                }
            }
        }
        console.log("max_width,max_height="+[max_width,max_height]);
        return [max_width,max_height];
    }

    /**
     * 
     * @param {string} combination_name - 組み合わせ名。例えば、"init","^^"など。
     **/
    getPosePattern(combination_name){
        console.log("呼び出し");
        const pose_pattern = this.pose_patterns.get(combination_name);
        return pose_pattern;
    }

    /**
     * @param {string} combination_name - 組み合わせ名。例えば、"init","^^"など。
     * @param {string} part_name - 体のパーツグループの名前。例えば、"口"など。
     **/
    getPartstatusInPosePattern(combination_name,part_name){
        const pose_pattern = this.getPosePattern(combination_name);
        const part_status = pose_pattern.get(part_name);
        return part_status;
    }


    /**
     * 
     * @param {InitImageInfo} init_image_info 
     * @return {ExtendedMap<string, ExtendedMap<string, InitData>>}
     */
    setPosePatternFromInitImageInfo(init_image_info){

        /**
         * @type {ExtendedMap<string, ExtendedMap<string, InitData>>}
         */
        const pose_pattern = new ExtendedMap();
        for (const [key, value] of Object.entries(init_image_info)) {
            
            if (key != "all_data"){
                
                /**
                 * @type {ExtendedMap<string, InitData>}
                 */
                const iamge_info = new ExtendedMap(Object.entries(value).sort(
                        (a, b) => {
                            const keyA = parseInt(a[0].split('_')[0]);
                            const keyB = parseInt(b[0].split('_')[0]);
                            //console.log(keyA, keyB);
                            return keyA - keyB;
                        }
                    ));
                
                pose_pattern.set(key,iamge_info);
            }
        }
        console.log("pose_pattern",pose_pattern);
        return pose_pattern;
    }


    setBodyParts2Elm(){
        var self = this
        //body_partsに対応するhtml要素を作成して、画像を各要素に配置する処理
        //各要素にはクリックしたときに別の画像に順番に切り替える処理を追加する
        console.log("画像の配置を開始")
        //各レイヤーに画像を配置するが、同じレイヤーに複数画像を配置できるようにする。
        let promise = new Promise(function(resolve,reject){                       
            /** @type {IterableIterator<[string, PartInfo]>} */
            let body_parts_info_entries = self.body_parts_info.entries();

            for (let [part_group_name, part_info] of body_parts_info_entries) {

                /** @type {IterableIterator<[string, ImageInfo]>} */
                let image_info_entries = part_info["imgs"].entries();

                for (let [part_name, iamge_info] of image_info_entries) {
                    const on_off = self.getImgStatus(part_group_name, part_name);
                    if (on_off == "off") {
                        continue;
                    } else {

                        let body_img = self.createBodyImageCanvasAndSetImgStatus(part_group_name,part_info,part_name,iamge_info,on_off);

                        //changeImage()でパーツを変更するときに使うので各パーツのelementをmap_body_parts_infoに格納する
                        self.setBodyImgElemnt(part_group_name, part_name, body_img)
                    }

                }

            }
            // @ts-ignore
            resolve()
        })
        promise.then(function(){
            console.log("画像の配置が完了しました。");
            //画像の配置が完了したのでno_image_humanクラスをこのエレメントから削除する
            self.human_window.classList.remove("no_image_human");
            //画像を操作するためのcanvasを作成する
            self.createOperatorCanvas();
        })                   
    }

    /**
     * 
     * @param {string} part_group_name
     * @param {PartInfo} part_info : const part_info = this.getPartInfoFromPartGroupName(part_group_name);
     * @param {string} part_name
     * @param {ImageInfo} iamge_info : const iamge_info = part_info["imgs"].get(part_name);
     * @param {"off" | "on"} on_off : const on_off = this.getImgStatus(part_group_name,part_name);
     * @return {HTMLCanvasElement} body_img
     */
    createBodyImageCanvasAndSetImgStatus(part_group_name,part_info,part_name,iamge_info,on_off){
            //canvasを作成して、そのcanvasに画像を描画する
            let body_img = this.createBodyImageCanvas(part_group_name,part_info,part_name,iamge_info)

            //画像のオンオフの現在のステータスを反映する
            this.changeImgStatus(part_group_name,part_name,on_off,body_img);

            return body_img;
    }

    /**
     * canvasを作成して、そのcanvasに画像を描画すし、z-indexを設定し、human_imagesの子エレメントに追加する
     * @param {string} part_group_name
     * @param {PartInfo} part_info : const part_info = this.getPartInfoFromPartGroupName(part_group_name);
     * @param {string} part_name
     * @param {ImageInfo} iamge_info : const iamge_info = part_info["imgs"].get(part_name);
     * @return {HTMLCanvasElement} body_img
     */
    createBodyImageCanvas(part_group_name,part_info,part_name,iamge_info){
        //canvasを作成して、そのcanvasに画像を描画する
        var body_img = this.createPartCanvas()
        body_img.classList.add("human_image",`${part_group_name}_img`,`${part_name}_img`,`${this.front_name}_img`)
        this.drawPart(body_img, iamge_info);
        //todo body_imgのz-indexを設定する
        body_img.style.zIndex = String(iamge_info["json"]["z_index"]);//String(part_info["z_index"]);
        this.human_images.appendChild(body_img);
        return body_img;
    }

    /**
     * @return {HTMLCanvasElement}
     */
    createPartCanvas(){
        var self = this;
        var part_canvas = document.createElement("canvas");
        //canvasの大きさを設定。場所は画面左上に設定。
        part_canvas.width = self.chara_canvas_init_data["width"];
        part_canvas.height = self.chara_canvas_init_data["height"];
        part_canvas.style.position = "absolute";
        part_canvas.style.top = String(self.chara_canvas_init_data["top"]);
        part_canvas.style.left = String(self.chara_canvas_init_data["left"]);
        //canvasにクラスを追加
        part_canvas.classList.add("part_canvas");

        return part_canvas;
    }

    /**
     * 
     * @param {HTMLCanvasElement} canvas - 画像を描画するcanvas
     * @param {ImageInfo} image_info - 体のパーツの情報を格納した辞書
     * 
     **/
     drawPart(canvas,image_info){
        var self = this;
        // console.log(image_info);
        //canvasに描画
        const ctx = /** @type {CanvasRenderingContext2D} */(canvas.getContext('2d'));
        //canvasをクリア。始点( x , y ) から幅w、高さhの矩形を透明色で初期化します。
        ctx.clearRect(0,0,canvas.width,canvas.height);
        //body_parts_infoの中の各パーツの画像をcanvasに描画する
        const body_part4canvas = new Image();
        const src = image_info["img"];
        const src_data = image_info["json"];
        // console.log("src_data=",src_data)
        body_part4canvas.src = `data:image/png;base64,${src}`;
        //src_dataは{"name": "1_*1.png","x": 760,"y": 398,"width": 337,"height": 477}のような形式。これの通りに画像の座標と縦横を設定する。
        body_part4canvas.onload = function(){
            ctx.drawImage(body_part4canvas,src_data["x"],src_data["y"],src_data["width"],src_data["height"]);
        }
    }

    createOperatorCanvas(){
        console.log("createOperatorCanvas");
        var self = this;
        //1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
        var oprator_canvas = document.createElement("canvas");
        
        
        oprator_canvas.width = self.chara_canvas_init_data["width"] //self.ONE_img_width;
        oprator_canvas.height = self.chara_canvas_init_data["height"];
        oprator_canvas.style.position = "absolute";
        oprator_canvas.style.top = String(self.chara_canvas_init_data["top"]);
        oprator_canvas.style.left = String(self.chara_canvas_init_data["left"]);
       
        //canvasにクラスを追加
        oprator_canvas.classList.add("human_image","operator_canvas",`${self.front_name}_img`);
        //canvasのstyleを設定。ONE_imgエレメントの位置に合わせる。
        oprator_canvas.style.zIndex = String(50000);
        //canvasをhuman_imagesクラスに追加
        var human_images_elem = this.human_window.getElementsByClassName("human_images")[0];
        human_images_elem.appendChild(oprator_canvas);
        this.oprator_canvas = oprator_canvas;
    }

    /**
     * @typedef {Object} HumanBodyCanvasCssStylePosAndSize
     * @property {string} height - The height of the operator canvas.
     * @property {string} top - The top position of the operator canvas.
     * @property {string} left - The left position of the operator canvas.
     */

    /**
     * 現在の体パーツのキャンバスの座標と大きさを取得する
     * @return {HumanBodyCanvasCssStylePosAndSize}
     */
    getOperatorCanvasCssStyle(){
        return {
            "height": this.oprator_canvas.style.height,
            "top": this.oprator_canvas.style.top,
            "left": this.oprator_canvas.style.left,
        }
    }

    /**
     * 体のパーツの画像のhtmlエレメントを設定する
     * @param {string} part_group_name
     * @param {string} part_name
     * @param {HTMLCanvasElement} body_img_elemnt
     */
    setBodyImgElemnt(part_group_name,part_name,body_img_elemnt){
        const part_info = this.getPartInfoFromPartGroupName(part_group_name);
        const body_img_elemnt_map = part_info.body_img_elemnt_map
        body_img_elemnt_map.set(part_name,body_img_elemnt);
    }

    /**
     * 体のパーツの画像のhtmlエレメントを取得する
     * @param {string} part_group_name 
     * @param {string} part_name 
     * @returns {HTMLCanvasElement|null}
     */
    getBodyImgElemnt(part_group_name,part_name){
        const part_info = this.getPartInfoFromPartGroupName(part_group_name);
        const body_img_elemnt_map = part_info.body_img_elemnt_map
        if (body_img_elemnt_map.has(part_name) == false){
            //initでoffになっているパーツの場合、まだ作られてないのでnullを返し、これから作る。
            return null;
        }
        const body_img_elemnt = body_img_elemnt_map.get(part_name);
        return body_img_elemnt;
    }

    /**
     * 体のパーツの画像のステータスを変更する
     * @param {string} image_group - 画像のグループ名
     * @param {string} image_name - 画像の名前
     * @param {"on"|"off"} on_off - 画像をonにするかoffにするか
     * @param {HTMLCanvasElement} body_img - 体のパーツの画像のhtmlエレメント
     */
    changeImgStatus(image_group, image_name, on_off, body_img){

        //body_imgをdisplay:noneにする
        if (on_off == "off") {
            body_img.style.display = "none";
        } else {
            body_img.style.display = "block";
        }
        //画像のステータスを変更する
        this.setImgStatus(image_group,image_name,on_off)
    }

    /**
     * 体のパーツ画像が設定されてるか確認し、されてる場合はchangeImgStatusし、されてない場合はcreateBodyImageCanvasを実行する
     * アコーディオンのクリックイベントで呼ばれる、キャラのパーツを変更するメソッド。
     * 
     * @param {string} image_group - 画像のグループ名
     * @param {string} image_name - 画像の名前
     * @param {"on"|"off"} on_off - 画像をonにするかoffにするか
     * 
     **/
    changeBodyPart(image_group,image_name,on_off){
        let body_img = this.getBodyImgElemnt(image_group,image_name);
        if (body_img == null){
            //body_imgがnullの場合、まだ作られてないので作成する。
            const part_info = this.getPartInfoFromPartGroupName(image_group);
            const iamge_info = part_info.imgs.get(image_name);
            // body_img = this.createBodyImageCanvas(image_group,part_info,image_name,iamge_info);
            let body_img = this.createBodyImageCanvasAndSetImgStatus(image_group,part_info,image_name,iamge_info,on_off);
            //最新の座標と大きさを設定
            this.setNowHumanBodyCanvasCssStylePosAndSize(body_img)
            //changeImage()でパーツを変更するときに使うので各パーツのelementをmap_body_parts_infoに格納する
            this.setBodyImgElemnt(image_group, image_name, body_img)
        } else {
            this.changeImgStatus(image_group,image_name,on_off,body_img);
        }
        
    }

    /**
     * 体のパーツの画像のステータスを変更する
     * @param {HTMLCanvasElement} body_img - 体のパーツの画像のhtmlエレメント
     */
    setNowHumanBodyCanvasCssStylePosAndSize(body_img){
        const style = this.getOperatorCanvasCssStyle();
        body_img.style.height = style.height;
        body_img.style.top = style.top;
        body_img.style.left = style.left;
    }

    /**
     * 各体のパーツのpart_infoを返す
     * @param {string} part_group_name 
     * @returns {PartInfo}
     */
    getPartInfoFromPartGroupName(part_group_name){
        const part_info = this.body_parts_info.get(part_group_name)
        return part_info;
    }

    /**
     * どの体のパーツがon,offになっているかのステータス辞書を返す
     * @param {string} image_group_name 
     * @returns {Record<string, "on"|"off">}
     */
    getNowImgGroupStatusFromPartGroupName(image_group_name){
        const imgs_status = this.getPartInfoFromPartGroupName(image_group_name).now_imgs_status;
        return imgs_status;
    }

    /**
     * 体の画像のグループ名から、オン(またはオフ)になっている画像の名前のリストを返す
     * @param {string} image_group_name
     * @param {"on"|"off"} on_off
     * @returns {string[]}
     */
    getNowOnImgNameList(image_group_name,on_off){
        const imgs_status = this.getNowImgGroupStatusFromPartGroupName(image_group_name);
        const on_img_name_list = Object.keys(imgs_status).filter((key) => imgs_status[key] === on_off);
        return on_img_name_list;
    }

    /**
     * 体の画像１枚がオンかオフかを返す
     * @param {string} image_group 
     * @param {string} image_name
     * @returns {"on"|"off"}
     */
    getImgStatus(image_group,image_name){
        const img_group_status = this.getNowImgGroupStatusFromPartGroupName(image_group);
        const img_status = img_group_status[image_name];
        return img_status;
    }

    /**
     * 体の画像１枚がオンかオフかを設定する
     * @param {string} image_group
     * @param {string} image_name
     * @param {"on"|"off"} on_off
     */
    setImgStatus(image_group,image_name,on_off){
        const img_group_status = this.getNowImgGroupStatusFromPartGroupName(image_group);
        img_group_status[image_name] = on_off;
    }

    /**
     * image_group_nameの中でimage_nameだけをオンにして、それ以外をオフにする
     * @param {string} image_group_name 
     * @param {string} image_name 
     * @param {"on"|"off"} on_off 
     */
    radioChangeImage(image_group_name,image_name,on_off){
        if (on_off == "on"){
            const now_on_img_names = this.getNowOnImgNameList(image_group_name,"on");
            for (let i=0;i<now_on_img_names.length;i++){
                const now_img_name = now_on_img_names[i];
                this.changeBodyPart(image_group_name,now_img_name,"off");
            }
            this.changeBodyPart(image_group_name,image_name,"on");
        } else {
            this.changeBodyPart(image_group_name,image_name,"off");
        }
    }

    /**
     * 口パクの画像を変更する
     * @param {string} char_name - キャラの名前
     * @param {string} phoneme - 音素
     */
    changeLipImage(char_name,phoneme){
        // if (this.mouse_images.size > 1) {
        //     console.log("口を動かす。",phoneme);
        //     if (this.mouse_images.has(phoneme)){
        //         const next_img_name = this.mouse_images.get(phoneme);
        //         this.radioChangeImage(this.mouse_folder_name, next_img_name, "on")
        //     }
        // }
        if (["a","i","u","e","o"].includes(phoneme) == false){
            return;
        }
        switch(this.lip_sync_mode){
            case "口":
                this.changePakuPakuImage("口",phoneme,"on");
                break;
            case "パクパク":
                if(this.prev_pakupaku == "close"){
                    // this.changePakuPakuImage("パクパク","open","on");
                    this.changeOnomatopoeiaImage("パク","open","on");
                    this.changeOnomatopoeiaImage("パク","close","off");
                    this.prev_pakupaku = "open";
                }else{
                    // this.changePakuPakuImage("パクパク","close","on");
                    this.changeOnomatopoeiaImage("パク","close","on");
                    this.changeOnomatopoeiaImage("パク","open","off");
                    this.prev_pakupaku = "close";
                }
                break;
            case "無し":
                break;
        }
    }

    /**
     * 
     * @param {string} pakupaku_mode - パクパクのモード。pakupaku_listの中から選べる。"口","パクパク","パチパチ","ぴょこぴょこ"など。
     * @param {string} pakupaku - パクパクの名前。口ならば音素、ぱちぱちならば目の形の名前など。
     * @param {"on"|"off"} on_off - オンかオフか
     */
    changePakuPakuImage(pakupaku_mode,pakupaku,on_off){
        if (this.pakupaku_info.has(pakupaku_mode)) {
            if (this.pakupaku_info.get(pakupaku_mode).has(pakupaku)){
                const pakupaku_folder_name = this.pakupaku_info.get(pakupaku_mode).get(pakupaku)[0];
                const next_img_name = this.pakupaku_info.get(pakupaku_mode).get(pakupaku)[1];
            }
        }
    }

    /**
     * @param {"パク"| "パチ" | "ぴょこ"} onomatopoeia_action_mode
     * @param {"open"|"close"} openCloseState - 開状態の画像を操作するか閉状態を操作するか
     * @param {"on"|"off"} on_off - 操作でオンにするかオフにするか
     */
    changeOnomatopoeiaImage(onomatopoeia_action_mode, openCloseState, on_off){
        let action_setting = this.onomatopoeia_action_setting[onomatopoeia_action_mode];
        let now_onomatopoeia_list = this.now_onomatopoeia_action[onomatopoeia_action_mode];
        if (now_onomatopoeia_list == undefined) {
            return;
        }
        if (openCloseState == "open") {
            if (on_off == "on") {
                //now_onomatopoeiaの画像を全てオンにする
                console.log("前回の開だったものをオンにします")
                for (let now_onomatopoeia of now_onomatopoeia_list){
                    console.log(now_onomatopoeia.folder_name, now_onomatopoeia.file_name);
                    this.voiro_ai_setting?.setGroupButtonOnOff(now_onomatopoeia.folder_name, now_onomatopoeia.file_name, "on");
                }
            } else {
                //action_setting["開候補"]の画像を全てオフにする
                console.log("開候補をオフにする")
                for (let onomatopoeia of action_setting["開候補"]){
                    this.voiro_ai_setting?.setGroupButtonOnOff(onomatopoeia.folder_name, onomatopoeia.file_name, "off");
                }
            }
        } else if (openCloseState == "close") {
            if (on_off == "on") {
                console.log("閉をオンにする")
                //action_setting["閉"]の画像からランダムで１つオンにする
                const random_close_enable = false
                if (action_setting["閉"].length > 0 && random_close_enable){
                    let onomatopoeia = action_setting["閉"][Math.floor(Math.random() * action_setting["閉"].length)];
                    this.voiro_ai_setting?.setGroupButtonOnOff(onomatopoeia.folder_name, onomatopoeia.file_name, "on");
                } else {
                    //action_setting["閉"]の画像をすべてオンにする
                    for (let onomatopoeia of action_setting["閉"]){
                        this.voiro_ai_setting?.setGroupButtonOnOff(onomatopoeia.folder_name, onomatopoeia.file_name, "on");
                    }
                }
            } else {
                //action_setting["閉"]の画像をすべてオフにする
                console.log("閉をオフにする")
                for (let onomatopoeia of action_setting["閉"]){
                    this.voiro_ai_setting?.setGroupButtonOnOff(onomatopoeia.folder_name, onomatopoeia.file_name, "off");
                }
            }
        }
    }

    /**
     * 
     * @param {"open"|"close"} open_close 
     */
    changeEyeImage(open_close){
        console.log("目を動かす。",open_close);
        if (this.eye_images.size > 1) {
            if (this.mouse_images.has(open_close)){
                const next_img_name = this.mouse_images.get(open_close);
                this.radioChangeImage(this.mouse_folder_name, next_img_name, "on")
            }
        }
    }
    
    /**
     * 
     * @param {string} patipati_mode   - パクパクのモード。pakupaku_listの中から選べる。"口","パクパク","パチパチ","ぴょこぴょこ"など。
     */
    async PatiPatiProcess(patipati_mode){
        console.log("パチパチプロセス開始");
        //20秒ごとにパチパチをする
        while (true){
            console.log(patipati_mode);
            await this.sleep(20000);
            this.changePakuPakuImage(patipati_mode,"close","on");
            this.changePakuPakuImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changePakuPakuImage(patipati_mode,"open","on");
            this.changePakuPakuImage(patipati_mode,"close","off");
        }
    }

    /**
     * 
     * @param {"パク" | "パチ" | "ぴょこ"} patipati_mode   - パクパクのモード。pakupaku_listの中から選べる。"口","パクパク","パチパチ","ぴょこぴょこ"など。
     */
    async PatiPatiProcess2(patipati_mode){
        console.log("パチパチプロセス開始");
        //20秒ごとにパチパチをする
        while (true){
            console.log(patipati_mode);
            await this.sleep(20000);
            this.changeOnomatopoeiaImage(patipati_mode,"close","on");
            this.changeOnomatopoeiaImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changeOnomatopoeiaImage(patipati_mode,"open","on");
            this.changeOnomatopoeiaImage(patipati_mode,"close","off");
        }
    }

    /**
     * 
     * @param {"パク" | "パチ" | "ぴょこ"} patipati_mode   - パクパクのモード。pakupaku_listの中から選べる。"口","パクパク","パチパチ","ぴょこぴょこ"など。
     */
    async PyokoPyokoProcess2(patipati_mode){
        console.log("ぴょこぴょこプロセス開始");
        //20秒ごとにぴょこぴょこをする
        while (true){
            console.log(patipati_mode);
            //5~20秒の間でランダムなタイミングでぴょこぴょこをする
            const timing = Math.floor(Math.random() * (20000 - 5000) + 5000);
            await this.sleep(timing);
            // await this.sleep(100);
            this.changeOnomatopoeiaImage(patipati_mode,"close","on");
            this.changeOnomatopoeiaImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changeOnomatopoeiaImage(patipati_mode,"open","on");
            this.changeOnomatopoeiaImage(patipati_mode, "close", "off")
            await this.sleep(100);
            this.changeOnomatopoeiaImage(patipati_mode,"close","on");
            this.changeOnomatopoeiaImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changeOnomatopoeiaImage(patipati_mode,"open","on");
            this.changeOnomatopoeiaImage(patipati_mode, "close", "off")
        }
    }

    /**
     * 
     * @param {string} patipati_mode   - パクパクのモード。pakupaku_listの中から選べる。"口","パクパク","パチパチ","ぴょこぴょこ"など。
     */
    async PyokoPyokoProcess(patipati_mode){
        console.log("ぴょこぴょこプロセス開始");
        //20秒ごとにぴょこぴょこをする
        while (true){
            console.log(patipati_mode);
            //5~20秒の間でランダムなタイミングでぴょこぴょこをする
            const timing = Math.floor(Math.random() * (20000 - 5000) + 5000);
            await this.sleep(timing);
            this.changePakuPakuImage(patipati_mode,"close","on");
            this.changePakuPakuImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changePakuPakuImage(patipati_mode,"open","on");
            this.changePakuPakuImage(patipati_mode,"close","off");
            await this.sleep(100);
            this.changePakuPakuImage(patipati_mode,"close","on");
            this.changePakuPakuImage(patipati_mode, "open", "off")
            await this.sleep(100);
            this.changePakuPakuImage(patipati_mode,"open","on");
            this.changePakuPakuImage(patipati_mode,"close","off");
        }
    }

    /**
     * 
     * @param {*} ms 
     * @returns 
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    initializeMouseMoveSetting(){
        this.lip_sync_mode = "口";

        if ("lip_sync" in this.setting){
            const lip_sync_mode_list = ["口","パクパク","無し"];
            if (lip_sync_mode_list.includes(this.setting["lip_sync"])){
                this.lip_sync_mode = this.setting["lip_sync"];
                if (this.lip_sync_mode == "パクパク"){
                    this.prev_pakupaku = "open";
                }
            } else if (this.checkOnPakuPaku() == true) {
                this.setLipSyncModeToPakuPaku("パク");
            } 
        }
        
    }

    /**
     * パクパク設定で「パク」がオンになっていてパクパクを起動するようにユーザーが思っているか確認する。
     * @returns {boolean}
     */
    checkOnPakuPaku(){
        return this.onomatopoeia_action_setting["パク"]["閉"].length > 0
    }

    /**
     * 
     * @param {"口" | "パク" | "パチ" | "ぴょこ"} onomatopoeia_action_mode 
     */
    setLipSyncModeToPakuPaku(onomatopoeia_action_mode){
        if (onomatopoeia_action_mode == "パク"){
            this.lip_sync_mode = "パクパク";
            this.prev_pakupaku = "open";
        }
    }

    /**
     * 
     * @param {"口" | "パク" | "パチ" | "ぴょこ"} onomatopoeia_action_mode 
     */
    setLipSyncModeToAIUEO(onomatopoeia_action_mode){
        if (onomatopoeia_action_mode == "口"){
            this.lip_sync_mode = "口";
            this.prev_pakupaku = "";
        }
    }

    /**
     * @param {"パク"| "パチ" | "ぴょこ"} onomatopoeia_action_mode
     * @param {"開候補"|"閉"} openCloseState 
     * @param {PartsPath} PartsPath 
     */
    setToOnomatopoeiaActionSetting(onomatopoeia_action_mode,openCloseState,PartsPath){
        let action_setting = this.onomatopoeia_action_setting[onomatopoeia_action_mode];
        action_setting[openCloseState].push(PartsPath);
        console.log(this.onomatopoeia_action_setting);
    }

    /**
     * @param {"パク"| "パチ" | "ぴょこ"} onomatopoeia_action_mode
     * @param {"開候補"|"閉"} openCloseState 
     * @param {PartsPath} PartsPath 
     */
    removeFromOnomatopoeiaActionSetting(onomatopoeia_action_mode, openCloseState, PartsPath){
        let action_setting = this.onomatopoeia_action_setting[onomatopoeia_action_mode];
        action_setting[openCloseState] = action_setting[openCloseState].filter((value) => {
            return !this.isEquivalentPartsPath(value,PartsPath);
        });
        console.log(this.onomatopoeia_action_setting)
    }

    /**
     * @param {PartsPath} PartsPath1
     * @param {PartsPath} PartsPath2
     * @returns {boolean} 
     */
    isEquivalentPartsPath(PartsPath1,PartsPath2){
        if (PartsPath1.folder_name == PartsPath2.folder_name && PartsPath1.file_name == PartsPath2.file_name){
            return true;
        } else {
            return false;
        }
    }

    /**
     * @param {VoiroAISetting} vas
     */
    BindVoiroAISetting(vas){
        this.voiro_ai_setting = vas;
    }

        

}

class iHumanBodyManager{
    /**
     * @property {boolean} debug - デバッグモードかどうか
     * @property {string} front_name - フロントエンドでのキャラの名前
     * @property {string} char_name - キャラの名前
     * @property {object} body_parts_images - 体のパーツの画像のurlを格納した辞書
     * @property {object} init_image_info - 体のパーツの画像の初期値を格納した辞書
     * @property {ExtendedMap} pose_patterns - ポーズのパターンを格納した辞書
     * @property {object} body_parts_info - 体のパーツの画像の情報を格納した辞書
     * @property {object} body_status - 体のパーツのどれをvisible = tue　にするかを管理するオブジェクト
     * @property {ExtendedMap} map_body_parts_info - body_parts_infoをMap型に変換したもの
     * 
     * @property {object} mouse_images - 口パクの画像を格納した辞書
     * @property {string} mouse_folder_name - 口パクの画像が格納されているフォルダの名前
     * 
     * @property {object} chara_canvas_init_data - キャラのcanvasの初期値を格納した辞書
     * 
     *  
     **/
    constructor(body_parts){
        this.debug = false;
        this.front_name = body_parts["front_name"];
        this.char_name = body_parts["char_name"];
        this.body_parts_images = body_parts["body_parts_iamges"];
        this.mode_chara_canvas = this.modeJudge();
        console.log(this.mode_chara_canvas)
        console.log("body_parts_imagesの中身を展開開始",this.body_parts_images);
        //body_parts["init_image_info"]["init"]がないエラーがあるので、エラーキャッチを実装
        try{
            if ("init_image_info" in body_parts){
                if ("init" in body_parts["init_image_info"]){
                    this.init_image_info = body_parts["init_image_info"]["init"];
                }else{
                    throw new Error("body_parts[\"init_image_info\"]はあるが、body_parts[\"init_image_info\"][\"init\"]がありません。")
                }
            }else{
                throw new Error("body_parts[\"init_image_info\"]がありません。")
            }
        }catch(e){
            console.log(e.message);
            this.init_image_info = {};
        }
        this.pose_patterns = this.getPosePatternFromInitImageInfo(body_parts["init_image_info"]);

        //body_partsはキーが体のパーツの名前、値がそのパーツの画像のurlの辞書
        //html上でbody_partsの画像を表示するときの情報を管理するオブジェクト
        this.body_parts_info = {};
        this.mouse_images = {};
        this.mouse_folder_name = "";
        var z_index_counter_start = 0;
        var z_index_counter_end = -1;
        for (var key_part_name in this.body_parts_images) {
            //key_part_nameの文字列に口が含まれていたら、それを特別なプロパティに格納。promiseで行う。
            if (key_part_name.includes("口")) {
                console.log("口が含まれている")
                this.mouse_folder_name = key_part_name;
                var phoneme_list = ["a","i","u","e","o","n"];

                for (let i=0;i<phoneme_list.length;i++){
                    var phoneme = phoneme_list[i];
                    console.log("phoneme="+phoneme,this.body_parts_images[key_part_name],key_part_name)
                    for (let mouse_img_name in this.body_parts_images[key_part_name])
                    {
                        console.log("phoneme="+phoneme,"mouse_img_name="+mouse_img_name);
                        if (mouse_img_name.includes(phoneme)){
                            this.mouse_images[phoneme] = this.body_parts_images[key_part_name][mouse_img_name]["img"];
                        }
                    }
                }
                console.log("this.mouse_images=",this.mouse_images);
                //体パーツのjsonファイルがある場合、口の情報を取得する
                if (this.mode_chara_canvas == 2) {
                    for (let mouse_img_name in this.body_parts_images[key_part_name])
                    {
                        console.log("mouse_img_name=",mouse_img_name);
                        const mouse_json = this.body_parts_images[key_part_name][mouse_img_name]["json"];
                        console.log("mouse_json=",mouse_json);
                        if ("口" in mouse_json){
                            const phoneme = mouse_json["口"];
                            this.mouse_images[phoneme] = mouse_img_name;
                        }
                        if ("口1" in mouse_json){
                            const phoneme1 = mouse_json["口1"];
                            this.mouse_images[phoneme1] = mouse_img_name;
                        }
                    }
                    console.log("this.mouse_images=",this.mouse_images);
                    

                }
            }

            if (key_part_name == "front_name" || key_part_name == "char_name"){
                continue;
            } else {
                console.log(key_part_name)
                z_index_counter_start = z_index_counter_end + 1;
                z_index_counter_end = z_index_counter_start + Object.keys(this.body_parts_images[key_part_name]).length - 1;
                //this.body_parts_images[key_part_name]の中身が再び辞書の場合があるので、それを展開する
                var init_image_name = "";
                if (key_part_name in this.init_image_info) {
                    init_image_name = this.init_image_info[key_part_name];
                }

                //key_part_nameは12後ろ髪のような体のパーツの名前。ここから数字の部分だけを取得。
                //中身を取得する方法の例は以下。
                //map_body_parts_info.get("12後ろ髪")["imgs"].get("12後ろ髪_1")
                const part_info = {
                    "z_index":(key_part_name.match(/\d+/))[0],
                    "z_index_range":{"start":z_index_counter_start,"end":z_index_counter_end},
                    "imgs":new ExtendedMap(Object.entries(this.body_parts_images[key_part_name]).sort(
                        (a, b) => {
                            const keyA = parseInt(a[0].split('_')[0]);
                            const keyB = parseInt(b[0].split('_')[0]);
                            console.log(keyA,keyB)
                            return keyA - keyB;
                        })),
                    "now_img_index":0,
                    "now_img_name":init_image_name,
                    "mode_radio_duplicate":"radio",
                    "name":key_part_name,
                    "element":null,
                    "duplicate_element":null,//'<div class="duplicate_mode"></div>'

                };
                console.log(part_info);
                this.body_parts_info[key_part_name] = part_info;
            }
        }
        this.map_body_parts_info = new ExtendedMap(Object.entries(this.body_parts_info).sort(
            (a, b) => {
                const keyA = parseInt(a[0].split('_')[0]);
                const keyB = parseInt(b[0].split('_')[0]);
                return keyA - keyB;
            }));
        console.log("search_canvasでのモード",[...this.map_body_parts_info.values()].reverse())
        console.log("body_parts_imagesの中身を展開終了",this.map_body_parts_info);

        //canvasの初期値を格納した辞書を作成。使うデータはbody_partsの中の最初の画像のデータ。
        this.chara_canvas_init_data = this.setCharaCanvasInitData();


        //body_statusは体のパーツのどれをvisible = tue　にするかを管理するオブジェクト。z_indexをキーにして、visible = trueのパーツの名前を格納する。
        this.body_status = {};
        //body_statusを初期化するために、body_parts_infoの配列の長さ分だけループを回す
        for (var i = 0; i < Object.keys(this.body_parts_info).length; i++) {
            this.body_status[i] = [];
        }
        console.log(this)
        console.log(this.front_name)
        //名前入力時点でhuman_windowのelementにnameも追加されてるのでそれを取得する。
        this.human_window = document.getElementsByClassName(`${this.front_name}`)[0];
        this.human_images = this.human_window.getElementsByClassName("human_images")[0];
        let promise_setBodyParts2Elm = new Promise((resolve,reject) => {
            if(this.mode_chara_canvas == 1){
                this.createCharaCanvas();
                this.setBodyPart2Canvas();
                console.log("chara_canvasの処理終了")
            } else {
                //search_canvasでのモード
                this.setBodyParts2Elm();
            } 
            resolve()
        })
        promise_setBodyParts2Elm.then(() => {
            console.log(`${this.front_name}インスタンスを生成しました。`);
            console.log(this.human_window);

            this.human_window = document.getElementsByClassName(`${this.front_name}`)[0];
            this.human_images = this.human_window.getElementsByClassName("human_images")[0];
            //画像をドラッグで動かせるようにする
            addMoveImageEvent(this.human_images,this);
        })

        

    }

    setCharaCanvasInitData(){
        const chara_canvas_init_data = {
            "width":3500,
            "height":3500,
            "top":0,
            "left":0,
        };
        return chara_canvas_init_data;
    }
    
    setBodyParts2Elm(){
        var self = this
        //画像の初期設定があるかどうかのスイッチ
        const init_image_switch = Object.keys(self.init_image_info).length
        //body_partsに対応するhtml要素を作成して、画像を各要素に配置する処理
        //各要素にはクリックしたときに別の画像に順番に切り替える処理を追加する
        console.log("画像の配置を開始")
        //各レイヤーに画像を配置するが、同じレイヤーに複数画像を配置できるようにする。
        let promise = new Promise(function(resolve,reject){                       
            for (const [part_group_name, part_info] of self.map_body_parts_info) {
                //part_group_nameは体のパーツの名前、part_infoはそのパーツの画像群の配列
                console.log(part_group_name,part_info)
                
                //init_image_infoが空でないなら、init_image_infoの画像を配置する
                if(self.mode_chara_canvas == 2){
                    //canvasを作成して、そのcanvasに画像を描画する
                    var body_img = self.createPartCanvas()
                    body_img.classList.add("human_image",`${part_group_name}_img`,`${self.front_name}_img`,"radio_mode_img")
                    if ("" != self.init_image_info[part_group_name]) {
                        
                        //初期配置の画像を描画する
                        const init_part_name = self.init_image_info[part_group_name];
                        self.drawPart(body_img, part_group_name, part_info, init_part_name)
                    } else {
                        //init_image_infoにpart_group_nameがない場合は、エレメントを非表示にする
                        body_img.style.visibility = "hidden";
                    }
                } else if (self.mode_chara_canvas == 0){
                    if ("" != self.init_image_info[part_group_name]) {
                        var body_img = document.createElement("img")
                        body_img.classList.add("human_image",`${part_group_name}_img`,`${self.front_name}_img`,"radio_mode_img")
                        body_img.src = `data:image/png;base64,${part_info["imgs"].get(self.init_image_info[part_group_name])["img"]}`
                    } else {
                        //init_image_infoにpart_group_nameがない場合は、エレメントを非表示にする
                        body_img.style.visibility = "hidden";
                    }
                }
                //body_imgのz-indexを設定する
                body_img.style.zIndex = part_info["z_index"];
                self.human_images.appendChild(body_img);
                //changeImage()でパーツを変更するときに使うので各パーツのelementをmap_body_parts_infoに格納する
                part_info["element"] = body_img;


            }
            resolve()
        })
        promise.then(function(){
            console.log("画像の配置が完了しました。");
            console.log(self.map_body_parts_info);
            //画像の配置が完了したのでno_image_humanクラスをこのエレメントから削除する
            self.human_window.classList.remove("no_image_human");
            //画像を操作するためのcanvasを作成する
            self.createOperatorCanvas();
        })                   
    }

    createPartCanvas(){
        var self = this;
        var part_canvas = document.createElement("canvas");
        //canvasの大きさを設定。場所は画面左上に設定。
        part_canvas.width = self.chara_canvas_init_data["width"];
        part_canvas.height = self.chara_canvas_init_data["height"];
        part_canvas.style.position = "absolute";
        part_canvas.style.top = self.chara_canvas_init_data["top"];
        part_canvas.style.left = self.chara_canvas_init_data["left"];
        //canvasにクラスを追加
        part_canvas.classList.add("part_canvas");

        return part_canvas;
    }

    /**
     * 
     * @param {object} canvas - 画像を描画するcanvas
     * @param {string} part_group_name - 体のパーツの名前
     * @param {object} part_info - 体のパーツの情報を格納した辞書
     * @param {string} part_name - 体のパーツの名前
     * 
     **/
    drawPart(canvas,part_group_name,part_info,part_name){
        console.log("drawPart")
        var self = this;

        //canvasに描画
        const ctx = canvas.getContext('2d');
        //canvasをクリア。始点( x , y ) から幅w、高さhの矩形を透明色で初期化します。
        ctx.clearRect(0,0,canvas.width,canvas.height);
        //body_parts_infoの中の各パーツの画像をcanvasに描画する
        const body_part4canvas = new Image();
        const body_img = part_info["imgs"].get(part_name);
        const src = body_img["img"];
        const src_data = body_img["json"];
        console.log("src_data=",src_data)
        body_part4canvas.src = `data:image/png;base64,${src}`;
        //src_dataは{"name": "1_*1.png","x": 760,"y": 398,"width": 337,"height": 477}のような形式。これの通りに画像の座標と縦横を設定する。
        body_part4canvas.onload = function(){
            ctx.drawImage(body_part4canvas,src_data["x"],src_data["y"],src_data["width"],src_data["height"]);
        }
    }

    createCharaCanvas(){
        var self = this;
        var chara_canvas = document.createElement("canvas");
        //canvasの大きさを設定。場所は画面左上に設定。
        chara_canvas.width = self.chara_canvas_init_data["width"];
        chara_canvas.height = self.chara_canvas_init_data["height"];
        chara_canvas.style.position = "absolute";
        chara_canvas.style.top = 0;
        chara_canvas.style.left = 0;
        //canvasにクラスを追加
        chara_canvas.classList.add("chara_canvas");
        //canvasをhuman_imagesクラスに追加
        self.human_images.appendChild(chara_canvas);
        self.chara_canvas = chara_canvas;

    }

    /**
     * now_img_nameを元に、body_parts_infoの画像をcanvasに描画する関数
     **/
    setBodyPart2Canvas(){
        //canvasを作成する
        var self = this;
        //canvasに描画
        var ctx = self.chara_canvas.getContext('2d');
        //canvasをクリア。始点( x , y ) から幅w、高さhの矩形を透明色で初期化します。
        ctx.clearRect(0,0,self.chara_canvas_init_data["width"],self.chara_canvas_init_data["height"]);
        //body_parts_infoの中の各パーツの画像をcanvasに描画する
        for(var part_info of [...this.map_body_parts_info.values()]){
            const body_part4canvas = new Image();
            const part_name = part_info["now_img_name"];
            //part_nameが""の場合は、画像を表示しない
            if (part_name == ""){
                continue;
            } else {
                const body_img = part_info["imgs"].get(part_name);
                const src = body_img["img"];
                const src_data = body_img["json"];
                body_part4canvas.src = `data:image/png;base64,${src}`;
                //src_dataは{"name": "1_*1.png","x": 760,"y": 398,"width": 337,"height": 477}のような形式。これの通りに画像の座標と縦横を設定する。
                body_part4canvas.onload = function(){
                    ctx.drawImage(body_part4canvas,src_data["x"],src_data["y"],src_data["width"],src_data["height"]);
                }
                //ctx.drawImage(body_part4canvas,0,0,self.ONE_img_width,self.ONE_img_height);
                //console.log(`${part_name}の画像の配置完了`);
            }
            
        }
    }

    createOperatorCanvas(){
        console.log("createOperatorCanvas");
        var self = this;
        //1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
        var oprator_canvas = document.createElement("canvas");
        //ONE_imgエレメントの大きさを取得
        var human_images_elem = this.human_window.getElementsByClassName("human_images")[0];
        var ONE_img = human_images_elem.getElementsByClassName("human_image")[0];
        console.log("ONE_img",ONE_img);
        self.ONE_img_width = ONE_img.clientWidth;
        self.ONE_img_height = ONE_img.clientHeight;
        //canvasの大きさを設定
        console.log("canvasの大きさを設定",{"ONE_img_width":self.ONE_img_width,"ONE_img_height":self.ONE_img_height});
        if (self.mode_chara_canvas == 0){
            oprator_canvas.width = self.ONE_img_width;
            oprator_canvas.height = self.ONE_img_height;
        } else if (self.mode_chara_canvas == 2){
            oprator_canvas.width = self.chara_canvas_init_data["width"] //self.ONE_img_width;
            oprator_canvas.height = self.chara_canvas_init_data["height"];
            oprator_canvas.style.position = "absolute";
            oprator_canvas.style.top = self.chara_canvas_init_data["top"];
            oprator_canvas.style.left = self.chara_canvas_init_data["left"];
        }
       
        //canvasにクラスを追加
        oprator_canvas.classList.add("human_image","operator_canvas",`${self.front_name}_img`);
        //canvasのstyleを設定。ONE_imgエレメントの位置に合わせる。
        oprator_canvas.style.zIndex = 50000;
        //canvasをhuman_imagesクラスに追加
        human_images_elem.appendChild(oprator_canvas);
        //SarchCanvaseを作成する
        self.createSarchCanvase();
        //oprator_canvasの左上端の点に点を描くイベントを追加
        drawFillRectInOpratorCanvas(0,0,50,50,"red");


        //canvasにイベントを追加
        oprator_canvas.addEventListener("click",function(e){
            console.log("oprator_canvasが左クリックされた");
            //clickした座標からcanvasのページ内での絶対座標を引く
            var canvas_rect = this.getBoundingClientRect();
            //opratpr_canvasのdata属性からscaleを取得
            var canvas_scale = this.dataset.scale;

            var x_on_canvas = (e.pageX - canvas_rect.left) / canvas_scale;
            var y_on_canvas = (e.pageY - canvas_rect.top) / canvas_scale;
            console.log("canvasのページ内での絶対座標",{x:x_on_canvas,y:y_on_canvas});
            const body_part = self.searchImage(x_on_canvas,y_on_canvas);
            if (   body_part["name"] == "eyer" 
                || body_part["name"] == "tail"){
                //2回変更する
                self.changeImage(body_part,"next");
                setTimeout(function(){
                    self.changeImage(body_part,"next")
                },50)
            }
            else{
                //body_partを次の画像に変更する
                self.changeImage(body_part,"next");
            }
            
            
        })
        oprator_canvas.addEventListener("contextmenu",function(e){
            //contextmenuは右クリックしたときのイベント。右クリックしたときには、前の画像に変更する。
            e.preventDefault();
            console.log("oprator_canvasが右クリックされた")
            //clickした座標からcanvasのページ内での絶対座標を引く
            var canvas_rect = this.getBoundingClientRect()
            var x_on_canvas = e.pageX - canvas_rect.left;
            var y_on_canvas = e.pageY - canvas_rect.top;
            console.log("canvasのページ内での絶対座標",{x:x_on_canvas,y:y_on_canvas})
            const body_part = self.searchImage(x_on_canvas,y_on_canvas)
            if (   body_part["name"] == "eyer" 
                || body_part["name"] == "tail"){
                //2回変更する
                self.changeImage(body_part,"prev");
                setTimeout(function(){
                    self.changeImage(body_part,"prev")
                },50);
            }
            else{
                //body_partを次の画像に変更する
                self.changeImage(body_part,"prev");
            }
        })
    }

    //search_canvasを作成する関数
    createSarchCanvase(){
        var self = this;
        //1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
        var search_canvas = document.createElement("canvas");
        //canvasの大きさを設定。場所は画面左上に設定。
        search_canvas.width = self.ONE_img_width;
        search_canvas.height = self.ONE_img_height;
        if (this.debug){
            search_canvas.style.zIndex = 50;
        } else{
            search_canvas.style.zIndex = -1;
        }
        
        search_canvas.style.position = "absolute";
        search_canvas.style.top = 0;
        search_canvas.style.left = 0;
        //canvasにクラスを追加
        search_canvas.classList.add("search_canvas");
        
        if (this.debug){
            //canvasをあかねクラスに追加
            var akane_window = document.getElementsByClassName("あかね")[0];
            akane_window.appendChild(search_canvas);
            console.log("search_canvasを作成した",this);
            this.search_canvas = search_canvas;
        } else {
            var search_canvas_elem = self.human_window.getElementsByClassName("search_canvas")[0];
            console.log("search_canvas_elem",search_canvas_elem);
            search_canvas_elem.appendChild(search_canvas);
            console.log("search_canvasを作成した",this);
            this.search_canvas = search_canvas;
        }
    }

    /**clickされた画像の座標の色を取得する関数を以下の手順で作る。
     * 0:clickされた座標のONE_imgエレメントの中心からの相対座標を入力する。
     * 1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
     * 2:this.body_parts_listの中の画像を下から順にcanvasに描画する。
     * 3:canvasの座標(x,y)の色を取得する。
     */
    searchImage(x,y){
        var self = this;
        console.log("searchImageが呼び出された");
        console.log(self);
        //canvasのcontextを取得
        var search_ctx = self.search_canvas.getContext("2d")
        //2:this.body_parts_listの中の画像を下から順にcanvasに描画する。
        console.log("2:this.body_parts_listの中の画像を下から順にcanvasに描画する。")
        for(var body_part of [...this.map_body_parts_info.values()].reverse()){
            console.log("body_partの中身を表示",body_part);
            const body_part4canvas = new Image();
            //now_indexから現在の各パーツの画像を取得
            var now_index = body_part["now_img_index"];
            console.log("now_index",now_index);
            body_part4canvas.src = `data:image/png;base64,${[...body_part["imgs"].values()][now_index]}`;
            //各パーツのz_indexを取得
            var z_index = body_part["z_index"];
            /*body_part4canvas.onload = function(){
                search_ctx.drawImage(body_part4canvas,0,0,self.ONE_img_width,self.ONE_img_height)
            }*/
            search_ctx.drawImage(body_part4canvas,0,0,self.ONE_img_width,self.ONE_img_height);
            console.log("画像の配置完了");
            //3:canvasの座標(x,y)の色を取得する。
            var imgData = search_ctx.getImageData(x,y,1,1);
            var data = imgData.data;
            console.log("取得した色",data);
            //取得した色が透明でない場合は、breakする。
            if(data[3] != 0){
                console.log(`${body_part["name"]}をクリックした`);
                if (false == this.debug){
                    //search_canvasをクリアする
                    search_ctx.clearRect(0,0,self.ONE_img_width,self.ONE_img_height);
                }
                return body_part;
            }
        }
        if (false == this.debug){
            //何もないところをクリックしたときも、search_canvasをクリアする
            search_ctx.clearRect(0,0,self.ONE_img_width,self.ONE_img_height);
        }
        return 0;
    }

    /**
     * this.tail_list = {"z_index":2,"imgs":tail_map,"now_img_index":0,"name":"tail","elemetn":..}
     * などが入力されるので、now_img_indexを次の画像に変更する関数
     * @param {*} body_part
     * @param {*} change_type
     */
    changeImage(body_part,change_type){
        if (body_part == 0){
            console.log("何もないところをクリックした");
            return 0;
        } else {
            const tmp_index = body_part["now_img_index"];
            if (change_type == "next"){
                var index = (body_part["now_img_index"] + 1) % body_part["imgs"].size;
            } else if (change_type == "prev"){
                var index = (body_part["now_img_index"] - 1 + body_part["imgs"].size) % body_part["imgs"].size;
            }
            if (tmp_index != index) {
                body_part["now_img_index"] = index;
                body_part["now_img_name"] = [...body_part["imgs"].keys()][index];
                
                if (this.char_name in setting_info) {
                    this.setBodyPartImage(body_part,index);
                } else {
                    body_part["element"].src = `data:image/png;base64,${[...body_part["imgs"].values()][index]}`;
                }
                console.log("画像を変更しました",index);   
            }
        }
    }

    /**
     * アコーディオンのクリックイベントで呼ばれる、キャラのパーツを変更するメソッド。
     * 
     * @param {string} image_group - 画像のグループ名
     * @param {string} image_name - 画像の名前
     * @param {string} on_off - 画像をonにするかoffにするか
     * 
     **/
    changeBodyPart(image_group,image_name,on_off){
        try {
            //now_img_nameとnow_img_indexを変更する
            if (on_off == "on"){
                this.setNowImageNameBodyPart(image_group,image_name);
                this.setNowImageIndexByNameBodyPart(image_group,image_name);
            } else if (on_off == "off"){
                this.setNowImageNameBodyPart(image_group,"");
                this.setNowImageIndexByNameBodyPart(image_group,"");
            }

            if (this.mode_chara_canvas == 1) {
                console.log("chara_canvas管理の場合")
                //chara_canvasに描画する
                this.setBodyPart2Canvas();
            } else {
                console.log("chara_canvas管理でない場合")
                //chara_canvas管理でない場合
                var ELM_taget_group_img = this.body_parts_info[image_group]["element"];
                console.log("ELM_taget_group_img",ELM_taget_group_img);
                
                if(image_name != "") {
                    const target = this.map_body_parts_info.get(image_group)["imgs"].get(image_name)["img"]
                    if (on_off == "on") {
                        if (this.mode_chara_canvas == 2) {
                            //ELM_taget_group_imgはcanvasなので、drawPartで描画する
                            this.drawPart(ELM_taget_group_img,image_group,this.map_body_parts_info.get(image_group),image_name)
                        }else {
                            ELM_taget_group_img.src = `data:image/png;base64,${target}`;
                        }
                        
                        ELM_taget_group_img.style.visibility = "visible";
                    } else if (on_off == "off"){
                        ELM_taget_group_img.style.visibility = "hidden";
                    }
                } else {
                    ELM_taget_group_img.style.visibility = "hidden";
                }
            }
        } catch (e) {
            console.log(`引数の一部が指定されていないので実行をスキップ。image_group:${image_group},image_name:${image_name},on_off:${on_off}`)
            console.log(e.message);
            exit();
        }
    }

    setBodyPartImage(body_part,index) {

        body_part["now_img_index"] = index;
        body_part["element"].src = `data:image/png;base64,${[...body_part["imgs"].values()][index]["img"]}`;
        //設定用アコーディオンの状態を変更する
        if (this.char_name in setting_info){
            const accordion = setting_info[this.char_name]
            const body_part_name = body_part["name"]
            const image_name = this.getNamesListBodyPartByIndex(body_part_name,index)
            accordion.setBodyPartImage(body_part_name,image_name)
        }
    }
    setBodyPartByNameImageByIndex(body_part_name,index) {
        const body_part = this.map_body_parts_info.get(body_part_name);
        this.setBodyPartImage(body_part,index);
    }

    changeLipImage(char_name,phoneme){
        if (Object.keys(this.mouse_images).length > 1) {
            //console.log("分分岐に入った");
            if (this.mode_chara_canvas == 0) {
                var ELM_mouse_img = this.body_parts_info[this.mouse_folder_name]["element"];
                if (phoneme == "a"){                           
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["a"]}`;
                } else if (phoneme == "i"){
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["i"]}`;
                } else if (phoneme == "u"){
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["u"]}`;
                } else if (phoneme == "e"){
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["e"]}`;
                } else if (phoneme == "o"){
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["o"]}`;
                } else if (phoneme == "end"){
                    ELM_mouse_img.src = `data:image/png;base64,${this.mouse_images["n"]}`;
                
                }
            } else if (this.mode_chara_canvas == 2) {
                console.log("口を動かす。",phoneme);
                if (phoneme in this.mouse_images){
                    const image_name = this.mouse_images[phoneme];
                    this.changeBodyPart(this.mouse_folder_name,image_name,"on");
                }
            }
        }
        
    }

    

    getInitImageNameBodyPart(image_group){
        if (image_group in this.init_image_info){
            return this.init_image_info[image_group];
        } else {
            return "";
        }
    }

    getNowNameBodyPart(image_group){
        return this.body_parts_info[image_group]["now_img_name"];
    }

    getNowIndexBodyPart(image_group){
        var now_index = this.body_parts_info[image_group]["now_img_index"];
        return now_index;
    }

    getNamesListBodyPartByIndex(image_group,index){
        const part_names = this.getNamesListBodyPart(image_group);
        const name = part_names[index];
        return name;
    }

    getNamesListBodyPart(image_group){
        const part_names = [...this.body_parts_info[image_group]["imgs"].keys()];
        return part_names;
    }

    getNowImageIndexByNameBodyPart(image_group,image_name){
        const part_names = this.getNamesListBodyPart(image_group);
        const index = part_names.indexOf(image_name);
        return index;
    }

    setNowImageIndexByNameBodyPart(image_group,image_name){
        const index = this.getNowImageIndexByNameBodyPart(image_group,image_name);
        this.map_body_parts_info.get(image_group)["now_img_index"] = index;
    }

    getNowImageNameBodyPart(image_group){
        return this.body_parts_info[image_group]["now_img_name"];
    }

    setNowImageNameBodyPart(image_group,image_name){
        this.body_parts_info[image_group]["now_img_name"] = image_name;
    }

    getPosePattern(combination_name){
        const pose_pattern = this.pose_patterns.get(combination_name);
        return pose_pattern;
    } 

    modeJudge(){
        //this.body_parts_imagesの1番目の画像のjsonがあるかどうかで、search_canvasでのモードか、chara_canvasでのモードかを判定する。
        try {
            let valuesArray = Object.values(this.body_parts_images);
            if ("json" in getNthValueFromObject(valuesArray[0],0)){
                return 2;//1;
            } else {
                return 0;
            }
        } catch (e) {
            console.log("modeJudgeでエラーが発生しました。");
            console.log(e.message);
            return 2;//1;
        }
    }

    getPosePatternFromInitImageInfo(init_image_info){
        const all_info = init_image_info;
        const pose_pattern = new ExtendedMap();
        for (const [key, value] of Object.entries(all_info)) {
            if (key != "init" || key != "all_data"){
                pose_pattern.set(key,value);
            }
        }
        console.log("pose_pattern",pose_pattern);
        return pose_pattern;
    }


}


function drawFillRectInOpratorCanvas(x,y,width,height,color){
    var debug = false;
    if (true == debug){
        console.log("drawFillRectInOpratorCanvasが呼び出された");
        console.log("引数",{"x":x,"y":y,"width":width,"height":height,"color":color});

        oprator_canvas = document.getElementsByClassName("operator_canvas")[0];
        var ctx = oprator_canvas.getContext('2d');
        ctx.fillStyle = color;
        ctx.fillRect(x,y,width,height);
    }
}

class HumanBodyManager{
    constructor(body_parts){
        this.front_name = body_parts["front_name"]
        this.char_name = body_parts["char_name"]
        this.body_parts = body_parts["body_parts_iamges"]
        
        var body_map = new Map(Object.entries(body_parts["0_body"]))
        var tail_map = new Map(Object.entries(body_parts["1_尻尾"]))
        var eyer_map = new Map(Object.entries(body_parts["2_耳"]))
        var arm_map = new Map(Object.entries(body_parts["3_腕"]))
        var mouse_map = new Map(Object.entries(body_parts["4_口"]))
        var eye_map = new Map(Object.entries(body_parts["5_眼球"]["左右有"]))
        var eye_light_map = new Map(Object.entries(body_parts["5_眼球"]["眼光"]))
        var eye_sp_map = new Map(Object.entries(body_parts["5_眼球"]["特殊目"]))
        var eye_tear_map = new Map(Object.entries(body_parts["5_眼球"]["涙"]))
        var eye_blows_map = new Map(Object.entries(body_parts["6_眉"]))
        var other_map = new Map(Object.entries(body_parts["7_その他"]))

        //各パーツの画像は配列ではなくmap形式で管理する。これのメリットは、画像の番号を指定して画像を取得できること。
        //各パーツのz_index、画像、現在の表示中の画像のインデックスを管理する
        //imgsには連想配列からmapに変換したものを格納する
        this.body_list = {"z_index":1,"imgs":body_map,"now_img_index":0,"name":"body","element":null}
        this.tail_list = {"z_index":2,"imgs":tail_map,"now_img_index":0,"name":"tail","element":null}
        this.eyer_list = {"z_index":3,"imgs":eyer_map,"now_img_index":0,"name":"eyer","element":null}
        this.arm_list = {"z_index":4,"imgs":arm_map,"now_img_index":0,"name":"arm","element":null}
        this.mouse_lsit = {"z_index":5,"imgs":mouse_map,"now_img_index":0,"name":"mouse","element":null}
        this.eye_list = {"z_index":6,"imgs":eye_map,"now_img_index":0,"name":"eye","element":null}
        this.eye_light_list = {"z_index":6,"imgs":eye_light_map,"now_img_index":0,"name":"eye_light","element":null}
        this.eye_sp_list = {"z_index":6,"imgs":eye_sp_map,"now_img_index":0,"name":"eye_sp","element":null}
        this.eye_tear_list = {"z_index":6,"imgs":eye_tear_map,"now_img_index":0,"name":"eye_tear","element":null}
        this.eye_blows_list = {"z_index":7,"imgs":eye_blows_map,"now_img_index":0,"name":"eye_blows","element":null}
        this.other_list = {"z_index":8,"imgs":other_map,"now_img_index":0,"name":"other","element":null}
        //各パーツオブジェクトをmapに格納する。このmapの順番で描画されるので、z_index順にならべるのが重要。
        this.now_body_parts_map = new Map([
            ["body",this.body_list],
            ["tail",this.tail_list],
            ["eyer",this.eyer_list],
            ["arm",this.arm_list],
            ["mouse",this.mouse_lsit],
            ["eye",this.eye_list],
            ["eye_light",this.eye_light_list],//["eye_sp",this.eye_sp_list],//["eye_tear",this.eye_tear_list],
            ["eye_blows",this.eye_blows_list],
            //["other",this.other_list]
        ])

        this.body_parts_list = {
            "body":this.body_list,
            "tail":this.tail_list,
            "eyer":this.eyer_list,
            "arm":this.arm_list,
            "mouse":this.mouse_lsit,
            "eye":this.eye_list,
            "eye_light":this.eye_light_list,
            //"eye_sp":this.eye_sp_list,
            //"eye_tear":this.eye_tear_list,
            "eye_blows":this.eye_blows_list,
            //"other":this.other_list
        }

        
        console.log(this.front_name)
        //名前入力時点でhuman_windowのelementにnameも追加されてるのでそれを取得する。
        this.human_window = document.getElementsByClassName(`${this.front_name}`)[0]
        this.setBodyParts2Elm()
        console.log("おねインスタンスを生成しました。")
        console.log(this.human_window)
    }   

    setBodyParts2Elm(){
        var self = this
        
        //body_partsに対応するhtml要素を作成して、画像を各要素に配置する処理
        //各要素にはクリックしたときに別の画像に順番に切り替える処理を追加する
        console.log("画像の配置を開始")
        //this.now_body_parts_map.forEach(function(value,key,map){
        for (const [key, value] of self.now_body_parts_map) {
            console.log(key)
            console.log(value)
            var body_img = document.createElement("img")
            body_img.classList.add("human_image",`${key}_img`,"ONE_img")
            body_img.src = `data:image/png;base64,${[...value["imgs"].values()][0] }`
            body_img.style.zIndex = value["z_index"]
            self.human_window.appendChild(body_img)
            //changeImage()でパーツを変更するときに使うので各パーツのelementをbody_parts_listに格納する
            value["element"] = body_img
        }//)
        console.log("画像の配置が完了しました。")
        //画像の配置が完了したのでno_image_humanクラスをこのエレメントから削除する
        self.human_window.classList.remove("no_image_human")
        //画像を操作するためのcanvasを作成する
        self.createOperatorCanvas()

        /*
        this.other_elem.addEventListener("click",function(e){
            console.log("other_imgがクリックされた")
            var x = e.pageX; //- this.offsetLeft;
            var y = e.pageY; //- this.offsetTop;
            self.searchImage(x,y)
            self.changeImage(x,y)

            self.changeTail("next")
            //0.05秒待つ
            setTimeout(function(){
                self.changeTail("next")
            },50)

            
            //this.changeONEimg("next")
        })
        */
    }

    //ONE_imgエレメントの切り替える画像を選択するためのcanvasを作成する関数
    createOperatorCanvas(){
        console.log("createOperatorCanvas")
        var self = this;
        //1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
        var oprator_canvas = document.createElement("canvas")
        //ONE_imgエレメントの大きさを取得
        var ONE_img = this.human_window.getElementsByClassName("ONE_img body_img")[0]
        self.ONE_img_width = ONE_img.clientWidth
        self.ONE_img_height = ONE_img.clientHeight
        //canvasの大きさを設定
        console.log("canvasの大きさを設定",{"ONE_img_width":self.ONE_img_width,"ONE_img_height":self.ONE_img_height})
        oprator_canvas.width = self.ONE_img_width;
        oprator_canvas.height = self.ONE_img_height;
        //canvasにクラスを追加
        oprator_canvas.classList.add("human_image","operator_canvas","ONE_img");
        //canvasのstyleを設定。ONE_imgエレメントの位置に合わせる。
        oprator_canvas.style.zIndex = 10;
        //canvasをhuman_windowに追加
        self.human_window.appendChild(oprator_canvas);
        //SarchCanvaseを作成する
        self.createSarchCanvase();
        //canvasにイベントを追加
        oprator_canvas.addEventListener("click",function(e){
            console.log("oprator_canvasが左クリックされた");
            //clickした座標からcanvasのページ内での絶対座標を引く
            var canvas_rect = this.getBoundingClientRect();
            var x_on_canvas = e.pageX - canvas_rect.left;
            var y_on_canvas = e.pageY - canvas_rect.top;
            console.log("canvasのページ内での絶対座標",{x:x_on_canvas,y:y_on_canvas});
            const body_part = self.searchImage(x_on_canvas,y_on_canvas);
            if (   body_part["name"] == "eyer" 
                || body_part["name"] == "tail"){
                //2回変更する
                self.changeImage(body_part,"next")
                setTimeout(function(){
                    self.changeImage(body_part,"next")
                },50)
            }
            else{
                //body_partを次の画像に変更する
                self.changeImage(body_part,"next");
            }
            
            
        })
        oprator_canvas.addEventListener("contextmenu",function(e){
            //contextmenuは右クリックしたときのイベント。右クリックしたときには、前の画像に変更する。
            e.preventDefault();
            console.log("oprator_canvasが右クリックされた")
            //clickした座標からcanvasのページ内での絶対座標を引く
            var canvas_rect = this.getBoundingClientRect()
            var x_on_canvas = e.pageX - canvas_rect.left;
            var y_on_canvas = e.pageY - canvas_rect.top;
            console.log("canvasのページ内での絶対座標",{x:x_on_canvas,y:y_on_canvas})
            const body_part = self.searchImage(x_on_canvas,y_on_canvas)
            if (   body_part["name"] == "eyer" 
                || body_part["name"] == "tail"){
                //2回変更する
                self.changeImage(body_part,"prev");
                setTimeout(function(){
                    self.changeImage(body_part,"prev")
                },50);
            }
            else{
                //body_partを次の画像に変更する
                self.changeImage(body_part,"prev");
            }
        })
    }
    //search_canvasを作成する関数
    createSarchCanvase(){
        var self = this;
        //1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
        var search_canvas = document.createElement("canvas");
        //canvasの大きさを設定。場所は画面左上に設定。
        search_canvas.width = self.ONE_img_width;
        search_canvas.height = self.ONE_img_height;
        search_canvas.style.zIndex = -1;
        search_canvas.style.position = "absolute";
        search_canvas.style.top = 0;
        search_canvas.style.left = 0;
        //canvasにクラスを追加
        search_canvas.classList.add("search_canvas");
        //canvasをあかねクラスに追加
        var akane_window = document.getElementsByClassName("あかね")[0];
        akane_window.appendChild(search_canvas);
        console.log("search_canvasを作成した",this);
        this.search_canvas = search_canvas;
    }

    /**clickされた画像の座標の色を取得する関数を以下の手順で作る。
     * 0:clickされた座標のONE_imgエレメントの中心からの相対座標を入力する。
     * 1:canvasを作成する。canvasの大きさはONE_imgエレメントの大きさと同じにする。
     * 2:this.body_parts_listの中の画像を下から順にcanvasに描画する。
     * 3:canvasの座標(x,y)の色を取得する。
     */
    searchImage(x,y){
        var self = this;
        console.log("searchImageが呼び出された");
        console.log(self);

        //canvasのcontextを取得
        var search_ctx = self.search_canvas.getContext("2d")
        //2:this.body_parts_listの中の画像を下から順にcanvasに描画する。
        console.log("2:this.body_parts_listの中の画像を下から順にcanvasに描画する。")
        for(var body_part of [...this.now_body_parts_map.values()].reverse()){
            const body_part4canvas = new Image();
            //now_indexから現在の各パーツの画像を取得
            var now_index = body_part["now_img_index"];
            console.log("now_index",now_index);
            body_part4canvas.src = `data:image/png;base64,${[...body_part["imgs"].values()][now_index]}`;
            //各パーツのz_indexを取得
            var z_index = body_part["z_index"];
            /*body_part4canvas.onload = function(){
                search_ctx.drawImage(body_part4canvas,0,0,self.ONE_img_width,self.ONE_img_height)
            }*/
            search_ctx.drawImage(body_part4canvas,0,0,self.ONE_img_width,self.ONE_img_height);
            console.log("画像の配置完了");
            //3:canvasの座標(x,y)の色を取得する。
            var imgData = search_ctx.getImageData(x,y,1,1);
            var data = imgData.data;
            console.log("取得した色",data);
            //取得した色が透明でない場合は、breakする。
            if(data[3] != 0){
                console.log(`${body_part["name"]}をクリックした`);
                //search_canvasをクリアする
                search_ctx.clearRect(0,0,self.ONE_img_width,self.ONE_img_height);
                return body_part;
            }
        }
        //何もないところをクリックしたときも、search_canvasをクリアする
        search_ctx.clearRect(0,0,self.ONE_img_width,self.ONE_img_height);
        return 0;
    }


    //this.tail_list = {"z_index":2,"imgs":tail_map,"now_img_index":0,"name":"tail","elemetn":..}などが入力されるので、now_img_indexを次の画像に変更する関数
    changeImage(body_part,change_type){
        if (body_part == 0){
            console.log("何もないところをクリックした");
            return 0;
        } else {
            if (change_type == "next"){
                var index = (body_part["now_img_index"] + 1) % body_part["imgs"].size;
            } else if (change_type == "prev"){
                var index = (body_part["now_img_index"] - 1 + body_part["imgs"].size) % body_part["imgs"].size;
            }
            body_part["now_img_index"] = index;
            body_part["element"].src = `data:image/png;base64,${[...body_part["imgs"].values()][index]}`;
            console.log("画像を変更しました");
        }
    }


    //入力された画像名によって各体パーツの画像を変更する関数
    changeTail(name){
        var tail_img = this.tail_elem;
        //var tail_img = this.human_window.getElementsByClassName("tail_img")[0]
        console.log("human_windowはこれです");
        console.log(this.human_window);
        if(name == "next"){
            //現在の画像の番号を取得
            const now_index = this.tail_list["now_img_index"];
            //次の画像の番号を取得
            const next_index = (now_index + 1) % this.tail_list["imgs"].size;
            this.tail_list["now_img_index"] = next_index;
            console.log(next_index);
            //次の画像の名前を取得
            const next_name = [...this.tail_list["imgs"].keys()][next_index];
            console.log(next_name);
            //次の画像のsrcを取得
            console.log("イベントを追加したいエレメント");
            console.log(tail_img);
            tail_img.src = `data:image/png;base64,${[...this.tail_list["imgs"].values()][next_index]}`;
        }else if(name == "back"){
        }else{
            tail_img.src = `data:image/png;base64,${this.tail_list["imgs"][`${name}.png`]}`;
        }
    }
    changeEyer(name){
        var eyer_img = this.human_window.getElementsByClassName("eyer_img")[0];
        eyer_img.src = `data:image/png;base64,${this.eyer_list["imgs"][`${name}.png`]}`;
    }
    changeArm(name){
        var arm_img = this.human_window.getElementsByClassName("arm_img")[0]
        arm_img.src = `data:image/png;base64,${this.arm_list["imgs"][`${name}.png`]}`
    }
    changeMouse(name){
        var mouse_img = this.human_window.getElementsByClassName("mouse_img")[0];
        mouse_img.src = `data:image/png;base64,${this.mouse_lsit["imgs"][`${name}.png`]}`;
    }
    changeEye(name){
        var eye_img = this.human_window.getElementsByClassName("eye_img")[0];
        eye_img.src = `data:image/png;base64,${this.eye_list["imgs"][`${name}.png`]}`;
    }
    changeEyeLight(name){
        var eye_light_img = this.human_window.getElementsByClassName("eye_light_img")[0];
        eye_light_img.src = `data:image/png;base64,${this.eye_light_list["imgs"][`${name}.png`]}`;
    }
    changeEyeBlows(name){
        var eye_blows_img = this.human_window.getElementsByClassName("eye_blows_img")[0];
        eye_blows_img.src = `data:image/png;base64,${this.eye_blows_list["imgs"][`${name}.png`]}`;
    }
    changeOther(name){
        var other_img = this.human_window.getElementsByClassName("other_img")[0];
        other_img.src = `data:image/png;base64,${this.other_list["imgs"][`${name}.png`]}`;
    }

}

function connect_ws() {
    ws = new WebSocket(`ws://${localhost}:${port}/ws/${client_id}`);

    ws.onmessage = function(event) {
        messageQueue.push(event);
        console.log("messageQueue=",messageQueue,"messageQueueをpushしました","isProcessing=",isProcessing);
        processMessages();
        console.log("messageQueue=",messageQueue,"イベントを一つとりだした後のmessageQueueです");
    };

    ws.onclose = closeEventProcces_ws;
}

function closeEventProcces_ws(event) {
    console.log("wsが切断されました。再接続します。");
    //id = audio_ws_onclose_event の音声を取得し、存在すれば再生。
    var audio = document.getElementById("audio_ws_onclose_event");
    if (audio) {
        //audio.play();
    }
    setTimeout(connect_ws, 1000);
}

async function getClientId() {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(`ws://${localhost}:${port}/id_create`);
        ws.onmessage = function(event) {
            console.log("data.id", event.data);
            ws.close();  // WebSocketの接続を閉じる
            resolve(event.data);
        };
        ws.onerror = function(error) {
            reject(error);
        };
    });
}

function chara_name2front_name(chara_name){
    //front2chara_nameのvalueがchara_nameと一致するkeyを取得する
    //この関数は、front2chara_nameオブジェクトのキーの中で、そのキーに対応する値がchara_nameと一致する最初のキーを返します。
    var front_name = Object.keys(front2chara_name).find(key => front2chara_name[key] === chara_name);
    if (front_name === undefined){
        //一致するキーがない場合は、"no_front_name"を返す
        return "no_front_name";
    }
    return front_name;
}

function humanWsOpen(){
    human_ws = new WebSocket(`ws://${localhost}:${port}/human/${client_id}`);
    human_ws.onmessage = receiveMessage;
    console.log("human_wsが接続されました。");
}



//ここから下がメイン処理
var message_box_manager = new MessageBoxManager();
const localhost = location.hostname;
const port = "8020"
var init_human_tab = /** @type {HTMLLIElement} */ (document.getElementsByClassName("tab human_tab")[0]);
addClickEvent2Tab(init_human_tab)
//var ws = new WebSocket("ws://localhost:${port}/InputGPT")
//var ws = new WebSocket("ws://localhost:${port}/InputPokemon");
var messageQueue = /** @type {MessageEvent[]} */ ([]);
var isProcessing = false;

/** @type {Record<string,HumanBodyManager2>} */
var humans_list = {};
/** @type {Record<string,string>} */
var front2chara_name = {};
/** @type {Record<string,VoiroAISetting>} */
var setting_info = {}; //どのキャラの設定がオンになっているかを管理する

let first_human_tab = document.getElementsByClassName("tab human_tab")[0];
/**@type {DragDropFile[]} */
let drag_drop_file_event_list = [new DragDropFile(first_human_tab)];
console.log("ドラッグアンドドロップイベントを追加しました。");

humans_list.ONE_chan = "おねねねねんえねねねねねねねｎ";
console.log(humans_list);

//これらの変数はグローバル変数にする必要がある
let client_id;
var ws;
var human_ws;
var test = 0;

getClientId().then(recieve_client_id => {
    client_id = recieve_client_id;
    ws = new WebSocket(`ws://${localhost}:${port}/ws/${client_id}`);
    ws.onmessage = function(event) {
        messageQueue.push(event);
        console.log("messageQueue=",messageQueue,"messageQueueをpushしました","isProcessing=",isProcessing);
        processMessages();
        console.log("messageQueue=",messageQueue,"イベントを一つとりだした後のmessageQueueです");
    };
    ws.onclose = closeEventProcces_ws;

    humanWsOpen();
    
    
});