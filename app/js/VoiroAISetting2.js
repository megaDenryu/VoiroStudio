///@ts-check

class VoiroAISetting{
    /** @type {HTMLDivElement} */ ELM_combination_name;
    /** @type {HTMLDivElement} */ ELM_body_setting;
    /** @type {HTMLInputElement} */ ELM_input_combination_name;
    /** @type {HTMLLIElement} */ ELM_combination_box;
    /** @type {HTMLElement} */ ELM_accordion;
    /** @type {Record<string, AccordionItem>} */ accordion_item_dict;


    /**
     * @param {HumanBodyManager2}chara_human_body_manager
     */
    constructor(chara_human_body_manager){
        console.log("VoiroAISetting constructor")
        this.ELM_body_setting = /** @type {HTMLDivElement} */ (document.querySelector(".body_setting"));
        this.chara_human_body_manager = chara_human_body_manager;

        var [ELM_accordion,accordion_item_dict] = this.createAccordion();
        this.ELM_accordion = ELM_accordion
        this.accordion_item_dict = accordion_item_dict
        this.ELM_body_setting.append(this.ELM_accordion);

        //オノマトペアクションの初期状態を設定する
        // todo ここで開閉ボタンを自動で押し、ぴょこ等も自動で押す処理を実装する
        this.setOnomatopeiaButtonToInitState();
        // todo ここでオンボタンをオンにする処理を実装する
        this.setOnBodyButtonToNowOnomatopeiaState();

    }

    /**
     * 
     * @returns {[HTMLElement,Record<string,AccordionItem>]} ELM_accordion,accordion_item_dict 
     */
    createAccordion(){
        var ELM_accordion = document.createElement("ul");
        ELM_accordion.classList.add("accordion");
        console.log(this.chara_human_body_manager)

        //組み合わせ名を表示する要素を追加
        this.ELM_combination_box = this.createElmCombinatioBox()
        ELM_accordion.appendChild(this.ELM_combination_box)

        var map = this.chara_human_body_manager.body_parts_info;
        
        /** @type {Record<string,AccordionItem>} */
        var accordion_item_dict = {};

        for (const [key, value] of map){
            //keyは体のパーツの名前、valueはそのパーツの画像群の配列
            var accordion_item = new AccordionItem(key, this.ELM_body_setting, this.chara_human_body_manager);

            /** @type {HTMLUListElement} */
            var ELM_accordion_item = /** @type {HTMLUListElement} */(accordion_item.html_doc.querySelector(".accordion_item"));

            console.log(ELM_accordion_item);
            var ELM_accordion_item_name = accordion_item.html_doc.getElementsByClassName("accordion_item_name")[0];
            ELM_accordion_item_name.addEventListener("click",accordion_item);
            accordion_item_dict[key] = accordion_item;
            console.log(ELM_accordion,ELM_accordion_item);
            ELM_accordion.appendChild(ELM_accordion_item);
            accordion_item.ELM = ELM_accordion_item;
        }
        //組み合わせ名を入力するinput要素を追加
        this.ELM_input_combination_name = /** @type {HTMLInputElement} */ (this.createElmInputCombinationName());
        ELM_accordion.appendChild(this.ELM_input_combination_name);

        return [ELM_accordion,accordion_item_dict];
    }

    /**
     * @returns {HTMLLIElement} ELM_combination_box
     */
    createElmCombinatioBox(){
        //boxを作成
        this.ELM_combination_box = document.createElement("li");
        this.ELM_combination_box.classList.add("combination_box","accordion_tab","open");

        //nameを作成
        this.ELM_combination_name = this.createElmCombinatioName();
        this.ELM_combination_box.appendChild(this.ELM_combination_name);

        //候補を作成
        this.ELM_combination_candidate = document.createElement("ul");
        this.ELM_combination_candidate.classList.add("combination_candidate");
        this.ELM_combination_box.appendChild(this.ELM_combination_candidate);
            //イベントハンドラーを追加
        const bcanm = new BodyCombinationAccordionManager(this.chara_human_body_manager, this, this.ELM_combination_box, this.ELM_combination_name, this.ELM_combination_candidate);
        this.ELM_combination_box.addEventListener("click",bcanm);

        return this.ELM_combination_box;
    }

    /**
     * "名無しの組み合わせ"というテキストを持つ、クラス名が "combination_name" の div 要素を作成します。
     * @returns {HTMLDivElement} "combination_name" クラスと "名無しの組み合わせ" テキストを持つ div 要素
     */
    createElmCombinatioName(){
        var ELM_combination_name = document.createElement("div");
        ELM_combination_name.classList.add("combination_name");
        ELM_combination_name.innerText = "名無しの組み合わせ";
        return ELM_combination_name;
    }


    /**
     * @returns {HTMLInputElement} "input_combination_name" クラスを持つ input 要素
     */
    createElmInputCombinationName(){
        var ELM_input_combination_name = document.createElement("input");
        ELM_input_combination_name.type = "text";
        ELM_input_combination_name.classList.add("input_combination_name");
        ELM_input_combination_name.placeholder = "組み合わせ名を入力";
        ELM_input_combination_name.addEventListener("keypress",this.saveCombinationName.bind(this));
        return ELM_input_combination_name;
    }

    /**
     * 
     * @param {KeyboardEvent} event
     * @returns {void}
     */
    saveCombinationName(event){
        if (event.key == "Enter"){
            console.log("Enterが押されたよ")
            const combination_name = this.ELM_input_combination_name.value;
            this.ELM_combination_name.innerText = combination_name;
            this.ELM_input_combination_name.value = "";
            //サーバーに組み合わせ名を送信する
            this.sendCombinationName(combination_name);
        }
    }

    /**
     * 
     * @param {string} combination_name
     * @returns {void}
     */
    sendCombinationName(combination_name){
        console.log("sendCombinationNameを呼び出したよ")
        const all_now_images = this.getAllNowImages()
        const data = {
            "chara_name":this.chara_human_body_manager.char_name,
            "front_name":this.chara_human_body_manager.front_name,
            "combination_name":combination_name,
            "combination_data":all_now_images
        }
        //all_now_imagesをサーバーに送信する
        //websocketを作成
        var ws_combi_img_sender = new WebSocket(`ws://${localhost}:${port}/img_combi_save`)
        ws_combi_img_sender.onopen = function(event){
            console.log("img_combi_saveが開かれた。このデータを送る。",data)
            ws_combi_img_sender.send(JSON.stringify(data));
        }
        //websocketを閉じる
        ws_combi_img_sender.onclose = function(event){
            console.log("img_combi_saveが閉じられたよ")
        }
        //サーバーからメッセージを受け取ったとき
        ws_combi_img_sender.onmessage = function(event){
            console.log("img_combi_saveからメッセージを受け取ったよ")
            console.log(event.data)
        }
    }

    getAllNowImages(){
        var image_status_dict = /** @type {Record<string, Record<string, "on" | "off">>} */( {} );
        for (const [key_name, accordion_item] of Object.entries(this.accordion_item_dict)){
            
            
            let part_dict_on_off = /** @type {Record<string,"on"|"off">} */( {} );

            for (const [key, value] of Object.entries(accordion_item.accordion_content_handler_list)){
                part_dict_on_off[key] = value.on_off;
            }
            image_status_dict[key_name] = part_dict_on_off;
        }
        return image_status_dict;    
    }

    /**
     * 
     * @param {string} body_part_name
     * @param {string} image_name
     * @returns {void}
     * todo: 使用箇所探索不能
     */
    setBodyPartImage(body_part_name,image_name) {
        this.accordion_item_dict[body_part_name].setBodyPartImage(image_name);
    }

    /** 
     * @param {string} group_name
     * @param {string} content_name
     * @param {"on"|"off"} on_off
     */
    setGroupButtonOnOff(group_name, content_name, on_off){
        this.accordion_item_dict[group_name].setGroupButtonOnOff(content_name,on_off);
    }

    /**
     * @param {string} group_name
     * @param {"パク" | "パチ" | "ぴょこ"} onomatopoeia_mode
     * @param {"on" | "off"} on_off
     */
    setOnomatpeiaModeButtonOnOff(group_name, onomatopoeia_mode, on_off){
        let accordion_item = this.accordion_item_dict[group_name];
        accordion_item.setOnomatpeiaModeButtonOnOff(onomatopoeia_mode, on_off);
    }

    /** 
     * @param {string} group_name
     * @param {string} content_name
     * @param {"open"|"close"} open_close
     */
    setOnomatpeiaButtonOnOff(group_name, content_name, open_close){
        let handler_list = this.accordion_item_dict[group_name].accordion_content_handler_list;
        let handler = handler_list[content_name];
        let pati_setting_toggle_event_object = handler.pati_setting_toggle_event_object;
        pati_setting_toggle_event_object.setButtonOpenClose(open_close);

    }

    /**
     * todo パチパク設定
     */
    setOnomatopeiaButtonToInitState(){
        
        let /** @type {"パク" | "パチ" | "ぴょこ"} */ key;
        let /** @type {"開候補" | "閉"} */ openCloseState;

        for (key in this.chara_human_body_manager.onomatopoeia_action_setting){
            let action_setting = this.chara_human_body_manager.onomatopoeia_action_setting[key];
            for (openCloseState in action_setting){
                let parts_list = action_setting[openCloseState];
                
                let /**@type {"open"|"close"} */ open_close = "open";
                if (openCloseState == "閉"){
                    open_close = "close";
                }

                for (let parts_path of parts_list){
                    // debugger;
                    this.setOnomatpeiaModeButtonOnOff(parts_path.folder_name, key, "on")
                    this.setOnomatpeiaButtonOnOff(parts_path.folder_name, parts_path.file_name, open_close)
                }
            }
            if (key == "パク" && action_setting["閉"].length > 0){
                // リップシンクをオンにするかどうかの処理
                this.chara_human_body_manager.setLipSyncModeToPakuPaku(key);
            }
        }
    }

    /**
     * todo オノマトペアクションでオンにしていた体パーツをオンにする
     */
    setOnBodyButtonToNowOnomatopeiaState(){
        let /** @type {"パク" | "パチ" | "ぴょこ"} */ key;
        for (key in this.chara_human_body_manager.now_onomatopoeia_action){
            let parts_list = this.chara_human_body_manager.now_onomatopoeia_action[key];
            for (let parts_path of parts_list){
                this.setGroupButtonOnOff(parts_path.folder_name, parts_path.file_name, "on");
            }
        }
    }

}

/**
 * @typedef {"口"|"パク"|"パチ"|"ぴょこ"|"無"} PatiMode
 */

/**
 * アコーディオンを展開したときに見えるアコーディオンコンテンツのクラス
 * パーツ名をクリックしたときに、ボタンの色を変え、人体モデルのパーツの表示を変え、プロパティのデータも変える
 */
class AccordionItem{

    /** 
     * AccordionItemのエレメント全体
     * @type {HTMLUListElement} */
    ELM

    /** @type {HTMLDivElement} */
    ELM_accordion_item_name;

    /** @type {HTMLUListElement} */
    ELM_accordion_contents;

    /** @type {HTMLCollection} */
    ELMs_accordion_content;

    /** @type {string[]} */
    contents_name_list;

    /** @type {string} */
    statu_open_close;

    /** @type {Record<string, ContentButtonEventobject>} */
    accordion_content_handler_list;

    /**
     * このアコーディオンがラジオモードかどうか 
     * @type {boolean} */
    radio_mode;

    /** @type {Record<string,"on"|"off">} */
    image_item_status

    /**
     * このアコーディオンのパチ設定のモード 
     * @type {PatiMode} */
    pati_setting_mode;

    /** @type {Document} */
    html_doc;

    /**
     * 
     * @param {string} name_acordion           body_setting要素内のアコーディオンの名前は、対応する画像名と同じにする
     * @param {HTMLElement} Parent_ELM_body_setting  body_settingの要素
     * @param {HumanBodyManager2} chara_human_body_manager
     */
    constructor(name_acordion, Parent_ELM_body_setting, chara_human_body_manager){
        //引数の登録
        this.name_acordion = name_acordion;
        this.Parent_ELM_body_setting = Parent_ELM_body_setting;
        this.chara_human_body_manager = chara_human_body_manager;
        //this.contents_name_list = [...this.chara_human_body_manager.body_parts_info.get(name_acordion).get("imgs").keys()]
        const /** @type  {PartInfo}*/ part_info = this.chara_human_body_manager.body_parts_info.get(name_acordion)
        this.contents_name_list = part_info.imgs.comvert2keysArray();
        
        console.log(this.contents_name_list)
        this.statu_open_close = "close";
        this.accordion_content_handler_list = {};
        //accordion_sampleを複製
        const HTML_str_accordion_sample = `
        <li class = "accordion_item close layer ">
            <div class="accordion_item_name accordion_tab">
                <div class="initial_display_object">
                    <div class="name_string">頭</div>
                    <div class="pati_setting">パチパク設定</div>
                </div>
                <div class="pati_setting_radio-buttons non_vissible">
                    <div class="pati_setting_radio-button kuchi">口</div>
                    <div class="pati_setting_radio-button kuchi">パク</div>
                    <div class="pati_setting_radio-button kuchi">パチ</div>
                    <div class="pati_setting_radio-button kuchi">ぴょこ</div>
                    <div class="pati_setting_radio-button kuchi on">無</div>
                </div>
            </div>
            <ul class = "accordion_contents non_vissible">
                <li class = "accordion_content body_part_image_name accordion_tab sample">
                    <div class="accordion_content_name_string">1.png</div>
                    <div class="accordion_content_pati_setting_toggle_button open">開</div>
                </li>
            </ul>
        </li>
        `;
        this.html_doc = ElementCreater.createnewDocumentFromHTMLString(HTML_str_accordion_sample)
        //名前を設定
        this.setAccordionItemName(name_acordion);
        this.radio_mode = false;
        this.setPatiSettingAction()
        //アコーディオンの中身を作成
        var [ELM_accordion_contents,accordion_content_handler_list] = this.createELMAccordionContents(name_acordion);
        this.ELM_accordion_contents = ELM_accordion_contents;
        this.ELM_accordion_item_name = /** @type {HTMLDivElement} */ (this.html_doc.querySelector(".accordion_item_name"));
        console.log(this.ELM_accordion_item_name)
        this.accordion_content_handler_list = accordion_content_handler_list;
        //オンになってるボタンがあるかどうか
        this.checkHasOnContentButton();
    }

    setPatiSettingAction(){
        this.setOpenPatiSettingAction();
        this.setClickPatiSettingAction();
    }

    setClickPatiSettingAction(){
        console.log("setClickPatiSettingActionが動いた")
        let ELMs_radio_button = this.html_doc.getElementsByClassName("pati_setting_radio-button");
        console.log(ELMs_radio_button)
        for (let i = 0; i < ELMs_radio_button.length; i++) {
            let ELM_radio_button = /** @type {HTMLElement}*/(ELMs_radio_button[i]);
            console.log(ELM_radio_button)
            ELM_radio_button.addEventListener("click", (event) => {
                console.log("pati_setting_radio-buttonがクリックされたよ")
                event.stopPropagation();
                let ELM_pati_setting_radio_buttons = event.target.parentElement;
                let innerELMs_radio_button = ELM_pati_setting_radio_buttons.getElementsByClassName("pati_setting_radio-button");

                //クリックしたら、他のボタンをオフにする。オフになったとき色も変える
                console.log(innerELMs_radio_button)
                for (let j = 0; j < innerELMs_radio_button.length; j++) {
                    innerELMs_radio_button[j].classList.remove("on");
                }
                //クリックしたボタンがオンの場合はオフにし、オフの場合はオンにする
                ELM_radio_button.classList.toggle("on");
                this.pati_setting_mode = /** @type {PatiMode}*/(ELM_radio_button.innerText);

                //todo:ここでnow_onomatopoeia_actionを取得し設定
                if (["パク","パチ","ぴょこ"].includes(this.pati_setting_mode)){
                    this.reflectOnItemToNowOnomatopoeiaAction(this.pati_setting_mode);
                }
                //全ての開閉状態を反映する
                this.reflectOnomatopoeiaActionViewStateToHumanModel();
            });
        }
    }

    /**
     * @param {"パク" | "パチ" | "ぴょこ"} onomatopoeia_mode
     * @param {"on" | "off"} on_off
     */
    setOnomatpeiaModeButtonOnOff(onomatopoeia_mode, on_off){
        // debugger;
        let ELMs_radio_button = this.ELM_accordion_item_name.getElementsByClassName("pati_setting_radio-button");
        console.log(ELMs_radio_button)
        for (let i = 0; i < ELMs_radio_button.length; i++) {
            let ELM_radio_button = /** @type {HTMLElement}*/(ELMs_radio_button[i]);
            if (ELM_radio_button.innerText == onomatopoeia_mode){
                if (on_off == "on"){
                    ELM_radio_button.classList.add("on");
                } else {
                    ELM_radio_button.classList.remove("on");
                }
            } else {
                ELM_radio_button.classList.remove("on");
            }
        }
    }

    /**
     * 今のアコーディオンの中身の状態を取得し、オンになっているものをnow_onomatopoeia_actionに反映する。オフになっているものは削除する。
     * なので先に今のアコーディオンに入っているパーツをすべて削除し、その後に反映する
     * @param {"パク" | "パチ" | "ぴょこ"} onomatopoeia_action_mode 
     */
    reflectOnItemToNowOnomatopoeiaAction(onomatopoeia_action_mode){
        if (["パク","パチ","ぴょこ"].includes(onomatopoeia_action_mode) == false){
            return;
        }

        let content_status_dict = this.getContentStatusDict()
        //now_onomatopoeia_actionからこのアコーディオンのパーツを削除
        let all_content_list = Object.keys(content_status_dict);
        for (let content of all_content_list){
            let part_path = {
                folder_name: this.name_acordion,
                file_name: content
            }
            this.chara_human_body_manager.now_onomatopoeia_action[onomatopoeia_action_mode] = this.chara_human_body_manager.now_onomatopoeia_action[onomatopoeia_action_mode].filter(
                (path) => this.chara_human_body_manager.isEquivalentPartsPath(path,part_path) == false
                );
        }

        //"on"を持つキーを取得
        let on_content_list = Object.keys(content_status_dict).filter((key) => content_status_dict[key] == "on");
        for (let on_content of on_content_list){
            let part_path = {
                folder_name: this.name_acordion,
                file_name: on_content
            }
            this.chara_human_body_manager.now_onomatopoeia_action[onomatopoeia_action_mode].push(part_path);
        }

        this.chara_human_body_manager.setLipSyncModeToPakuPaku(onomatopoeia_action_mode)
        
    }

    reflectOnomatopoeiaActionViewStateToHumanModel(){
        for (const [key, value] of Object.entries(this.accordion_content_handler_list)){
            
            const pati_setting_toggle_event_object = /**@type {PatiSettingToggleEventObject} */(value.pati_setting_toggle_event_object);
            //オノマトペアクションリストのすべてと開閉を探索して、このパーツパスを削除
            pati_setting_toggle_event_object.removePartsPathFromOnomatopoeiaActionSetting();

            //オノマトペアクションリストの現在の選択アクションに対してこのパーツパスを追加
            const now_state = pati_setting_toggle_event_object.now_state;
            pati_setting_toggle_event_object.reflectOnomatopoeiaActionState(now_state);
        }
    }


    setOpenPatiSettingAction(){
        
        let ELM_pati_setting = this.html_doc.querySelector(".pati_setting");
        let ELM_radio_buttons = this.html_doc.querySelector(".pati_setting_radio-buttons");
        ELM_pati_setting?.addEventListener("click", (event) => {
            event.stopPropagation();
            ELM_radio_buttons?.classList.toggle("non_vissible");
        });
    }
    
    /**
     * 
     * @param {Event} event
     */
    handleEvent(event){
        console.log("AccordionItemがクリックされたよ",this.ELM)
        //clickイベントの場合。アコーディオンの開閉を行う
        if(event.type == "click"){
            var ELM_accordion_item = this.ELM
            console.log(ELM_accordion_item)
            if (this.statu_open_close == "close") {
                ELM_accordion_item.classList.replace("close", "open");
                this.statu_open_close = "open";
                // @ts-ignore
                ELM_accordion_item.querySelector(".accordion_contents").classList.remove("non_vissible");
            } else {
                ELM_accordion_item.classList.replace("open", "close");
                this.statu_open_close = "close";
                // @ts-ignore
                ELM_accordion_item.querySelector(".accordion_contents").classList.add("non_vissible");
            }
        }
        //hoverしたとき色を変える
        if(event.type == "mouseover"){
            console.log("mouseover")
            this.ELM.classList.add("hover");
        }
    }


    // /**
    //  * 
    //  * @param {string} image_name 
    //  */
    // imageStatusChange(image_name) {
    //     if (this.image_item_status[image_name] == "on") {
    //         this.image_item_status[image_name] = "off";
    //         this.changeELMAccordionContent(image_name)
    //         this.chara_human_body_manager.changeBodyPart(image_name,"off");
    //     } else {
    //         this.image_item_status[image_name] = "on";
    //         this.chara_human_body_manager.changeBodyPart(image_name,"on");
    //     }
    // }

    // /**
    //  * アコーディオンのエレメントの最新の状態をプロパティに反映する
    //  */
    // loadNowAccordionELMStatus(){
    //     //todo: コードが適当なので確認すること
    //     for (let i = 0; i < this.ELMs_accordion_content.length; i++) {
    //         let image_name = this.ELMs_accordion_content[i].id;
    //         this.image_item_status[image_name] = this.ELMs_accordion_content[i].value;
    //     }

    // }

    /**
     * 
     * @param {string} name_acordion 
     */
    setAccordionItemName(name_acordion){
        //accordion_item_nameを変更
        // "1_10_葵_10_素体"などが入るので、最初の"1_10_"などを削除し、途中の数字も削除
        //数字（\d+）とそれに続くアンダースコア（_*）をすべて削除します。その後、アンダースコアをスペースに置換します。
        const new_name_acordion = name_acordion.replace( /\d+_+/g, '').replace(/_/g, ' ');
        // @ts-ignore
        this.html_doc.querySelector(".accordion_item_name").querySelector(".name_string").innerText = new_name_acordion;
    }

    /**
     * 
     * @param {string} name_acordion 
     * @returns {[HTMLUListElement,Record<string, ContentButtonEventobject>]} ELM_accordion_contents,accordion_content_handler_list
     */
    createELMAccordionContents(name_acordion){
        //this.contents_name_listには画像の名前が入っている。ELM_accordion_contentを複製してELM_accordion_contentsに追加する。
        let ELM_accordion_contents = /** @type {HTMLUListElement} */(this.html_doc.querySelector(".accordion_contents"));
        const ELM_accordion_content = /** @type {HTMLLIElement} */(this.html_doc.querySelector(".accordion_content"));

        var accordion_content_handler_list = /** @type {Record<String,ContentButtonEventobject>}*/( {} );
        for (let i = 0; i < this.contents_name_list.length; i++) {
            //ELM_accordion_contentを複製
            /** @type {HTMLLIElement} */
            let ELM_accordion_content_clone = /** @type {HTMLLIElement} */(ELM_accordion_content.cloneNode(true));
            // ELM_accordion_content_clone.innerText = this.contents_name_list[i];
            ELM_accordion_content_clone.getElementsByClassName("accordion_content_name_string")[0].innerText = this.contents_name_list[i];
            //画像の名前から、画像のパスを取得
            //let image_path = this.chara_human_body_manager.map_body_parts_info.get(name_acordion)["imgs"].get(this.contents_name_list[i]);
            const image_name = this.contents_name_list[i];
            //アコーディオンの中身のボタンにイベントハンドラーを追加
            let content_button_event_object = new ContentButtonEventobject(image_name, "off", ELM_accordion_content_clone,this);
            ELM_accordion_content_clone.addEventListener("click", content_button_event_object);
            ELM_accordion_content_clone.classList.remove("sample");

            let ELM_accordion_content_pati_setting_toggle_button = /** @type {HTMLElement}*/(ELM_accordion_content_clone.getElementsByClassName("accordion_content_pati_setting_toggle_button")[0]);
            let pati_setting_toggle_button_event_object = new PatiSettingToggleEventObject(ELM_accordion_content_pati_setting_toggle_button, this, content_button_event_object);

            //アコーディオンの中身を追加
            ELM_accordion_contents.appendChild(ELM_accordion_content_clone);
            //console.log(ELM_accordion_content_clone);
            accordion_content_handler_list[image_name] = content_button_event_object;
        }
        
        // @ts-ignore html_docからsampleクラスを持つ要素を削除
        this.html_doc.querySelector(".sample").remove();
        

        return [ELM_accordion_contents,accordion_content_handler_list];
    }

    

    /**
     * @returns {Record<string,"on"|"off">}
     */
    getContentStatusDict(){
        /** @type {Record<string,"on"|"off">} */
        var item_status_dict = {};
        for (const [key, value] of Object.entries(this.accordion_content_handler_list)){
            item_status_dict[key] = value.on_off;
        }
        return item_status_dict;
    }

    /**
     * @param {Record<string,"on"|"off">} image_item_status
     * @returns {number}
     */
    countOnContentButton(image_item_status){
        var count = 0;
        for (const [key, value] of Object.entries(image_item_status)){
            if (value == "on"){
                count += 1;
            }
        }
        return count;
    }

    /**
     * ONになっているボタンがあるかどうかをチェックし、アコーディオンのcssクラスを変える
     * @returns {void}
     */
    checkHasOnContentButton(){
        // console.log("checkHasOnContentButtonが動いた: " + new Date());
        const image_item_status = this.getContentStatusDict();
        const count_on_content_button = this.countOnContentButton(image_item_status);
        const ELM_accordion_item_name = this.ELM_accordion_item_name;
        // console.log(this.ELM_accordion_contents);
        // console.log(this.html_doc);
        // console.log(ELM_accordion_item_name);
        if (count_on_content_button > 0){
            if (ELM_accordion_item_name.classList.contains("has_on_content_button") == false){
                ELM_accordion_item_name.classList.add("has_on_content_button");
            }
        } else {
            if (ELM_accordion_item_name.classList.contains("has_on_content_button") == true){
                ELM_accordion_item_name.classList.remove("has_on_content_button");
            }
        }
    }
    /**
     * @param {string} image_name 
     */
    setBodyPartImage(image_name) {
        this.accordion_content_handler_list[image_name].clickEvent();
    }

    /** 
     * @param {string} content_name
     * @param {"on"|"off"} on_off
     */
    setGroupButtonOnOff(content_name, on_off){
        if (content_name != ""){
            const accordion_content_handler = this.accordion_content_handler_list[content_name];
            accordion_content_handler.setButtonOnOff(on_off);
        } else {
            this.setAllButtonOff();
        }
    }

    setAllButtonOff(){
        for (const [key, value] of Object.entries(this.accordion_content_handler_list)){
            value.setButtonOnOff("off");
        }
    }

}

class PatiSettingToggleEventObject{
    /** @type {HTMLElement} */
    ELM_accordion_content_pati_setting_toggle_button;
    /** @type {AccordionItem} */
    parent_accordion_item_instance;
    /** @type {HumanBodyManager2} */
    human_body_manager;
    /** @type {string} */
    image_name;
    /** @type {"open"|"close"} */
    now_state = "open";
    /**
     * @param {HTMLElement} ELM_accordion_content_pati_setting_toggle_button
     * @param {AccordionItem} parent_accordion_item_instance
     * @param {ContentButtonEventobject} content_button_event_object
     */
    constructor(
        ELM_accordion_content_pati_setting_toggle_button, 
        parent_accordion_item_instance,
        content_button_event_object
    ){
        this.ELM_accordion_content_pati_setting_toggle_button = ELM_accordion_content_pati_setting_toggle_button;
        this.parent_accordion_item_instance = parent_accordion_item_instance;
        this.human_body_manager = parent_accordion_item_instance.chara_human_body_manager;
        this.ELM_accordion_content_pati_setting_toggle_button.addEventListener("click",this);
        this.image_name = content_button_event_object.image_name;
        this.content_button_event_object = content_button_event_object;
        this.content_button_event_object.bindPatiSettingToggleEventObject(this);
        this.now_state = this.pullInitStateFromDataStorage();
    }

    /**
     * @param {any} event
     */
    handleEvent(event){
        //下のボタンにイベントを伝えない
        event.stopPropagation();
        //イベント
        if (this.ELM_accordion_content_pati_setting_toggle_button?.classList.contains("open") == true){
            this.setButtonOpenClose("close");
        } else {
            this.setButtonOpenClose("open");
        }
        this.reflectOnomatopoeiaActionState(this.now_state);
        
    }

    /**
     * @param {"open"|"close"} open_close
     */
    setButtonOpenClose(open_close){
        if (open_close == "open"){
            this.ELM_accordion_content_pati_setting_toggle_button?.classList.replace("close","open");
            this.ELM_accordion_content_pati_setting_toggle_button.innerText = "開";
        } else if (open_close == "close"){
            this.ELM_accordion_content_pati_setting_toggle_button?.classList.replace("open","close");
            this.ELM_accordion_content_pati_setting_toggle_button.innerText = "閉";
        }
        this.now_state = open_close;
    }

    /**
     * @param {"open"|"close"} open_close
     */
    reflectOnomatopoeiaActionState(open_close){
        //パチパク設定のモードによって、human_body_managerのプロパティを変える
        /**@type {PartsPath} */
        const parts_path = {
            folder_name: this.parent_accordion_item_instance.name_acordion,
            file_name: this.image_name
        }
        console.log(this.parent_accordion_item_instance.pati_setting_mode)
        if (this.parent_accordion_item_instance.pati_setting_mode == "口"){
            
        } else if (["パク","パチ","ぴょこ"].includes(this.parent_accordion_item_instance.pati_setting_mode)){
            console.log("パチパク設定のモードによって、human_body_managerのプロパティを変える")
            
            const mode = /**@type {"パク"|"パチ"|"ぴょこ"}*/(this.parent_accordion_item_instance.pati_setting_mode);
            if (open_close == "open"){
                //開候補リストに登録
                this.human_body_manager.setToOnomatopoeiaActionSetting(mode,"開候補", parts_path)
                this.human_body_manager.removeFromOnomatopoeiaActionSetting(mode,"閉", parts_path)
            } else if (open_close == "close"){
                this.human_body_manager.removeFromOnomatopoeiaActionSetting(mode,"開候補", parts_path)
                this.human_body_manager.setToOnomatopoeiaActionSetting(mode,"閉", parts_path)
            }
        } else if (this.parent_accordion_item_instance.pati_setting_mode == "無"){
            
        }

        //新しい状態をサーバーに送信する
        this.sendOnomatopoeiaNewStateToDataStorage();
    }

    sendOnomatopoeiaNewStateToDataStorage(){
        /**
         * onomatopoeia_action_settingの新しい状態をサーバーに送信する.
         * サーバー側でデータを保存するためにはinit_image_infoに到達するための情報が必要。
         */
        const data = {
            "chara_name":this.human_body_manager.char_name,
            "front_name":this.human_body_manager.front_name,
            "pati_setting":this.human_body_manager.onomatopoeia_action_setting,
            "now_onomatopoeia_action":this.human_body_manager.now_onomatopoeia_action,
        }

        console.log("パチパク設定データ",data)

        //Postで送信する
        const url = `http://${localhost}:${port}/pati_setting`
        fetch(url, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })

    }

    /** todo: 未実装。データストレージから初期状態を取得する
     * @returns {"open"|"close"}
     */
    pullInitStateFromDataStorage(){
        return "open";
    }

    removePartsPathFromOnomatopoeiaActionSetting(){
        for (let mode of ["パク","パチ","ぴょこ"]){
            const parts_path = {
                folder_name: this.parent_accordion_item_instance.name_acordion,
                file_name: this.image_name
            }
            this.human_body_manager.removeFromOnomatopoeiaActionSetting(mode,"開候補", parts_path)
            this.human_body_manager.removeFromOnomatopoeiaActionSetting(mode,"閉", parts_path)
        }
    
    }

}
       

class ContentButtonEventobject{

    /** @type {string} */ image_name;
    /** @type {"on"|"off"} */ on_off;
    /** @type {HTMLElement} */ ELM_accordion_content;
    /** @type {AccordionItem} */ parent_accordion_item_instance;
    /** @type {HumanBodyManager2} */ chara_human_body_manager;
    /** @type {PatiSettingToggleEventObject} */ pati_setting_toggle_event_object;

    /**
     * 各コンテンツのボタンのイベントハンドラーに追加するクラス
     * このクラスとコンテンツボタンはAccordionContent.createELMAccordionContents一対一で作成される。
     * 
     * @param {string} image_name 
     * @param {"on"|"off"} on_off 
     * @param {HTMLElement} ELM_accordion_content 
     * @param {AccordionItem} parent_accordion_item_instance
     */
    constructor(image_name, on_off, ELM_accordion_content,parent_accordion_item_instance){
        this.image_name = image_name;
        this.on_off = on_off;
        this.ELM_accordion_content = ELM_accordion_content;
        this.parent_accordion_item_instance = parent_accordion_item_instance;
        this.chara_human_body_manager = parent_accordion_item_instance.chara_human_body_manager;
        //このコンテンツが最初からオンになってるかどうかをチェックする
        //this.checkInitContentStatus();
        this.checkContentStatus();
    }

    /**
     * @param {Event} event
     * @returns {void}
     */
    handleEvent(event){
        //clickイベントの場合
        // console.log("ContentButtonEventobjectクリックしたよ")
        if(event.type == "click"){
            this.clickEvent();
        }
        //hoverしたとき色を変える
        if(event.type == "mouseover"){
            this.ELM_accordion_content.classList.add("hover");
        }
    }
    clickEvent(){
        // console.log("ContentButtonEventobjectクリックしたよ")
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        //ボタンの色を変え,プロパティのデータを変える
        // console.log(this.ELM_accordion_content);
        if(this.on_off == "off"){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"on");
            this.on_off = "on";
            //他のボタンでonになっているものをoffにする
            if (this.parent_accordion_item_instance.radio_mode == true) {
                for (const [key, value] of Object.entries(this.parent_accordion_item_instance.accordion_content_handler_list)){
                    // console.log(key,value)
                    if (key != this.image_name){
                        value.ELM_accordion_content.classList.remove("on_accordion_content");
                        value.parent_accordion_item_instance.chara_human_body_manager.changeBodyPart(accordion_name,key,"off");
                        value.on_off = "off";
                    }
                }
            }
            // now_onomatopoeia_actionを更新。パチパク設定のモードがパク、パチ、ぴょこの場合のみ反映される
            this.parent_accordion_item_instance.reflectOnItemToNowOnomatopoeiaAction(this.parent_accordion_item_instance.pati_setting_mode);

        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"off");
            this.on_off = "off";
            // now_onomatopoeia_actionを更新。パチパク設定のモードがパク、パチ、ぴょこの場合のみ反映される
            this.parent_accordion_item_instance.reflectOnItemToNowOnomatopoeiaAction(this.parent_accordion_item_instance.pati_setting_mode);
        }
        this.parent_accordion_item_instance.checkHasOnContentButton();
    }

    /**
     * 
     * @param {"on"|"off"} on_off
     * @returns {void}
     */
    setButtonOnOff(on_off){
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        if (on_off == "on"){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"on");
            this.on_off = "on";
            //他のボタンでonになっているものをoffにする
            if (this.parent_accordion_item_instance.radio_mode == true) {
                for (const [key, value] of Object.entries(this.parent_accordion_item_instance.accordion_content_handler_list)){
                    console.log(key,value)
                    if (key != this.image_name){
                        value.ELM_accordion_content.classList.remove("on_accordion_content");
                        value.parent_accordion_item_instance.chara_human_body_manager.changeBodyPart(accordion_name,key,"off");
                        value.on_off = "off";
                    }
                }
            }
        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"off");
            this.on_off = "off";
        }
        this.parent_accordion_item_instance.checkHasOnContentButton();
    }

    /**
     * @returns {void}
     */
    checkContentStatus(){
        //HumanBodyManager2のプロパティのデータとアコーディオンの状態を比較して、アコーディオンの状態を変える
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        const on_off = this.chara_human_body_manager.getImgStatus(accordion_name,this.image_name);
        if (on_off == "on"){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.on_off = "on";
        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.on_off = "off";
        }
    }

    /**オノマトペアクションコントローラーをバインドする
     * @param {PatiSettingToggleEventObject} pati_setting_toggle_event_object
     */
    bindPatiSettingToggleEventObject(pati_setting_toggle_event_object){
        this.pati_setting_toggle_event_object = pati_setting_toggle_event_object;   
    }
}

class BodyCombinationAccordionManager{

    /** @type {HumanBodyManager2} */ human_body_manager;
    /** @type {VoiroAISetting} */ VoiroAISetting
    /** @type {HTMLElement} */ ELM_combination_box
    /** @type {HTMLElement} */ ELM_combination_name
    /** @type {HTMLElement} */ ELM_combination_candidate
    /** @type {HTMLElement} */ ELM_now_combination_name
    /** 
     * 組み合わせ名のアコーディオンの開閉状態を管理するMap。番号でも状態を取得したいのでMapを使う。オンのパターンの名前だけだとそれができないので。
     * todo: 未使用プロパティ
     * @type {ExtendedMap<string,*>} 
     */
     combination_box_status
    /** @type {ExtendedMap<string,CombinationContent>} */ conbination_contents

    
    /**
     * VoiroAISetting.ELM_combination_nameを押したらアコーディオンが開いて、human_body_manager.pose_patternsの組み合わせ名が全て表示される
     * キャラの組み合わせ名を選択するアコーディオンを管理するクラス
     * 
     * @param {HumanBodyManager2} human_body_manager
     * @param {VoiroAISetting} VoiroAISetting
     * @param {HTMLElement} ELM_combination_box
     * @param {HTMLElement} ELM_combination_name
     * @param {HTMLElement} ELM_combination_candidate
     */
    constructor(human_body_manager, VoiroAISetting, ELM_combination_box, ELM_combination_name, ELM_combination_candidate){
        this.human_body_manager = human_body_manager;
        this.VoiroAISetting = VoiroAISetting;
        this.ELM_combination_box = ELM_combination_box;
        console.log("bcamを作成した",this.ELM_combination_box)
        this.ELM_now_combination_name = ELM_combination_name;
        this.ELM_combination_candidate = ELM_combination_candidate;
        this.combination_box_status = new ExtendedMap(); 
        this.conbination_contents = new ExtendedMap();
        console.log("setAllCombinationを呼び出す")
        this.setAllCombination()
    }

    /**
     * @param {Event} event
     * @returns {void}
     */
    handleEvent(event){
        if(event.type == "click"){
            console.log("BodyCombinationAccordionManagerがクリックされたよ")
            console.log(this)
            console.log(this.ELM_combination_box)
            if (this.ELM_combination_box.classList.contains("close") == true){
                this.ELM_combination_box.classList.replace("close","open");
                this.setCombinationCandidateVisivility("open");
            } else {
                this.ELM_combination_box.classList.replace("open","close");
                this.setCombinationCandidateVisivility("close");
            }
            
        }
    }

    /**
     * 
     * @param {string} combination_name 
     * @param {*} status 
     * @returns {void}
     * todo: 未使用関数
     */
    setCombinationBoxStatus(combination_name, status){
        this.combination_box_status.set(combination_name,status);
    }

    /**
     * @param {string} combination_name
     * @returns {"on"|"off"}
     * todo: 未使用関数
     */
    getCombinationBoxStatus(combination_name){
        return this.combination_box_status.get(combination_name);
    }
    setAllCombination(){
        //human_body_manager.pose_patternsの組み合わせ名を全てアコーディオンに追加する
        const pose_patterns = this.human_body_manager.pose_patterns;
        console.log(pose_patterns)
        for (const [combination_name, combination_data] of pose_patterns.entries()){
            //settingとOnomatopeiaActionSettingは特別なのでアコーディオンに追加しない
            if (["setting","OnomatopeiaActionSetting","NowOnomatopoeiaActionSetting"].includes(combination_name) == true){
                continue;
            }

            console.log(combination_name)
            this.addCombination(combination_name);
        }
    }

    /**
     * @param {string} combination_name
     * @returns {void}
     */
    addCombination(combination_name){
        //human_body_manager.pose_patternsの組み合わせ名をアコーディオンに追加する
        var combination_content = new CombinationContent(combination_name, this, this.human_body_manager);
        var ELM_combination_content = combination_content.ELM_combination_name_button;
        ELM_combination_content.addEventListener("click",combination_content);
        this.ELM_combination_candidate.appendChild(ELM_combination_content);
        this.conbination_contents.set(combination_name,combination_content);
    }

    /**
     * @param {"open"|"close"} open_close
     * @returns {void}
     */
    setCombinationCandidateVisivility(open_close){
        if (open_close == "open"){
            this.ELM_combination_candidate.classList.remove("non_vissible");
        } else {
            this.ELM_combination_candidate.classList.add("non_vissible");
        }
    }
}

class CombinationContent{
    /**
     * 
     * キャラの組み合わせ名を選択するアコーディオンの中身のパターンNのボタンなどを管理するクラス
     * @param {string} combination_name
     * @param {BodyCombinationAccordionManager} body_combination_accordion_manager
     * @param {HumanBodyManager2} human_body_manager
     * @property {HTMLElement} ELM_combination_name_button
     * @property {string} on_off
     * 
     */
    constructor(combination_name, body_combination_accordion_manager, human_body_manager){
        this.combination_name = combination_name;
        this.body_combination_accordion_manager = body_combination_accordion_manager;
        this.human_body_manager = human_body_manager;
        
        this.ELM_combination_name_button = this.createELMCombinationNameButton();
        this.ELM_combination_name_button.addEventListener("click",this);
        this.on_off = "off";

    }
    
    /**
     * クリックした時に
     * 1:AccordionCombinationのELM_now_combination_nameのinnerTextを変更する
     * 2:VoiroAISettingの各アコーディオンのボタンをクリックするイベント発生さえて以下を実現する。
     * - human_body_managerのpose_patternを変更する
     * - human_body_managerのbody_partを変更する
     * 
     * HumanBodyManager2に対応させやすいようにするためにも
     * - AccordionCombinationがVoiroidAISettingを操作し、VoiroidAISettingがHumanBodyManagerを操作するようにする
     * 今はHumanBodyManagerの操作者は
     * - 1:AccordionCombination
     * - 2:文章による口パク制御
     * - 3:人間がボタンをVoiroidAISettingのクリックしたとき
     * - 4:gptによる「手を上げる」などの操作。
     * がある。
     * @param {Event} event 
     */
    handleEvent(event){
        if(event.type == "click"){
            //AccordionCombinationのELM_now_combination_nameのinnerTextを変更する
            this.body_combination_accordion_manager.ELM_now_combination_name.innerText = this.combination_name;
            //VoiroAISettingの各アコーディオンのボタンをクリックするイベント発生させて以下を実現する。
            //human_body_managerのpose_patternを変更する
            //human_body_managerのbody_partを変更する
            console.log("CombinationContentがクリックされたよ,ボタン名＝",this.combination_name,"現在の状態:",this.human_body_manager.pose_patterns)
            let combination_data = this.getCombinationData();
            for (const [body_group, part_candidate_info] of combination_data.entries()){
                //part_candidate_info = {10_体:"on"}のようなjson
                // console.log(body_group," なのだ ",part_candidate_info,"を適用する。現在の状態:",this.human_body_manager.pose_patterns)
                //part_candidate_info = {10_体:"on"}のようなjsonのキーと値を取得する
                for (const [image_name, on_off] of Object.entries(part_candidate_info)){
                    // console.log(image_name, on_off)
                    this.body_combination_accordion_manager.VoiroAISetting.setGroupButtonOnOff(body_group, image_name, on_off);
                }
            }
        }
        console.log("コンビネーション適用完了！現在の状態:",this.human_body_manager.pose_patterns)
    }

    createELMCombinationNameButton(){
        var ELM_combination_name_button = document.createElement("li");
        ELM_combination_name_button.classList.add("combination_name_button","accordion_tab","off");
        ELM_combination_name_button.innerText = this.combination_name;
        console.log(ELM_combination_name_button);
        return ELM_combination_name_button;
    }

     /**
     * 
     * @returns 
     */
     getCombinationData(){
        const pose_pattern = this.human_body_manager.getPosePattern(this.combination_name);
        return pose_pattern;
    }
}

/**
 * GPTの設定を管理するクラス
 * got_settingエレメントをクリックすると開く。
 * gptのモードが列挙されたボタンがある。
 * 
 * 選択したモードは各キャラのMessageBoxとMessageBoxMabagerに送信され、すべてのキャラのGPTのモードが1元管理される。
 */
class GPTSettingButtonManagerModel {

    /**
     * モード名：on_off 
     * @type {ExtendedMap<string,"on"|"off">} */
    gpt_setting_status;

    /** todo
     * モード名：ボタンのDOM
     * @type {ExtendedMap<string,HTMLElement>} */
    Map_ELM_gpt_setting_button;

    /** @type {MessageBox} */
    message_box;

    /** @type {string} */
    front_name ;

    /** @type {string[]} */
    gpt_mode_name_list;

    /** @type {HTMLUListElement} */
    ELM_gpt_setting;

    /** @type {HTMLElement} */
    gpt_mode_accordion_open_close_button


    /**
     * 
     * @param {string} front_name 
     * @param {MessageBox} message_box 
     * @param {string[]} gpt_mode_name_list 
     */
    constructor(front_name, message_box, gpt_mode_name_list) {
        this.front_name = front_name;
        this.message_box = message_box;
        this.gpt_mode_name_list = gpt_mode_name_list;

        const human_tab = /** @type {Element} */ (this.message_box.message_box_elm.closest(".human_tab"));
        this.ELM_gpt_setting = /** @type {HTMLUListElement} */ (human_tab.querySelector(".gpt_setting"));


        this.gpt_setting_status = this.getGPTSettingStatus(gpt_mode_name_list);
        this.Map_ELM_gpt_setting_button = this.getMapELMGPTSettingButton(gpt_mode_name_list);
        this.Map_ELM_gpt_setting_button.forEach((value, key, map) => {
            let ELM_gpt_setting_button = value;
            const mode_name = key;
            ELM_gpt_setting_button.addEventListener("click", (/** @type {Event} */ event) => { 
                this.clickEvent(event, mode_name);
            });
        });
        this.gpt_mode_accordion_open_close_button = /** @type {HTMLElement} */ (this.ELM_gpt_setting.querySelector(".gpt_mode_accordion_open_close_button"));
        this.gpt_mode_accordion_open_close_button.addEventListener("click", this.open_closeAcordion.bind(this));

        //ELM_gpt_settingからfocusが外れたときに、gpt_mode_accordion_open_close_buttonをcloseにする
        this.ELM_gpt_setting.addEventListener("focusout", this.closeAccordion.bind(this));
    }

    /**
     * @param {string[]} gpt_mode_name_list
     * @returns {ExtendedMap<string,"on"|"off">}
     */
    getGPTSettingStatus(gpt_mode_name_list) {
        /** @type {ExtendedMap<string,"on"|"off">} */
        var gpt_setting_status = new ExtendedMap();
        for (let i = 0; i < gpt_mode_name_list.length; i++) {
            gpt_setting_status.set(gpt_mode_name_list[i], "off");
        }
        return gpt_setting_status;
    }

    /**
     * @param {string[]} gpt_mode_name_list
     * @returns {ExtendedMap<string,HTMLElement>}
     */
    getMapELMGPTSettingButton(gpt_mode_name_list) {
        /** @type {ExtendedMap<string,HTMLElement>} */
        var Map_ELM_gpt_setting_button = new ExtendedMap();
        for (let i = 0; i < gpt_mode_name_list.length; i++) {
            var ELM_gpt_setting_button = this.createELMGPTSettingButton(gpt_mode_name_list[i]);
            Map_ELM_gpt_setting_button.set(gpt_mode_name_list[i], ELM_gpt_setting_button);
        }
        return Map_ELM_gpt_setting_button;
    }

    /**
     * 
     * @param {string} mode
     * @returns {HTMLElement} ELM_gpt_setting_button
     */
    createELMGPTSettingButton(mode) {
        //<li class="bar_button gpt_mode" style="display: ;">off</li> などを作成する
        var ELM_gpt_setting_button = document.createElement("li");
        ELM_gpt_setting_button.classList.add("bar_button", "gpt_mode", "off", "non_vissible");
        ELM_gpt_setting_button.innerText = mode;
        //human_tabからgpt_settingに追加する
        this.ELM_gpt_setting.appendChild(ELM_gpt_setting_button);

        return ELM_gpt_setting_button;
    }

    open_closeAcordion() {
        if (this.gpt_mode_accordion_open_close_button.classList.contains("close") == true) {
            this.openAccordion();
        } else {
            this.closeAccordion();
        }
    }
    closeAccordion() {
        this.gpt_mode_accordion_open_close_button.classList.replace("open", "close");
        this.Map_ELM_gpt_setting_button.forEach((value, key, map) => {
            let ELM_gpt_setting_button = value;
            ELM_gpt_setting_button.classList.add("non_vissible");
        });
    }

    openAccordion() {
        this.gpt_mode_accordion_open_close_button.classList.replace("close", "open");
        this.Map_ELM_gpt_setting_button.forEach((value, key, map) => {
            let ELM_gpt_setting_button = value;
            ELM_gpt_setting_button.classList.remove("non_vissible");
        });
    }

    /**
     * 
     * @param {Event} event
     * @param {string} mode
     * @returns {void}
     */
    clickEvent(event, mode) {
        console.log("GPTSettingButtonManaerModelがクリックされたよ")
        console.log(event, mode)
        this.radioChangeGPTSettingStatus(mode);
        this.radioChangeButtonView(mode);
        this.sendGPTSettingStatus(mode);
        this.sendGPTSettingStatus2Server(mode);
    }

    /**
     * @param {string} target_mode
     * @returns {void}
     */
    radioChangeGPTSettingStatus(target_mode) {
        this.gpt_mode_name_list.forEach(
            (mode) => {
                if (mode == target_mode) {
                    this.setGPTSettingStatus(mode, "on");
                } else {
                    this.setGPTSettingStatus(mode, "off");
                }
            }
        )
    }

    /**
     * @param {string} mode
     * @param {"on"|"off"} on_off
     * @returns {void}
     */
    setGPTSettingStatus(mode,on_off) {
        this.gpt_setting_status.set(mode, on_off);
        if (on_off == "on") {
            this.message_box.setGptMode(mode);
        }
    }

    /**
     * @param {string} mode
     * @returns {void}
     */
    radioChangeButtonView(mode) {
        this.gpt_mode_name_list.forEach(
            (mode) => {
                if (this.gpt_setting_status.get(mode) == "on") {
                    this.setButtonView(mode, "on");
                    this.gpt_mode_accordion_open_close_button.innerText = `GPT : ${mode}`;
                } else {
                    this.setButtonView(mode, "off");
                }
            }
        )
    }

    /**
     * @param {string} mode
     * @param {"on"|"off"} on_off
     * @returns {void}
     */
    setButtonView(mode, on_off) {
        const ELM_gpt_setting_button = this.Map_ELM_gpt_setting_button.get(mode);
        if (on_off == "off") {
            ELM_gpt_setting_button.classList.remove("on");
            ELM_gpt_setting_button.classList.add("off");
        } else {
            ELM_gpt_setting_button.classList.remove("off");
            ELM_gpt_setting_button.classList.add("on");
        }
    }

    /**
     * @param {string} mode
     * @returns {void}
     */
    sendGPTSettingStatus(mode) {
        this.message_box.gpt_mode = mode;
    }

    /**
     * @param {string} mode
     * @returns {void}
     */
    sendGPTSettingStatus2Server(mode) { 
        //websocketを作成
        var ws_gpt_mode_sender = new WebSocket(`ws://${localhost}:${port}/gpt_mode`)
        ws_gpt_mode_sender.onopen =  ( _ ) => {
            const data = {[this.front_name]: mode}
            console.log("gpt_modeが開かれた。このデータを送る。", mode)
            ws_gpt_mode_sender.send(JSON.stringify(data));
            ws_gpt_mode_sender.close();
        }
        //websocketを閉じる
        ws_gpt_mode_sender.onclose = function (event) {
            console.log("gpt_modeが閉じられたよ")
        }
        //サーバーからメッセージを受け取ったとき。今は使ってない。
        ws_gpt_mode_sender.onmessage = function (event) {
            console.log("gpt_modeからメッセージを受け取ったよ")
            console.log(event.data)
            ws_gpt_mode_sender.close();
        }
    }
}



