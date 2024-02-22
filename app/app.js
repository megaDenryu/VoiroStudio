// モジュールのロード
const http = require('http');
const fs = require('fs');
const path = require('path');

// 拡張子とContent-Typeの対応表
const mimeTypes = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.ico': 'image/vnd.microsoft.icon',
  '.png': 'image/png',
  '.jpg': 'image/jpeg'
};

const root = ".."

// サーバーオブジェクトの作成
const server = http.createServer((req,res)=>{
  // パスを取得
  var target;
  console.log(req.url)
  switch (req.url) {
    case "/":
      target = "index.html";
      break;
    default:
      target = "."+decodeURIComponent(req.url);//日本語がUNICODEにencodeされてるので、デコードして元に戻さないとpathにたどり着けない。
      break;
  }
  
  // 拡張子を取得
  var extname = path.extname(target);
  
  // Content-Typeを取得
  var contentType = mimeTypes[extname] || 'text/plain';

  // パスとContent-Typeを表示
  console.log("ここから新しいリクエスト");
  console.log("パス: " + target);
  console.log("Content-Type: " + contentType);
  
   // 非同期処理でファイルを読み込む（エンコーディング指定）
   fs.readFile(target, {encoding: null}, (err, data) => {
    
     // エラー処理
     if (err) {
       res.writeHead(500, {"Content-Type": "text/plain"});
       res.write("500 Internal Server Error\n");
       res.end();
       return;
     }
     
     // Content-Typeとデータを送信（charset指定）
     res.writeHead(200, {'Content-Type': `${contentType}; charset=utf-8`});
     res.end(data);
   });
});

// サーバー起動
server.listen(8080);
console.log('Server start!');