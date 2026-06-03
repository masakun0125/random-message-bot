import json
import os
import random
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import app_commands
from discord.ext import commands

TOKEN = "YOUR_BOT_TOKEN_HERE"  
CHANNEL_ID = 123456789012345678 
DATA_FILE = "bot_config.json"  

DEFAULT_DATA = {"time": "08:00", "messages": ["初期メッセージ1", "初期メッセージ2"]}


def load_data():
    """設定ファイルを読み込む"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_DATA.copy()


def save_data(data):
    """設定ファイルを保存する"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class MyBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.scheduler = AsyncIOScheduler(timezone="Asia/Tokyo")

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}")
        self.update_schedule()
        if not self.scheduler.running:
            self.scheduler.start()

    def update_schedule(self):
        """スケジュールを更新する（時間変更時に呼び出す）"""
        self.scheduler.remove_all_jobs()

        data = load_data()
        time_str = data["time"]
        hour, minute = map(int, time_str.split(":"))

        self.scheduler.add_job(
            self.send_random_message, "cron", hour=hour, minute=minute
        )
        print(f"スケジュールを {time_str} に設定しました。")

    async def send_random_message(self):
        """指定時間にランダムメッセージを送信"""
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("エラー: チャンネルが見つかりません。")
            return

        data = load_data()
        messages = data.get("messages", [])

        if messages:
            chosen = random.choice(messages)
            await channel.send(chosen)
        else:
            await channel.send("【警告】送信するメッセージが登録されていません。")


bot = MyBot()

@bot.tree.command(name="list", description="登録されているメッセージと送信時間の一覧を表示します")
async def list_messages(interaction: discord.Interaction):
    data = load_data()
    msg_list = "\n".join(
        [f"{i+1}: {m}" for i, m in enumerate(data["messages"])]
    )

    embed = discord.Embed(title="Bot設定状況", color=discord.Color.blue())
    embed.add_field(name="現在の送信時間", value=data["time"], inline=False)
    embed.add_field(
        name="登録メッセージ一覧",
        value=msg_list if msg_list else "登録なし",
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="add", description="メッセージを新しく登録します")
@app_commands.describe(text="追加したいメッセージ")
async def add_message(interaction: discord.Interaction, text: str):
    data = load_data()
    data["messages"].append(text)
    save_data(data)
    await interaction.response.send_message(
        f"追加しました: `{text}`", ephemeral=True
    )


@bot.tree.command(name="delete", description="指定した番号のメッセージを削除します")
@app_commands.describe(number="削除したいメッセージの番号（/listで確認してください）")
async def delete_message(interaction: discord.Interaction, number: int):
    data = load_data()
    messages = data["messages"]

    if 1 <= number <= len(messages):
        removed = messages.pop(number - 1)
        save_data(data)
        await interaction.response.send_message(
            f"削除しました: `{removed}`", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "無効な番号です。/list で番号を確認してください。", ephemeral=True
        )


@bot.tree.command(name="set_time", description="送信時間を変更します")
@app_commands.describe(time="送信時間（例: 08:30, 21:00）")
async def set_time(interaction: discord.Interaction, time: str):
    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await interaction.response.send_message(
            "時間の形式が正しくありません。`HH:MM` (例 08:00 や 23:15) で入力してください。",
            ephemeral=True,
        )
        return

    data = load_data()
    data["time"] = f"{hour:02d}:{minute:02d}"
    save_data(data)

    bot.update_schedule()

    await interaction.response.send_message(
        f"送信時間を `{data['time']}` に変更しました。", ephemeral=True
    )


if __name__ == "__main__":
    bot.run(TOKEN)
