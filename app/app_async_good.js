//非同期サーバー。app_async.jsをAIに改善してもらった。レスポンスのhttpヘッダーがバグるかどうかは不明。

// モジュールのロード
const http = require('http');
const fs = require('fs').promises; // PromiseベースのAPIに変更
const path = require('path'); // 拡張子チェック用

// コールバック関数を別に定義
function handleFileRead(error, data) {
    if (error) {
        res.writeHead(500, {"Content-Type": "text/plain"});
        res.write("500 Internal Server Error\n");
        res.end();
    } else {
        // 拡張子チェック
        var extname = path.extname(target); // 拡張子を取得
        
        // Content-Typeの設定
        var contentType; 
        if (extname == '.css') { // .cssならtext/cssに設定
            contentType = 'text/css';
        } else if(extname == '.js') {
            contentType = 'text/javascript';
        }else if (extname == '.ico') {
            contentType = 'image/vnd.microsoft.icon';
        } else { // それ以外ならmimeモジュールでMIMEタイプを取得(今はmimeをインストールしてないので全てhtmlにする)
            contentType = 'text/html';
        }
        
        console.log("content_type:" + contentType)
        
        // index.htmlを表示
        res.writeHead(200,{'Content-Type':contentType}); 
        res.write(data);
        
    }
}

// サーバーオブジェクトの作成
const server = http.createServer((req,res)=>{
    switch (req.url) {
        case "/":
            target = "index.html";
            break;
        default:
            target = "."+req.url;
            break;
    }

    
    console.log(target);
    
    // ファイル読み込み。Promiseベースなのでthenやcatchで処理をチェーンする。
    fs.readFile(target,'utf8') // 文字コードを直接指定するとエンコーディングされた文字列が返される。
      .then(data => handleFileRead(null,data)) // 成功時はhandleFileReadにデータを渡す。
      .catch(error => handleFileRead(error,null)) // 失敗時はhandleFileReadにエラーを渡す。
      .finally(() => res.end()); // 最後にレスポンスを終了する。
});

// 待ち受け開始
server.listen(8080);
console.log('Server running');