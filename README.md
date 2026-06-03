# Random-Message-Bot

登録したメッセージの中から、指定した時間にランダムなものを送信するbot。設定はSlashCommandでできます。

## 設定手順

### 1章.Botの作成とサーバーへの招待
1. [Discord Developer Portal](https://discord.com/developers/home)にアクセスして、ログインをする。
2. 「New Application」をクリックして、適当な名前（例: TimerBot）などを入力して作成をする。
3. 左メニューの「Bot」を選択し、「Reset Token」をクリックして表示された文字列(BotToken）をコピーして手元にメモをする。メモを忘れるとめんどいことになるからしっかりとメモをしておこう!
4. 同じ「Bot」画面を少し下にスクロールして「MESSAGE CONTENT INTENT」をON(青色の状態)にして保存する。
5. 「インストール」を押して「インストールリンク」というところのリンクをコピーする。(コピーボタンはリンクの右にあります)
6. 左メニューの 「OAuth2」 ＞ 「URL Generator」 を押す。
6-1. 「SCOPES(スコープって書いてあるかも)」の欄にある`bot`と`applications.commands`にチェックを入れる。
6-2. 「BOT PERMISSIONS(Botの権限って書いてあるかも)」の欄にある`Send Messages`と`Embed Links`にチェックを入れる。
7. 一番下に生成された URLをコピーしてブラウザで開き、Botを自分のDiscordサーバーに招待する!

### 2章.Botの稼働
・通常は Python と必要なライブラリのインストールが必要だが、今回は利用者がコンピュータを操作できないため、その手順は省略する。

### 3章.Botを24時間稼働させる方法
- VPS(ConoHaやAWSなど)や、レンタルサーバー(Renderなど)で常時起動させる。
**Renderは無料でソースコードを動かせるのでとてもおすすめです**

以上の説明を踏まえてBotを起動すると、あらかじめ登録したメッセージの中からランダムに1つ選択し、指定した時間に送信することができる。

