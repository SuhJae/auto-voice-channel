# discord_auto_voice_channel
![](https://img.shields.io/pypi/pyversions/nextcord?style=flat-square)
![](https://img.shields.io/github/release-date-pre/HongWonYul/discord_auto_voice_channel?style=flat-square)
![](https://img.shields.io/github/downloads/HongWonYul/discord_auto_voice_channel/total?style=flat-square)
![](https://img.shields.io/github/license/hongwonyul/discord_auto_voice_channel?style=flat-square)

This project is in development, but it is still usable.

This is a Discord bot that will allow users to create auto voice channels, so when the user joins the auto voice channel, the bot will automatically generate a voice channel for them.
This project uses Redis to store data, so it is swift and fully scalable using shards in the future.

## Requirments
Redis server

Python packages: Redis, nextcord

## Setup
1. Go to https://discord.com/developers/applications and create an application.
2. Press the bot on the left menu and the "activate bot" button.
3. Navigate the "Privileged Gateway Intents" section in the bot menu and check all intents.
4. Press the "reset token" button at the top and save the token for later.
5. Install the Redis server or get hosting for it. Check https://redis.io/docs/getting-started/ for more info.
5. Copy this repository.
6. Open config.ini and replace "YOUR_TOKEN_HERE" with the discord bot token you got in step 4.
7. Replace "YOUR_ID_HERE" with discord ID (Not tag)
8. If you just installed the Redis client on your computer and did not make any changes, delete "YOUR_PASSWORD_HERE."
9. You must edit the host, port, and password accordingly if using an external Redis server.
10. Change the bot's state message by editing config under SETTINGS.
11. You can customize all messages and the command's name by editing the language.ino
12. Run main.py
13. Invite your bot and enjoy!

## Commands

/create `channel` - Sets channel as an automatic voice channel.

/delete `channel` - Deactivates auto voice channel, so it no longer makes a channel when a user joins.

/list - View all acvive automatic voice channel.

/clear - Delets all channels created by the bot. (In case of the bot going offline for a bit)
