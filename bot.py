import os
import asyncio
import discord
from datetime import datetime, timedelta

DISCORD_BOT_TOKEN = os.environ['DISCORD_TOKEN']
TARGET_CHANNEL_ID = int(os.environ['TARGET_CHANNEL_ID'])
TARGET_WEBHOOK_ID = os.environ['TARGET_WEBHOOK_ID']
DELETE_THRESHOLD_MIN = int(os.getenv('DELETE_THRESHOLD_MIN', 30))

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

    channel = client.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        print("❌ Channel not found.")
        await client.close()
        return

    delete_before = datetime.utcnow() - timedelta(minutes=DELETE_THRESHOLD_MIN)
    async for message in channel.history(limit=100):
        if (str(message.author.id) == TARGET_WEBHOOK_ID and
                message.created_at < delete_before):
            try:
                await message.delete()
                print(f"🗑️ Deleted message from {message.author} at {message.created_at}")
            except Exception as e:
                print(f"⚠️ Failed to delete message: {e}")

    await client.close()

asyncio.run(client.start(DISCORD_BOT_TOKEN))
