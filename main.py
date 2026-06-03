import os
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import app_commands
from discord.ext import commands
from supabase import create_client, Client

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_time():
    response = supabase.table("bot_config").select("target_time").eq("id", "default").execute()
    if response.data:
        return response.data[0]["target_time"]
    return "08:00"

def save_time(time_str):
    supabase.table("bot_config").update({"target_time": time_str}).eq("id", "default").execute()

def load_messages():
    response = supabase.table("bot_messages").select("id", "message_text").execute()
    return response.data

def add_message_to_db(text):
    supabase.table("bot_messages").insert({"message_text": text}).execute()

def delete_message_from_db(msg_id):
    supabase.table("bot_messages").delete().eq("id", msg_id).execute()

class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

def run_web_server():
    server = HTTPServer(("0.0.0.0", 8080), WebServer)
    server.serve_forever()

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
        self.scheduler.remove_all_jobs()
        time_str = load_time()
        hour, minute = map(int, time_str.split(":"))
        self.scheduler.add_job(
            self.send_random_message, "cron", hour=hour, minute=minute
        )

    async def send_random_message(self):
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            return
        messages = load_messages()
        if messages:
            chosen = random.choice(messages)
            await channel.send(chosen["message_text"])
        else:
            await channel.send("【警告】送信するメッセージが登録されていません。")

bot = MyBot()

@bot.tree.command(name="list", description="登録されているメッセージと送信時間の一覧を表示します")
async def list_messages(interaction: discord.Interaction):
    current_time = load_time()
    messages = load_messages()
    msg_list = "\n".join([f"ID {m['id']}: {m['message_text']}" for m in messages])
    
    embed = discord.Embed(title="Bot設定状況", color=discord.Color.blue())
    embed.add_field(name="現在の送信時間", value=current_time, inline=False)
    embed.add_field(name="登録メッセージ一覧", value=msg_list if msg_list else "登録なし", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add", description="メッセージを新しく登録します")
@app_commands.describe(text="追加したいメッセージ")
async def add_message(interaction: discord.Interaction, text: str):
    add_message_to_db(text)
    await interaction.response.send_message(f"追加しました: `{text}`", ephemeral=True)

@bot.tree.command(name="delete", description="指定したIDのメッセージを削除します")
@app_commands.describe(number="削除したいメッセージのID（/listで確認してください）")
async def delete_message(interaction: discord.Interaction, number: int):
    messages = load_messages()
    valid_ids = [m["id"] for m in messages]
    
    if number in valid_ids:
        delete_message_from_db(number)
        await interaction.response.send_message(f"ID {number} のメッセージを削除しました。", ephemeral=True)
    else:
        await interaction.response.send_message("無効なIDです。/list で確認できるIDを指定してください。", ephemeral=True)

@bot.tree.command(name="set_time", description="送信時間を変更します")
@app_commands.describe(time="送信時間（例: 08:30, 21:00）")
async def set_time(interaction: discord.Interaction, time: str):
    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await interaction.response.send_message("時間の形式が正しくありません。`HH:MM` で入力してください。", ephemeral=True)
        return

    formatted_time = f"{hour:02d}:{minute:02d}"
    save_time(formatted_time)
    bot.update_schedule()
    await interaction.response.send_message(f"送信時間を `{formatted_time}` に変更しました。", ephemeral=True)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.run(TOKEN)
