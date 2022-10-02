import configparser

config = configparser.ConfigParser()

config['CREDENTIALS'] = {
    'token': 'YOUR_TOKEN_HERE',
    'owner_id': 'YOUR_ID_HERE'
}
config['SETTINGS'] = {
    'prefix': '!',
    'status': 'online',
    'status_message': 'Auto Voice Channels',
    'status_type': 'playing'
}
config['REDIS'] = {
    'host': 'localhost',
    'port': '6379',
    'password': 'YOUR_PASSWORD_HERE',
    'db': '0'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
