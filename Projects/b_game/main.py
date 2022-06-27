# Packages
import numpy as np
import pandas as pd
import random
import names
import collections
import pickle

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, Integer, JSON, Boolean, ForeignKey, ARRAY


engine = create_engine('postgresql://jjbokan3:sEals091sands@localhost:5432/bgame_db')
Session = sessionmaker()
Base = declarative_base()

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

ma = {
    'R/G': 4.53,
    'PA': 37.43,
    'AB': 33.33,
    'R': 4.53,
    'H': 8.13,
    '1B': 5.15,
    '2B': 1.62,
    '3B': 0.14,
    'HR': 1.22,
    'RBI': 4.32,
    'SB': 0.46,
    'CS': 0.15,
    'BB': 3.25,
    'SO': 8.68,
    'BA': .244,
    'OBP': .317,
    'SLG': .411,
    'OPS': .728,
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
    df_main['parent_position'] = df_main.apply(lambda row: assign_parent_position(), axis=1)
    df_main['position'] = df_main.apply(lambda row: assign_position(row['parent_position']), axis=1)
    df_main["handed"] = df_main.apply(lambda row: assign_handed(row['parent_position']), axis=1)
    df_main["attributes"] = df_main.apply(lambda row: (assign_hitting_attributes(row['main_rating']) if row['parent_position'] == 'B' else assign_pitching_attributes(row['main_rating'])), axis=1)
    df_main["name"] = df_main.apply(lambda row: names.get_full_name(gender="male"), axis=1)
    df_main.reset_index(inplace=True)
    df_main.rename(columns={
        'index': 'id'
    }, inplace=True)

    return df_main


class Player(Base):

    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    parent_position = Column(String(2), nullable=False)
    position = Column(String(2), nullable=False)
    main_rating = Column(Integer, nullable=False)
    handed = Column(String(5), nullable=False)
    attributes = Column(JSON)
    injured = Column(Boolean, nullable=False)
    current_team = Column(Integer, ForeignKey('teams.id'), nullable=True)

    def __init__(self, name: str, parent_position: str, position: str, main_rating: int, handed: str, attributes: dict, injured: bool, current_team: int):
        self.name = name
        self.main_rating = main_rating
        self.parent_position = parent_position
        self.position = position
        self.handed = handed
        self.attributes = attributes
        self.injured = injured
        self.current_team = current_team

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"Player({self.name}, {self.position}, {self.main_rating}, {self.handed}, {self.attributes})"


class Pitcher(Player):

    __tablename__ = 'pitchers'
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    days_rest = Column(Integer)
    pitcher_priority = Column(Integer, nullable=True)

    def __init__(self, name, parent_position, position, main_rating, handed, attributes, injured, current_team, days_rest: int, pitcher_priority):
        super().__init__(name, parent_position, position, main_rating, handed, attributes, injured, current_team)

        self.days_rest = days_rest
        self.pitcher_priority = pitcher_priority

    def play(self, opp):
        if isinstance(opp, Pitcher):
            raise Exception('Cannot face two pitchers against each other!')


class Batter(Player):

    __tablename__ = 'batters'
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    switch = Column(Boolean, nullable=True)
    num_in_lineup = Column(Integer, nullable=True)

    def __init__(self, name, parent_position, position, main_rating, handed, attributes, injured, current_team, switch, num_in_lineup):
        super().__init__(name, parent_position, position, main_rating, handed, attributes, injured, current_team)

        self.switch = switch
        self.num_in_lineup = num_in_lineup

    def play(self, opp):
        if isinstance(opp, Batter):
            raise Exception('Cannot face two batters against each other!')




class Team(Base):

    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    league = Column(Integer, ForeignKey('leagues.id'), nullable=True)
    record = Column(String(10), nullable=False)
    starting_lineup = Column(ARRAY(String))
    pitching_rotation = Column(ARRAY(String))
    bullpen = Column(ARRAY(String))

    def __int__(self, name: str, city: str, league: int, record: dict, starting_lineup: list[str], pitching_rotation: list[str], bullpen: list[str]):
        self.name = name
        self.city = city
        self.league = league
        self.record = record
        self.starting_lineup = starting_lineup
        self.pitching_rotation = pitching_rotation
        self.bullpen = bullpen





class League(Base):

    __tablename__ = 'leagues'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    level = Column(String(20), nullable=False)

    def __init__(self, name: str, level: str):
        self.name = name
        self.level = level

