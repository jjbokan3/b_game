# from typing import List

# from Projects.b_game.main import PitcherGameStats, BatterGameStats
from main import *
from operator import attrgetter

import collections

# Details stats that will determine the outcome of an at-bat
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
    'avg_pitches': 6
}

# Set pitch limits for starters and relievers
starter_pitch_limit = 100
reliever_pitch_limit = 25

# Create local session to query for batters and pitchers
local_session = Session(bind=engine)

# Highest level function to take in results from play_ball and outcome_modifier
def play(home_team_id: int, away_team_id: int):
    # Define variables for home and away teams
    current_game = Game(home_team_id, away_team_id, current_year)
    local_session.add(current_game)
    local_session.commit()
    current_game = local_session.query(Game).filter_by(home_team=home_team_id, away_team=away_team_id, season_id=current_year).first()

    max_outs = 54
    total_outs = 0
    inning_outs = 0
    away_pitch_count = 0
    home_pitch_count = 0
    home_batter = 0
    away_batter = 0
    home_score = 0
    away_score = 0
    outcome = ''
    bases = {
        '1st': None,
        '2nd': None,
        '3rd': None,
    }  # TODO: Include player speed as well?
    home_hitting: bool = False

    home_team = local_session.query(Team).filter(Team.id == home_team_id).first()
    away_team = local_session.query(Team).filter(Team.id == away_team_id).first()
    home_batters = local_session.query(Batter).filter(Batter.current_team == home_team_id).all()
    away_batters = local_session.query(Batter).filter(Batter.current_team == away_team_id).all()

    home_starters = local_session.query(Pitcher).filter((Pitcher.current_team == home_team_id) & (Pitcher.position == 'SP')).all()
    away_starters = local_session.query(Pitcher).filter((Pitcher.current_team == away_team_id) & (Pitcher.position == 'SP')).all()
    home_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == home_team_id) & (Pitcher.position == 'RP')).all()
    away_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == away_team_id) & (Pitcher.position == 'RP')).all()

    for pitchers in [home_starters, away_starters, home_relievers, away_relievers]:
        for pitcher in pitchers:
            if pitcher.energy + 20 > 100:
                pitcher.energy = 100
            else:
                pitcher.energy += 20

    home_starters.sort(key=attrgetter('energy', 'pitcher_priority'), reverse=True)
    away_starters.sort(key=attrgetter('energy', 'pitcher_priority'), reverse=True)
    home_relievers.sort(key=attrgetter('energy', 'pitcher_priority'), reverse=True)
    away_relievers.sort(key=attrgetter('energy', 'pitcher_priority'), reverse=True)

    home_batters_stats: list[BatterGameStats] = [BatterGameStats(batter.id, current_game.id) for batter in home_batters]
    away_batters_stats: list[BatterGameStats] = [BatterGameStats(batter.id, current_game.id) for batter in away_batters]
    home_starters_stats: list[PitcherGameStats] = [PitcherGameStats(pitcher.id, current_game.id) for pitcher in home_starters]
    away_starters_stats: list[PitcherGameStats] = [PitcherGameStats(pitcher.id, current_game.id) for pitcher in away_starters]
    home_relievers_stats: list[PitcherGameStats] = [PitcherGameStats(pitcher.id, current_game.id) for pitcher in home_relievers]
    away_relievers_stats: list[PitcherGameStats] = [PitcherGameStats(pitcher.id, current_game.id) for pitcher in away_relievers]

    for x in [home_batters_stats, away_batters_stats, home_starters_stats, away_starters_stats, home_relievers_stats, away_relievers_stats]:
        for y in x:
            local_session.add(y)

    local_session.commit()

    home_pitcher = home_starters[0]
    away_pitcher = away_starters[0]
    home_reliever_number = 0
    away_reliever_number = 0

    while total_outs != max_outs:
        while inning_outs < 3:
            if home_hitting:
                outcome, pitch_count_inc = play_ball(away_pitcher, home_batters[home_batter % 9])
                if away_reliever_number == 0:
                    current_pitcher_stats = [pitcher_stats for pitcher_stats in away_starters_stats if pitcher_stats.pitcher_id == away_pitcher.id][0]
                else:
                    current_pitcher_stats = [pitcher_stats for pitcher_stats in away_relievers_stats if pitcher_stats.pitcher_id == away_pitcher.id][0]
                bases, away_pitch_count, home_score, away_score, inning_outs = outcome_modifier(outcome, bases, away_pitch_count, pitch_count_inc, home_score, away_score, home_hitting, inning_outs, away_pitcher, home_batters[home_batter % 9], current_pitcher_stats, home_batters_stats)
                home_batter += 1
                if away_pitcher.position == 'SP' and away_pitch_count > starter_pitch_limit:
                    away_pitcher.energy -= 100
                    away_pitcher = away_relievers[away_reliever_number]
                    away_reliever_number += 1
                    away_pitch_count = 0
                elif away_pitcher.position == 'RP' and away_pitch_count > reliever_pitch_limit:
                    away_pitcher.energy -= 40
                    away_pitcher = away_relievers[away_reliever_number]
                    away_reliever_number += 1
                    away_pitch_count = 0

            else:
                outcome, pitch_count_inc = play_ball(home_pitcher, away_batters[away_batter % 9])
                if home_reliever_number == 0:
                    current_pitcher_stats = [pitcher_stats for pitcher_stats in home_starters_stats if pitcher_stats.pitcher_id == home_pitcher.id][0]
                else:
                    current_pitcher_stats = [pitcher_stats for pitcher_stats in home_relievers_stats if pitcher_stats.pitcher_id == home_pitcher.id][0]
                bases, home_pitch_count, home_score, away_score, inning_outs = outcome_modifier(outcome, bases, home_pitch_count, pitch_count_inc, home_score, away_score, home_hitting, inning_outs, home_pitcher, away_batters[away_batter % 9], current_pitcher_stats, away_batters_stats)
                away_batter += 1
                if home_pitcher.position == 'SP' and home_pitch_count > starter_pitch_limit:
                    home_pitcher = home_relievers[home_reliever_number]
                    home_reliever_number += 1
                    home_pitch_count = 0
                elif home_pitcher.position == 'RP' and home_pitch_count > reliever_pitch_limit:
                    home_pitcher = home_relievers[home_reliever_number]
                    home_reliever_number += 1
                    home_pitch_count = 0

        home_hitting = not home_hitting
        bases = {
            '1st': None,
            '2nd': None,
            '3rd': None,
        }
        total_outs += inning_outs
        inning_outs = 0

    if home_score > away_score:
        home_team.wins += 1
        away_team.losses += 1
    else:
        away_team.wins += 1
        home_team.losses += 1

    # home_starters0 = [hs for hs in home_starters_stats if hs.pitches == 0]
    # local_session.delete(home_starters0)
    #
    # away_starters0 = [aws for aws in away_starters_stats if aws.pitches == 0]
    # local_session.delete(away_starters0)
    #
    # home_relievers0 = [hr for hr in home_relievers_stats if hr.pitches == 0]
    # local_session.delete(home_relievers0)
    #
    # away_relievers0 = [awr for awr in away_relievers_stats if awr.pitches == 0]
    # local_session.delete(away_relievers0)

    no_pitching = [[hs for hs in home_starters_stats if hs.pitches == 0], [aws for aws in away_starters_stats if aws.pitches == 0], [hr for hr in home_relievers_stats if hr.pitches == 0], [awr for awr in away_relievers_stats if awr.pitches == 0]]

    for pitchers in no_pitching:
        for pitcher in pitchers:
            local_session.delete(pitcher)

    current_game.home_score = home_score
    current_game.away_score = away_score

    local_session.commit()


def outcome_modifier(outcome, bases, pitch_count, pitch_count_inc, home_score, away_score, home_hitting, inning_outs, pitcher: Pitcher, batter: Batter, pitcher_stats: PitcherGameStats, batters_stats: list[BatterGameStats]):

    # TODO: Implement stealing
    #       If caught and third out, how to handle stats already
    #       added to player in play_ball()

    # if list(map(type, list(bases.values()))) == list(map(type, [1, None, None])):
    #     if pitcher.handed == 'L':
    #
    #
    # elif list(map(type, list(bases.values()))) == list(map(type, [None, 1, None])):

    scorers = []
    # Nobody on
    if list(map(type, list(bases.values()))) == list(map(type, [None, None, None])):
        if outcome in ['walk', 'single']:
            bases['1st'] = batter.id

        elif outcome == 'double':
            bases['2nd'] = batter.id

        elif outcome == 'triple':
            bases['3rd'] = batter.id

        elif outcome == 'home_run':
            # TODO: Implement runs
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'out':
            inning_outs += 1

    # Man on first
    elif list(map(type, list(bases.values()))) == list(map(type, [1, None, None])):
        if outcome in ['walk', 'single']:
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id

        elif outcome == 'double':
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None

        elif outcome == 'triple':
            scorers.append(bases['1st'])
            bases['3rd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'home_run':
            scorers.extend([bases['1st'], batter.id])
            bases['1st'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            inning_outs += 1

    # Man on second
    elif list(map(type, list(bases.values()))) == list(map(type, [None, 1, None])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            scorers.append(bases['2nd'])
            bases['1st'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            scorers.append(bases['2nd'])
            bases['2nd'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            scorers.append(bases['2nd'])
            bases['3rd'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'home_run':
            scorers.extend([bases['2nd'], batter.id])
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            inning_outs += 1

    # Man on third
    elif list(map(type, list(bases.values()))) == list(map(type, [None, None, 1])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            scorers.append(bases['3rd'])
            bases['1st'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            scorers.append(bases['3rd'])
            bases['2nd'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            scorers.append(bases['3rd'])
            bases['3rd'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'home_run':
            scorers.extend([bases['3rd'], batter.id])
            bases['3rd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            inning_outs += 1

    # Man on first and second
    elif list(map(type, list(bases.values()))) == list(map(type, [1, 1, None])):
        if outcome in ['walk']:
            bases['3rd'] = bases['2nd']
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id

        elif outcome == 'single':
            scorers.append(bases['2nd'])
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            scorers.append(bases['2nd'])
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            scorers.extend([bases['2nd'], bases['1st']])
            bases['3rd'] = batter.id
            bases['2nd'] = None
            bases['1st'] = None
            # bases = {
            #     '1st': False,
            #     '2nd': False,
            #     '3rd': True
            # }
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'home_run':
            scorers.extend([bases['2nd'], bases['1st'], batter.id])
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'out':
            inning_outs += 1

    # Man on second and third
    elif list(map(type, list(bases.values()))) == list(map(type, [None, 1, 1])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            scorers.extend([bases['3rd'], bases['2nd']])
            bases['1st'] = batter.id
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'double':
            scorers.extend([bases['3rd'], bases['2nd']])
            bases['2nd'] = batter.id
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'triple':
            scorers.extend([bases['3rd'], bases['2nd']])
            bases['3rd'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'home_run':
            scorers.extend([bases['3rd'], bases['2nd'], batter.id])
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'out':
            inning_outs += 1

    # Man on first and third
    elif list(map(type, list(bases.values()))) == list(map(type, [1, None, 1])):
        if outcome in ['walk']:
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id

        elif outcome == 'single':
            scorers.append(bases['3rd'])
            bases['3rd'] = None
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id

            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            scorers.append(bases['3rd'])
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            scorers.extend([bases['3rd'], bases['1st']])
            bases['3rd'] = batter.id
            bases['2nd'] = None
            bases['1st'] = None

            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'home_run':
            scorers.extend([bases['3rd'], bases['1st'], batter.id])
            bases['3rd'] = None
            bases['1st'] = None

            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'out':
            inning_outs += 1

    # Bases loaded
    elif list(map(type, list(bases.values()))) == list(map(type, [1, 1, 1])):
        if outcome in ['walk']:
            scorers.append(bases['3rd'])
            bases['3rd'] = bases['2nd']
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'single':
            scorers.extend([bases['3rd'], bases['2nd']])
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'double':
            scorers.extend([bases['3rd'], bases['2nd']])
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'triple':
            scorers.extend([bases['3rd'], bases['2nd'], bases['1st']])
            bases['3rd'] = batter.id
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'home_run':
            scorers.extend([bases['3rd'], bases['2nd'], bases['1st'], batter.id])
            bases['3rd'] = None
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 4
            else:
                away_score += 4

        elif outcome == 'out':
            inning_outs += 1

# ---------------- UPDATE STAT OBJECTS  ----------------

    current_batter_stats = [batter_stats for batter_stats in batters_stats if batter_stats.batter_id == batter.id][0]  # Grab current batter stats

    current_batter_stats.rbis += len(scorers)  # Increment RBIs based on how many scored

    if batter.id in scorers:  # If the current batter is also in scorers (home run) increment runs by 1
        current_batter_stats.runs += 1

    if outcome != 'walk':  # Increment at bats only if the outcome is not a walk TODO: Strikeouts, sac fly, HBP
        current_batter_stats.at_bats += 1

    outcome_plural = outcome + 's'  # Make outcome plural (single is an outcome; singles is an attribute of stat object)

    if outcome_plural != 'outs':  # Add outcome to stat object
        setattr(current_batter_stats, outcome_plural, getattr(current_batter_stats, outcome_plural) + 1)

    # Updates runners on base with whether they got a run or not
    if len(scorers) != 0:
        scorer_stats = [runner_stats for runner_stats in batters_stats if runner_stats.batter_id in scorers]
        for scorer in scorer_stats:
            scorer.runs += 1

        pitcher_stats.runs += len(scorers)  # Adds to pitcher runs allowed

    # Update pitcher with what they got (strikeout, walk, hit, etc)
    if outcome_plural != 'outs':
        setattr(pitcher_stats, outcome_plural, getattr(pitcher_stats, outcome_plural) + 1)
    pitcher_stats.pitches += pitch_count_inc
    pitch_count += pitch_count_inc

    return bases, pitch_count, home_score, away_score, inning_outs


def play_ball(pitcher: Pitcher, batter: Batter):

    single = ma["1B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    double = ma["2B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    triple = ma["3B"] * ((batter.attributes['speed/stealing'] / 80 + batter.attributes['power'] / 90) / 2)
    home_run = ma["HR"] * (batter.attributes['power'] / pitcher.attributes['movement'])
    walk = ma['BB'] * (batter.attributes['eye'] / pitcher.attributes['control'])
    out = ma['PA'] - (single+double+triple+home_run+walk)
    pitches = (ma['avg_pitches'] + np.random.randint(-3, 2))

    outcome = random.choices(['single', 'double', 'triple', 'home_run', 'walk', 'out'], [single, double, triple, home_run, walk, out])
    # TODO: Player by season table (each row is a player and the year of the stats -- composite key)
    #       Player by season-game table (each row is a players's stats within a specific game
    #       Add onto season table while create new entry for each game
    #       Should it be involved here or in play()?

    # TODO: Implement strikeout vs flyout/groundout (and possible error?)
    # if outcome == 'out':
    return outcome[0], pitches


leagues = [1, 2, 3, 4, 5]


week_schedule = local_session.query(LeagueSeasonSchedule).filter(LeagueSeasonSchedule.league_id == leagues[0]).one().schedule

for count, week in enumerate(week_schedule[:30]):
    for game in week:

        away_team_id = game[0]
        home_team_id = game[1]

        play(home_team_id, away_team_id)
        local_session.commit()

    print(f"Week {count + 1} complete!")

    # TODO: Add week to game object to differentiate when teams play each other more than once
    #       Use 'vars.json' to store the week number after you run a number of weeks of play
    #       Figure out how to `effectively iterate weeks and update the given var in json file
