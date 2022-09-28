#imports
import nextcord
from nextcord.ext import commands
import configparser

#load config
config = configparser.ConfigParser()
config.read('config.ini')

print(config['CREDENTIALS']['token'])



#discord setup
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)