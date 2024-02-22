// モジュールのロード
const http = require('http');
const fs = require('fs');

// サーバーオブジェクトの作成
const server = http.createServer((req,res)=>{
  // ファイル読み込み
  fs.readFile('index.html','UTF-8',
    (error, data) => {
        // エラー処理
        if (error) {
            response.writeHead(500, {"Content-Type": "text/plain"});
            response.write("500 Internal Server Error\n");
            res.end();
        }
        // index.htmlを表示
        res.writeHead(200,{'Content-Type':'text/html'});
        res.write(data);
        res.end();
    });
});

// 待ち受け開始
server.listen(8080);
console.log('Server running');