#imports
import nextcord
from nextcord.ext import commands
import configparser

#load config
config = configparser.ConfigParser()
config.read('config.ini')

token = config['CREDENTIALS']['token']
owner_id = config['CREDENTIALS']['owner_id']

prefix = config['SETTINGS']['prefix']
status = config['SETTINGS']['status']
status_message = config['SETTINGS']['status_message']
status_type = config['SETTINGS']['status_type']

host = config['REDIS']['host']
port = config['REDIS']['port']
password = config['REDIS']['password']

#discord setup
intents = nextcord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)