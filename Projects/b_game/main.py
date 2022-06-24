# Packages
import numpy as np
import pandas as pd
import random
import names
import pickle

# Constants
NUM_PLAYERS = 3000  # Number of players to create
MEAN_MAIN_RATING = 70  # Mean rating for creation of main ratings
STD_MAIN_RATING = 9  # Standard deviation for creation of main ratings
ATTRIBUTE_STD = 6  # How much to adjust the incremental change each attribute

# Batting attribute weights
BATTING_ATTRIBUTES = {
    "contact": 3,
    "power": 1.5,
    "speed/stealing": 2.5,
    "fielding": 3,
    "eye": 2,
    "avoid ks": 2,
}

# Batting attribute weights
PITCHING_ATTRIBUTES = {
    "stuff": 2,
    "movement": 2.5,
    "control": 3,
}

POSITIONS = {
    'SP': 'Starting Pitcher',
    'RP': 'Relief Pitcher',
    'C': 'Catcher',
    '1B': 'First Baseman',
    '2B': 'Second Baseman',
    '3B': 'Third Baseman',
    'SS': 'Shortstop',
    'LF': 'Left Fielder',
    'CF': 'Center Fielder',
    'RF': 'Right Fielder'
}

PARENT_POSITION_PROB = {
    'B': .6,
    'P': .4,
}

POSITION_PROB = {
    'B': {
        'C': .125,
        '1B': .125,
        '2B': .125,
        '3B': .125,
        'SS': .125,
        'LF': .125,
        'CF': .125,
        'RF': .125,
    },
    'P': {
        'SP': .4,
        'RP': .6,
    }

}

HANDED_PROB = {
    'P': {
        'L': .25,
        'R': .75,
    },
    'B': {
        'L': .35,
        'R': .65,
    }
}


def assign_parent_position():
    return random.choices(list(PARENT_POSITION_PROB.keys()), list(PARENT_POSITION_PROB.values()))[0]


def assign_position(position: str):
    return random.choices(list(POSITION_PROB[position].keys()), list(POSITION_PROB[position].values()))[0]


def assign_handed(position: str) -> str:
    """
    Will return whether a hitter or batter is left or right throwing/hitting

    Args:
        position: Position to base percentage off of

    Returns: left or right

    """
    return random.choices(list(HANDED_PROB[position].keys()), list(HANDED_PROB[position].values()))[0]


def assign_hitting_attributes(main_rating: int) -> dict:
    """
    Assigns attribute to player
    Args:
        main_rating: Current main rating of player

    Returns: dictionary of attributes

    """
    temp_dict = BATTING_ATTRIBUTES.copy()

    return_dict = {}
    mr = main_rating
    for x in range(len(temp_dict)):
        choice = random.choices(list(temp_dict.keys()), list(temp_dict.values()))[0]
        att_rating = np.around(np.random.normal(main_rating, ATTRIBUTE_STD))
        z_score = (att_rating - mr) / ATTRIBUTE_STD
        return_dict.update({choice: att_rating})
        temp_dict.pop(choice)
        mr -= abs((5 + z_score))

    return return_dict


def assign_pitching_attributes(main_rating: int) -> dict:
    """
    Assigns attribute to player
    Args:
        main_rating: Current main rating of player

    Returns: dictionary of attributes

    """
    temp_dict = PITCHING_ATTRIBUTES.copy()

    return_dict = {}
    mr = main_rating
    for x in range(len(temp_dict)):
        choice = random.choices(list(temp_dict.keys()), list(temp_dict.values()))[0]
        att_rating = np.around(np.random.normal(main_rating, ATTRIBUTE_STD))
        z_score = (att_rating - mr) / ATTRIBUTE_STD
        return_dict.update({choice: att_rating})
        temp_dict.pop(choice)
        mr -= abs((5 + z_score))

    return return_dict


def create_player_df():
    df_main = pd.DataFrame(
        np.around(np.random.normal(MEAN_MAIN_RATING, STD_MAIN_RATING, NUM_PLAYERS)),
        columns=["main_rating"],
    )
    df_main['position'] = df_main.apply(lambda row: assign_parent_position(), axis=1)
    df_main['sec_position'] = df_main.apply(lambda row: assign_position(row['position']), axis=1)
    df_main["handed"] = df_main.apply(lambda row: assign_handed(row['position']), axis=1)
    df_main["attributes"] = df_main.apply(lambda row: (assign_hitting_attributes(row['main_rating']) if row['position'] == 'hit' else assign_pitching_attributes(row['main_rating'])), axis=1)
    df_main["name"] = df_main.apply(lambda row: names.get_full_name(gender="male"), axis=1)
    df_main.reset_index(inplace=True)
    df_main.rename(columns={
        'index': 'id'
    }, inplace=True)

    return df_main


class Player:

    def __init__(self, id: int, name: str, parent_position: str, position: str, main_rating: int, handed: str, attributes: dict, injured: bool = False):
        self.id = id
        self.name = name
        self.main_rating = main_rating
        self.parent_position = parent_position
        self.position = position
        self.handed = handed
        self.attributes = attributes
        self.injured = injured

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return f"Player({self.id}, {self.name}, {self.position}, {self.main_rating}, {self.handed}, {self.attributes})"


class Pitcher(Player):

    def __init__(self, id, name, parent_position, position, main_rating, handed, attributes, injured, days_rest: int):
        super().__init__(id, name, parent_position, position, main_rating, handed, attributes, injured)

        self.days_rest = days_rest


class Batter(Player):

    def __init__(self, id, name, parent_position, position, main_rating, handed, attributes, injured):
        super().__init__(id, name, parent_position, position, main_rating, handed, attributes, injured)


class Team:
    def __int__(self, name: str, city: str, league: str, players: list[Player], record: dict):
        self.name = name
        self.city = city
        self.league = league
        self.players = players
        self.record = record

    # def play(self, opp):


class League:
    def __init__(self, name: str, level: str, teams: list[Team]):
        self.name = name
        self.level = level
        self.teams = teams

