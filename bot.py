import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta

# === Environment Variables ===
TOKEN = os.environ['DISCORD_TOKEN']
TARGET_CHANNEL_ID = int(os.environ['TARGET_CHANNEL_ID'])
TARGET_WEBHOOK_ID = os.environ['TARGET_WEBHOOK_ID']
DELETE_THRESHOLD_MIN = int(os.getenv('DELETE_THRESHOLD_MIN', 45))
GUILD_ID = int(os.environ.get('DISCORD_GUILD_ID', 0))  # Optional for faster sync

# === Intents ===
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Slash Command for Badge
@bot.tree.command(name="musta", description="Ping pong test command.")
async def musta(interaction: discord.Interaction):
    await interaction.response.send_message("Goods ra ang bot!", ephemeral=True)

# === Message Deletion Logic ===
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

# 🕒 Auto shutdown after X minutes
async def auto_shutdown(minutes: int):
    await asyncio.sleep(minutes * 60)
    print(f"⏳ {minutes} minutes passed. Shutting down bot.")
    await bot.close()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    try:
        if not hasattr(bot, 'synced'):
            if GUILD_ID:
                guild = discord.Object(id=GUILD_ID)
                bot.tree.copy_global_to(guild=guild)
                synced = await bot.tree.sync(guild=guild)
            else:
                synced = await bot.tree.sync()
            print(f"🔁 Synced {len(synced)} slash command(s).")
            bot.synced = True
    except Exception as e:
        print(f"⚠️ Error syncing commands: {e}")

    # Run background tasks
    bot.loop.create_task(delete_old_messages())
    bot.loop.create_task(auto_shutdown(minutes=55))  # ⏱ Adjust if needed

# === Run Bot ===
bot.run(TOKEN)
