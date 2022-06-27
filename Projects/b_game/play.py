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


def play_ball(pitcher: Pitcher, batter: Batter):

    single = ma["1B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    double = ma["2B"] * (batter.attributes['contact'] / pitcher.attributes['stuff'])
    triple = ma["3B"] * ((batter.attributes['speed/stealing'] / 80 + batter.attributes['power'] / 90) / 2)
    hr = ma["HR"] * (batter.attributes['power'] / pitcher.attributes['movement'])
    walk = ma['BB'] * (batter.attributes['eye'] / pitcher.attributes['control'])
    out = ma['PA'] - (single+double+triple+hr+walk)
    pitches = (ma['avg_pitches'] + np.random.randint(-3, 2))

    return random.choices(['single', 'double', 'triple', 'hr', 'walk', 'out'], [single, double, triple, hr, walk, out]), pitches


    # local_session = Session(bind=engine)
    #
    # pitcher = local_session.query(Pitcher).filter(Pitcher.main_rating == 65).first()
    # batter = local_session.query(Batter).filter(Batter.main_rating == 75).first()
    #
    # print(pitcher.attributes)
    # print(batter.attributes)
    #
    # l = play_ball(pitcher, batter)
    #
    # print(collections.Counter(l))


def outcome_modifier(outcome, bases, pitch_count, pitch_count_inc, home_score, away_score, home_hitting):
    if all(value == False for value in bases.values()): # Nobody on
        if outcome in ['walk', 'single']:
            bases = {
                '1st': True,
                '2nd': False,
                '3rd': False
            }
        elif outcome == 'double':
            bases = {
                '1st': False,
                '2nd': True,
                '3rd': False
            }
        elif outcome == 'triple':
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': True
            }
        elif outcome == 'hr':
            if home_hitting:
                home_score += 1
            else:
                away_score += 1
        elif outcome == 'out':
            pass
    elif list(bases.values()) == [True, False, False]: # Man on first
        if outcome in ['walk', 'single']:
            bases = {
                '1st': True,
                '2nd': True,
                '3rd': False
            }
        elif outcome == 'double':
            bases = {
                '1st': False,
                '2nd': True,
                '3rd': True
            }
        elif outcome == 'triple':
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': True
            }
            if home_hitting:
                home_score += 1
            else:
                away_score += 1
        elif outcome == 'hr':
            if home_hitting:
                home_score += 2
            else:
                away_score += 2
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': False
            }
        elif outcome == 'out':
            pass

    elif list(bases.values()) == [False, True, False]: # Man on second
        if outcome in ['walk', 'single']:
            bases = {
                '1st': True,
                '2nd': True,
                '3rd': False
            }
        elif outcome == 'double':
            bases = {
                '1st': False,
                '2nd': True,
                '3rd': True
            }
        elif outcome == 'triple':
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': True
            }
            if home_hitting:
                home_score += 1
            else:
                away_score += 1
        elif outcome == 'hr':
            if home_hitting:
                home_score += 2
            else:
                away_score += 2
            bases = {
                '1st': False,
                '2nd': False,
                '3rd': False
            }
        elif outcome == 'out':
            pass


    pitch_count += pitch_count_inc





def play(home: Team, away: Team):
    max_outs = 54
    total_outs = 0
    inning_outs = 0
    pitch_count = 0
    pitch_count_inc = 0
    batter_increment = 0
    next_batter = batter_increment % 9
    home_score = 0
    away_score = 0
    outcome = ''
    bases = {
        '1st': False,
        '2nd': False,
        '3rd': False
    } #TODO: Include player speed as well?
    home_hitting = False



    local_session = Session(bind=engine)

    home_batters = local_session.query(Batter).filter(Batter.current_team == home.id).all()
    away_batters = local_session.query(Batter).filter(Batter.current_team == away.id).all()
    home_starters = local_session.query(Pitcher).filter((Pitcher.current_team == home.id) & (Pitcher.position == 'SP')).all()
    away_starters = local_session.query(Pitcher).filter((Pitcher.current_team == away.id) & (Pitcher.position == 'SP')).all()
    home_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == home.id) & (Pitcher.position == 'RP')).all()
    away_relievers = local_session.query(Pitcher).filter((Pitcher.current_team == away.id) & (Pitcher.position == 'RP')).all()



    batter = away_batters[0]
    pitcher = home_starters[0] #TODO: Variable for next starter in lineup
    while total_outs < max_outs:

        while inning_outs < 3:
            outcome, pitch_count_inc = play_ball(pitcher, batter)

        home_hitting = True

        while inning_outs < 3:
            pass


        home_hitting = False


