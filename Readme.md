# YouTrack Integration with Discord

This Python script polls YouTrack issues and sends new issue updates to a Discord channel via a webhook.

## Features
* Uses YouTrack's REST API with a permanent token
* Sends useful issue fields (Issue ID, Summary, Status, Description) to the Discord channel
* Sends notifications automatically to a Discord channel via webhook
* Configurable base URL, token, and Discord webhook
* Polls YouTrack every 60 seconds for new issues
* Can create issues from Discord

## Requirements
* Python 3.8+
* Python libraries
```bash
pip install requests discord.py
```

## Running the Script
1. Clone or download the script 
2. Run the script using the following: 
```bash
python youtrack_discord_notifier.py

```

## Configuration 
1. Create a webhook in your Discord server by going to **Server Settings → Integrations → Webhooks**
2. Then copy and paste the URL into the script under DISCORD_WEBHOOK_URL
3. Create discord bot token at: https://discord.com/developers/applications 
4. In discord developer portal create an invite link for your bot and invite it to your test discord server
5. Use !help after running for command info
6. if you want to test in production you have to set the DONT_SEND_FLAG to false to start sending POST requests to the server
7. By default, the script uses JetBrains’ public YouTrack as the BASE_URL. Replace this with your own YouTrack instance eg. https://youtrack.mycompany.com/api
8. Go to your YouTrack profile and generate a Permanent Token 
9. Then paste your token under PERMANENT_TOKEN where it says "<YOUR_JETBRAINS_PERMANENT_TOKEN>/678U6J "
10. By default, the script poll is set to 60 sec. You can increase or decrease this interval if needed




