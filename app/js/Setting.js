///@ts-check

// Model

// 画面全体の機能ブロックを保管して追加、削除、更新、検索、可視不可視切り替えする機能を提供する
class ManageBlocks {
    /** @type {SettingBlock[]} */ blocks;
    constructor() {
        
        
    }

}

// 機能ブロックの子オブジェクトを1まとめにして、機能を提供する
class SettingBlock {
    /** @type {SettingKey} */ key;
    /** @type {ISettingInput} */ input;
    /** @type {SettingSender} */ sender;
}

// キー名の文字色の変更などの機能を提供する
class SettingKey {
    /** @type {string} */ name;
}

// 入力機能を提供する
class ISettingInput {

}

// JSONにしてサーバーに送信する機能を提供する
class SettingSender {
    
}


//View

/**
 * 画面の大きさ
 */
class RectangleFrame {
    /** 
     * @param {VectorN} position
     * @param {VectorN} size
     * */ 
    constructor(position, size) {
        this.position = position;
        this.size = size;
        this.html = this.createHtml();
    }


    
    
}
