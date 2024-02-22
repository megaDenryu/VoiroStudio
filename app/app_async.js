//非同期サーバー。レスポンスのhttpヘッダーがバグる。

// モジュールのロード
const http = require('http');
const fs = require('fs');
const path = require('path'); // 拡張子チェック用

var rooting = {
    "/":"index.html",
    "/InputPokemon":"./InputPokemon/InputPokemonPage.html",
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
    
    // ファイル読み込み。非同期なのでコンテンツタイプがバグることがある。例えばjsをcssとしてhttpレスポンス返したりするのでくそ。
    fs.readFile(target,{flag: 'r', encoding: 'utf8'}, // オプションオブジェクトを渡す
    (error, data) => {
        // エラー処理
        if (error) {
            response.writeHead(500, {"Content-Type": "text/plain"});
            response.write("500 Internal Server Error\n");
            res.end();
        }
        
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
        res.end();
    });
});

// 待ち受け開始
server.listen(8080);
console.log('Server running');

