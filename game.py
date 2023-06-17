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

DEFAULT_ROLES = ['NI', 'NK', 'NP', 'NS', 'EI', 'ES']
MIN_PLAYERS = 10
ROUND_LENGTH = 24
TOWN_NAME = "TOWN"
MIN_FACTION_SIZE = 1

game_roles={
        "Town": {
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
				"background": """One day after returning home from work you stumbled upon your spouse laying in bed with two deep puncture marks on her neck.  When you checked their pulse, you 
found none and their skin was cold to the touch, just before dialing 911 you called their name and their eyes snapped open at the sound of your voice.  They launched from the bed and lunged at you but you were 
quicker and happened to grab a piece of splintered wood that had been sitting on top of the nightstand, stabbing them in the chest.  As they died in your arms you realized that it was your duty to prevent this 
fate from happening to anyone else.""",
				"private_actions": ["investigate", "stake"]
			},
			"Veteran": {
				"background": """You returned home from war only to find yourself in a new kind of war on the streets of the city you grew up in.  Wracked with PTSD and enough combat training 
to make you a threat to anyone who would dare stand against you, you hunker down in your home waiting for the perfect opportunity to strike back.""",
				"private_actions": ["alert"]
			},
			"Vigilante": {
				"background": """You walk the streets at night, safe in the knowledge that you alone can save the day.  With just a gun and the vague notion of justice on your side, you have 
decided to take the city back, even if you have to do it yourself.""",
				"private_actions": ["attack"]
			}
		},
                "TP": {
			"Bodyguard": {
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
				"public_actions": ["reveal"]
			},
			"Medium": {
				"background": """A gravedigger, one night you thought you heard voices coming from one of the freshly filled grave’s in the graveyard.  Over time you have come to accept and 
even look forward to hearing the voices of the dead while you work.""",
				"private_actions": ["apparate"]
			},
			"Police Officer": {
				"background": """One of the few police officers who refused to take money from the Godfather, you do your best to do your job while also staying vigilant for the knife that your 
fellow officers might be preparing to stab you in the back with.""",
				"private_actions": ["role_block"]
			},
			"Resurrectionist": {
				"background": """One night your apartment was broken into by members of the Mafia who demanded payment from your roommate, when they could not pay up they were executed and left 
for dead.  You arrived home from a late shift to find their dead body, but when you went to check their vital signs they were miraculously returned to life.  The two of you swore to keep your secret safe, in 
order to prevent the Mafia from exploit it.""",
				"private_actions": ["resurrect"]
			}
		}
        }, "Mafia": {
                "MI": {
			"Consigliere": {
				"background": """A secretary in the former Mayor’s cabinet, they retained access to the FBI database in order to better help the Mafia identify and eliminate their competition 
within the city.  They do their best to stay under the radar in order to avoid raising suspicion and have their access revoked.""",
				"private_actions": ["investigate"]
			}
		},
                "MK": {
			"Ambusher": {
				"background": """An eager young member of the mafia looking to prove their worth to the Godfather, they are still a little sloppy often leaving behind evidence of their crimes.  
They hope to someday be promoted into the role of Mafioso in order to better server the Mafia.""",
				"private_actions": ["ambusher"]
			},
			"Mafioso": {
				"background": """The second in command within the Mafia, hand picked by the current Godfather to someday take over the Mafia themselves.  They want nothing else but to prove 
their worth and step into the leadership role that they were chosen for.""",
				"private_actions": ["attack"]
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
				"private_actions": ["role_block"]
			},
			"Corrupt Politician": {
				"background": """A member of the former Mayor’s cabinet who acted as a liaison between the mayor and the Godfather.  They still hold some sway within the city.""",
				"public_actions": ["reveal"]
			},
			"Diplomat": {
				"background": """A member of the Mafia dedicated to the idea that all of the families should be united under a single banner in order to better control the city.  They spend 
their time attempting to unify the Mafia families of the city.""",
				"private_actions": ["unite"]
			},
			"Forger": {
				"background": """A coroner within the police department who is being paid off by the Godfather to modify the bodies of Mafia victims in order to prevent them from being properly 
identified.""",
				"private_actions": ["forge"]
			},
			"Godfather": {
				"background": """A childhood friend of the former Mayor, the Godfather became upset when they lost the election and vowed to make the new Mayor regret running for office.  
Targeting businesses and civilians alike, the Godfather has used the Mafia to plunge the city into chaos and anarchy, establishing a kangaroo court in the town square and re-introducing public hangings as a 
means of punishing those who oppose him.""",
				"private_actions": ["attack", "promote"]
			}
		},
        }, "Vampire Coven": {
                "VK": {
			"Vampire": {
				"background": """The vampire coven views the citizens of the city as a source of food and any group that takes their food from them as an enemy that needs to be eliminated.""",
				"private_actions": ["action", "attack", "convert"]
			}
		}
        }, "Neutral": {
                "NI": {
			"Executioner": {
				"background": """A former judge, they find the current kangaroo court that the Godfather has set up to be a mockery of the legal system and are dedicated to exposing it’s 
cruelty by using it to execute someone under false pretenses."""
			}
		},
                "NK": {
			"Jester": {
				"background": """Driven mad by the chaos around them, their sole focus is on finding the sweet release of death through hanging.  It is as if a supernatural force is driving 
them towards seeking this out and they feel as though something wonderful will happen if they are able to achieve their goal.""",
				"private_actions": ["attack"]
			}
		},
                "NP": {
			"Guardian Angel": {
				"background": """They were granted mystical abilities one night and felt a deep desire to protect a specific individual within the town.  They don’t understand why they have 
these abilities or why this person is so important but have accepted their role as a protector.""",
				"private_actions": ["protect"]
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
		"FK": {
			"Fire Starter": {
				"background": """A librarian by trade, they lived a relatively peaceful life until the day the former mayor passed a law outlawing the possession and distribution of books.  
Soon after the law was passed the cities libraries were closed and their employees were forced to burn the collection they had spent their lives collecting and preserving. For most it was a difficult task, but 
for some it was an awakening which grew into an obsession that carried them far beyond the walls of the library.""",
				"private_actions": ["douse", "ignite"]
			}
		}
	},
	"Renegade": {
		"RK": {
			"Renegade": {
				"background": """Either because of a lack of oversight or a mistake in the clerks office a convicted serial killer has been released onto the streets.  It didn’t take long 
before they started killing again.""",
				"private_actions": ["attack"]
			}
		}
	},
	"Werewolf": {
		"WK": {
			"Werewolf": {
				"background": """When they were young a wolf bit them in the arm, ever since then every other night they transform into a rampaging monster.  They have done their best to avoid 
detection by chaining themself to your bed each night to prevent themself from harming others, but recently they noticed that the chains they were using are starting to fall apart and one of them appears to 
have broken last night.""",
				"private_actions": ["attack"]
			}
		}
	} }

def get_all_roles():
	role_list = {}

	for faction in game_roles.keys():
		for category in game_roles[faction].keys():
			for role in game_roles[faction][category].keys():
				role_list[role] = {'faction': faction, 'category': category}

	return role_list

def get_specific_roles(field, values):
	role_list = {}
	all_roles = get_all_roles()
	for role in all_roles:
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
			if current_game['factions'][faction_id]['name'] == channel:
				return current_game['factions'][faction_id]['channel_id']

	return ""

def get_players(game):
	current_game = running_games[game]
	return current_game['players']

def get_players_with_role(game, role):
	role_players = []
	players = get_players(game)
	for player in players:
		if 'role_name' in players[player] and players[player]['role_name'].lower() == role:
			role_players.append(player)

	return role_players

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
					return game_roles[faction][category][role]
	return {}

def get_running_game_state(game):
	if game in running_games:
		return json.dumps(running_games[game], indent=4)
	else:
		return list(running_games.keys())

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
				players_in_games[player]['game'] = game_data['town_name_abbreviated']
		store_game_state(game_data, "open")

def store_game_state(game_data, state):
	game_object = json.dumps(game_data, indent=4)
	with open("{}/{}.{}".format(SAVE_PATH, game_data['town_name_abbreviated'], state), "w") as outfile:
		outfile.write(game_object)

def action_assign_player_roles(game):
	game_players = running_games[game]['players']
	game_factions = running_games[game]['factions']
	default_roles = get_specific_roles('category', running_games[game]['default_roles'])
	total_players = len(game_players)
	unaccounted_players = total_players
	for faction_id in game_factions:
		faction = game_factions[faction_id]

		if 'players' not in faction:
			faction['players'] = []
		current_faction_players = len(faction['players'])

		unaccounted_players -= current_faction_players

		if faction['size_type'] == "fixed":
			faction_players = faction['size']
		else:
			faction_players = math.floor(total_players*faction['size']/100)
		if faction_players > unaccounted_players:
			faction_players = unaccounted_players
		faction_roles = get_specific_roles('faction', [faction['type']])

		while(current_faction_players < faction_players):
			chosen_player_data = random.choice(list(game_players.items()))
			while('faction' not in chosen_player_data[1]):
				chosen_player_data = random.choice(list(game_players.items()))
			role_chosen = random.choice(list(faction_roles.items()))
			chosen_player = game_players[chosen_player_data[0]]
			if faction['type'] != "mafia":
				chosen_player['role_name'] = role_chosen[0]
				chosen_player['role_faction'] = role_chosen[1]['faction']
				chosen_player['role_category'] = role_chosen[1]['category']
			chosen_player['faction'] = faction['name']
			chosen_player['faction_type'] = faction['type']
			players_in_games[chosen_player_data[0]] = chosen_player
			current_faction_players += 1
			if 'players' not in faction:
				faction['players'] = []
			faction['players'].append(chosen_player_data[0])

			unaccounted_players -= 1
	for player in game_players:
		if game_players[player] == {'game': game}:
			current_player = game_players[player]
			role_chosen = random.choice(list(default_roles.items()))
			current_player['role_name'] = role_chosen[0]
			current_player['role_faction'] = role_chosen[1]['faction']
			current_player['role_category'] = role_chosen[1]['category']
			players_in_games[player] = current_player


def command_available_game_commands(user_id):
	game_commands = []

	if user_id in players_in_games:
		game_commands = ['leave']
		if 'round' in running_games[players_in_games[user_id]['game']]:
			game_commands.append('list')
			game_commands.append('role')
	else:
		game_commands.append(['join'])

	return game_commands

def command_available_private_actions(user_id):
	private_actions = []

	if user_id in players_in_games:
		if 'role_name' in players_in_games[user_id]:
			role_details = get_role_details(players_in_games[user_id]['role_name'])
			if 'private_actions' in role_details:
				private_actions = role_details['private_actions']
		elif 'faction_type' in players_in_games[user_id]:
			private_actions.append('choose')

	return private_actions

def command_available_public_actions(user_id):
	public_actions = []

	if user_id in players_in_games:
		public_actions = []
		if 'role_name' in players_in_games[user_id]:
			role_details = get_role_details(players_in_games[user_id]['role_name'])

			if 'public_actions' in role_details:
				for public_action in role_details['public_actions']:
					public_actions.append(public_action)

		if 'jurors' in running_games[players_in_games[user_id]['game']] and len(running_games[players_in_games[user_id]['game']]['jurors']) < 3:
			public_actions.append('juror')

		if 'jurors' in running_games[players_in_games[user_id]['game']] and user_id in running_games[players_in_games[user_id]['game']]['jurors']:
			public_actions.append('hang')

	return public_actions

def command_channels_for_game(game):
	town_channel = "{}-town-square".format(game)
	graveyard_channel = "{}-graveyard".format(game)
	faction_channels = []
	for faction_id in running_games[game]['factions'].keys():
		faction_type = running_games[game]['factions'][faction_id]["type"]
		faction_name = running_games[game]['factions'][faction_id]["name"].lower().replace(" ", "_")

		if 'channel_id' not in running_games[game]['factions'][faction_id]:
			if faction_type == 'vampire_coven':
				faction_channels.append({'channel_name': "{}-{}-vampire-coven".format(game, faction_name), 'faction_id': faction_id})
			if faction_type == 'mafia':
				faction_channels.append({'channel_name': "{}-{}-family-mafia".format(game, faction_name), 'faction_id': faction_id})

	if 'town_channel_id' in running_games[game]:
		town_channel = ""
	if 'graveyard_channel_id' in running_games[game]:
		graveyard_channel = ""

	return town_channel, faction_channels, graveyard_channel

def command_game_join(meta_data, game):
	user_id = meta_data['user_id']

	if user_id in players_in_games:
		return "You are already in a game.".format(user_id)
	else:
		if game in running_games:
			players_in_games[user_id] = {}
			players_in_games[user_id]['game'] = game
			players_in_games[user_id]['user_name'] = meta_data['user_name']

			if 'players' not in running_games[game]:
				running_games[game]['players'] = {}
			running_games[game]['players'][user_id] = players_in_games[user_id]['game']

			store_game_state(running_games[game], "open")
			return "You are joining {}.".format(game)
		else:
			running_games_output = []
			for game in running_games.keys():
				if 'round' in running_games[game]:
					running_games.append("{} (In Progress)".format(game))
				else:
					running_games.append(game)
			return running_games_output

def command_game_start(game):
	if game in running_games:
		if 'round' not in running_games[game]:
			running_games[game]['round'] = 1
			running_games[game]['jurors'] = []
			action_assign_player_roles(game)

			store_game_state(running_games[game], "open")
			return "*Starting game {}.*".format(game)
		else:
			return "*Game {} is already running.*".format(game)
	else:
		return list(running_games.keys())

def command_store_channel_information(game, town_channel_id, faction_channels, graveyard_channel_id):
	running_games[game]['town_channel_id'] = town_channel_id
	running_games[game]['graveyard_channel_id'] = graveyard_channel_id
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

def command_intro_message(game, player):
	role = running_games[game]['players'][player]['role_name']
	
	role_details = get_role_details(role)

	response = role_details['background']

	response = "{}\n\nYou are the *{}*.\n\n".format(response, role)

	if 'private_actions' in role_details:
		for private_action in role_details['private_actions']:
			response = "{}/mafia_private_action {}\n".format(response, private_action)

	if 'public_actions' in role_details:
		for public_action in role_details['public_actions']:
			response = "{}/mafia_public_action {}\n".format(response, public_action)

	return response
