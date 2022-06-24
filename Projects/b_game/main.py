# Packages
import numpy as np
import pandas as pd
import random
import names
import pickle

# Constants
NUM_PLAYERS = 3000  # Number of players to create
PITCH_PROB = 11 / 27  # Probability of choosing pitcher
HITTER_PROB = 1 - PITCH_PROB  # Probability of choosing hitter
LEFT_PITCH_PROB = .25  # Probability of choosing left-handed pitcher
LEFT_HIT_PROB = .35  # Probability of choosing left-handed batter
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

PITCHING_PROB = {
    'SP': .4,
    'RP': .6,
}

BATTING_PROB = {
    'C': .125,
    '1B': .125,
    '2B': .125,
    '3B': .125,
    'SS': .125,
    'LF': .125,
    'CF': .125,
    'RF': .125,
}

POSITION_PROB = {
    'B': .6,
    'P': .4,
}


def assign_position():
    if random.choices(list(POSITION_PROB.keys()), list(POSITION_PROB.values())) == 'B':
        return random.choices(list(BATTING_PROB.keys()), list(BATTING_PROB.values()))

    else:
        return random.choices(list(PITCHING_PROB.keys()), list(PITCHING_PROB.values()))


def left_right(position: str) -> str:
    """
    Will return whether a hitter or batter is left or right throwing/hitting

    Args:
        position: Position to base percentage off of

    Returns: left or right

    """
    if position == "hit":
        return np.random.choice(["left", "right"], p=[LEFT_HIT_PROB, 1 - LEFT_HIT_PROB])

    else:
        return np.random.choice(
            ["left", "right"], p=[LEFT_PITCH_PROB, 1 - LEFT_PITCH_PROB]
        )


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
    df_main["position"] = df_main.apply(lambda row: assign_position(), axis=1)
    df_main["handed"] = df_main.apply(lambda row: left_right(row['position']), axis=1)
    df_main["attributes"] = df_main.apply(lambda row: (assign_hitting_attributes(row['main_rating']) if row['position'] == 'hit' else assign_hitting_attributes(row['main_rating'])), axis=1)
    df_main["name"] = df_main.apply(lambda row: names.get_full_name(gender="male"), axis=1)
    df_main.reset_index(inplace=True)
    df_main.rename(columns={
        'index': 'id'
    }, inplace=True)

    return df_main


class Player:

    def __init__(self, id: int, name: str, position: str, main_rating: int, handed: str, attributes: dict, injured: bool):
        self.id = id
        self.name = name
        self.main_rating = main_rating
        self.position = position
        self.handed = handed
        self.attributes = attributes
        self.injured = injured

    def set_name(self):
        self.name = names.get_full_name(gender="male")

    def set_main_rating(self):
        self.main_rating = np.around(np.random.normal(MEAN_MAIN_RATING,
                                                      STD_MAIN_RATING,
                                                      NUM_PLAYERS))

    def set_position(self):
        self.position = np.random.choice(["pitch", "hit"], p=[PITCH_PROB,
                                                              HITTER_PROB])

    def set_handed(self):
        self.handed = left_right(self.position)

    # def set_attributes(self):
    #     self.attributes = assign_attributes(self.position, self.main_rating)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def __repr__(self):
        return f"Player({self.id}, {self.name}, {self.position}, {self.main_rating}, {self.handed}, {self.attributes})"


class Pitcher(Player):

    def __init__(self, id, name, position, main_rating, handed, attributes, injured, days_rest):
        super().__init__(id, name, position, main_rating, handed, attributes, injured)

        self.days_rest = days_rest

class Batter(Player):

    def __init__(self, id, name, position, main_rating, handed, attributes, injured):
        super().__init__(id, name, position, main_rating, handed, attributes, injured)



class Team:
    def __int__(self, name: str, city: str, league: str, players: list[Player], record: dict):
        self.name = name
        self.city = city
        self.league = league
        self.players = players
        self.record = record

    # def play(self, opp):


player_list = []

df1 = create_player_df()
print(df1.head())

df1_dict = df1.to_dict('records')

for player in df1_dict:
    temp = Player(player['id'], player['name'], player['position'], player['main_rating'], player['handed'], player['attributes'])
    player_list.append(temp)


# with open("player_list.txt", "wb") as t:
#     pickle.dump(player_list, t)
# with open("player_list.txt", "rb") as t:
#     list2 = pickle.load(t)

print(player_list[0].__dict__)

