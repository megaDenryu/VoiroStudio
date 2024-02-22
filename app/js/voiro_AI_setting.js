
/**
 * @param {iHumanBodyManager}chara_human_body_manager
 */

class VoiroAISetting{
    constructor(chara_human_body_manager){
        console.log("VoiroAISetting constructor")
        this.ELM_body_setting = document.querySelector(".body_setting");
        this.chara_human_body_manager = chara_human_body_manager;
        this.ELM_combination_name;
        this.ELM_input_combination_name;

        var [ELM_accordion,accordion_item_dict] = this.createAccordion();
        this.ELM_accordion = ELM_accordion
        this.accordion_item_dict = accordion_item_dict
        this.ELM_body_setting.append(this.ELM_accordion);
    }

    /**
     * 
     * @returns {HTMLElement,object} ELM_accordion,accordion_item_dict 
     */
    createAccordion(){
        var ELM_accordion = document.createElement("ul");
        ELM_accordion.classList.add("accordion");
        console.log(this.chara_human_body_manager)

        //組み合わせ名を表示する要素を追加
        this.ELM_combination_box = this.createElmCombinatioBox()
        ELM_accordion.appendChild(this.ELM_combination_box)

        var map = this.chara_human_body_manager.map_body_parts_info;
        var accordion_item_dict = {};
        for (const [key, value] of map){
            //keyは体のパーツの名前、valueはそのパーツの画像群の配列
            var accordion_item = new AccordionItem(key, this.ELM_body_setting, this.chara_human_body_manager);
            var ELM_accordion_item = accordion_item.html_doc.querySelector(".accordion_item");
            console.log(ELM_accordion_item);
            var ELM_accordion_item_name = accordion_item.html_doc.getElementsByClassName("accordion_item_name")[0];
            ELM_accordion_item_name.addEventListener("click",accordion_item);
            accordion_item_dict[key] = accordion_item;
            console.log(ELM_accordion,ELM_accordion_item);
            ELM_accordion.appendChild(ELM_accordion_item);
            accordion_item.ELM = ELM_accordion_item;
        }
        //組み合わせ名を入力するinput要素を追加
        this.ELM_input_combination_name = this.createElmInputCombinationName();
        ELM_accordion.appendChild(this.ELM_input_combination_name);

        return [ELM_accordion,accordion_item_dict];
    }

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
        const bcanm = new BodyCombinationAccordionManager(this.chara_human_body_manager, this.ELM_combination_box, this.ELM_combination_name, this.ELM_combination_candidate, this);
        this.ELM_combination_box.addEventListener("click",bcanm);

        return this.ELM_combination_box;
    }

    createElmCombinatioName(){
        var ELM_combination_name = document.createElement("div");
        ELM_combination_name.classList.add("combination_name");
        ELM_combination_name.innerText = "名無しの組み合わせ";
        //this.ELM_now_combination_name = this.createELMNowCombinationName();
        return ELM_combination_name;
    }

    createELMNowCombinationName(){
        var ELM_now_combination_name = document.createElement("p");
        ELM_now_combination_name.classList.add("now_combination_name");
        ELM_now_combination_name.innerText = "名無しの組み合わせ";
        this.ELM_combination_name.appendChild(this.ELM_now_combination_name);
    }

    createElmInputCombinationName(){
        var ELM_input_combination_name = document.createElement("input");
        ELM_input_combination_name.type = "text";
        ELM_input_combination_name.classList.add("input_combination_name");
        ELM_input_combination_name.placeholder = "組み合わせ名を入力";
        ELM_input_combination_name.addEventListener("keypress",this.saveCombinationName.bind(this));
        return ELM_input_combination_name;
    }

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
            ws_combi_img_sender.close();
        }
    }
    getAllImageStatusDict(){
        var image_status_dict = {};
        for (const [key_name, accordion_item] of Object.entries(this.accordion_item_dict)){
            image_status_dict[key_name] = accordion_item.getNamesOnContentButton();
        }
        return image_status_dict;    
    }

    getAllNowImages(){
        var image_status_dict = {};
        for (const [key_name, accordion_item] of Object.entries(this.accordion_item_dict)){
            image_status_dict[key_name] = this.chara_human_body_manager.getNowNameBodyPart(key_name);
        }
        return image_status_dict;    
    }

    setBodyPartImage(body_part_name,image_name) {
        this.accordion_item_dict[body_part_name].setBodyPartImage(image_name);
    }

    setGroupButtonOnOff(group_name, content_name, on_off){
        this.accordion_item_dict[group_name].setGroupButtonOnOff(content_name,on_off);
    }

}

/**
 * アコーディオンを展開したときに見えるアコーディオンコンテンツのクラス
 * パーツ名をクリックしたときに、ボタンの色を変え、人体モデルのパーツの表示を変え、プロパティのデータも変える
 * @property {string} statu_open_close
 * @property {object} image_item_status
 * @property {HTMLElement} ELM_accordion_contents  
 */

class AccordionItem{
    /**
     * 
     * @param {string} name_acordion           body_setting要素内のアコーディオンの名前は、対応する画像名と同じにする
     * @param {HTMLElement} Parent_ELM_body_setting  body_settingの要素
     * @param {iHumanBodyManager} chara_human_body_manager: iHumanBodyManager
     * @property {string} statu_open_close
     * @property {HTMLElement} ELM_accordion_contents
     * @property {HTMLCollection} ELMs_accordion_content
     * @property {object} accordion_content_handler_list
     * @property {object} has_on_content_button
     */
    constructor(name_acordion, Parent_ELM_body_setting, chara_human_body_manager){
        //引数の登録
        this.name_acordion = name_acordion;
        this.Parent_ELM_body_setting = Parent_ELM_body_setting;
        this.chara_human_body_manager = chara_human_body_manager;
        this.contents_name_list = [...this.chara_human_body_manager.map_body_parts_info.get(name_acordion)["imgs"].keys()]
        
        this.statu_open_close = "close";
        this.accordion_content_handler_list = {};
        //accordion_sampleを複製
        this.HTML_str_accordion_sample = `
        <li class = "accordion_item close layer ">
            <div class = "accordion_item_name accordion_tab">
                頭
            </div>
            <ul class = "accordion_contents non_vissible">
                <li class = "accordion_content body_part_image_name accordion_tab sample">1.png</li>
            </ul>
        </li>
        `;
        const parser = new DOMParser();
        this.html_doc = parser.parseFromString(this.HTML_str_accordion_sample, "text/html");
        //名前を設定
        this.setAccordionItemName(name_acordion);
        //アコーディオンの中身を作成
        var [ELM_accordion_contents,accordion_content_handler_list] = this.createELMAccordionContents(name_acordion);
        this.ELM_accordion_contents = ELM_accordion_contents;
        this.ELM_accordion_item_name = this.html_doc.querySelector(".accordion_item_name");
        this.accordion_content_handler_list = accordion_content_handler_list;
        //オンになってるボタンがあるかどうか
        this.checkHasOnContentButton();
    }
    
    handleEvent(event){
        //clickイベントの場合。アコーディオンの開閉を行う
        if(event.type == "click"){
            var ELM_accordion_item = this.ELM
            console.log(ELM_accordion_item)
            if (this.statu_open_close == "close") {
                ELM_accordion_item.classList.replace("close", "open");
                this.statu_open_close = "open";
                ELM_accordion_item.querySelector(".accordion_contents").classList.remove("non_vissible");
            } else {
                ELM_accordion_item.classList.replace("open", "close");
                this.statu_open_close = "close";
                ELM_accordion_item.querySelector(".accordion_contents").classList.add("non_vissible");
            }
        }
        //hoverしたとき色を変える
        if(event.type == "mouseover"){
            console.log("mouseover")
            this.ELM.classList.add("hover");
        }
    }


    /**
     * 
     * @param {string} image_name 
     */
    imageStatusChange(image_name) {
        if (this.image_item_status[image_name] == "on") {
            this.image_item_status[image_name] = "off";
            this.changeELMAccordionContent(image_name)
            this.chara_human_body_manager.changeBodyPart(image_name,"off");
        } else {
            this.image_item_status[image_name] = "on";
            this.chara_human_body_manager.changeBodyPart(image_name,"on");
        }
    }

    /**
     * アコーディオンのエレメントの最新の状態をプロパティに反映する
     */
    loadNowAccordionELMStatus(){
        //todo: コードが適当なので確認すること
        for (let i = 0; i < this.ELMs_accordion_content.length; i++) {
            let image_name = this.ELMs_accordion_content[i].id;
            this.image_item_status[image_name] = this.ELMs_accordion_content[i].value;
        }

    }

    setAccordionItemName(name_acordion){
        //accordion_item_nameを変更
        this.html_doc.querySelector(".accordion_item_name").innerText = name_acordion;
    }

    /**
     * 
     * @param {string} name_acordion 
     * @returns {HTMLElement,object} ELM_accordion_contents,accordion_content_handler_list
     * 
     */
    createELMAccordionContents(name_acordion){
        //this.contents_name_listには画像の名前が入っている。ELM_accordion_contentを複製してELM_accordion_contentsに追加する。
        var ELM_accordion_contents = this.html_doc.querySelector(".accordion_contents");
        const ELM_accordion_content = this.html_doc.querySelector(".accordion_content");
        var accordion_content_handler_list = {};
        for (let i = 0; i < this.contents_name_list.length; i++) {
            //ELM_accordion_contentを複製
            var ELM_accordion_content_clone = ELM_accordion_content.cloneNode(true);
            ELM_accordion_content_clone.innerText = this.contents_name_list[i];

            //画像の名前から、画像のパスを取得
            //let image_path = this.chara_human_body_manager.map_body_parts_info.get(name_acordion)["imgs"].get(this.contents_name_list[i]);
            const image_name = this.contents_name_list[i];
            //アコーディオンの中身のボタンにイベントハンドラーを追加
            let content_button_event_object = new ContentButtonEventobject(image_name, "off", ELM_accordion_content_clone,this);
            ELM_accordion_content_clone.addEventListener("click", content_button_event_object);
            ELM_accordion_content_clone.classList.remove("sample");

            //アコーディオンの中身を追加
            ELM_accordion_contents.appendChild(ELM_accordion_content_clone);
            //console.log(ELM_accordion_content_clone);
            accordion_content_handler_list[image_name] = content_button_event_object;
        }
        
        //html_docからsampleクラスを持つ要素を削除
        //console.log(this.html_doc);
        this.html_doc.querySelector(".sample").remove();
        //.log(this.html_doc);
        //console.log(this.html_doc.querySelector(".sample"));
        

        return [ELM_accordion_contents,accordion_content_handler_list];
    }

    getContentStatusDict(){
        var item_status_dict = {};
        for (const [key, value] of Object.entries(this.accordion_content_handler_list)){
            item_status_dict[key] = value.on_off;
        }
        return item_status_dict;
    }

    getNamesOnContentButton(){
        var name_on_content_button = [];
        for (const [key, value] of Object.entries(this.accordion_content_handler_list)){
            if (value.on_off == "on"){
                name_on_content_button.push(key);
            }
        }
        return name_on_content_button;
    }

    countOnContentButton(image_item_status){
        var count = 0;
        for (const [key, value] of Object.entries(image_item_status)){
            if (value == "on"){
                count += 1;
            }
        }
        return count;
    }
    checkHasOnContentButton(){
        console.log("checkHasOnContentButtonが動いた: " + new Date());
        const image_item_status = this.getContentStatusDict();
        const count_on_content_button = this.countOnContentButton(image_item_status);
        const ELM_accordion_item_name = this.ELM_accordion_item_name;
        console.log(this.ELM_accordion_contents);
        console.log(this.html_doc);
        console.log(ELM_accordion_item_name);
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

    setBodyPartImage(image_name) {
        this.accordion_content_handler_list[image_name].clickEvent();
    }

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

class ContentButtonEventobject{
    /**
     * 各コンテンツのボタンのイベントハンドラーに追加するクラス
     * このクラスとコンテンツボタンはAccordionContent.createELMAccordionContents一対一で作成される。
     * 
     * @param {string} image_name 
     * @param {string} on_off 
     * @param {HTMLElement} ELM_accordion_content 
     * @param {AccordionItem} parent_accordion_item_instance
     * @property {iHumanBodyManager} chara_human_body_manager
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
    handleEvent(event){
        //clickイベントの場合
        console.log("ContentButtonEventobjectクリックしたよ")
        if(event.type == "click"){
            this.clickEvent(event);
        }
        //hoverしたとき色を変える
        if(event.type == "mouseover"){
            console.log("mouseover")
            this.ELM_accordion_content.classList.add("hover");
        }
    }
    clickEvent(){
        console.log("ContentButtonEventobjectクリックしたよ")
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        //ボタンの色を変え,プロパティのデータを変える
        console.log(this.ELM_accordion_content);
        if(this.on_off == "off"){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"on");
            this.on_off = "on";
            //他のボタンでonになっているものをoffにする
            for (const [key, value] of Object.entries(this.parent_accordion_item_instance.accordion_content_handler_list)){
                console.log(key,value)
                if (key != this.image_name){
                    value.ELM_accordion_content.classList.remove("on_accordion_content");
                    //value.parent_accordion_item_instance.chara_human_body_manager.changeBodyPart(accordion_name,key,"off");
                    value.on_off = "off";
                }
            }

        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"off");
            this.on_off = "off";
        }
        this.parent_accordion_item_instance.checkHasOnContentButton();
    }

    setButtonOnOff(on_off){
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        if (on_off == "on"){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"on");
            this.on_off = "on";
            //他のボタンでonになっているものをoffにする
            for (const [key, value] of Object.entries(this.parent_accordion_item_instance.accordion_content_handler_list)){
                console.log(key,value)
                if (key != this.image_name){
                    value.ELM_accordion_content.classList.remove("on_accordion_content");
                    //value.parent_accordion_item_instance.chara_human_body_manager.changeBodyPart(accordion_name,key,"off");
                    value.on_off = "off";
                }
            }
        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.chara_human_body_manager.changeBodyPart(accordion_name,this.image_name,"off");
            this.on_off = "off";
        }
        this.parent_accordion_item_instance.checkHasOnContentButton();
    }

    checkInitContentStatus(){
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        const now_part_name = this.chara_human_body_manager.getInitImageNameBodyPart(accordion_name);
        if (now_part_name == this.image_name){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.on_off = "on";
        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.on_off = "off";
        }
    }

    checkContentStatus(){
        const accordion_name = this.parent_accordion_item_instance.name_acordion;
        const now_part_name = this.chara_human_body_manager.getNowNameBodyPart(accordion_name);
        if (now_part_name == this.image_name){
            this.ELM_accordion_content.classList.add("on_accordion_content");
            this.on_off = "on";
        } else {
            this.ELM_accordion_content.classList.remove("on_accordion_content");
            this.on_off = "off";
        }
    }
}

class BodyCombinationAccordionManager{
    
    /**
     * VoiroAISetting.ELM_combination_nameを押したらアコーディオンが開いて、human_body_manager.pose_patternsの組み合わせ名が全て表示される
     * キャラの組み合わせ名を選択するアコーディオンを管理するクラス
     * 
     * @param {iHumanBodyManager} human_body_manager
     * @param {HTMLElement} ELM_combination_box
     * @param {HTMLElement} ELM_now_combination_name
     * @param {VoiroAISetting} VoiroAISetting
     * @property {iHumanBodyManager} human_body_manager
     * @property {VoiroAISetting} VoiroAISetting
     * @property {HTMLElement} ELM_now_combination_name
     * @property {ExtendedMap} combination_box_status
     * @property {ExtendedMap} conbination_contents
     * 
     */
    constructor(human_body_manager, ELM_combination_box, ELM_combination_name, ELM_combination_candidate,VoiroAISetting){
        this.human_body_manager = human_body_manager;
        this.VoiroAISetting = VoiroAISetting;
        this.ELM_combination_box = ELM_combination_box;
        console.log("bcamを作成した",this.ELM_combination_box)
        this.ELM_now_combination_name = ELM_combination_name;
        this.ELM_combination_candidate = ELM_combination_candidate;
        this.combination_box_status = new ExtendedMap(); //組み合わせ名のアコーディオンの開閉状態を管理するMap。番号でも状態を取得したいのでMapを使う。オンのパターンの名前だけだとそれができないので。
        this.conbination_contents = new ExtendedMap();
        console.log("setAllCombinationを呼び出す")
        this.setAllCombination()
    }
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
    setCombinationBoxStatus(combination_name, status){
        this.combination_box_status.set(combination_name,status);
    }
    getCombinationBoxStatus(combination_name){
        return this.combination_box_status.get(combination_name);
    }
    setAllCombination(){
        //human_body_manager.pose_patternsの組み合わせ名を全てアコーディオンに追加する
        const pose_patterns = this.human_body_manager.pose_patterns;
        console.log(pose_patterns)
        for (const [combination_name, combination_data] of pose_patterns.entries()){
            console.log(combination_name)
            this.addCombination(combination_name);
        }
    }
    addCombination(combination_name){
        //human_body_manager.pose_patternsの組み合わせ名をアコーディオンに追加する
        var combination_content = new CombinationContent(combination_name, this, this.human_body_manager);
        var ELM_combination_content = combination_content.ELM_combination_name_button;
        ELM_combination_content.addEventListener("click",combination_content);
        this.ELM_combination_candidate.appendChild(ELM_combination_content);
        this.conbination_contents.set(combination_name,combination_content);
    }
    setCombinationCandidateVisivility(on_off){
        if (on_off == "open"){
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
     * @param {iHumanBodyManager} human_body_manager
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
     * 
     * @returns {object} combination_data
     */
    getCombinationData(){
        return this.human_body_manager.getPosePattern(this.combination_name);
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
            console.log("CombinationContentがクリックされたよ")
            const combination_data = this.getCombinationData();
            for (const [body_group, image_name] of Object.entries(combination_data)){
                console.log(body_group," なのだ ",image_name)
                this.body_combination_accordion_manager.VoiroAISetting.setGroupButtonOnOff(body_group, image_name, "on")
            }
        }

    }

    createELMCombinationNameButton(){
        var ELM_combination_name_button = document.createElement("li");
        ELM_combination_name_button.classList.add("combination_name_button","accordion_tab","off");
        ELM_combination_name_button.innerText = this.combination_name;
        console.log(ELM_combination_name_button);
        return ELM_combination_name_button;
    }
}

/**
 * GPTの設定を管理するクラス
 * got_settingエレメントをクリックすると開く。
 * gptのモードが列挙されたボタンがある。
 * 
 * 選択したモードは各キャラのMessageBoxとMessageBoxMabagerに送信され、すべてのキャラのGPTのモードが1元管理される。
 * 
 * @property {ExtendedMap} gpt_setting_status モード名：on_off
 * @property {ExtendedMap[DOM]} Map_ELM_gpt_setting_button モード名：ボタンのDOM
 * @property {MessageBox} message_box
 * @property {string} front_name 
 * @property {Array} gpt_mode_name_list
 * @property {HTMLElement} ELM_gpt_setting
 */
class GPTSettingButtonManagerModel {
    /**
     * 
     * @param {string} front_name 
     * @param {MessageBox} message_box 
     * @param {Array} gpt_mode_name_list 
     */
    constructor(front_name, message_box, gpt_mode_name_list) {
        this.front_name = front_name;
        this.message_box = message_box;
        this.gpt_mode_name_list = gpt_mode_name_list;
        this.ELM_gpt_setting = this.message_box.message_box_elm.closest(".human_tab").querySelector(".gpt_setting");
        this.gpt_setting_status = this.getGPTSettingStatus(gpt_mode_name_list);
        this.Map_ELM_gpt_setting_button = this.getMapELMGPTSettingButton(gpt_mode_name_list);
        this.Map_ELM_gpt_setting_button.forEach((value, key, map) => {
            let ELM_gpt_setting_button = value;
            const mode_name = key;
            ELM_gpt_setting_button.addEventListener("click", function (event) { 
                this.clickEvent(event, mode_name);
            }.bind(this));
        });
        this.gpt_mode_accordion_open_close_button = this.ELM_gpt_setting.querySelector(".gpt_mode_accordion_open_close_button");
        this.gpt_mode_accordion_open_close_button.addEventListener("click", this.open_closeAcordion.bind(this));

        //ELM_gpt_settingからfocusが外れたときに、gpt_mode_accordion_open_close_buttonをcloseにする
        this.ELM_gpt_setting.addEventListener("focusout", this.closeAccordion.bind(this));
    }

    getGPTSettingStatus(gpt_mode_name_list) {
        var gpt_setting_status = new ExtendedMap();
        for (let i = 0; i < gpt_mode_name_list.length; i++) {
            gpt_setting_status.set(gpt_mode_name_list[i], "off");
        }
        return gpt_setting_status;
    }

    getMapELMGPTSettingButton(gpt_mode_name_list) {
        var Map_ELM_gpt_setting_button = new ExtendedMap();
        for (let i = 0; i < gpt_mode_name_list.length; i++) {
            var ELM_gpt_setting_button = this.createELMGPTSettingButton(gpt_mode_name_list[i]);
            Map_ELM_gpt_setting_button.set(gpt_mode_name_list[i], ELM_gpt_setting_button);
        }
        return Map_ELM_gpt_setting_button;
    }

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

    clickEvent(event, mode) {
        console.log("GPTSettingButtonManaerModelがクリックされたよ")
        console.log(event, mode)
        this.radioChangeGPTSettingStatus(mode);
        this.radioChangeButtonView(mode);
        this.sendGPTSettingStatus(mode);
        this.sendGPTSettingStatus2Server(mode).bind(this);
    }

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

    setGPTSettingStatus(mode,on_off) {
        this.gpt_setting_status.set(mode, on_off);
        if (on_off == "on") {
            this.message_box.setGptMode(mode);
        }
    }

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

    sendGPTSettingStatus(mode) {
        this.message_box.gpt_mode = mode;
    }

    sendGPTSettingStatus2Server(mode) { 
        //websocketを作成
        var ws_gpt_mode_sender = new WebSocket(`ws://${localhost}:${port}/gpt_mode`)
        ws_gpt_mode_sender.onopen = function (event) {
            const data = {[this.front_name]: mode}
            console.log("gpt_modeが開かれた。このデータを送る。", mode)
            ws_gpt_mode_sender.send(JSON.stringify(data));
            ws_gpt_mode_sender.close();
        }.bind(this)
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



