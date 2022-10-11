# imports
import configparser
import platform
import time

import nextcord
import redis
from nextcord import Interaction
from nextcord.ext import commands

# load config & language
config = configparser.ConfigParser()
config.read('config.ini')
lang = configparser.ConfigParser()
lang.read('language.ini')

token = config['CREDENTIALS']['token']
owner_id = str(config['CREDENTIALS']['owner_id'])
prefix = config['SETTINGS']['prefix']
status = config['SETTINGS']['status']
status_message = config['SETTINGS']['status_message']
status_type = config['SETTINGS']['status_type']
host = config['REDIS']['host']
port = config['REDIS']['port']
password = config['REDIS']['password']
db = config['REDIS']['db']

# check config
error_count = 0

if len(prefix) > 1:
    print('Error: Prefix must be only one character.')
    error_count += 1

if status not in ['online', 'idle', 'dnd', 'invisible']:
    print('Error: Status must be one of online, idle, dnd, or invisible.')
    error_count += 1

if status_type not in ['playing', 'streaming', 'listening', 'watching']:
    print('Error: Status type must be one of playing, streaming, listening, or watching.')
    error_count += 1

if len(status_message) > 128:
    print('Error: Status message must be less than 128 characters.')
    error_count += 1

if error_count > 0:
    print('Please change the config file (config.ini) and try again.')
    print('Exiting in 5 seconds...')
    time.sleep(5)
    exit()

# check redis connection
try:
    print(f'Connecting to Redis... ({host}:{port} Database: {db})')
    r = redis.Redis(host=host, port=port, password=password, decode_responses=True, db=db)
    r.ping()
    print(f"Connected to redis.")
except:
    print('Error: Could not connect to Redis server.')
    print('Please change the config file (config.ini) and try again.')
    print('Exiting in 5 seconds...')
    time.sleep(5)
    exit()

# discord setup
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix=prefix, intents=intents)


# Bot startup
@client.event
async def on_ready():
    # set status
    if status_type == 'playing':
        await client.change_presence(activity=nextcord.Game(name=status_message), status=status)
    elif status_type == 'streaming':
        await client.change_presence(activity=nextcord.Streaming(name=status_message, url='https://twich.tv'),
                                     status=status)
    elif status_type == 'listening':
        await client.change_presence(
            activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=status_message), status=status)
    elif status_type == 'watching':
        await client.change_presence(
            activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status_message), status=status)
    # print startup message
    owner_name = await client.fetch_user(owner_id)
    print('======================================')
    print(f'Logged in as {client.user.name}#{client.user.discriminator} ({client.user.id})')
    print(f"Owner: {owner_name} ({owner_id})")
    print(f'Currenly running nextcord {nextcord.__version__} on python {platform.python_version()}')
    print('======================================')


# create command
@client.slash_command(name=lang['CREATE']['name'], description=lang['CREATE']['description'], dm_permission=False,
                      default_member_permissions=8)
async def create_intro(interaction: Interaction,
                       channel: nextcord.VoiceChannel = nextcord.SlashOption(
                           description=lang['CREATE']['argument_description'],
                           required=True,
                       ),
                       ):
    try:
        if r.exists(f"auto:{channel.guild.id}:{channel.id}"):
            embed = nextcord.Embed(title=lang['CREATE']['duplicate'],
                                   description=lang['CREATE']['duplicate_description'], color=nextcord.Color.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            r.set(f"auto:{channel.guild.id}:{channel.id}", channel.category.id)
            embed = nextcord.Embed(title=lang['CREATE']['success'],
                                   description=lang['CREATE']['success_description'].format(channel.mention),
                                   color=nextcord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    except:
        embed = nextcord.Embed(title=lang['CREATE']['error'], description=lang['CREATE']['error_description'],
                               color=nextcord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


# deactive command
@client.slash_command(name=lang['DELETE']['name'], description=lang['DELETE']['description'], dm_permission=False,
                      default_member_permissions=8)
async def delete_intro(interaction: Interaction,
                       channel: nextcord.VoiceChannel = nextcord.SlashOption(
                           description=lang['DELETE']['argument_description'],
                           required=True,
                       ),
                   ):
    try:
        if r.exists(f"auto:{channel.guild.id}:{channel.id}"):
            r.delete(f"auto:{channel.guild.id}:{channel.id}")
            embed = nextcord.Embed(title=lang['DELETE']['success'],
                                   description=lang['DELETE']['success_description'].format(channel.mention),
                                   color=nextcord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(title=lang['DELETE']['not_found'],
                                   description=lang['DELETE']['not_found_description'], color=nextcord.Color.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        embed = nextcord.Embed(title=lang['DELETE']['error'], description=lang['DELETE']['error_description'],
                               color=nextcord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


# list command
@client.slash_command(name=lang['LIST']['name'], description=lang['LIST']['description'], dm_permission=False)
async def list_intro(interaction: Interaction):
    try:
        keys = r.keys(f"auto:{interaction.guild.id}:*")
        temp_keys = r.keys(f"temp:{interaction.guild.id}:*")
        if len(keys) + len(temp_keys) == 0:
            embed = nextcord.Embed(title=lang['LIST']['empty'],
                                   description=lang['LIST']['empty_description'].format(interaction.guild.name),
                                   color=nextcord.Color.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:

            embed = nextcord.Embed(title=lang['LIST']['embed_title'],
                                   description=lang['LIST']['embed_description'].format(len(keys), interaction.guild.name),
                                   color=nextcord.Color.green())

            del_count = 0
            final_list = []
            hub_list = []

            for num, key in enumerate(keys):
                try:
                    final_list.append(f"\n\n`{num + 1}.`  <#{int(key.split(':')[2])}>")
                    hub_list.append(int(key.split(":")[2]))
                except:
                    r.delete(key)
                    del_count += 1
            for key in temp_keys:
                try:
                    ch = r.get(key)
                    if int(ch) in hub_list:
                        #find the index of the channel in the hub_list
                        index = hub_list.index(int(ch))
                        final_list.insert(index + 1, f"\n` └`  <#{key.split(':')[2]}>")
                        hub_list.insert(index + 1, int(ch))
                except:
                    r.delete(key)
                    del_count += 1
            value = ""
            for i in range(len(final_list)):
                value = value + final_list[i]

            embed.add_field(name=lang['LIST']['embed_field_name'], value=value, inline=False)

            if del_count > 0:
                embed.set_footer(text=lang['LIST']['embed_footer'].format(del_count))
            await interaction.response.send_message(embed=embed, ephemeral=True)

    except:
        embed = nextcord.Embed(title=lang['LIST']['error'], description=lang['LIST']['error_description'],color=nextcord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

# clear command
@client.slash_command(name=lang['CLEAR']['name'], description=lang['CLEAR']['description'], dm_permission=False, default_member_permissions=8)
async def clear(interaction: Interaction):
    keys = r.keys(f"temp:{interaction.guild.id}:*")
    if len(keys) == 0:
        embed = nextcord.Embed(title=lang['CLEAR']['empty'],
                               description=lang['CLEAR']['empty_description'].format(interaction.guild.name),
                               color=nextcord.Color.yellow())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = nextcord.Embed(title=lang['CLEAR']['loading'],
                               description=lang['CLEAR']['loading_description'].format(len(keys), len(keys)),
                               color=nextcord.Color.blue())
        output = await interaction.response.send_message(embed=embed, ephemeral=True)
        error_count = 0
        for key in keys:
            r.delete(key)
            try:
                channel = client.get_channel(int(key.split(':')[2]))
                await channel.delete()
            except:
                error_count += 1
        if error_count == 0:
            embed = nextcord.Embed(title=lang['CLEAR']['success'],
                                   description=lang['CLEAR']['success_description'].format(len(keys)),
                                   color=nextcord.Color.green())
        elif error_count == len(keys):
            embed = nextcord.Embed(title=lang['CLEAR']['failure'],
                                   description=lang['CLEAR']['failure_description'].format(len(keys)),
                                   color=nextcord.Color.red())
            embed = nextcord.Embed(title=lang['CLEAR']['partial'],
                                   description=lang['CLEAR']['partial_description'].format(len(keys), error_count),
                                   color=nextcord.Color.yellow())
        await output.edit(embed=embed)

@client.slash_command(name=lang['HELP']['name'], description=lang['HELP']['description'], dm_permission=True)
async def help(interaction: Interaction,
                arg: str = nextcord.SlashOption(
                    name=lang['HELP']['argument'],
                    description=lang['HELP']['argument_description'],
                    required=False,
                    choices=[lang['CREATE']['name'], lang['DELETE']['name'], lang['LIST']['name'], lang['CLEAR']['name'], lang['HELP']['name'], lang['INVITE']['name'], lang['PING']['name']])
                ):
    if arg == None:
        embed = nextcord.Embed(title=lang['HELP']['embed_title'], description=lang['HELP']['embed_description'],
                               color=nextcord.Color.green())
        embed.add_field(name=f"**· /{lang['CREATE']['name']} `{lang['HELP']['voice_channel']}`**", value=lang['CREATE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['DELETE']['name']} `{lang['HELP']['voice_channel']}`**", value=lang['DELETE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['LIST']['name']}**", value=lang['LIST']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['CLEAR']['name']}**", value=lang['CLEAR']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['INVITE']['name']}**", value=lang['INVITE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['PING']['name']}**", value=lang['PING']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['HELP']['name']} `{lang['HELP']['command']}` ({lang['HELP']['optional']})**", value=lang['HELP']['description'], inline=False)
        embed.set_footer(text=lang['HELP']['footer'].format(f"/{lang['HELP']['name']} <{lang['HELP']['command']}>"))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if arg == lang['CREATE']['name']:
            embed = nextcord.Embed(title=f"{lang['CREATE']['name']}", description=lang['CREATE']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['CREATE']['name']} `{lang['HELP']['voice_channel']}`", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`", inline=False)
        elif arg == lang['DELETE']['name']:
            embed = nextcord.Embed(title=f"{lang['DELETE']['name']}", description=lang['DELETE']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['DELETE']['name']} `{lang['HELP']['voice_channel']}`", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`", inline=False)
        elif arg == lang['LIST']['name']:
            embed = nextcord.Embed(title=f"{lang['LIST']['name']}", description=lang['LIST']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['LIST']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['CLEAR']['name']:
            embed = nextcord.Embed(title=f"{lang['CLEAR']['name']}", description=lang['CLEAR']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['CLEAR']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`", inline=False)
        elif arg == lang['HELP']['name']:
            embed = nextcord.Embed(title=f"{lang['HELP']['name']}", description=lang['HELP']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['HELP']['name']} `{lang['HELP']['command']}` ({lang['HELP']['optional']})", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['INVITE']['name']:
            embed = nextcord.Embed(title=f"{lang['INVITE']['name']}", description=lang['INVITE']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['INVITE']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['PING']['name']:
            embed = nextcord.Embed(title=f"{lang['PING']['name']}", description=lang['PING']['description'], color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['PING']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.slash_command(name=lang['PING']['name'], description=lang['PING']['description'], dm_permission=True)
async def ping(interaction: Interaction):
    embed = nextcord.Embed(title=lang['PING']['embed_title'], description=lang['PING']['embed_description'].format(round(client.latency * 1000)), color=nextcord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.slash_command(name=lang['INVITE']['name'], description=lang['INVITE']['description'], dm_permission=True)
async def invite(interaction: Interaction):
    embed = nextcord.Embed(title=lang['INVITE']['embed_title'], description=lang['INVITE']['embed_description'], color=nextcord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


# on user joining/leaving voice channel
@client.event
async def on_voice_state_update(member, before, after):
    # if user leaves a voice channel
    if before.channel != None:
        if r.get(f"temp:{before.channel.guild.id}:{before.channel.id}") != None:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                r.delete(f"temp:{before.channel.guild.id}:{before.channel.id}")

    # if user joins / transfers to a voice channel
    if after.channel != None:
        if r.get(f"auto:{after.channel.guild.id}:{after.channel.id}") != None:
            category = after.channel.category
            overwrites = {member: nextcord.PermissionOverwrite(manage_channels=True)}
            new_channel = await after.channel.guild.create_voice_channel(name=member.display_name, category=category, overwrites=overwrites)
            await member.move_to(new_channel)
            r.set(f"temp:{after.channel.guild.id}:{new_channel.id}", after.channel.id)

#when voice channel is deleted
@client.event
async def on_guild_channel_delete(channel):
    if r.get(f"auto:{channel.guild.id}:{channel.id}") != None:
        r.delete(f"auto:{channel.guild.id}:{channel.id}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.content.startswith(".l"):
        embed = nextcord.Embed(title="담화 도령 봇을 소개합니다!", description="담화 도령은 유저들이 필요할 때 **자신만의 음성 채널**을 만들 수 있게 해주는 봇 입니다! 기존 자동 음성 봇과 다른 **차세데 데이타 베이스**를 적용하여 빠른 속도와 안정성을 선사합니다! 또한, 봇에 대한 신뢰성을 위해 모든 코드를 자신있게 **오픈소스**로 공개하였습니다! 한번 <#978993126653952080> 음성 채널을 확인해 보세요!", color=nextcord.Color.green())
        embed.set_image(url="https://archive.cysub.net/bot.gif")
        embed.add_field(name="**초대**", value="`/초대` 명령어를 사용하거나 [여기](https://discord.com/api/oauth2/authorize?client_id=1024514599216746496&&permissions=17902608&scope=bot%20applications.commands)를 클릭하여 초대해 주세요!", inline=False)
        embed.add_field(name="**도움말**", value="`/도움말` 명령어를 사용하거나 [여기](https://github.com/HongWonYul/auto-voice-channel#commands)를 클릭하여 확인하세요!", inline=False)
        embed.add_field(name="**소스코드**", value="[여기서](https://github.com/HongWonYul/auto-voice-channel) 확인하세요!", inline=False)

        await message.channel.send(embed=embed)

client.run(token)

