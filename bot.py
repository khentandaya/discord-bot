import os
import discord
import asyncio
from datetime import datetime, timezone, timedelta

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
TARGET_CHANNEL_ID = int(os.environ['TARGET_CHANNEL_ID'])
TARGET_WEBHOOK_ID = int(os.environ['TARGET_WEBHOOK_ID'])
DELETE_THRESHOLD_MIN = int(os.environ.get('DELETE_THRESHOLD_MIN', 30))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    try:
        channel = await client.fetch_channel(TARGET_CHANNEL_ID)
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=DELETE_THRESHOLD_MIN)

        deleted_count = 0
        async for message in channel.history(limit=100, before=now):
            if (
                message.author.id == TARGET_WEBHOOK_ID and
                message.created_at < cutoff
            ):
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(1)  # avoid rate limits
                except discord.Forbidden:
                    print(f"Missing permissions to delete message ID {message.id}")
                except discord.HTTPException as e:
                    print(f"Failed to delete message ID {message.id}: {e}")

        print(f"Deleted {deleted_count} old messages from webhook ID {TARGET_WEBHOOK_ID}")
    except Exception as e:
        print(f"Error during deletion: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
