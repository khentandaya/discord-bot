import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta

TOKEN = os.environ['DISCORD_TOKEN']
TARGET_CHANNEL_ID = int(os.environ['TARGET_CHANNEL_ID'])
TARGET_WEBHOOK_ID = os.environ['TARGET_WEBHOOK_ID']
DELETE_THRESHOLD_MIN = int(os.getenv('DELETE_THRESHOLD_MIN', 30))

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"⚠️ Error syncing commands: {e}")

    # Start deletion logic
    await delete_old_messages()

# ✅ Slash command for Active Developer Badge
@bot.tree.command(name="ping", description="Ping pong test command.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!", ephemeral=True)

async def delete_old_messages():
    await bot.wait_until_ready()
    channel = bot.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        print(f"❌ Channel {TARGET_CHANNEL_ID} not found.")
        return

    threshold_time = datetime.now(timezone.utc) - timedelta(minutes=DELETE_THRESHOLD_MIN)
    deleted_count = 0

    async for message in channel.history(limit=100):
        if str(message.author.id) == TARGET_WEBHOOK_ID:
            if message.created_at < threshold_time:
                try:
                    await message.delete()
                    deleted_count += 1
                except discord.errors.Forbidden:
                    print("⚠️ Missing permissions to delete message.")
                except discord.errors.HTTPException as e:
                    print(f"⚠️ Error deleting message: {e}")

    print(f"🧹 Deleted {deleted_count} old messages.")

bot.run(TOKEN)
