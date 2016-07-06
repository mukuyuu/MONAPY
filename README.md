# MONAPY
monachat client with python
## MONAPYについて
+ もなちゃと用クライアントです
+ 使用言語：python3.5
+ 予定：早くちゃんとしたクライアントにしたい。いずれbotを組み込むはず…。
+ 注意：例外処理をちゃんとしてないので、コマンドを正しく打ち込まなかったりすると止まる可能性があります。また正しく捜査してもバグがある可能性があります。

## 使用方法
+ python3.5をインストール
+ monapy.pyを実行
+ 一番下にあるエントリーボックスにコマンドを打ち込んでください

## コマンド
+ /login  
 もなちゃとに接続します(入口に入る)
+ /room ルーム番号  
 ルーム番号に入ります
 * /room  
  入口に入ります  
+ /quit  
 終了します  
+ /config
 config.jsonの中身をコンソールに表示
 * /config save:hoge  
  hogeという名前で今の状態を記録します  
 * /config load:hoge  
  hogeという名前の設定に変更します
+ /set x:18 y:250 scl:100 r:100 name:hogehoge etc..  
 場所などの設定変更
+ /wclose roominfo(or netlog or datalog)  
 ウィンドウを閉じる
+ /wopen roominfo(or netlog or datalog)
 ウィンドウを開く

不具合あり：/wclose,/wopen
その他使わなくていいコマンド、/connect,/exit,/enter

## 表示
+ menu bar  
 そのうち機能が追加されるはず
+ chat log  
 チャット内容を表示します  
+ network log  
 受信内容をそのまま表示します  
+ room info  
 部屋の名前と人数、部屋にいるユーザー情報を表示します  
+ entry box  
 ここにいろいろ打ち込んでください  
