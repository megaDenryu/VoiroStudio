# コメント
# PowerShellのコメントは「#」記号で始まります。

# 変数
$myVariable = "Hello, World!" # 文字列を変数に代入
Write-Host $myVariable # 変数の内容を表示

# 配列
$myArray = 1,2,3,4,5 # 配列の作成
Write-Host $myArray[0] # 配列の最初の要素を表示

# ハッシュテーブル（辞書）
$myHashTable = @{ "key1" = "value1"; "key2" = "value2" } # ハッシュテーブルの作成
Write-Host $myHashTable["key1"] # ハッシュテーブルの要素を表示

# 制御構造
if ($myVariable -eq "Hello, World!") { # if文
    Write-Host "The variable contains Hello, World!"
} else {
    Write-Host "The variable contains something else."
}

for ($i=0; $i -lt 5; $i++) { # forループ
    Write-Host $i
}

foreach ($element in $myArray) { # foreachループ
    Write-Host $element
}

# 関数
function SayHello($name) { # 関数の定義
    Write-Host "Hello, $name!"
}
SayHello("World") # 関数の呼び出し

# クラスの定義
class MyClass {
    # プロパティ
    [string]$MyProperty

    # コンストラクタ
    MyClass([string]$Property) {
        $this.MyProperty = $Property
    }

    # メソッド
    [string]SayHello() {
        return "Hello, " + $this.MyProperty
    }
}

# オブジェクトの作成
$myObject = [MyClass]::new("World")

# メソッドの呼び出し
Write-Host $myObject.SayHello()

