import log

import pprint
import json
import math
import os
import random

pp = pprint.PrettyPrinter(indent=4)

global running_games, finished_games, players_in_games

running_games = {}
finished_games = {}
players_in_games = {}

SAVE_PATH = "game_save"

ACTIONS = ['attack', 'convert', 'standard']
DEFAULT_ROLES = ['NI', 'NK', 'NP', 'NS', 'EI', 'ES']
MIN_PLAYERS = 10
ROUND_LENGTH = 24
TOWN_NAME = "TOWN"
MIN_FACTION_SIZE = 1

ATTACK_LEVELS = ["No Attack", "Basic Attack", "Unstoppable Attack"]
DEFENSE_LEVELS = ["No Defense", "Basic Defense", "Unbreakable Defense"]

game_roles={
        "Town": {
		"Data": {
			"alignment": "good"
		},
                "TI": {
			"Detective": {
				"background": """Raised in the city, the detective has seen first hand the devastating effect crime has had and will stop at nothing to protect their home. They are not above 
breaking the rules in their investigation if that means keeping dangerous criminals off of the streets.""",
				"private_actions": ["investigate"]
			},
			"Examiner": {
				"background": """A mortician, due to the recent crime wave they have chosen to focus their energy on examining the bodies that come in for clues that can be used to stop the 
various threats in the city.  Recently they received several calls and a threatening note covered in blood warning them to stop snooping around, as a precaution they have begun working with an underground news 
organization to release their unsanctioned autopsy reports anonymously.""",
				"private_actions": ["examine"]
			},
			"Investigator": {
				"background": """There was very little need for therapists once the killings began, people were too afraid to leave their homes to go for a consultation.  In order to continue 
to provide support to the city, those trained in the art of mental health began acting as forensic profilers, observing patterns of behavior in order to identify and classify dangerous individuals and groups 
within the city.""",
				"private_actions": ["investigate"]
			},
			"Lookout": {
				"background": """Originally hired as a private eye investigating an infidelity case, while staking out the home they saw a group of thugs entering a home heard the sound of a 
gun going off and knew they were too late to stop it.  Desperate for answers and haunted by the memory of that night they have dedicated themselves to using their skills for the good of the city rather than 
for private gain.""",
				"private_actions": ["watch"]
			},
			"Profiler": {
				"background": """Back when the city was still innocent they were some of the police departments top criminal profilers.  As criminals took over, they continued to dutifully 
execute their job, identifying killers and running them up the chain of command.  After repeatedly being ignored by authority figures, they began sharing their findings with anyone who would listen, hoping 
desperately that someone out there was willing to act on their leads and bring order to the chaos.""",
				"private_actions": ["investigate"]
			},
			"Psychic": {
				"background": """One night they had a dream and in the dream they saw three people brutally murdering an innocent bystander on the subway, later that week while watching the 
news they saw video footage of one of the people from their dream being led away in handcuffs after being charged with a subway mugging gone wrong.  Out of fear of the mafia they have chosen to stay silent 
about their vision, but one can only keep silent for so long.""",
				"private_actions": ["vision"]
			},
			"Sheriff": {
				"background": """The county had always underfunded the sheriffs department, so it came as no surprise when it was fully dismantled by the former mayor.  Many went on to join the 
local police department, but some choose to pursue other means of protecting the city, silently staking out suspicious individuals looking for signs of foul play.""",
				"private_actions": ["investigate"]
			},
			"Spy": {
				"background": """A former CIA hobbyist, they have accrued an impressive array of surveillance gear that they use to investigate the happenings of their neighbors.  One night a 
particularly well hidden microphone happened to pick up a Mafia meeting at the dock that included information about a stolen shipment that they were planning on trafficking.  Since then they have been placing 
microphones everywhere in the hopes of uncovering more information that can be used to finally put an end to the Mafia’s control over the city.""",
				"private_actions": ["investigate"]
			},
			"Tracker": {
				"background": """Stalking celebrities had always been their passion, but once the tourism board closed down and people stopped visiting they decided to put their skills to 
better use.  Instead of following the rich and famous they began to follow random people on the street, always keeping just out of sight in order to avoid being caught.""",
				"private_actions": ["watch"]
			}
		},
                "TK": {
			"Vampire Hunter": {
				"attack": 2,
				"background": """One day after returning home from work you stumbled upon your spouse laying in bed with two deep puncture marks on her neck.  When you checked their pulse, you 
found none and their skin was cold to the touch, just before dialing 911 you called their name and their eyes snapped open at the sound of your voice.  They launched from the bed and lunged at you but you were 
quicker and happened to grab a piece of splintered wood that had been sitting on top of the nightstand, stabbing them in the chest.  As they died in your arms you realized that it was your duty to prevent this 
fate from happening to anyone else.""",
				"private_actions": ["investigate", "stake"]
			},
			"Veteran": {
				"attack": 2,
				"background": """You returned home from war only to find yourself in a new kind of war on the streets of the city you grew up in.  Wracked with PTSD and enough combat training 
to make you a threat to anyone who would dare stand against you, you hunker down in your home waiting for the perfect opportunity to strike back.""",
				"private_actions": ["alert"],
				"role_block_immune": True
			},
			"Vigilante": {
				"attack": 1,
				"background": """You walk the streets at night, safe in the knowledge that you alone can save the day.  With just a gun and the vague notion of justice on your side, you have 
decided to take the city back, even if you have to do it yourself.""",
				"private_actions": ["attack"]
			}
		},
                "TP": {
			"Bodyguard": {
				"attack": 2,
				"background": """You used to be the bouncer at a popular club, but all of the clubs have been abandoned, now you sell your services as a bodyguard, protecting whomever is 
willing to pay for your services.  Sometimes you feel guilty that you aren’t doing more to protect the city, but protecting the city isn’t going to pay the bills.""",
				"private_actions": ["protect"]
			},
			"Doctor": {
				"background": """You were a surgeon back before the hospital closed down, now you run a clinic out of your basement, dragging wounded civilians off of the street and doing 
whatever you can to nurse them back to health.  Someday you hope to return to the comfort of the surgery ward, but for now you do what you can to get people the help they desperately need.""",
				"private_actions": ["protect"]
			},
			"Secret Service": {
				"attack": 1,
				"background": """A security guard for the former mayor, you were present for many meetings where illegal business was discussed, it was an unpleasant experience and you were 
tempted to file an anonymous report but never got the courage to go through with it.  Now that the new mayor has gone into hiding, you have decided to use your skills to defend the city against the criminals 
who would like to see it fall.""",
				"private_actions": ["protect"]
			}
		},
                "TS": {
			"Mayor": {
				"background": """The day you were elected was the same day that the city fell to shambles.  You had always suspected that your opponent had ties to the Mafia but you never 
imagined how deep those ties went until they lost the popular vote.  In order to stay safe you had to change your identity and hide out, hoping that the Mafia and the former mayor would leave you alone, but 
knowing that it was just a matter of time before you were found.""",
				"public_actions": ["reveal"],
				"unique": True,
				"role_block_immune": True
			},
			"Medium": {
				"background": """A gravedigger, one night you thought you heard voices coming from one of the freshly filled grave’s in the graveyard.  Over time you have come to accept and 
even look forward to hearing the voices of the dead while you work.""",
				"private_actions": ["apparate"],
				"role_block_immune": True
			},
			"Police Officer": {
				"background": """One of the few police officers who refused to take money from the Godfather, you do your best to do your job while also staying vigilant for the knife that your 
fellow officers might be preparing to stab you in the back with.""",
				"private_actions": ["role_block"],
				"role_block_immune": True
			},
			"Resurrectionist": {
				"background": """One night your apartment was broken into by members of the Mafia who demanded payment from your roommate, when they could not pay up they were executed and left 
for dead.  You arrived home from a late shift to find their dead body, but when you went to check their vital signs they were miraculously returned to life.  The two of you swore to keep your secret safe, in 
order to prevent the Mafia from exploit it.""",
				"private_actions": ["resurrect"]
			}
		}
        }, "Mafia": {
		"Data": {
			"alignment": "evil"
		},
                "MI": {
			"Consigliere": {
				"background": """A secretary in the former Mayor’s cabinet, they retained access to the FBI database in order to better help the Mafia identify and eliminate their competition 
within the city.  They do their best to stay under the radar in order to avoid raising suspicion and have their access revoked.""",
				"private_actions": ["investigate"]
			}
		},
                "MK": {
			"Ambusher": {
				"attack": 1,
				"background": """An eager young member of the mafia looking to prove their worth to the Godfather, they are still a little sloppy often leaving behind evidence of their crimes.  
They hope to someday be promoted into the role of Mafioso in order to better server the Mafia.""",
				"private_actions": ["ambush"]
			},
			"Mafioso": {
				"attack": 1,
				"background": """The second in command within the Mafia, hand picked by the current Godfather to someday take over the Mafia themselves.  They want nothing else but to prove 
their worth and step into the leadership role that they were chosen for.""",
				"private_actions": ["attack"],
				"unique": True
			}
		},
                "MP": {
			"Disguiser": {
				"background": """An artist who fell in with the wrong crowd, their natural talent was encourage by the Godfather and they work tirelessly to develop high tech disguises in order 
to ensure that members of the Mafia are unrecognizable even when caught on camera.""",
				"private_actions": ["disguise"]
			}
		},
                "MS": {
			"Corrupt Police Officer": {
				"background": """A police officer who is being paid off by the Godfather to help the Mafia accomplish it’s goals and turn a blind eye to the crimes that they commit.""",
				"private_actions": ["role_block"],
				"role_block_immune": True
			},
			"Corrupt Politician": {
				"background": """A member of the former Mayor’s cabinet who acted as a liaison between the mayor and the Godfather.  They still hold some sway within the city.""",
				"public_actions": ["reveal"],
				"unique": True,
				"role_block_immune": True
			},
			"Diplomat": {
				"background": """A member of the Mafia dedicated to the idea that all of the families should be united under a single banner in order to better control the city.  They spend 
their time attempting to unify the Mafia families of the city.""",
				"private_actions": ["unite"],
				"unique": True
			},
			"Forger": {
				"background": """A coroner within the police department who is being paid off by the Godfather to modify the bodies of Mafia victims in order to prevent them from being properly 
identified.""",
				"private_actions": ["forge"]
			},
			"Godfather": {
				"attack": 1,
				"background": """A childhood friend of the former Mayor, the Godfather became upset when they lost the election and vowed to make the new Mayor regret running for office.  
Targeting businesses and civilians alike, the Godfather has used the Mafia to plunge the city into chaos and anarchy, establishing a kangaroo court in the town square and re-introducing public hangings as a 
means of punishing those who oppose him.""",
				"defense": 1,
				"private_actions": ["attack", "promote"],
				"unique": True,
				"role_block_immune": True
			}
		},
        }, "Vampire Coven": {
		"Data": {
			"alignment": "evil"
		},
                "VK": {
			"Vampire": {
				"attack": 1,
				"background": """The vampire coven views the citizens of the city as a source of food and any group that takes their food from them as an enemy that needs to be eliminated.""",
			}
		}
        }, "Neutral": {
		"Data": {
			"alignment": "neutral"
		},
                "NI": {
			"Executioner": {
				"background": """A former judge, they find the current kangaroo court that the Godfather has set up to be a mockery of the legal system and are dedicated to exposing it’s 
cruelty by using it to execute someone under false pretenses.""",
				"role_block_immune": True,
			}
		},
                "NK": {
			"Jester": {
				"attack": 2,
				"background": """Driven mad by the chaos around them, their sole focus is on finding the sweet release of death through hanging.  It is as if a supernatural force is driving 
them towards seeking this out and they feel as though something wonderful will happen if they are able to achieve their goal.""",
				"private_actions": ["attack"],
				"role_block_immune": True
			}
		},
                "NP": {
			"Guardian Angel": {
				"background": """They were granted mystical abilities one night and felt a deep desire to protect a specific individual within the town.  They don’t understand why they have 
these abilities or why this person is so important but have accepted their role as a protector.""",
				"private_actions": ["protect"],
				"role_block_immune": True
			},
			"Survivor": {
				"background": """They’ve always been a survivalist, stocking up on supplies, preparing for doomsday scenarios and making contingency plans for every possible scenario.  When the 
Mafia started attacking, all of their fears were confirmed and they went into hiding, putting all of their training and preparation to good use.""",
				"private_actions": ["protect"]
			}
		},
                "NS": {
			"Amnesiac": {
				"background": """They suffered a head injury that caused them to lose their long term memory during a Mafia attack and now roam the city looking for clues about who they once 
were.  Every night they feel drawn to visit the local cemetery."""
			},
				"private_actions": ["become"]
		}
        }, "Evil": {
		"Data": {
                        "alignment": "evil"
                },
                "EI": {
			"Cultist": {
				"background": """A former cult member, they were granted unusual abilities by a supernatural force the night that their former cult leader was executed by the city.  They are in 
search of a new charismatic leader who will help them get their revenge.""",
				"private_actions": ["boost"]
			}
		},
                "ES": {
			"Necromancer": {
				"background": """One night a young teen was out late causing trouble when they felt drawn to an alley, there they saw a dead drug dealer.  They touched the drug dealers pocket, 
hoping to steal any cash they had on them, as soon as they touched the clothing the drug dealers eyes snapped open and they screamed in horror that their face had been stolen.  When the teen got home, shaken 
from the encounter they took a look at themself in the mirror and noticed that their body had changed and they now looked just like the drug dealer that they had raised from the dead.""",
				"private_actions": ["resurrect"]
			}
		}
        },
	"Fire Starter": {
		"Data": {
			"alignment": "evil"
		},
		"FK": {
			"Fire Starter": {
				"attack": 2,
				"background": """A librarian by trade, they lived a relatively peaceful life until the day the former mayor passed a law outlawing the possession and distribution of books.  
Soon after the law was passed the cities libraries were closed and their employees were forced to burn the collection they had spent their lives collecting and preserving. For most it was a difficult task, but 
for some it was an awakening which grew into an obsession that carried them far beyond the walls of the library.""",
				"defense": 1,
				"private_actions": ["douse", "ignite"]
			}
		}
	},
	"Renegade": {
		"Data": {
			"alignment": "evil"
		},
		"RK": {
			"Renegade": {
				"attack": 1,
				"background": """Either because of a lack of oversight or a mistake in the clerks office a convicted serial killer has been released onto the streets.  It didn’t take long 
before they started killing again.""",
				"defense": 1,
				"private_actions": ["attack"]
			}
		}
	},
	"Werewolf": {
		"Data": {
			"alignment": "evil"
		},
		"WK": {
			"Werewolf": {
				"attack": 2,
				"background": """When they were young a wolf bit them in the arm, ever since then every other night they transform into a rampaging monster.  They have done their best to avoid 
detection by chaining themself to your bed each night to prevent themself from harming others, but recently they noticed that the chains they were using are starting to fall apart and one of them appears to 
have broken last night.""",
				"defense": 1,
				"private_actions": ["attack"]
			}
		}
	}
}

def display_faction(faction, admin=False):
	response = "{} ({})".format(faction['name'], faction['type'])
	if admin:
		human_readable_players = []
		for player in faction['players']:
			human_readable_players.append(get_player(player)['user_name'])
		response = "{} *Players*: {}".format(response, ", ".join(human_readable_players))

	return response

def display_player(player, admin=False):
	response = "{}".format(player['user_name'])
	if 'status' in player:
		response = "{} ({})".format(response, player['status'])

	if admin:
		response = "{}{}".format(response, get_role_reveal(player))

	return response

def get_all_roles():
	role_list = {}

	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			for role in game_roles[faction][category].keys():
				role_list[role] = {'faction': faction, 'category': category, 'role': role}
				if 'unique' in game_roles[faction][category][role]:
					role_list[role]['unique'] = game_roles[faction][category][role]['unique']

	return role_list

def get_game(player_id):
	return players_in_games[player_id]['game']

def get_faction_by_name(game, faction_name):
	for faction_id in running_games[game]['factions']:
		faction = running_games[game]['factions'][faction_id]
		if faction['name'] == faction_name:
			return faction
	return None

def get_faction(player_id, type):
	for faction_id in running_games[get_game(player_id)]['factions']:
		faction = running_games[get_game(player_id)]['factions'][faction_id]
		if player_id in faction['players'] and faction['type'] == type:
			return faction
	return None

def get_player(player_id):
	return players_in_games[player_id]

def get_player_alive_status(player_id):
	if 'status' in players_in_games[player_id] and players_in_games[player_id]['status'] == 'alive':
		return True
	else:
		return False

def get_role(input_role):
	role_value = {}

	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			for role in game_roles[faction][category].keys():
				if role == input_role:
					role_value = {'faction': faction, 'category': category, 'role': role}
					if 'unique' in game_roles[faction][category][role]:
						role_value['unique'] = game_roles[faction][category][role]['unique']
					return role_value

def get_kills_reveal(player, kills):
	response = []

	for kill in kills:
		if kill['type'] != "hanging":
			response.append("*{}* was killed by a *{}*.".format(player['user_name'], kill['killer_role']))
		else:
			continue

	return response

def get_killed_reveal(player):
	response = []

	for role in player['roles']:
		if 'role_name' in role:
			response.append("*{}* was a *{}*.".format(player['user_name'], role['role_name']))
		else:
			response.append("*{}* was a *-missing data error-*.".format(player['user_name']))

	return response

def get_role_reveal(player):
	response = ""

	for role in player['roles']:
		response = "{}\n\t\t*Role*:".format(response)
		if 'role_name' in role:
			response = "{} {}".format(response, role['role_name'])
		if 'faction' in role:
			response = "{} In The {}".format(response, role['faction'])

	return response

def get_specific_roles(field, values, players=[], required_roles=[]):
	role_list = {}

	current_roles = []
	unassigned_players_count = len(players)
	for player in players:
		player_roles = get_player_roles(player)
		for current_role in get_player_roles(player):
			role = get_role(current_role['role_name'])
			for value in values:
				if role[field].lower().replace(" ", "_") == value.lower().replace(" ", "_"):
					current_roles.append(current_role['role_name'])
					unassigned_players_count -= 1

	for role in required_roles:
		if role not in current_roles:
			role_list[role] = get_role(role)
			if len(role_list) >= unassigned_players_count:
				return role_list

	all_roles = get_all_roles()
	for role in all_roles:
		if 'unique' not in all_roles[role] or role not in current_roles:
			for value in values:
				if all_roles[role][field].lower().replace(" ", "_") == value.lower().replace(" ", "_"):
					role_list[role] = all_roles[role]

	return role_list

def get_all_role_categories():
	role_categories = []
	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			role_categories.append(category)
	return role_categories

def get_channel_id(game, channel):
	current_game = running_games[game]
	if channel == "town":
		return current_game['town_channel_id']
	elif channel == "graveyard":
		return current_game['graveyard_channel_id']
	else:
		for faction_id in current_game['factions'].keys():
			if current_game['factions'][faction_id]['name'] == channel and 'channel_id' in current_game['factions'][faction_id]:
				return current_game['factions'][faction_id]['channel_id']

	return ""

def get_faction_current_players(faction):
	if 'players' in faction:
		return len(faction['players'])
	else:
		return 0

def get_faction_min_players(total_players, faction):
	if faction['size_type'] == "fixed":
		return faction['size']
	else:
		return math.floor(total_players*faction['size']/100)

def get_min_players(game):
	if 'min_players' in running_games[game]:
		return running_games[game]['min_players']
	else:
		return 0

def get_non_assigned_players(game_players):
	non_assigned_players = []

	for player in game_players:
		player_data = game_players[player]
		if 'roles' in player_data and len(player_data['roles']) == 0:
			non_assigned_players.append(player)

	return non_assigned_players

def get_players(game):
	if 'players' in running_games[game]:
		return running_games[game]['players']
	else:
		return []

def get_dead_players(game):
	dead_players = []
	players = get_players(game)
	for player in players:
		if not get_player_alive_status(player):
			dead_players.append(player)

	return dead_players

def get_faction_players(game, player_id, faction_type):
	player_faction = get_faction(player_id, faction_type)
	faction_players = []
	players = get_players(game)
	for player in players:
		if player_faction == get_faction(player, faction_type):
			faction_players.append(player)

	return faction_players

def get_living_players(game):
	living_players = []
	players = get_players(game)
	for player in players:
		if get_player_alive_status(player):
			living_players.append(player)

	return living_players

def get_players_with_role(game, role):
	role_players = []
	players = get_players(game)
	for player in players:
		if 'role_name' in players[player] and players[player]['role_name'].lower() == role:
			role_players.append(player)

	return role_players

# TO DO: Change to using 'role' once that is made an array.
def get_player_roles(player_id):
	result_roles = []
	if 'role_name' in players_in_games[player_id]:
		result_roles.append(players_in_games[player_id])
	return result_roles

def get_factions_with_channels(game):
	factions = []
	for faction_id in running_games[game]['factions']:
		if 'channel_id' in running_games[game]['factions'][faction_id]:
			factions.append(running_games[game]['factions'][faction_id])

	return factions

def get_role_details(selected_role):
	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			for role in game_roles[faction][category]:
				if role == selected_role:
					if 'Data' in game_roles[faction]:
						game_roles[faction][category][role].update(game_roles[faction]['Data'])
					if 'attack' not in game_roles[faction][category][role]:
						game_roles[faction][category][role]['attack'] = 0
					if 'defense' not in game_roles[faction][category][role]:
						game_roles[faction][category][role]['defense'] = 0
					pp.pprint(game_roles[faction][category][role])
					return game_roles[faction][category][role]
	return {}

def get_round(game):
	if 'round' in running_games[game]:
		return running_games[game]['round']
	else:
		return 0

def get_running_game_state(game_name):
	response = ""

	if game_name in running_games:
		game = running_games[game_name]
		response = "{}*Town Name*: {}\n".format(response, game['town_name'])
		if 'round_length' in game:
			response = "{}*Round Length*: {} hours\n".format(response, game['round_length'])
		if 'round' in game:
			response = "{}*Current Round*: {}\n".format(response, game['round'])
		if 'jurors' in game:
			response = "{}*Jurors:* {}\n".format(response, ", ".join(game['jurors'].keys()))

		response = "{}*Factions:*\n".format(response)
		for faction_id in game['factions']:
			faction = game['factions'][faction_id]
			response = "{}*\tFaction* - {}\n".format(response, display_faction(faction, admin=True))

		response = "{}*Living Players:*\n".format(response)
		for player_id in get_living_players(game_name):
			player = get_player(player_id)
			response = "{}*\tPlayer* - {}\n".format(response, display_player(player, admin=True))

		response = "{}*Dead Players:*\n".format(response)
		for player_id in get_dead_players(game_name):
			player = get_player(player_id)
			response = "{}*\tPlayer* - {}\n".format(response, display_player(player, admin=True))
	else:
		response = list(running_games.keys())

	return response

def initialize_game_state():
	dir_path = SAVE_PATH
	open_games = []
	for file in os.listdir(dir_path):
		if file.endswith('.open'):
			open_games.append(file)
	for file in open_games:
		with open("{}/{}".format(dir_path, file), 'r') as openfile:
			game_data = json.load(openfile)
		upload_game_state(game_data)

def upload_game_state(game_data):
	game_name = game_data['town_name_abbreviated']

	if game_name in running_games:
		log.error("Game with this name is already running.")
	else:
		running_games[game_name] = game_data
		if 'players' in game_data:
			for player in game_data['players']:
				players_in_games[player] = game_data['players'][player]
		store_game_state(game_data, "open")

def store_game_state(game_data, state):
	game_object = json.dumps(game_data, indent=4)
	with open("{}/{}.{}".format(SAVE_PATH, game_data['town_name_abbreviated'], state), "w") as outfile:
		outfile.write(game_object)

def action_assign_player_roles(game):
	game_players = get_players(game)
	game_factions = running_games[game]['factions']

	for faction_id in game_factions:
		non_assigned_players = get_non_assigned_players(game_players)
		total_available_players = len(non_assigned_players)
		if total_available_players > 0:
			faction = game_factions[faction_id]

			if 'players' not in faction:
				faction['players'] = []

			faction_min_players = get_faction_min_players(len(game_players), faction)
			faction_current_players = get_faction_current_players(faction)

			faction_player_requirement = faction_min_players - faction_current_players

			if faction_player_requirement > total_available_players:
				faction_player_requirement = total_available_players

			# TO DO: Add logic for unique roles.
			faction_available_roles = get_specific_roles('faction', [faction['type']], players=game_players)

			while(faction_player_requirement > 0):
				role_info = {}
				chosen_player_id = random.choice(list(non_assigned_players))
				chosen_player = game_players[chosen_player_id]

				if faction['type'] != "mafia":
					role_chosen = random.choice(list(faction_available_roles.items()))
					role_info['role_name'] = role_chosen[0]
					role_info['role_faction'] = role_chosen[1]['faction']
					role_info['role_category'] = role_chosen[1]['category']
				role_info['faction'] = faction['name']
				role_info['faction_type'] = faction['type']
				chosen_player['status'] = 'alive'
				chosen_player['deaths'] = []
				chosen_player['revealed_info'] = []
				assign_role_to_player(role_info, chosen_player)

				players_in_games[chosen_player_id] = chosen_player

				faction['players'].append(chosen_player_id)

				non_assigned_players = get_non_assigned_players(game_players)
				faction_player_requirement -= 1

	keep_factions = {}
	for faction_id in game_factions:
		faction = game_factions[faction_id]
		if 'players' in faction and len(faction['players']) > 0:
			keep_factions[faction_id] = faction

	running_games[game]['factions'] = keep_factions
	if len(non_assigned_players) > 0:
		default_roles = get_specific_roles('category', running_games[game]['default_roles'], players=game_players)
		for player_id in non_assigned_players:
			role_info = {}
			player = running_games[game]['players'][player_id]
			role_chosen = random.choice(list(default_roles.items()))
			role_info['role_name'] = role_chosen[0]
			role_info['role_faction'] = role_chosen[1]['faction']
			role_info['role_category'] = role_chosen[1]['category']
			player['status'] = 'alive'
			player['deaths'] = []
			player['revealed_info'] = []
			assign_role_to_player(role_info, player)

			players_in_games[player_id] = player 

def assign_role_to_player(role_info, player):
	updated = False
	for role_id, role in enumerate(player['roles']):
		if 'faction' in role and 'faction' in role_info and role['faction'] == role_info['faction']:
			updated = True
			player['roles'][role_id] = role_info

	if not updated:
		player['roles'].append(role_info)

def record_action(game, player_id, channel_id, action_data):
	round_night_info = command_initialize_round(game)['night']
	action_storage_location = round_night_info['actions']

	action_data.update({'user': player_id})

	for faction_id in running_games[game]['factions']:
		faction = running_games[game]['factions'][faction_id]
		if 'channel_id' in faction and channel_id == faction['channel_id']:
			action_storage_location = round_night_info['faction'][faction['name']]

	if player_id in action_storage_location and action_storage_location[player_id] == action_data:
		del action_storage_location[player_id]
		return False
	else:
		action_storage_location[player_id] = action_data
		return True

def round_gather_actions(game, round_night_info, round_output_info):
	actions_count = 0
	actions = []

	for faction_name in round_night_info['faction']:
		faction = get_faction_by_name(game, faction_name)
		### TO DO: Godfather overriding mafioso action. ###
		if 'vampire_coven' == faction['type']:
			if 'action' not in faction:
				faction['action'] = 'convert'
			if faction['action'] != 'standard':
				for vampire in faction['players']:
					if get_player_alive_status(vampire):
						# These are recorded but don't count as their own unique action.
						actions.append({'type': 'vampire_role_block', 'user': vampire, 'faction': faction_name})
		for action_id in round_night_info['faction'][faction_name]:
			if action_id in players_in_games:
				round_night_info['faction'][faction_name][action_id].update({'faction': faction_name})
				actions.append(round_night_info['faction'][faction_name][action_id])
				actions_count += 1

	for action_id in round_night_info['actions']:
		if action_id in players_in_games:
			actions.append(round_night_info['actions'][action_id])
			actions_count += 1

	round_output_info['actions'] = actions
	round_output_info['actions_taken'] = actions_count

def round_process_actions(game_name, round_night_info, round_output_info):
	game = running_games[game_name]

	round_output_info['messages'] = []

	# Possess
	# Role Block
	process_actions_role_block(game_name, round_night_info, round_output_info)
	# Douse
	# Examine
	process_actions_examine(game_name, round_night_info, round_output_info)
	# Player Modification
	# Ressurection
	# Role Change
	# Random Number Generator
	# Investigation
	# Mafia Merge
	# Mulitple Attack
	# Attack
	# Event

def process_actions_examine(game_name, round_night_info, round_output_info):
	game = running_games[game_name]

	examinations = {}

	for action in round_output_info['actions']:
		kills_info = []
		killed_info = []
		if action['type'] == 'examine':
			target_player_id = action['value']
			target_player = get_player(action['value'])
			player_deaths = target_player['deaths']
			kills_info = get_kills_reveal(target_player, player_deaths)
			killed_info = get_killed_reveal(target_player)
		elif action['type'] == 'forge':
			target_player_id = action['forged']
			target_player = get_player(action['forged'])
			forged_player = {"user_name": target_player['user_name'], 'roles': [{"role_name": action['forged_role']}]}
			player_deaths = [action]
			kills_info = get_kills_reveal(forged_player, player_deaths)
			killed_info = get_killed_reveal(forged_player)

		if target_player_id not in examinations:
			examinations[target_player_id] = {'kills': [], 'killed': []}

		examinations[target_player_id]['kills'] += kills_info
		examinations[target_player_id]['kills'].sort()
		examinations[target_player_id]['killed'] += killed_info
		examinations[target_player_id]['killed'].sort()

	channel = get_channel_id(game_name, "town")

	for player in examinations:
		for kill in examinations[player]['kills']:
			if kill not in game['players'][player]['revealed_info']:
				game['players'][player]['revealed_info'].append(kill)
			record_message(round_output_info, channel, kill)
		for killed in examinations[player]['killed']:
			if killed not in game['players'][player]['revealed_info']:
				game['players'][player]['revealed_info'].append(killed)
			record_message(round_output_info, channel, killed)

def process_actions_role_block(game, round_night_info, round_output_info):
	role_blocks = []
	for action in round_output_info['actions']:
		if 'role_block' in action['type']:
			role_blocks.append(action)

	for role_block in role_blocks:
		action = role_block
		if 'faction' in action:
			channel = get_channel_id(game, action['faction'])
		else:
			channel = action['user']
		if action['type'] == 'role_block':
			target = get_player(action['target'])
			message = "{} has been prevented from doing anything.".format(player['user_name'])
			process_handle_role_block(round_output_info, action['user'], action['target'])
			record_message(round_output_info, channel, message)
		elif action['type'] == 'vampire_role_block':
			process_handle_role_block(round_output_info, action['user'], action['user'], action['faction'])

def process_handle_role_block(round_output_info, user_name, target_name, faction=''):
	user = get_player(user_name)
	target = get_player(target_name)

	role_block_immune = False
	role_blocked_actions = []

	for role in target['roles']:
		role_details = get_role_details(role['role_name'])
		if 'role_block_immune' in role_details and role_details['role_block_immune']:
			role_block_immune = role_details['role_block_immune']

	for action in round_output_info['actions']:
		if action['user'] == target_name:
			if 'faction' in action:
				channel = get_channel_id(target['game'], action['faction'])
				noun = "you"
			else:
				channel = target_name
				noun = target['user_name']
			# Skip when it's vampire role block on self during vampire action.
			if user == target and 'faction' in action and action['faction'] == faction:
				continue
			elif role_block_immune:
				message = "Somebody tried to role block {}, but *you are immune*.".format(noun)
			else:
				message = "Somebody *role blocked {}*.".format(noun)
				role_blocked_actions.append(action)

			record_message(round_output_info, channel, message)

	for action in role_blocked_actions:
		round_output_info['actions'].remove(action)

def process_round(game, debug = False):
	result = {}

	round_info = command_initialize_round(game)
	round_night_info = round_info['night']
	if 'night_output' not in round_info:
		round_info['night_output'] = {}
	round_output_info = round_info['night_output']

#	round_assign_unassigned_players(game)
	round_gather_actions(game, round_night_info, round_output_info)
	round_process_actions(game, round_night_info, round_output_info)
#	result = round_output_cleanup(game, round_night_info, round_output_info)

	return result

def record_message(round_output_info, message, channel):
	round_output_info['messages'].append({"channel": channel, "message": message})

def collect_vote(user, vote, game_name, type='vote', location_override=''):
	if location_override == '':
		game_round = command_initialize_round(game_name)['day']
	else:
		game_round = location_override

	if type not in game_round:
		game_round[type] = {}

	if vote not in game_round[type]:
		game_round[type][vote] = []

	if user in game_round[type][vote] or type != 'action' and not get_player_alive_status(vote):
		return False
	else:
		game_round[type][vote].append(user)
		return True

def command_action_choose_role(user, role_selection):
	user_id = user['user_id']
	user_name = user['user_name']

	game = players_in_games[user_id]['game']

	faction = get_faction(user_id, 'mafia')
	available_roles = get_specific_roles('faction', [faction['type']], players=faction['players'], required_roles=['Godfather', 'Mafioso'])

	if role_selection not in available_roles:
		return list(available_roles.keys())
	else:
		player = running_games[players_in_games[user_id]['game']]['players'][user_id]

		role_info = {}
		role_info['role_name'] = available_roles[role_selection]['role']
		role_info['role_faction'] = available_roles[role_selection]['faction']
		role_info['role_category'] = available_roles[role_selection]['category']
		role_info['faction'] = faction['name']
		role_info['faction_type'] = faction['type']
		assign_role_to_player(role_info, player)

		players_in_games[user_id] = player

		store_game_state(running_games[game], "open")

		return "{} has chosen the {}!".format(user_name, role_selection)

def command_available_game_commands(user_id):
	game_commands = []

	if user_id in players_in_games:
		game_commands = ['leave']
		if 'round' in running_games[players_in_games[user_id]['game']]:
			game_commands.append('list')
			game_commands.append('role')
	else:
		game_commands.append('join')

	return game_commands

def command_available_private_actions(user_id):
	private_actions = {}
	private_actions[''] = []

	player = get_player(user_id)

	for role in player['roles']:
		faction = {}
		role_actions = []

		if 'faction_type' in role:
			faction = get_faction(user_id, role['faction_type'])
		if 'role_name' in role:
			role_details = get_role_details(role['role_name'])
			if 'private_actions' in role_details:
				role_actions = role_details['private_actions']

		if 'channel_id' in faction:
			if faction['type'] == 'vampire_coven':
				if 'action' in faction:
					if faction['action'] == "attack":
						role_actions.append("attack")
					if faction['action'] == "convert" and 'charge' in faction and faction['charge'] + 1 >= len(faction['players']):
						role_actions.append("convert")
				else:
					role_actions.append("action")
			elif faction['type'] == 'mafia' and len(role_actions) == 0:
				role_actions.append("choose")
			private_actions[faction['channel_id']] = role_actions
		else:
			for action in role_actions:
				private_actions[''].append(action)

	return private_actions

def command_available_public_actions(user_id):
	public_actions = []

	game = get_game(user_id)

	if user_id in players_in_games:
		public_actions = []
		if 'role_name' in players_in_games[user_id]:
			role_details = get_role_details(players_in_games[user_id]['role_name'])

			if 'public_actions' in role_details:
				for public_action in role_details['public_actions']:
					public_actions.append(public_action)

		if 'jurors' in running_games[game] and len(running_games[game]['jurors']) < 3:
			public_actions.append('vote')

		if 'jurors' in running_games[game] and user_id in running_games[game]['jurors'] and len(running_games[game]['round_data'][str(running_games[game]['round'])]['day']['hanging']) == 0:
			public_actions.append('hang')

	return public_actions

def command_default_channels_for_game(game):
	town_channel = "{}_town_square".format(game)
	graveyard_channel = "{}_graveyard".format(game)

	if 'town_channel_id' in running_games[game]:
		town_channel = ""
	if 'graveyard_channel_id' in running_games[game]:
		graveyard_channel = ""

	return town_channel, graveyard_channel

def command_channels_for_game(game):
	faction_channels = []
	for faction_id in running_games[game]['factions'].keys():
		faction_type = running_games[game]['factions'][faction_id]["type"]
		faction_name = running_games[game]['factions'][faction_id]["name"].lower().replace(" ", "_")

		if 'players' in running_games[game]['factions'][faction_id] and len(running_games[game]['factions'][faction_id]['players']) > 0 and 'channel_id' not in running_games[game]['factions'][faction_id]:
			if faction_type == 'vampire_coven':
				faction_channels.append({'channel_name': "{}_{}_vampire_coven".format(game, faction_name), 'faction_id': faction_id})
			if faction_type == 'mafia':
				faction_channels.append({'channel_name': "{}_{}_family_mafia".format(game, faction_name), 'faction_id': faction_id})

	return faction_channels

def command_game_action(user, vote_action):
	user_id = user['user_id']
	user_name = user['user_name']

	game = get_game(user_id)
	faction = get_faction(user_id, "vampire_coven")

	response_channel = user_id

	actions = ACTIONS
	vote_cast = False

	round_night_info = command_initialize_round(game)['night']
	faction_round_night_info = round_night_info['faction'][faction['name']]

	for action in actions:
		if action == vote_action:
			if collect_vote(user_id, action, game, type='action', location_override=faction_round_night_info):
				vote_cast = True
				current_vote = len(faction_round_night_info['action'][vote_action])
				total_votes_needed = math.floor(len(faction['players'])/2) + 1
				if current_vote >= total_votes_needed:
					response = "{} has voted on action {}".format(user_name, action)
					if action != "convert" or 'charge' in faction and faction['charge'] == len(faction['players']) - 1:
						response = "{}.  The {} will perform action {} tonight.".format(response, faction['name'], action)
					else:
						response = "{}.  The {} will prepare to perform action {} at a later date.".format(response, faction['name'], action)
					faction['action'] = action
					faction_round_night_info['action_selected'] = {"type": "action", "value": action}
				else:
					response = "{} has voted on action {}.  {} more votes needed to perform action {}.\n\n  To vote for this action, you can use the command:\n/mafia_private_action action {}".format(user_name, action, total_votes_needed - current_vote, action, action)
				response_channel = faction['channel_id']

				store_game_state(running_games[game], "open")
			else:
				vote_cast = True
				response = "You have already voted on action {} today.".format(action)

	if not vote_cast:
		response = list(actions)

	return response_channel, response

def command_game_attack_no_target(user, death_note, type):
	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	action_data = {"type": type, "value": "alert", "death_note": death_note}

	if not record_action(game, player_id, channel_id, action_data):
		response = "{} has decided not to {}.".format(user['user_name'], type)
	else:
		response = "{} has decided to {}.".format(user['user_name'], type)
		if len(death_note) > 0:
			response = "{}  They will leave the following death note \"{}\".".format(response, death_note)

	store_game_state(running_games[game], "open")

	return response

def command_game_attack(user, target_name, death_note, type = "attack"):
	response = ""

	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	living_players = get_living_players(game)
	living_players_human_readable = []

	for living_player in living_players:
		target = get_player(living_player)
		living_players_human_readable.append(target['user_name'])
		if target_name.replace('@', '') == target['user_name']:
			action_data = {"type": type, "value": living_player, "death_note": death_note}
			if not record_action(game, player_id, channel_id, action_data):
				response = "{} has decided not to {} {}.".format(user['user_name'], type, target['user_name'])
			else:
				response = "{} has decided to {} {}.".format(user['user_name'], type, target['user_name'])
				if len(death_note) > 0:
					response = "{}  They will leave the following death note \"{}\".".format(response, death_note)

			store_game_state(running_games[game], "open")

	if len(response) == 0:
		response = list(living_players_human_readable)

	return response

def command_game_basic_action(user, target_name, type = ""):
	response = ""

	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	living_players = get_living_players(game)
	living_players_human_readable = []

	for living_player in living_players:
		target = get_player(living_player)
		living_players_human_readable.append(target['user_name'])
		if target_name.replace('@', '') == target['user_name']:
			action_data = {"type": type, "value": living_player}
			if not record_action(game, player_id, channel_id, action_data):
				response = "{} has decided not to {} a user.".format(user['user_name'], type)
			else:
				response = "{} has decided to {} {}.".format(user['user_name'], type, target['user_name'])

			store_game_state(running_games[game], "open")

	if len(response) == 0:
		response = list(living_players_human_readable)

	return response

def command_game_basic_action_dead(user, target_name, type = ""):
	response = ""

	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	dead_players = get_dead_players(game)
	dead_players_human_readable = []

	for dead_player in dead_players:
		target = get_player(dead_player)
		dead_players_human_readable.append(target['user_name'])
		if target_name.replace('@', '') == target['user_name']:
			action_data = {"type": type, "value": dead_player}
			if not record_action(game, player_id, channel_id, action_data):
				response = "{} has decided not to {} {}.".format(user['user_name'], type, target['user_name'])
			else:
				response = "{} has decided to {} {}.".format(user['user_name'], type, target['user_name'])

			store_game_state(running_games[game], "open")

	if len(response) == 0:
		response = list(dead_players_human_readable)

	return response

def command_game_apparate(user):
	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	action_data = {"type": "apparate", "value": "apparate"}

	if not record_action(game, player_id, channel_id, action_data):
		response = "{} has decided not to appear in town.".format(user['user_name'])
	else:
		response = "{} has decided to appear in town.".format(user['user_name'])

	store_game_state(running_games[game], "open")

	return response

def command_game_disguise(user, disguised_name, disguise_name):
	response = ""
        
	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)
        
	living_players = get_living_players(game)
	living_players_human_readable = []

	faction_players = get_faction_players(game, player_id, faction_type = "mafia")
	faction_players_human_readable = []

	disguised = ""
	disguise = ""

	for living_player in living_players:
		target = get_player(living_player)
		living_players_human_readable.append(target['user_name'])
		if disguise_name.replace('@', '') == target['user_name']:
			disguise = living_player
		if living_player in faction_players:
			faction_players_human_readable.append(target['user_name'])
			if disguised_name.replace('@', '') == target['user_name']:
				disguised = living_player

	if disguised == "" or disguise == "":
		response = {
			'living_players': living_players_human_readable,
			'faction_players': faction_players_human_readable
		}
	else:
		action_data = {"type": "disguise", "disguised": disguised, "disguise": disguise}

		if not record_action(game, player_id, channel_id, action_data):
			response = "{} has decided not to disguise {} as {}.".format(user['user_name'], disguised_name, disguise_name)
		else:
			response = "{} has decided to disguise {} as {}.".format(user['user_name'], disguised_name, disguise_name)
                
		store_game_state(running_games[game], "open")		

	return response

def command_game_forge(user, forged_name, forged_role_name, killer_role_name):
	response = ""

	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	dead_players = get_dead_players(game)
	dead_players_human_readable = []

	all_roles = get_all_roles()
	all_roles_human_readable = []

	forged = ""
	forged_role = ""
	killer_role = ""

	for dead_player in dead_players:
		target = get_player(dead_player)
		dead_players_human_readable.append(target['user_name'])
		if forged_name.replace('@', '') == target['user_name']:
			forged = dead_player

	for role in all_roles:
		all_roles_human_readable.append(role)
		if forged_role_name.lower() == role.lower():
			forged_role = role
		if killer_role_name.lower() == role.lower():
			killer_role = role

	if forged == "" or forged_role == "" or killer_role == "":
		response = {
			'dead_players': dead_players_human_readable,
			'roles': all_roles_human_readable
		}

	else:
		action_data = {"type": "forge", "forged": forged, "forged_role": forged_role, "killer_role": killer_role}
		if not record_action(game, player_id, channel_id, action_data):
			response = "{} has decided not to forge {} as {} killed by {}.".format(user['user_name'], forged_name, forged_role, killer_role)
		else:
			response = "{} has decided to forge {} as {} killed by {}.".format(user['user_name'], forged_name, forged_role, killer_role)
		store_game_state(running_games[game], "open")

	return response

def command_game_hang(user, hanging_user):
	user_id = user['user_id']
	user_name = user['user_name']

	game = players_in_games[user_id]['game']

	response_channel = user_id

	game_players = running_games[game]['players']
	game_players_human_readable = {}
	hanging_vote_cast = False

	for player in game_players:
		if get_player_alive_status(player):
			game_players_human_readable[game_players[player]['user_name']] = True
			if hanging_user['user_id'] == player:
				if collect_vote(user_id, hanging_user['user_id'], game, type="hang_vote"):
					hanging_vote_cast = True
					round_info = running_games[game]['round_data'][str(running_games[game]['round'])]
					round_day_info = round_info['day']
					current_votes = len(round_day_info['hang_vote'][hanging_user['user_id']])
					total_votes_needed = len(running_games[game]['jurors'])
					if current_votes >= total_votes_needed:
						round_info['day']['hanging'][hanging_user['user_id']] = True
						game_players[player]['status'] = 'dead'

						if 'deaths' not in game_players[player]:
							game_players[player]['deaths'] = []
						game_players[player]['deaths'].append({"round": running_games[game]['round'], "type": "hanging"})

						if 'revealed_info' not in game_players[player]:
							game_players[player]['revealed_info'] = []
						game_players[player]['revealed_info'].append(get_role_reveal(game_players[player]))

						players_in_games[player] = game_players[player]
						response = "{} has voted to hang {}.  {} by judgement of the town, you will be hung by the neck{}".format(user_name, hanging_user['user_name'], 
hanging_user['user_name'], get_role_reveal(game_players[player]))
					else:
						response = "{} has voted to hang {}.  {} more votes needed to hang {}.\n\n  To vote for as player to be hung, you can use the command:\n/mafia_public_action hang {}".format(user_name, hanging_user['user_name'], total_votes_needed - current_votes, hanging_user['user_name'], hanging_user['user_name'])
					response_channel = running_games[game]['town_channel_id']

					store_game_state(running_games[game], "open")
				else:
					hanging_vote_cast = True
					response = "You have already voted to hang {} today.".format(hanging_user['user_name'])

	if not hanging_vote_cast:
		response = list(game_players_human_readable.keys())

	return response_channel, response

def command_game_join(meta_data, game):
	user_id = meta_data['user_id']

	if user_id in players_in_games:
		response = "You are already in a game.".format(user_id)
		response_channel = user_id
	else:
		if game in running_games:
			if 'left_game' in running_games[game] and user_id in running_games[game]['left_game']:
				players_in_games[user_id] = running_games[game]['left_game'][user_id]
				del running_games[game]['left_game'][user_id]

				response = "{} is rejoining {}.".format(meta_data['user_name'], game)
			else:
				players_in_games[user_id] = {}
				players_in_games[user_id]['game'] = game
				players_in_games[user_id]['user_name'] = meta_data['user_name']
				players_in_games[user_id]['roles'] = []

				if 'players' not in running_games[game]:
					running_games[game]['players'] = {}

				response = "{} is joining {}.".format(meta_data['user_name'], game)
			running_games[game]['players'][user_id] = players_in_games[user_id]

			response_channel = running_games[game]['town_channel_id']

			if 'round' in running_games[game]:
				action_assign_player_roles(game)

			store_game_state(running_games[game], "open")
		else:
			running_games_output = []
			for game in running_games.keys():
				if 'round' in running_games[game]:
					running_games_output.append("{} (Status: Round {}, Min Players: {}, Current Players: {})".format(game, get_round(game), get_min_players(game), len(get_players(game))))
				else:
					running_games_output.append("{} (Status: Not Started, Min Players: {}, Current Players: {})".format(game, get_min_players(game), len(get_players(game))))

			response = running_games_output
			response_channel = user_id

	return response_channel, response

def command_game_vision(user, vision_type_name):
	response = ""

	channel_id = user['channel_id']
	player_id = user['user_id']
	game = get_game(player_id)

	vision_types = ['Good', 'Evil']

	vision_type = ""

	for type in vision_types:
		if type.lower() == vision_type_name.lower():
			vision_type = type

	if vision_type == "":
		response = vision_types
	else:
		action_data = {"type": "vision", "vision": vision_type}
		if not record_action(game, player_id, channel_id, action_data):
			response = "{} has decided not to get {} vision.".format(user['user_name'], vision_type)
		else:
			response = "{} has decided to get {} vision.".format(user['user_name'], vision_type)

	return response	

def command_game_vote(user, voted_user):
	user_id = user['user_id']
	user_name = user['user_name']

	game = players_in_games[user_id]['game']

	response_channel = user_id

	game_players = running_games[game]['players']
	game_players_human_readable = {}
	vote_cast = False

	for player in game_players:
		if get_player_alive_status(player) and player not in running_games[game]['jurors']:
			game_players_human_readable[game_players[player]['user_name']] = True
			if voted_user['user_id'] == player:
				if collect_vote(user_id, voted_user['user_id'], game):
					vote_cast = True
					round_info = running_games[game]['round_data'][str(running_games[game]['round'])]
					round_day_info = round_info['day']
					current_votes = len(round_day_info['vote'][voted_user['user_id']])
					total_votes_needed = round_info['required_vote']
					if current_votes >= total_votes_needed:
						running_games[game]['jurors'][voted_user['user_id']] = {'until_round': running_games[game]['round']+2}
						if len(running_games[game]['jurors']) == 3:
							response = "*{} has voted for {}*. {} has been elected juror with {} votes! All juror spots have been filled, jurors please deliberate and cast your votes on who to hang.\n\n To case a vote on who to hang, you can use the command:\n /mafia_public_action hang player".format(user_name, voted_user['user_name'], voted_user['user_name'], current_votes)
						else:
							response = "*{} has voted for {}*. {} has been elected juror with {} votes!  There are {} remaining juror roles to fill.".format(user_name, voted_user['user_name'], voted_user['user_name'], current_votes, 3-len(running_games[game]['jurors']))
					else:
						response = "*{} has voted for {}* as juror, {} more votes needed to be elected.\n\n  To vote for {} as juror, you can use the command:\n/mafia_public_action vote {}".format(user_name, voted_user['user_name'], total_votes_needed-current_votes, voted_user['user_name'], voted_user['user_name'])
					response_channel = running_games[game]['town_channel_id']

					store_game_state(running_games[game], "open")
				else:
					vote_cast = True
					response = "You have already voted for {} today.".format(voted_user['user_name'])

	if not vote_cast:
		response = list(game_players_human_readable.keys())

	return response_channel, response

def command_game_leave(meta_data):
	response = "{} has left the game...".format(meta_data['user_name'])

	user_id = meta_data['user_id']

	if user_id in players_in_games:
		del players_in_games[user_id]
	else:
                response = "Something has gone wrong, please try again later."
                response_channel = user_id
	for game in running_games:
		if 'players' in running_games[game] and user_id in running_games[game]['players']:
			user_info = running_games[game]['players'][user_id]
			if 'left_game' not in running_games[game]:
				running_games[game]['left_game'] = {}
			running_games[game]['left_game'][user_id] = user_info
			del running_games[game]['players'][user_id]

			response_channel = running_games[game]['town_channel_id']

			store_game_state(running_games[game], "open")

	return response_channel, response

def command_game_progress(game):
	if game in running_games:
		process_round(game)
#		running_games[game]['round'] += 1
#		command_initialize_round(game)

		store_game_state(running_games[game], "open")
		return "*Progressing game {} to round {}.*".format(game, running_games[game]['round'])
	else:
		return list(running_games.keys())

def command_game_start(game):
	if game in running_games:
		if 'players' in running_games[game] and len(running_games[game]['players']) >= running_games[game]['min_players']:
			if 'round' not in running_games[game]:
				running_games[game]['round'] = 1
				running_games[game]['jurors'] = {}
				command_initialize_round(game)
				action_assign_player_roles(game)

				store_game_state(running_games[game], "open")
				return "*Starting game {}.*".format(game)
			else:
				return "*Game {} is already running.*".format(game)
		else:
			return "*Game {} has not met minimum player requirement.*".format(game)
	else:
		return list(running_games.keys())

def command_store_default_channel_information(game, town_channel_id, graveyard_channel_id):
	running_games[game]['town_channel_id'] = town_channel_id
	running_games[game]['graveyard_channel_id'] = graveyard_channel_id

	store_game_state(running_games[game], "open")

def command_store_channel_information(game, faction_channels):
	for faction_channel in faction_channels:
		running_games[game]['factions'][faction_channel['faction_id']]['channel_id'] = faction_channel['channel_id']

	store_game_state(running_games[game], "open")

def command_initialize(game_data):
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

	upload_game_state(game_data)

def command_initialize_round(game_name):
	game = running_games[game_name]

	round = "0"
	if 'round' in game:
		round = str(game['round'])

	if 'round_data' not in game:
		game['round_data'] = {}

	if round not in game['round_data']:
		game['round_data'][round] = {}

	if 'required_vote' not in game['round_data'][round]:
		if int(round) - 1 not in game['round_data']:
			total_votes = len(game['players'])
		else:
			total_votes = game['round_data'][round-1]['night_output']['actions_taken']

		game['round_data'][round]['required_vote'] = math.floor(total_votes/2) + 1

	if 'night' not in game['round_data'][round]:
		game['round_data'][round]['night'] = {}

	if 'faction' not in game['round_data'][round]['night']:
		game['round_data'][round]['night']['faction'] = {}

	for faction_id in game['factions']:
		faction = game['factions'][faction_id]
		if faction['name'] not in game['round_data'][round]['night']['faction']:
			game['round_data'][round]['night']['faction'][faction['name']] = {}

	if 'actions' not in game['round_data'][round]['night']:
		game['round_data'][round]['night']['actions'] = {}

	if 'day' not in game['round_data'][round]:
		game['round_data'][round]['day'] = {}

	if 'vote' not in game['round_data'][round]['day']:
		game['round_data'][round]['day']['vote'] = {}

	if 'hang_vote' not in game['round_data'][round]['day']:
		game['round_data'][round]['day']['hang_vote'] = {}

	if 'hanging' not in game['round_data'][round]['day']:
		game['round_data'][round]['day']['hanging'] = {}

	return game['round_data'][round]

def command_intro_message(game, player):
	response = ""

	player_data = running_games[game]['players'][player]

	for role_data in player_data['roles']:
		if 'role_name' in role_data:
			role = role_data['role_name']
	
			role_details = get_role_details(role)

			background = "{}{}".format(response, role_details['background'])

			response = "{}{}\n\nYou are the *{}*.\n\n".format(response, background, role)

			if 'private_actions' in role_details:
				for private_action in role_details['private_actions']:
					response = "{}/mafia_private_action {}\n".format(response, private_action)

			if 'public_actions' in role_details:
				for public_action in role_details['public_actions']:
					response = "{}/mafia_public_action {}\n".format(response, public_action)

	return response
