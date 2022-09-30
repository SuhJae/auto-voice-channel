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
        if len(keys) == 0:
            embed = nextcord.Embed(title=lang['LIST']['empty'],
                                   description=lang['LIST']['empty_description'].format(interaction.guild.name),
                                   color=nextcord.Color.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = nextcord.Embed(title=lang['LIST']['loading'],
                                   description=lang['LIST']['loading_description'].format(len(keys), interaction.guild.name,
                                                                                          len(keys)),
                                   color=nextcord.Color.blue())
            output = await interaction.response.send_message(embed=embed, ephemeral=True)

            embed = nextcord.Embed(title=lang['LIST']['embed_title'],
                                   description=lang['LIST']['embed_description'].format(len(keys), interaction.guild.name),
                                   color=nextcord.Color.green())
            value = ""

            for num, key in enumerate(keys):
                channel = await client.fetch_channel(int(key.split(":")[2]))
                value = f"{value}\n`{num + 1}`  {channel.mention}"

            embed.add_field(name=lang['LIST']['embed_field_name'], value=value, inline=False)
            await output.edit(embed=embed)

    except:
        embed = nextcord.Embed(title=lang['LIST']['error'], description=lang['LIST']['error_description'],color=nextcord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


# on user joining/leaving voice channel
@client.event
async def on_voice_state_update(member, before, after):
    if after.channel == None:
        if r.get(f"temp:{before.channel.guild.id}:{before.channel.id}") != None:
            if len(before.channel.members) == 0:
                await before.channel.delete()
                r.delete(f"temp:{before.channel.guild.id}:{before.channel.id}")
    else:
        if r.get(f"auto:{after.channel.guild.id}:{after.channel.id}") != None:
            category = after.channel.category
            new_channel = await after.channel.guild.create_voice_channel(name=member.display_name, category=category)
            await member.move_to(new_channel)
            r.set(f"temp:{after.channel.guild.id}:{new_channel.id}", member.id)


client.run(token)
