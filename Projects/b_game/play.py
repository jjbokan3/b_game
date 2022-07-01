from main import *

import collections

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

starter_pitch_limit = 100
reliever_pitch_limit = 25

local_session = Session(bind=engine)

home_batters = local_session.query(Batter).filter(Batter.current_team == home.id).all()
away_batters = local_session.query(Batter).filter(Batter.current_team == away.id).all()
home_starters = local_session.query(Pitcher).filter((Pitcher.current_team == home.id) & (Pitcher.position == 'SP')).all()
away_starters = local_session.query(Pitcher).filter((Pitcher.current_team == away.id) & (Pitcher.position == 'SP')).all()
home_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == home.id) & (Pitcher.position == 'RP')).all()
away_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == away.id) & (Pitcher.position == 'RP')).all()


def play_ball(pitcher: Pitcher, batter: Batter):

    single = ma["1B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    double = ma["2B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    triple = ma["3B"] * ((batter.attributes['speed/stealing'] / 80 + batter.attributes['power'] / 90) / 2)
    hr = ma["HR"] * (batter.attributes['power'] / pitcher.attributes['movement'])
    walk = ma['BB'] * (batter.attributes['eye'] / pitcher.attributes['control'])
    out = ma['PA'] - (single+double+triple+hr+walk)
    pitches = (ma['avg_pitches'] + np.random.randint(-3, 2))

    outcome = random.choices(['single', 'double', 'triple', 'hr', 'walk', 'out'], [single, double, triple, hr, walk, out])
    # TODO: Player by season table (each row is a player and the year of the stats -- composite key)
    #       Player by season-game table (each row is a players's stats within a specific game
    #       Add onto season table while create new entry for each game
    #       Should it be involved here or in play()?
    return pitches


def outcome_modifier(outcome, bases, pitch_count, pitch_count_inc, home_score, away_score, home_hitting, pitcher: Pitcher, batter: Batter):
    # Nobody on
    if list(map(type, list(bases.values()))) == list(map(type, [None, None, None])):
        if outcome in ['walk', 'single']:
            bases['1st'] = batter.id

        elif outcome == 'double':
            bases['2nd'] = batter.id

        elif outcome == 'triple':
            bases['3rd'] = batter.id

        elif outcome == 'hr':
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'out':
            pass

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
            bases['3rd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'hr':
            bases['1st'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            pass

    # Man on second
    elif list(map(type, list(bases.values()))) == list(map(type, [None, 1, None])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            bases['1st'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            bases['2nd'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            bases['3rd'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'hr':
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            pass

    # Man on third
    elif list(map(type, list(bases.values()))) == list(map(type, [None, None, 1])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            bases['1st'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            bases['2nd'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            bases['3rd'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'hr':
            bases['3rd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'out':
            pass

    # Man on first and second
    elif list(map(type, list(bases.values()))) == list(map(type, [1, 1, None])):
        if outcome in ['walk']:
            bases['3rd'] = bases['2nd']
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id

        elif outcome == 'single':
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'double':
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'triple':
            bases['3rd'] = batter.id
            bases['2nd'] = None
            bases['1st'] = None
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': True
            }
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'hr':
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'out':
            pass

    # Man on second and third
    elif list(map(type, list(bases.values()))) == list(map(type, [None, 1, 1])):
        if outcome in ['walk']:
            bases['1st'] = batter.id

        elif outcome == 'single':
            bases['1st'] = batter.id
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'double':
            bases['2nd'] = batter.id
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'triple':
            bases['3rd'] = batter.id
            bases['2nd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'hr':
            bases['3rd'] = None
            bases['2nd'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'out':
            pass

    # Bases loaded
    elif list(map(type, list(bases.values()))) == list(map(type, [1, 1, 1])):
        if outcome in ['walk']:
            bases['3rd'] = bases['2nd']
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            if home_hitting:
                home_score += 1
            else:
                away_score += 1

        elif outcome == 'single':
            bases['2nd'] = bases['1st']
            bases['1st'] = batter.id
            bases['3rd'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'double':
            bases['3rd'] = bases['1st']
            bases['2nd'] = batter.id
            bases['1st'] = None
            if home_hitting:
                home_score += 2
            else:
                away_score += 2

        elif outcome == 'triple':
            bases['3rd'] = batter.id
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 3
            else:
                away_score += 3

        elif outcome == 'hr':
            bases['3rd'] = None
            bases['2nd'] = None
            bases['1st'] = None
            if home_hitting:
                home_score += 4
            else:
                away_score += 4

        elif outcome == 'out':
            pass

    pitch_count += pitch_count_inc

    return bases, pitch_count, home_score, away_score


def play(home: Team, away: Team):
    max_outs = 54
    total_outs = 0
    inning_outs = 0
    away_pitch_count = 0
    home_pitch_count = 0
    home_batter = 0
    away_batter = 0
    next_home_batter = home_batter % 9
    next_away_batter = away_batter % 9
    home_pitcher = None
    away_pitcher = None
    reliever_number = 0
    home_score = 0
    away_score = 0
    outcome = ''
    bases = {
        '1st': None,
        '2nd': None,
        '3rd': None,
    }  # TODO: Include player speed as well?
    home_hitting = False

    while total_outs != max_outs:
        while inning_outs != 3:
            if home_hitting:
                outcome, pitch_count_inc = play_ball(away_starters[0], home_batters[next_home_batter])
                bases, pitch_count, home_score, away_score = outcome_modifier(outcome, bases, away_pitch_count, pitch_count_inc, home_score, away_score, home_hitting)
                home_batter += 1
                if away_pitcher.attributes['position'] == 'SP' and away_pitch_count > starter_pitch_limit:
                    away_pitcher = away_relievers[reliever_number]
                    reliever_number += 1
                elif away_pitcher.attributes['position'] == 'RP' and away_pitch_count > reliever_pitch_limit:
                    away_pitcher = away_relievers[reliever_number]
                    reliever_number += 1

            else:
                outcome, pitch_count_inc = play_ball(home_starters[0], away_batters[next_away_batter])
                bases, pitch_count, home_score, away_score = outcome_modifier(outcome, bases, home_pitch_count, pitch_count_inc, home_score, away_score, home_hitting)
                away_batter += 1
                if home_pitcher.attributes['position'] == 'SP' and home_pitch_count > starter_pitch_limit:
                    home_pitcher = home_relievers[reliever_number]
                    reliever_number += 1
                elif home_pitcher.attributes['position'] == 'RP' and home_pitch_count > reliever_pitch_limit:
                    home_pitcher = home_relievers[reliever_number]
                    reliever_number += 1

        home_hitting = not home_hitting
        bases = {
            '1st': None,
            '2nd': None,
            '3rd': None,
        }
        inning_outs = 0

    if home_score > away_score:
        home.wins += 1
    else:
        away.wins += 1
    # TODO: Increment player stats at end or in play()?







    batter = away_batters[0]
    pitcher = home_starters[0]  # TODO: Variable for next starter in lineup
    while total_outs < max_outs:

        while inning_outs < 3:
            outcome, pitch_count_inc = play_ball(pitcher, batter)

        home_hitting = True

        while inning_outs < 3:
            pass


        home_hitting = False


