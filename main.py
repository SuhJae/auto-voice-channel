# imports
import configparser
import platform
import time

import nextcord
import redis
from nextcord import Interaction, Locale
from nextcord.ext import commands

# load config & language
config = configparser.ConfigParser()
config.read('config.ini')
fallback_lang = configparser.ConfigParser()
fallback_lang.read('language.ini')
english = configparser.ConfigParser()
english.read('language/en_us.ini')
korean = configparser.ConfigParser()
korean.read('language/ko_kr.ini')
chinese = configparser.ConfigParser()
chinese.read('language/zh_cn.ini')

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

TESTING_GUILD_ID = 1023440388352114749

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


def lang_check(locale):
    if locale == "en-US":
        return english
    elif locale == "ko":
        return korean
    elif locale == "zh-CN":
        return chinese
    else:
        return fallback_lang


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
@client.slash_command(name=fallback_lang['CREATE']['name'], description=fallback_lang['CREATE']['description'],
                      dm_permission=False,
                      default_member_permissions=8)
async def create_intro(interaction: Interaction,
                       channel: nextcord.VoiceChannel = nextcord.SlashOption(
                           description=fallback_lang['CREATE']['argument_description'],
                           required=True,
                       ),
                       ):
    lang = lang_check(interaction.locale)

    try:
        if r.exists(f"auto:{channel.guild.id}:{channel.id}"):
            embed = nextcord.Embed(title=fallback_lang['CREATE']['duplicate'],
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
@client.slash_command(name=fallback_lang['DELETE']['name'], description=fallback_lang['DELETE']['description'],
                      dm_permission=False,
                      default_member_permissions=8)
async def delete_intro(interaction: Interaction,
                       channel: nextcord.VoiceChannel = nextcord.SlashOption(
                           description=fallback_lang['DELETE']['argument_description'],
                           required=True,
                       ),
                       ):
    lang = lang_check(interaction.locale)
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
@client.slash_command(name=fallback_lang['LIST']['name'], description=fallback_lang['LIST']['description'],
                      dm_permission=False)
async def list_intro(interaction: Interaction):
    lang = lang_check(interaction.locale)
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
                                   description=lang['LIST']['embed_description'].format(len(keys),
                                                                                        interaction.guild.name),
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
                        # find the index of the channel in the hub_list
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
        embed = nextcord.Embed(title=lang['LIST']['error'], description=lang['LIST']['error_description'],
                               color=nextcord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


# clear command
@client.slash_command(name=fallback_lang['CLEAR']['name'], description=fallback_lang['CLEAR']['description'],
                      dm_permission=False, default_member_permissions=8)
async def clear(interaction: Interaction):
    lang = lang_check(interaction.locale)
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
        else:
            embed = nextcord.Embed(title=lang['CLEAR']['partial'],
                                   description=lang['CLEAR']['partial_description'].format(len(keys), error_count),
                                   color=nextcord.Color.yellow())
        await output.edit(embed=embed)


# help command
@client.slash_command(name=fallback_lang['HELP']['name'], description=fallback_lang['HELP']['description'],
                      dm_permission=True)
async def help(interaction: Interaction,
               arg: str = nextcord.SlashOption(
                   name=fallback_lang['HELP']['argument'],
                   description=fallback_lang['HELP']['argument_description'],
                   required=False,
                   choices=[fallback_lang['CREATE']['name'], fallback_lang['DELETE']['name'],
                            fallback_lang['LIST']['name'], fallback_lang['CLEAR']['name'],
                            fallback_lang['HELP']['name'], fallback_lang['INVITE']['name'],
                            fallback_lang['PING']['name'], fallback_lang['DASHBOARD']['name']]
               )):
    lang = lang_check(interaction.locale)
    if arg == None:
        embed = nextcord.Embed(title=lang['HELP']['embed_title'], description=lang['HELP']['embed_description'],
                               color=nextcord.Color.green())
        embed.add_field(name=f"**· /{lang['CREATE']['name']} `{lang['HELP']['voice_channel']}`**",
                        value=lang['CREATE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['DELETE']['name']} `{lang['HELP']['voice_channel']}`**",
                        value=lang['DELETE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['LIST']['name']}**", value=lang['LIST']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['CLEAR']['name']}**", value=lang['CLEAR']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['INVITE']['name']}**", value=lang['INVITE']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['PING']['name']}**", value=lang['PING']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['HELP']['name']} `{lang['HELP']['command']}` ({lang['HELP']['optional']})**",
                        value=lang['HELP']['description'], inline=False)
        embed.add_field(name=f"**· /{lang['DASHBOARD']['name']}**", value=lang['DASHBOARD']['description'],
                        inline=False)
        embed.set_footer(text=lang['HELP']['footer'].format(f"/{lang['HELP']['name']} <{lang['HELP']['command']}>"))
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if arg == lang['CREATE']['name']:
            embed = nextcord.Embed(title=f"{lang['CREATE']['name']}", description=lang['CREATE']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'],
                            value=f"/{lang['CREATE']['name']} `{lang['HELP']['voice_channel']}`", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`",
                            inline=False)
        elif arg == lang['DELETE']['name']:
            embed = nextcord.Embed(title=f"{lang['DELETE']['name']}", description=lang['DELETE']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'],
                            value=f"/{lang['DELETE']['name']} `{lang['HELP']['voice_channel']}`", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`",
                            inline=False)
        elif arg == lang['LIST']['name']:
            embed = nextcord.Embed(title=f"{lang['LIST']['name']}", description=lang['LIST']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['LIST']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['CLEAR']['name']:
            embed = nextcord.Embed(title=f"{lang['CLEAR']['name']}", description=lang['CLEAR']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['CLEAR']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`",
                            inline=False)
        elif arg == lang['HELP']['name']:
            embed = nextcord.Embed(title=f"{lang['HELP']['name']}", description=lang['HELP']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'],
                            value=f"/{lang['HELP']['name']} `{lang['HELP']['command']}` ({lang['HELP']['optional']})",
                            inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['INVITE']['name']:
            embed = nextcord.Embed(title=f"{lang['INVITE']['name']}", description=lang['INVITE']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['INVITE']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['PING']['name']:
            embed = nextcord.Embed(title=f"{lang['PING']['name']}", description=lang['PING']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['PING']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_none']}`", inline=False)
        elif arg == lang['DASHBOARD']['name']:
            embed = nextcord.Embed(title=f"{lang['DASHBOARD']['name']}", description=lang['DASHBOARD']['description'],
                                   color=nextcord.Color.green())
            embed.add_field(name=lang['HELP']['usage'], value=f"/{lang['DASHBOARD']['name']}", inline=False)
            embed.add_field(name=lang['HELP']['permission'], value=f"`{lang['HELP']['permission_administrator']}`",
                            inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


# ping command
@client.slash_command(name=fallback_lang['PING']['name'], description=fallback_lang['PING']['description'],
                      dm_permission=True, guild_ids=[TESTING_GUILD_ID])
async def ping(interaction: Interaction):
    templang = lang_check(interaction.locale)
    embed = nextcord.Embed(title=templang['PING']['embed_title'],
                           description=templang['PING']['embed_description'].format(round(client.latency * 1000)),
                           color=nextcord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


# invite command
@client.slash_command(name=fallback_lang['INVITE']['name'], description=fallback_lang['INVITE']['description'],
                      dm_permission=True)
async def invite(interaction: Interaction):
    lang = lang_check(interaction.locale)
    embed = nextcord.Embed(title=lang['INVITE']['embed_title'], description=lang['INVITE']['embed_description'],
                           color=nextcord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


# dashboard command
@client.slash_command(name=fallback_lang['DASHBOARD']['name'], description=fallback_lang['DASHBOARD']['description'],
                      dm_permission=False, default_member_permissions=8)
async def settings(interaction: Interaction):
    lang = lang_check(interaction.locale)
    keys = r.keys(f"auto:{interaction.guild.id}:*")
    temp_keys = r.keys(f"temp:{interaction.guild.id}:*")
    embed = nextcord.Embed(title=lang['DASHBOARD']['embed_title'].format(interaction.guild.name),
                           description=lang['DASHBOARD']['embed_description'], color=nextcord.Color.green())

    # Gets all the voice channels and adds them to the embed field
    final = ''
    if len(keys) > 0:
        for key in keys:
            final += f"\n<#{int(key.split(':')[2])}>"
    else:
        final = lang['DASHBOARD']['none']

    embed.add_field(name=lang['DASHBOARD']['auto_channel'].format(len(keys)), value=final, inline=True)

    # Gets all the temp voice channels and adds them to the embed field
    final = ''
    if len(temp_keys) > 0:
        for key in temp_keys:
            final += f"\n<#{int(key.split(':')[2])}>"
    else:
        final = lang['DASHBOARD']['none']
    embed.add_field(name=lang['DASHBOARD']['temp_channel'].format(len(temp_keys)), value=final, inline=True)

    selections = [
        nextcord.SelectOption(label=lang['DASHBOARD']['selection_add'], value='add', emoji='➕'),
        nextcord.SelectOption(label=lang['DASHBOARD']['selection_remove'], value='remove', emoji='➖'),
        nextcord.SelectOption(label=lang['DASHBOARD']['selection_clear'], value='clear', emoji='🧹'),
        nextcord.SelectOption(label=lang['DASHBOARD']['selection_list'], value='list', emoji='📜'),
    ]
    view = DropdownMenu(selections)
    await interaction.response.send_message(embed=embed, ephemeral=True, view=view)


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
            new_channel = await after.channel.guild.create_voice_channel(name=member.display_name, category=category,
                                                                         overwrites=overwrites)
            r.set(f"temp:{after.channel.guild.id}:{new_channel.id}", after.channel.id)
            await member.move_to(new_channel)


# when voice channel is deleted
@client.event
async def on_guild_channel_delete(channel):
    if r.get(f"auto:{channel.guild.id}:{channel.id}") != None:
        r.delete(f"auto:{channel.guild.id}:{channel.id}")


# Class to handle the dropdown
class Dropdown(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder=fallback_lang['DROPDOWN']['placeholder'], options=options)

    async def callback(self, interaction: Interaction):
        lang = lang_check(interaction.locale)
        if self.values[0] == 'clear':
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
                else:
                    embed = nextcord.Embed(title=lang['CLEAR']['partial'],
                                           description=lang['CLEAR']['partial_description'].format(len(keys),
                                                                                                   error_count),
                                           color=nextcord.Color.yellow())
                await output.edit(embed=embed)

        elif self.values[0] == 'add':
            selections = []
            # get all the voice channels in the server
            for channel in interaction.guild.voice_channels:
                # check if the channel is already added
                if r.get(f"auto:{interaction.guild.id}:{channel.id}") == None:
                    selections.append(nextcord.SelectOption(label=channel.name, emoji='🔊', description=channel.id,
                                                            value=f'addvoice:{channel.id}'))
            if len(selections) == 0:
                embed = nextcord.Embed(title=lang['DROPDOWN']['add_empty'],
                                       description=lang['DROPDOWN']['add_empty_description'].format(
                                           interaction.guild.name),
                                       color=nextcord.Color.yellow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                view = DropdownMenu(selections)
                embed = nextcord.Embed(title=lang['DROPDOWN']['add_title'],
                                       description=lang['DROPDOWN']['add_description'], color=nextcord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

        elif self.values[0] == 'remove':
            selections = []
            # get all the voice channels in the server from redis
            keys = r.keys(f"auto:{interaction.guild.id}:*")
            if len(keys) == 0:
                embed = nextcord.Embed(title=lang['DROPDOWN']['remove_empty'],
                                       description=lang['DROPDOWN']['remove_empty_description'].format(
                                           interaction.guild.name),
                                       color=nextcord.Color.yellow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                for key in keys:
                    channel = client.get_channel(int(key.split(':')[2]))
                    selections.append(nextcord.SelectOption(label=channel.name, emoji='🔊', description=channel.id,
                                                            value=f'removevoice:{channel.id}'))
                view = DropdownMenu(selections)
                embed = nextcord.Embed(title=lang['DROPDOWN']['remove_title'],
                                       description=lang['DROPDOWN']['remove_description'], color=nextcord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

        elif self.values[0] == 'list':
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
                                           description=lang['LIST']['embed_description'].format(len(keys),
                                                                                                interaction.guild.name),
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
                                # find the index of the channel in the hub_list
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
                embed = nextcord.Embed(title=lang['LIST']['error'], description=lang['LIST']['error_description'],
                                       color=nextcord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.values[0].startswith('addvoice:'):
            channel_id = self.values[0].split(':')[1]
            category = client.get_channel(int(channel_id)).category
            try:
                if r.exists(f"auto:{interaction.guild.id}:{channel_id}"):
                    embed = nextcord.Embed(title=lang['CREATE']['duplicate'],
                                           description=lang['CREATE']['duplicate_description'],
                                           color=nextcord.Color.yellow())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    r.set(f"auto:{interaction.guild.id}:{channel_id}", category.id)
                    embed = nextcord.Embed(title=lang['CREATE']['success'],
                                           description=lang['CREATE']['success_description'].format(f'<#{channel_id}>'),
                                           color=nextcord.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                embed = nextcord.Embed(title=lang['CREATE']['error'], description=lang['CREATE']['error_description'],
                                       color=nextcord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.values[0].startswith('removevoice:'):
            channel_id = self.values[0].split(':')[1]
            try:
                if r.exists(f"auto:{interaction.guild.id}:{channel_id}"):
                    r.delete(f"auto:{interaction.guild.id}:{channel_id}")
                    embed = nextcord.Embed(title=lang['DELETE']['success'],
                                           description=lang['DELETE']['success_description'].format(f'<#{channel_id}>'),
                                           color=nextcord.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = nextcord.Embed(title=lang['DELETE']['not_found'],
                                           description=lang['DELETE']['not_found_description'],
                                           color=nextcord.Color.yellow())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                embed = nextcord.Embed(title=lang['DELETE']['error'], description=lang['DELETE']['error_description'],
                                       color=nextcord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)


class DropdownMenu(nextcord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.add_item(Dropdown(options))


client.run(token)
