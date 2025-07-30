import os
import discord
import asyncio
from datetime import datetime, timedelta

TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_USER_ID = int(os.getenv("TARGET_USER_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    channel = client.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        print("❌ Channel not found.")
        await client.close()
        return

    deleted_count = 0
    now = datetime.utcnow()
    async for message in channel.history(limit=100):
        if (
            message.author.id == TARGET_USER_ID and
            message.created_at < now - timedelta(minutes=30)
        ):
            try:
                await message.delete()
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete message: {e}")

    print(f"✅ Deleted {deleted_count} messages older than 30 minutes.")
    await client.close()

client.run(TOKEN)
