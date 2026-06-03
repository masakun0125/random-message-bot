# Random-Message-Bot

登録したメッセージの中から、指定した時間にランダムなものを送信するbot。設定はSlashCommandでできます。

## 設定手順

### Botの招待
1. [Discord Developer Portal](https://discord.com/developers/home)にアクセスし、ログインをする。
2. 「New Application」をクリックして、適当な名前（例: TimerBot）などを入力して作成をする。
3. 左メニューの「Bot」を選択し、「Reset Token」をクリックして表示された文字列(BotToken）をコピーして手元にメモをする。メモを忘れるとめんどいことになるからしっかりとメモをしておこう!
4. 同じ「Bot」画面を少し下にスクロールして「MESSAGE CONTENT INTENT」をON(青色の状態)にして保存する。
5. 「インストール」を押して「インストールリンク」というところのリンクをコピーする。(コピーボタンはリンクの右にあります)
6. 左メニューの 「OAuth2」 ＞ 「URL Generator」 を押す。
6-1. 「SCOPES(スコープって書いてあるかも)」の欄にある`bot`と`applications.commands`にチェックを入れる。
6-2. 「BOT PERMISSIONS(Botの権限って書いてあるかも)」の欄にある`Send Messages`と`Embed Links`にチェックを入れる。
7. 一番下に生成された URLをコピーしてブラウザで開き、Botを自分のDiscordサーバーに招待する!

### これでBotの作成は完了!
