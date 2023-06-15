import log
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)

DEFAULT_ROLES = ['TI']
MIN_PLAYERS = 10
ROUND_LENGTH = 24
TOWN_NAME = "TOWN"
MIN_FACTION_SIZE = 1

game_roles={
        "Town": {
                "TI": ["Detective", "Examiner", "Investigator", "Lookout", "Profiler", "Psychic", "Sheriff", "Spy", "Tracker"],
                "TK": ["Vampire Hunter", "Veteran", "Vigilante"],
                "TP": ["Bodyguard", "Doctor", "Secret Service"],
                "TS": ["Mayor", "Medium", "Police Officer", "Resurrectionist"]
        },
        "Mafia": {
                "MI": ["Consigliere"],
                "MK": ["Ambusher", "Mafioso"],
                "MP": ["Disguiser"],
                "MS": ["Corrupt Police Officer", "Corrupt Politician", "Diplomat", "Forger", "Godfather"]
        },
        "Vampire Coven": {
                "VK": ["Vampire"]
        },
        "Neutral": {
                "NI": ["Executioner"],
                "NK": ["Jester"],
                "NP": ["Guardian Angel", "Survivor"],
                "NS": ["Amnesiac"]
        },
        "Evil": {
                "EI": ["Cultist"],
                "ES": ["Necromancer"]
        },
        "Fire Starter": {
                "FK": ["Fire Starter"]
        },
        "Renegade": {
                "RK": ["Renegade"]
        },
        "Werewolf": {
                "WK": ["Werewolf"]
        }
}

def get_all_role_categories():
	role_categories = []
	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			role_categories.append(category)
	return role_categories

def store_game_state(game_data, state):
	game_object = json.dumps(game_data, indent=4)
	with open("game_save/{}.{}".format(game_data['town_name_abbreviated'], state), "w") as outfile:
		outfile.write(game_object)

def initialize(game_data):
	role_categories = get_all_role_categories()
	default_roles = game_data['default_roles']
	for role in default_roles:
		if role not in role_categories:
			game_data['default_roles'].remove(role)
			log.debug("Removing {} from default_roles".format(role))
	if len(game_data['default_roles']) == 0:
		game_data['default_roles'] = DEFAULT_ROLES
		log.debug("Setting default_roles to {}".format(DEFAULT_ROLES))
	if int(game_data['min_players']) <= 0:
		game_data['min_players'] = MIN_PLAYERS
		log.debug("Setting min_players to {}".format(MIN_PLAYERS))
	if int(game_data['round_length']) <= 0:
		game_data['round_length'] = ROUND_LENGTH
		log.debug("Setting round_length to {}".format(ROUND_LENGTH))
	for faction_id in game_data['factions'].keys():
		if game_data['factions'][faction_id]['size'] <= 0:
			game_data['factions'][faction_id]['size'] = MIN_FACTION_SIZE
			log.debug("Setting faction {} size to {}".format(game_data['factions'][faction_id]['name'], MIN_FACTION_SIZE))

	store_game_state(game_data, "open")