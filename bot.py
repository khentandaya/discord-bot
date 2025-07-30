import os
import asyncio
import discord
from datetime import datetime, timedelta, timezone

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
TARGET_WEBHOOK_ID = int(os.getenv('TARGET_WEBHOOK_ID'))
DELETE_THRESHOLD_MIN = int(os.getenv('DELETE_THRESHOLD_MIN', 30))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def run_cleanup():
    print("Starting cleanup...")
    channel = await client.fetch_channel(TARGET_CHANNEL_ID)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=DELETE_THRESHOLD_MIN)

    deleted_count = 0
    async for message in channel.history(limit=50, before=now):  # You can adjust limit if needed
        if message.author.id == TARGET_WEBHOOK_ID and message.created_at < cutoff:
            try:
                await message.delete()
                deleted_count += 1
                if deleted_count % 5 == 0:
                    await asyncio.sleep(1)  # Throttle every 5 deletions
            except Exception as e:
                print(f"Error deleting message: {e}")

    print(f"Cleanup complete. Deleted {deleted_count} messages.")

@client.event
async def on_ready():
    print("Bot logged in.")
    try:
        await asyncio.wait_for(run_cleanup(), timeout=120)  # 2-minute timeout
    except asyncio.TimeoutError:
        print("Cleanup task timed out.")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
