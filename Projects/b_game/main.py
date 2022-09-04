# Packages
import numpy as np
import pandas as pd
import random
import names
import collections
import pickle
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, String, DateTime, Integer, JSON, Boolean, ForeignKey, ARRAY, INTEGER, Sequence


engine = create_engine('postgresql://jjbokan3:sEals091sands@localhost:5432/bgame_db')
# engine = create_engine('postgresql://jjbokan3@localhost:5432/bgame_db')
Session = sessionmaker()
Base = declarative_base()

# Constants
NUM_PLAYERS = 15000  # Number of players to create
MEAN_MAIN_RATING = 70  # Mean rating for creation of main ratings
STD_MAIN_RATING = 9  # Standard deviation for creation of main ratings
LOWER_BOUND_MAIN_RATING = 50
HIGHER_BOUND_MAIN_RATING = 100
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

current_year = datetime.datetime.now().year

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


def create_player_df() -> pd.DataFrame:
    df_main = pd.DataFrame(
        np.around(np.random.randint(LOWER_BOUND_MAIN_RATING, HIGHER_BOUND_MAIN_RATING, NUM_PLAYERS)),
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

    batter = relationship("Batter", backref="player", uselist=False)
    pitcher = relationship("Pitcher", backref="player", uselist=False)

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
    energy = Column(Integer)
    pitcher_priority = Column(Integer, nullable=True)

    pitcher_stats = relationship("PitcherGameStats", backref="pitcher")

    def __init__(self, name, parent_position, position, main_rating, handed, attributes, injured, current_team, energy: int, pitcher_priority):
        super().__init__(name, parent_position, position, main_rating, handed, attributes, injured, current_team)

        self.energy = energy
        self.pitcher_priority = pitcher_priority

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_position': self.parent_position,
            'position': self.position,
            'main_rating': self.main_rating,
            'handed': self.handed,
            'attributes': self.attributes,
            'injured': self.injured,
            'current_team': self.current_team,
            'energy': self.energy,
            'pitcher_priority': self.pitcher_priority
        }


class Batter(Player):

    __tablename__ = 'batters'
    id = Column(Integer, ForeignKey('players.id'), primary_key=True)
    switch = Column(Boolean, nullable=True)
    num_in_lineup = Column(Integer, nullable=True)

    batter_stats = relationship("BatterGameStats", backref="batter")

    def __init__(self, name, parent_position, position, main_rating, handed, attributes, injured, current_team, switch, num_in_lineup):
        super().__init__(name, parent_position, position, main_rating, handed, attributes, injured, current_team)

        self.switch = switch
        self.num_in_lineup = num_in_lineup

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent_position': self.parent_position,
            'position': self.position,
            'main_rating': self.main_rating,
            'handed': self.handed,
            'attributes': self.attributes,
            'injured': self.injured,
            'current_team': self.current_team,
            'switch': self.switch,
            'num_in_lineup': self.num_in_lineup
        }


class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    home_team = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.year'), nullable=False)
    home_score = Column(Integer, nullable=False)
    away_score = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=True)

    def __init__(self, home_team, away_team, season_id, home_score=0, away_score=0, date=None):
        self.home_team = home_team
        self.away_team = away_team
        self.season_id = season_id
        self.home_score = home_score
        self.away_score = away_score
        self.date = date


class Season(Base):
    __tablename__ = 'seasons'
    year = Column(Integer,
                  Sequence('article_aid_seq', start=current_year, increment=1),
                  primary_key=True)


class PitcherGameStats(Base):

    __tablename__='pitcher_stats_game'
    id = Column(Integer, primary_key=True)
    pitcher_id = Column(Integer, ForeignKey('pitchers.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    innings_pitched = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)
    holds = Column(Integer)
    saves = Column(Integer)
    singles = Column(Integer)
    doubles = Column(Integer)
    triples = Column(Integer)
    home_runs = Column(Integer)
    runs = Column(Integer)
    walks = Column(Integer)
    pitches = Column(Integer)

    def __init__(self, pitcher_id, game_id, innings_pitched=0, wins=0, losses=0, holds=0, saves=0, singles=0, doubles=0, triples=0, home_runs=0, runs=0, walks=0, pitches=0):
        self.pitcher_id = pitcher_id
        self.game_id = game_id
        self.innings_pitched = innings_pitched
        self.wins = wins
        self.losses = losses
        self.holds = holds
        self.saves = saves
        self.singles = singles
        self.doubles = doubles
        self.triples = triples
        self.home_runs = home_runs
        self.runs = runs
        self.walks = walks
        self.pitches = pitches
        self.era = self.calc_era()
        self.whip = self.calc_whip()

    def calc_era(self):
        try:
            return 9 * self.runs / self.innings_pitched
        except ZeroDivisionError:
            return 0

    def calc_whip(self):
        try:
            return (self.singles + self.doubles + self.triples + self.home_runs + self.walks) / self.innings_pitched
        except ZeroDivisionError:
            return 0

    def to_dict(self):
        return {
            'pitcher_name': self.pitcher.name,
            'pitcher_id': self.pitcher_id,
            'game_id': self.game_id,
            'innings_pitched': self.innings_pitched,
            'wins': self.wins,
            'losses': self.losses,
            'holds': self.holds,
            'saves': self.saves,
            'singles': self.singles,
            'doubles': self.doubles,
            'triples': self.triples,
            'home_runs': self.home_runs,
            'runs': self.runs,
            'walks': self.walks,
            'pitches': self.pitches,
            'era': self.era,
            'whip': self.whip
        }

    def __add__(self, other):
        if self.batter_id != other.batter_id:
            raise Exception("Cannot aggregate stats from different players!")
        else:
            result = PitcherGameStats(self.pitcher_id, self.game_id, self.innings_pitched + other.innings_pitched, self.wins + other.wins, self.losses + other.losses, self.holds + other.holds, self.saves + other.saves, self.singles + other.singles, self.doubles + other.doubles, self.triples + other.triples, self.home_runs + other.home_runs, self.runs + other.runs, self.walks + other.walks)
            # TODO: Configure how to add innings pitched regarding decimal notation
            result.pitcher_id = self.pitcher_id
            result.game_id = None
            result.pitcher = self.pitcher
            return result

    def __str__(self):
        return f"Pitcher ID: {self.pitcher_id} Game ID: {self.game_id}"

    def __repr__(self):
        return f"PitcherGameStats({self.pitcher_id}, {self.game_id}, {self.innings_pitched}, {self.wins}, {self.losses}, {self.holds}, {self.saves}, {self.singles}, {self.doubles}, {self.triples}, {self.home_runs}, {self.runs}, {self.walks})"

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


class BatterGameStats(Base):

    __tablename__ = 'batter_stats_game'
    id = Column(Integer, primary_key=True)
    batter_id = Column(Integer, ForeignKey('batters.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    at_bats = Column(Integer)
    runs = Column(Integer)
    rbis = Column(Integer)
    singles = Column(Integer)
    doubles = Column(Integer)
    triples = Column(Integer)
    home_runs = Column(Integer)
    walks = Column(Integer)
    stolen_bases = Column(Integer)
    caught_stealing = Column(Integer)
    strikeouts = Column(Integer)

    def __init__(self, batter_id, game_id, at_bats=0, runs=0, rbis=0, singles=0, doubles=0, triples=0, home_runs=0, walks=0, stolen_bases=0, caught_stealing=0, strikeouts=0):

        self.batter_id = batter_id
        self.game_id = game_id
        self.at_bats = at_bats
        self.runs = runs
        self.rbis = rbis
        self.singles = singles
        self.doubles = doubles
        self.triples = triples
        self.home_runs = home_runs
        self.walks = walks
        self.stolen_bases = stolen_bases
        self.caught_stealing = caught_stealing
        self.strikeouts = strikeouts
        self.plate_appearances = self.at_bats + self.walks
        self.obp = self.calc_obp()
        self.slg = self.calc_slg()
        self.ops = self.obp + self.slg

    def calc_obp(self) -> float:
        """
        Calculates On-Base-Percentage from the given statistics

        Returns:
            On-Base-Percentage
        """
        try:
            return (self.singles + self.doubles + self.triples + self.home_runs + self.walks) / (self.at_bats + self.walks)
        except ZeroDivisionError:
            return 0


    def calc_slg(self) -> float:
        """
        Calculates Slugging from the given statistics

        Returns:
            Slugging
        """
        try:
            return (self.singles + (self.doubles * 2) + (self.triples * 3) + (self.home_runs * 4)) / self.at_bats
        except ZeroDivisionError:
            return 0

    def to_dict(self) -> dict:
        return {
            'batter name': self.batter.name,
            'batter_id': self.batter_id,
            'game_id': self.game_id,
            'at_bats': self.at_bats,
            'runs': self.runs,
            'rbis': self.rbis,
            'singles': self.singles,
            'doubles': self.doubles,
            'triples': self.triples,
            'home_runs': self.home_runs,
            'walks': self.walks,
            'stolen_bases': self.stolen_bases,
            'caught_stealing': self.caught_stealing,
            'strikeouts': self.strikeouts,
            'plate_appearances': self.plate_appearances,
            'obp': self.obp,
            'slg': self.slg,
            'ops': self.ops
        }

    def __add__(self, other):
        if self.batter_id != other.batter_id:
            raise Exception("Cannot aggregate stats from different players!")
        else:
            result = BatterGameStats(self.batter_id, self.game_id, self.at_bats + other.at_bats, self.runs + other.runs, self.rbis + other.rbis, self.singles + other.singles, self.doubles + other.doubles, self.triples + other.triples, self.home_runs + other.home_runs, self.walks + other.walks, self.stolen_bases + other.stolen_bases, self.caught_stealing + other.caught_stealing, self.strikeouts + other.strikeouts)
            result.batter_id = self.batter_id
            result.game_id = None
            result.batter = self.batter
            return result


    def __str__(self):
        return f"Player ID: {self.batter_id} Game ID: {self.game_id}"

    def __repr__(self):
        return f"BatterGameStats({self.batter_id}, {self.game_id}, {self.at_bats}, {self.runs}, {self.rbis}, {self.singles}, {self.doubles}, {self.triples}, {self.home_runs}, {self.walks}, {self.stolen_bases}, {self.caught_stealing}, {self.strikeouts})"

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


class Team(Base):

    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

    players = relationship("Player", backref="team")

    def __init__(self, name: str, league_id: int, wins: int = 0, losses: int = 0):
        self.name = name
        self.league_id = league_id
        self.wins = wins
        self.losses = losses
# TODO: Add team stats and structure for league stats (team and player)


class League(Base):

    __tablename__ = 'leagues'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    # division_list = Column(ARRAY(Integer))
    teams = relationship("Team", backref="league")

    def __init__(self, name: str, schedule: list = None):
        self.name = name
        self.schedule = schedule


class LeagueSeasonSchedule(Base):

    __tablename__ = 'league_season_schedule'
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey('leagues.id'))
    season_id = Column(Integer, ForeignKey('seasons.year'))
    schedule = Column(ARRAY(Integer), nullable=True)

    def __init__(self, league_id: int, season_id: int, schedule: list = None):
        self.league_id = league_id
        self.season_id = season_id
        self.schedule = schedule

# class Division(Base):
#
#     __tablename__ = 'divisions'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     league = Column(Integer, ForeignKey('leagues.id'), nullable=False)
#     team_list = Column(ARRAY(Integer))

# TODO: Look into relationships and mapping within sqlalchemy

