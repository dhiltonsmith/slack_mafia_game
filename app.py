import os

from slack_bolt import App, Ack, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk import errors

import log
import pprint
import re
import game

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN").strip()
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN").strip()

log.logging_level = log.INFO
pp = pprint.PrettyPrinter(indent=4)

app = App(token=SLACK_BOT_TOKEN)  # initializes your app with your bot token and socket mode handler


global faction_counter
faction_counter = 1

def handler_post_message(client, channel, text):
	try:
		client.chat_postMessage(
			channel=channel,
			text=text
		)
	except errors.SlackApiError:
		log.error("Cannot send message to channel {}.".format(channel))

def handler_invite_channel(client, channel_id, users):
	# TO DO: Add logic to remove any users already in channel.
	for user in users:
		try:
			client.conversations_invite(channel=channel_id, users=user)
		except errors.SlackApiError:
			log.warn("User {} already in channel {}.".format(user, channel_id))

def handler_create_channel(client, channel_name, private):
	try:
		response = client.conversations_create(
			name = channel_name,
			is_private = private
		)

		channel_id = response["channel"]["id"]
	except errors.SlackApiError:
		log.warn("Channel {} already exists.".format(channel_name))
		response = client.conversations_list()
		while response["response_metadata"]["next_cursor"]:
			for channel in response["channels"]:
				if channel['name'] == channel_name:
					channel_id = channel['id']
			response = client.conversations_list(cursor = response["response_metadata"]["next_cursor"])
		response = client.conversations_list(types="private_channel")
		while response["response_metadata"]["next_cursor"]:
			for channel in response["channels"]:
				if channel['name'] == channel_name:
					channel_id = channel['id']
			response = client.conversations_list(cursor = response["response_metadata"]["next_cursor"], types="public_channel, private_channel")

	handler_invite_channel(client, channel_id, admin_users)

	return channel_id

def add_users_to_channels(client, message):
	town_channel_id = game.get_channel_id(message, "town")

	players = game.get_players(message)
	handler_invite_channel(client, town_channel_id, players)

	factions = game.get_factions_with_channels(message)

	for faction in factions:
		handler_invite_channel(client, faction['channel_id'], faction['players'])

	medium_players = game.get_players_with_role(message, "medium")
	if len(medium_players) > 0:
		graveyard_channel_id = game.get_channel_id(message, "graveyard")
		handler_invite_channel(client, graveyard_channel_id, medium_players)

def create_default_channels(client, message):
	town_channel, graveyard_channel = game.command_default_channels_for_game(message)

	if len(town_channel) != 0:
		town_channel_id = handler_create_channel(client, town_channel, False)
	else:
		town_channel_id = game.get_channel_id(message, "town")

	if len(graveyard_channel) != 0:
		graveyard_channel_id = handler_create_channel(client, graveyard_channel, True)
	else:
		graveyard_channel_id = game.get_channel_id(message, "graveyard")

	game.command_store_default_channel_information(message, town_channel_id, graveyard_channel_id)

def create_channels(client, message):
	faction_channels = game.command_channels_for_game(message)

	for faction_channel in faction_channels:
		faction_channel_id = handler_create_channel(client, faction_channel['channel_name'], True)
		faction_channel['channel_id'] = faction_channel_id

	game.command_store_channel_information(message, faction_channels)

def initial_messages(client, message):
	for player in game.running_games[message]['players']:
		if 'faction_types' not in game.running_games[message]['players'][player] or game.running_games[message]['players'][player]['faction_type'] not in ['mafia', 'vampire_coven']:
			player_message = game.command_intro_message(message, player)
			handler_post_message(client, player, player_message)

#Stub unless this ends up being needed later.
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

@app.view("initialize_game")
def handle_initialize_game(ack, body, client):
	ack()
	log.info(body)

	game_data = {}
	game_data['factions'] = {}

	game_options_raw = body['view']['state']['values']

	for game_option_id in game_options_raw.keys():
		for game_option in game_options_raw[game_option_id].keys():
			if game_option == 'town_name':
				game_data['town_name'] = game_options_raw[game_option_id][game_option]['value']
				game_data['town_name_abbreviated'] = game_data['town_name'].lower().replace(" ", "_")
			elif game_option == 'default_roles':
				default_roles_list = game_options_raw[game_option_id][game_option]['value'].split(",")
				game_data['default_roles'] = default_roles_list
			elif game_option == 'game_recruiting_start':
				game_data['game_recruiting_start'] = game_options_raw[game_option_id][game_option]['selected_date_time']
			elif game_option == 'round_length':
				game_data['round_length'] = float(game_options_raw[game_option_id][game_option]['value'])
			elif game_option == 'min_players':
				game_data['min_players'] = int(game_options_raw[game_option_id][game_option]['value'])
			elif 'faction' in game_option:
				faction_id = re.search(r'\d+$', game_option).group()
				if faction_id not in game_data['factions']:
					game_data['factions'][faction_id] = {}
				if 'name' in game_option:
					game_data['factions'][faction_id]['name'] = game_options_raw[game_option_id][game_option]['value']
				elif 'size_type' in game_option:
					game_data['factions'][faction_id]['size_type'] = game_options_raw[game_option_id][game_option]['selected_option']['value']
				elif 'size' in game_option:
					game_data['factions'][faction_id]['size'] = int(game_options_raw[game_option_id][game_option]['value'])
				elif 'type' in game_option:
					game_data['factions'][faction_id]['type'] = game_options_raw[game_option_id][game_option]['selected_option']['value']

	game.command_initialize(game_data)

	create_default_channels(client, game_data['town_name_abbreviated'])

@app.action("add_faction")
def handle_add_faction(ack, body, client):
	ack()

	global faction_counter
	faction_counter += 1

	for faction_item in faction_block():
		body['view']['blocks'].insert(-1, faction_item)

	client.views_update(view_id=body["view"]["id"], hash=body["view"]["hash"], view={
		"type": body["view"]["type"],
		"callback_id": body["view"]["callback_id"],
		"title": body["view"]["title"],
		"close": body["view"]["close"],
		"submit": body["view"]["submit"],
		"blocks": body["view"]["blocks"]
	})

def faction_block():
	faction_types = game.game_roles.keys()

	faction_type_options = []
	for faction_type in faction_types:
		if faction_type != "Neutral" and faction_type != "Evil":
			faction_type_options.append({"text": {"type": "plain_text", "text": faction_type,}, "value": faction_type.lower().replace(" ", "_")})

	faction_block =  [{
		"type": "divider"
	}, {
		"type": "header", "text": {"type": "plain_text", "text": "Faction {}".format(faction_counter)}
	}, {
		"type": "input", "label": {"type": "plain_text", "text": "Faction Name"}, "element": {"type": "plain_text_input", "action_id": "faction_name{}".format(faction_counter)}, "optional": False
	}, {
		"type": "input", "element": {"type": "static_select", "placeholder": {"type": "plain_text", "text": "Select a Faction Type",}, "options": faction_type_options, "action_id": "faction_type{}".format(faction_counter)}, "label": {"type": "plain_text", "text": "Label"}, "optional": False
	}, {
		"type": "input", "label": {"type": "plain_text","text": "Faction Size"}, "element": {"type": "number_input", "is_decimal_allowed": True, "action_id": "faction_size{}".format(faction_counter)}, "optional": False,
	}, {
		"type": "input", "element": {"type": "radio_buttons", "options": [{"text": {"type": "plain_text", "text": "Fixed Number",}, "value": "fixed"},{"text": {"type": "plain_text", "text": "Percentage",}, "value": "percent"}], "action_id": 
"faction_size_type{}".format(faction_counter)}, "label": {"type": "plain_text", "text": "Faction Size Type",}, "optional": False
	}]

	return faction_block

# Derek and Sri as initial admin's.
admin_users = ['U01HB0HCL5T', 'U03NUHNPBUK']

def admin_actions(command, message, client, meta_data):
	return "actions"

def admin_assign_users(command, message, client, meta_data):
	pp.pprint(message)

	return "assign users"

def admin_initialize(command, message, client, meta_data):
	global faction_counter
	faction_counter = 1

	view_blocks = [ {
		"type": "input", "label": {"type": "plain_text","text": "Town Name"}, "element": {"type": "plain_text_input", "action_id": "town_name"}, "optional": False
	}, {
		"type": "input", "label": {"type": "plain_text","text": "Default Roles"}, "element": {"type": "plain_text_input", "action_id": "default_roles"}, "optional": False
	}, {
		"type": "input", "label": {"type": "plain_text","text": "Minimum Players"}, "element": {"type": "number_input", "is_decimal_allowed": False, "action_id": "min_players"}, "optional": False
	}, {
		"type": "input", "label": {"type": "plain_text","text": "Game Recruiting Start Time"}, "element": {"type": "datetimepicker", "action_id": "game_recruiting_start"}, "optional": False
	}, {
		"type": "input", "label": {"type": "plain_text","text": "Round Length (in hours)"}, "element": {"type": "number_input", "is_decimal_allowed": True, "action_id": "round_length"}, "optional": False
	}, {
		"type": "actions", "elements": [{"type": "button", "action_id": "add_faction", "text": { "type": "plain_text", "text": "Add another option  "}}]
	}]

	for faction_item in faction_block():
		view_blocks.insert(-1, faction_item)

	faction_counter += 1
	for faction_item in faction_block():
		view_blocks.insert(-1, faction_item)

	client.views_open(
	        trigger_id=meta_data["trigger_id"],
        	# A simple view payload for a modal
        	view={
			"type": "modal",
			"callback_id": "initialize_game",
			"title": {"type": "plain_text", "text": "Initialize Mafia Game"},
			"close": {"type": "plain_text", "text": "Close"},
			"submit": {"type": "plain_text", "text": "Save"},
			"blocks": view_blocks,
		}
	)

	return "Game Initializing..."

def admin_outputs (command, message, client, meta_data):
	return "outputs"

def admin_start (command, message, client, meta_data):
	response = game.command_game_start(message)

	if type(response) == list:
		response = "*List of games*: {}".format(', '.join(response))
	elif 'already running' not in response:
		create_channels(client, message)
		add_users_to_channels(client, message)
		initial_messages(client, message)

	return response

def admin_state (command, message, client, meta_data):
	response = game.get_running_game_state(message)

	if type(response) == list:
		response = "List of games: {}".format(', '.join(response))
	else:
		response = "Game State of {} is: {}".format(message, response)

	return response

admin_commands = {
	'actions': {
		'function': admin_actions,
		'help_text': "Actions taken in a game."
	},
	'assign_users': {
		'function': admin_assign_users,
		'help_text': "Assign users to a game."
	},
	'initialize': {
		'function': admin_initialize,
		'help_text': "Initialize a game."
	},
	'outputs': {
		'function': admin_outputs,
		'help_text': "Outputs in a game."
	},
	'start': {
		'function': admin_start,
		'help_text': "Start a game."
	},
	'state': {
		'function': admin_state,
		'help_text': "State for a game."
	}
}

def game_join (command, message, client, meta_data):
	town_channel_id, response = game.command_game_join(meta_data, message)

	if type(response) == list:
		response = "*List of games*: {}".format(', '.join(response))
	else:
		add_users_to_channels(client, message)
		handler_post_message(client, town_channel_id, response)

	return response

def game_leave (command, message, client, meta_data):
	town_channel_id, response = game.command_game_leave(meta_data)

	handler_post_message(client, town_channel_id, response)

	return response

def game_list (command, message, client, meta_data):
	return "list"

def game_role (command, message, client, meta_data):
	return "role"

game_commands = {
	'join': {
		'function': game_join,
		'help_text': "Join a game."
	},
	'leave': {
		'function': game_leave,
		'help_text': "Leave the game."
	},
	'list': {
		'function': game_list,
		'help_text': "List players in the game."
	},
	'role': {
		'function': game_role,
		'help_text': "Get role information."
	}
}

# TO DO: REMOVE THIS!
def private_action_default(command, message, client, meta_data):
	return "default"

private_action_commands = {
	'action': {
		'function': private_action_default,
		'help_text': "Vampires select an action to take."
	},
	'alert': {
		'function': private_action_default,
		'help_text': "Go on alert to attack all visitors and leave a Death Note."
	},
	'ambush': {
		'function': private_action_default,
		'help_text': "Set an ambush and leave a Death Note."
	},
	'apparate': {
		'function': private_action_default,
		'help_text': "Appear in town and interacte as usual for a day."
	},
	'attack': {
		'function': private_action_default,
		'help_text': "Attack a player and leave a Death Note."
	},
	'become': {
		'function': private_action_default,
		'help_text': "Change role to match a dead players."
	},
	'boost': {
		'function': private_action_default,
		'help_text': "Enhance the attack and defense of a player and get information about them."
	},
	'choose': {
		'function': private_action_default,
		'help_text': "Choose a role within the faction."
	},
	'convert': {
		'function': private_action_default,
		'help_text': "Select a player to convert into your faction."
	},
	'disguise': {
		'function': private_action_default,
		'help_text': "Change a player in your mafia to look like a role if investigated."
	},
	'douse': {
		'function': private_action_default,
		'help_text': "Prepare a player to be ignited."
	},
	'event': {
		'function': private_action_default,
		'help_text': "Trigger an event for the town."
	},
	'examine': {
		'function': private_action_default,
		'help_text': "Check the role and the killers role for a dead player."
	},
	'forge': {
		'function': private_action_default,
		'help_text': "Create a fake examination result for a dead player."
	},
	'ignite': {
		'function': private_action_default,
		'help_text': "Attack all doused players and leave a Death Note."
	},
	'investigate': {
		'function': private_action_default,
		'help_text': "Gain information about a player."
	},
	'possess': {
		'function': private_action_default,
		'help_text': "Guess the role of a player to possess them."
	},
	'promote': {
		'function': private_action_default,
		'help_text': "Promote a player into the new Mafioso."
	},
	'protect': {
		'function': private_action_default,
		'help_text': "Protect a player."
	},
	'resurrect': {
		'function': private_action_default,
		'help_text': "Bring a player back to life."
	},
	'role_block': {
		'function': private_action_default,
		'help_text': "Stop the action of another player."
	},
	'stake': {
		'function': private_action_default,
		'help_text': "Attack all identified vampires and leave a Death Note."
	},
	'unite': {
		'function': private_action_default,
		'help_text': "Unite mafia factions."
	},
	'vision': {
		'function': private_action_default,
		'help_text': "Receive a vision about other players in the game."
	},
	'watch': {
		'function': private_action_default,
		'help_text': "Focus on a specific player."
	}
}

# TO DO: REMOVE THIS!
def public_action_default(command, message, client, meta_data):
	return "default"
        
public_action_commands = {
	'hang': {
		'function': public_action_default,
		'help_text': "Hang a player."
	},
	'juror': {
		'function': public_action_default,
		'help_text': "Vote for a juror."
	},
	'reval': {
		'function': public_action_default,
		'help_text': "Reveal your identity to the town."
	}
}

def menu_help(command, menu_options):
	options = ""
	for key in menu_options:
		options += "*{0}*: {1}\n".format(key, menu_options[key]['help_text'])
		
	text = "Usage:\n{0} *OPTION*\n\nOptions:\n{1}".format(command, options)
	return text

def selection_menu(command, message, menu_options, client, meta_data):
	if len(message) == 0:
		option_selected = 'help'
	else:
		message_split = message.split(' ', 1)

		option_selected = message_split[0].lower()
		if len(message_split) == 1:
			message = ""
		else:
			message = message[message.index(' ') + 1:]

	if option_selected in menu_options:
		return menu_options[option_selected]['function'](command, message, client, meta_data)
	else:
		return menu_help (command, menu_options)

# The mafia_admin command allows administration of games.
@app.command("/mafia_admin")
def mafia_admin(ack: Ack, command: dict, client: WebClient):
	ack()

	user_id = command['user_id']
	channel_id = command['channel_id']
	message = command['text']
	command_string = command['command']

	is_admin = False

	if user_id in admin_users:
		is_admin = True

	if is_admin:
		text = selection_menu(command_string, message, admin_commands, client, command)
	else:
		text = "Not a Mafia Game Admin."

	log.info(command)

	handler_post_message(client, user_id, text)

# The mafia_game command shows information about the game.
@app.command("/mafia_game")
def mafia_game(ack: Ack, command: dict, client: WebClient):
	ack()

	user_id = command['user_id']
	channel_id = command['channel_id']
	message = command['text']
	command_string = command['command']

	player_game_commands = game.command_available_game_commands(user_id)
	adjusted_game_commands = {}

	for selected_command in player_game_commands:
		adjusted_game_commands[selected_command] = game_commands[selected_command]

	text = selection_menu(command_string, message, adjusted_game_commands, client, command)

	log.info(command)

	handler_post_message(client, user_id, text)

# The mafia_private_action command shows information about the game.
@app.command("/mafia_private_action") 
def mafia_private_action(ack: Ack, command: dict, client: WebClient):
	ack()

	user_id = command['user_id']
	channel_id = command['channel_id']
	message = command['text']
	command_string = command['command']

	player_private_commands = game.command_available_private_actions(user_id)
	adjusted_private_action_commands = {}
	for selected_command in player_private_commands:
		adjusted_private_action_commands[selected_command] = private_action_commands[selected_command]

	if len(adjusted_private_action_commands) > 0:
		text = selection_menu(command_string, message, adjusted_private_action_commands, client, command)
	else:
		text = "Currently no available Private Action Commands."

	log.info(command)

	handler_post_message(client, user_id, text)

# The mafia_public_action command shows information about the game.
@app.command("/mafia_public_action")
def mafia_public_action(ack: Ack, command: dict, client: WebClient):
	ack()

	user_id = command['user_id']
	channel_id = command['channel_id']
	message = command['text']
	command_string = command['command']

	player_public_commands = game.command_available_public_actions(user_id)
	adjusted_public_action_commands = {}
	for selected_command in player_public_commands:
		adjusted_public_action_commands[selected_command] = public_action_commands[selected_command]

	if len(adjusted_public_action_commands) > 0:
		text = selection_menu(command_string, message, adjusted_public_action_commands, client, command)
	else:
		text = "Currently no available Public Action Commands."

	log.info(command)

	handler_post_message(client, user_id, text)

game.initialize_game_state()

if __name__ == "__main__":
	SocketModeHandler(app, SLACK_APP_TOKEN).start()
