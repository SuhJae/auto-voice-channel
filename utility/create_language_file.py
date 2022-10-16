import configparser

config = configparser.ConfigParser()

config['CREATE'] = {
    'name': 'create',
    'description': 'Set a voice channel as a automatic voice channel',
    'argument_description': 'Select a voice channel that will be used as a automatic voice channel',
    'success': 'Success!',
    'success_description': 'The bot will now create a new voice channel when someone joins {0}!',
    'error': 'Error!',
    'error_description': 'There was an error while trying to create the automatic voice channel!',
    'duplicate': 'Error!',
    'duplicate_description': 'This voice channel is already an automatic voice channel!'
}

config['DELETE'] = {
    'name': 'delete',
    'description': 'Deactivate a automatic voice channel',
    'argument_description': 'Select a voice channel that will be deactivated',
    'success': 'Success!',
    'success_description': 'The bot will no longer create a new voice channel when someone joins {0}!',
    'error': 'Error!',
    'error_description': 'There was an error while trying to deactivate the automatic voice channel!',
    'not_found': 'Error!',
    'not_found_description': 'This voice channel is not an automatic voice channel!'
}

config['LIST'] = {
    'name': 'list',
    'description': 'List all automatic voice channels',
    'error': 'Error!',
    'error_description': 'There was an error while trying to list the automatic voice channels!',
    'embed_title': 'Automatic voice channels',
    'embed_description': 'There are **{0}** automatic voice channels in **{1}**!',
    'embed_field_name': 'Automatic voice channel',
    'empty': 'No automatic voice channels!',
    'empty_description': 'There are no automatic voice channels in **{0}**!',
    'embed_footer': 'There are {0} deleted channels which were removed from our database.'
}

config['CLEAR'] = {
    'name': 'clear',
    'description': 'Removes all voice channels created by the bot',
    'success': 'Success!',
    'success_description': 'All **{0}** voice channels created by the bot have been removed!',
    'partial': 'Success!',
    'partial_description': '**{0}** voice channels created by the bot have been removed! **{1}** voice channels could not be removed.',
    'failure': 'Error!',
    'failure_description': 'There was an error while trying to remove all voice channels created by the bot! Please check the permission of the bot.',
    'error': 'Error!',
    'error_description': 'There was an error while trying to remove all voice channels created by the bot!',
    'empty': 'Error!',
    'empty_description': 'There are no voice channels created by the bot!',
    'loading': 'Loading...',
    'loading_description': 'There are **{0}** voice channels created by the bot. It will take up to **{1}** seconds to delete them all!',
}

config['HELP'] = {
    'name': 'help',
    'description': 'Shows a list of all commands or information about a specific command',
    'argument': 'command',
    'argument_description': 'Select a command to get more information about it',
    'embed_title': 'Help',
    'embed_description': 'Here is a list of all commands. Invite the bot to your server with [this link](https://discord.com/api/oauth2/authorize?client_id=1024514599216746496&permissions=75792&scope=bot%%20applications.commands)!',
    'voice_channel': 'Voice channel',
    'command': 'Command',
    'optional': 'Optional',
    'usage': 'Usage',
    'permission': 'Permission',
    'permission_administrator': 'Administrator',
    'permission_none': 'None',
    'footer' : 'You can use {0} to get info on a specific command!'
}

config['INVITE'] = {
    'name': 'invite',
    'description': 'Get the invite link of the bot',
    'embed_title': 'Invite',
    'embed_description': 'You can invite the bot to your server with [this link](https://discord.com/api/oauth2/authorize?client_id=1024514599216746496&permissions=75792&scope=bot%%20applications.commands)!',
}

config['PING'] = {
    'name': 'ping',
    'description': 'Get the latency of the bot',
    'embed_title': 'Ping',
    'embed_description': 'The bot has a ping of **{0}** ms!',
}

config['DASHBOARD'] = {
    'name': 'dashboard',
    'description': 'Opens the dashboard of the bot',
    'embed_title': 'Dashboard of **{0}**',
    'embed_description': 'You can use dropdown below to change settings.',
    'selection_add': 'Add Auto Voice Channel',
    'selection_remove': 'Remove Auto Voice Channel',
    'selection_clear': 'Clear Auto Voice Channels',
    'selection_list': 'List Auto Voice Channels',
    'none': '`None`',
}

config['DROPDOWN'] = {
    'placeholder': 'Select an option',
    'add_title': 'Add Auto Voice Channel',
    'add_description': 'Select a voice channel that will be used as a automatic voice channel',
    'add_empty': 'There are no voice channels in this server!',
    'add_empty_description': 'Please create a voice channel first!',
    'remove_title': 'Remove Auto Voice Channel',
    'remove_description': 'Select a voice channel to remove it from the list of automatic voice channels.',
    'remove_empty': 'There are no automatic voice channels in this server!',
    'remove_empty_description': 'Please create a automatic voice channel first!',
}



with open('../language.ini', 'w') as configfile:
    config.write(configfile)
