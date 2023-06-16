import os

from slack_bolt import App, Ack, Respond
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient

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

#Stub unless this ends up being needed later.
@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)

@app.view("initialize_game")
def handle_initialize_game(ack, body):
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

	game.initialize(game_data)

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
	return "Game Initialized"

def admin_outputs (command, message, client, meta_data):
	return "outputs"

def admin_start (command, message, client, meta_data):
	return "start"

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
		'help_text': "Actions taken in the game."
	},
	'initialize': {
		'function': admin_initialize,
		'help_text': "Initialize the game."
	},
	'outputs': {
		'function': admin_outputs,
		'help_text': "Outputs in the game."
	},
	'start': {
		'function': admin_start,
		'help_text': "Start the game."
	},
	'state': {
		'function': admin_state,
		'help_text': "State for the game."
	}
}

def game_join (command, message, client, meta_data):
	print("HERE")
	pp.pprint(meta_data)

	return "join"

def game_leave (command, message, client, meta_data):
	return "leave"

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

	client.chat_postMessage(
		channel=user_id,
		text=text
	)


# The mafia_game command shows information about the game.
@app.command("/mafia_game")
def mafia_game(ack: Ack, command: dict, client: WebClient):
	ack()

	channel_id = command['channel_id']
	message = command['text']
	command_string = command['command']

	text = selection_menu(command_string, message, game_commands, client, command)

	log.info(command)

	client.chat_postMessage(
		channel=channel_id,
		text=text
	)

# The mafia_private_action command shows information about the game.
@app.command("/mafia_private_action") 
def mafia_private_action(ack: Ack, command: dict, client: WebClient):
	ack()

# The mafia_public_action command shows information about the game.
@app.command("/mafia_public_action")
def mafia_public_action(ack: Ack, command: dict, client: WebClient):
	ack()

game.initialize_game_state()

if __name__ == "__main__":
	SocketModeHandler(app, SLACK_APP_TOKEN).start()
