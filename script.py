import requests
import time
import datetime
import discord
import asyncio
import threading

# YouTrack setup
DISCORD_TOKEN = "<YOUR_DISCORD_BOT_TOKEN>"  # Replace with your bot token
CHANNEL_ID = 1422317316128903200  # Replace with your channel ID
BASE_URL = "https://youtrack.jetbrains.com/api"
PERMANENT_TOKEN = "<YOUR_JETBRAINS_PERMANENT_TOKEN>"  # Replace with your YouTrack token
HEADERS = {"Authorization": f"Bearer {PERMANENT_TOKEN}", "Accept": "application/json", "content-type": "application/json"}
DONT_SEND_FLAG = True
INTERVAL = 60
# Discord webhook
DISCORD_WEBHOOK_URL = "<YOUR_DISCORD_WEBHOOK_URL>"  # Replace with your Discord webhook URL
# discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)


def create_issue(summary: str) -> dict:
    data = {
        "title": "issue from Discord",
        "summary": summary,
        "description": "Created via Discord bot",
        "project": {"id": "0-0"},  # Adjust project ID as needed

    }
    if DONT_SEND_FLAG:
        print("DONT_SEND_FLAG is set, not creating issue.")
        print(f"Would create issue with summary: {summary}")
        return {"idReadable": "DONT_SEND"}

    resp = requests.post(f"{BASE_URL}/issues", headers=HEADERS, json=data)
    resp.raise_for_status()  # Raise an error for bad responses
    return resp.json()


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (id: {client.user.id})")
    print("Ready.")


@client.event
async def on_message(message: discord.Message):
    # Ignore our own messages
    print(f"Received message: {message.content} from {message.author} from channel {message.channel.id}")
    if message.author.id == client.user.id:
        return

    # Only act in the specific channel
    if message.channel.id != CHANNEL_ID:
        return
    msg = message.content.strip()
    if msg.startswith("!create "):
        summary = msg[len("!create "):].strip()
        if summary:
            issue = create_issue(summary)
            await message.channel.send(f"Issue created: {issue['idReadable']}")
        else:
            await message.channel.send("Please provide a summary for the issue.")
    elif msg == "!help":
        help_msg = ("Commands:\n"
                    "!create <summary> - Create a new issue with the given summary.\n"
                    "!help - Show this help message.")
        await message.channel.send(help_msg)


def run_bot():
    async def runner():
        try:
            await client.start(DISCORD_TOKEN)
        finally:
            await client.close()

    asyncio.run(runner())


# Start bot in a background thread
t = threading.Thread(target=run_bot, name="discord-bot", daemon=True)
t.start()
last_check = datetime.datetime.now(datetime.UTC)


def send_discord(msg):
    data = {
        "content": msg
    }
    requests.post(DISCORD_WEBHOOK_URL, json=data)


try:
    while True:
        # Format timestamp for YouTrack query
        since = last_check.strftime("%Y-%m-%dT%H:%M:%SZ")
        params: dict = {
            "fields": "idReadable,summary,description,fields(name,value(name)),created"
        }

        resp = requests.get(f"{BASE_URL}/issues", headers=HEADERS, params=params)
        resp.raise_for_status()
        issues = resp.json()
        print(f"checking {len(issues)} issues since {since}")
        for issue in issues:
            # Get the status from custom fields
            if int(issue["created"]) < last_check.timestamp() * 1000:
                continue
            print(f"checking {issue['id']}")
            status = next(
                (f['value']['name'] for f in issue.get('fields', []) if f['name'] == 'State'),
                'Unknown'
            )
            # Compose a Discord-friendly message
            msg = f"**[{issue['idReadable']}] {issue['summary']}**\nStatus: {status}\n{issue.get('description', '')}"
            send_discord(msg)

        last_check = datetime.datetime.now(datetime.UTC)
        time.sleep(INTERVAL)  # poll every 60 seconds
except KeyboardInterrupt:
    print("Shutting down...")
    client.loop.call_soon_threadsafe(client.loop.stop)
    t.join()
finally:
    print("Exited.")