from main import *
import pandas as pd
import random
import time
from collections import defaultdict

local_session = Session(bind=engine)

# TODO: Create leagues THEN teams or vice versa?
leagues = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
# divisions = ['Red', 'Blue', 'Purple']
# Diamond (95, 100]
# Platinum (90, 95]
# Gold (80, 90]
# Silver (70, 80]
# Bronze (60, 70)

league_ratings = {
    'Diamond': 92.5,
    'Platinum': 87.5,
    'Gold': 80.0,
    'Silver': 70.0,
    'Bronze': 60.0,
}

animals = pd.read_csv('Team Name Data/animals.csv', header=None)
animals.columns = ['Animals']
animals_list = animals['Animals'].to_list()

cities = pd.read_csv('Team Name Data/uscities.csv', usecols=[0])
cities_list = cities['city'].to_list()

team_name = f"{random.sample(cities_list, 1)[0]} {random.sample(animals_list, 1)[0]}"

"""
Get lists of all batters, starters, and relievers
randomly select 13 batters, 5 starters, and 8 relievers to each team
"""

all_batters = local_session.query(Batter).all()
all_pitchers = local_session.query(Pitcher).all()

infield_choices = ['1B', '2B', '3B', 'SS']
outfield_choices = ['LF', 'CF', 'RF']

starters = ['SP', 'SP', 'SP', 'SP', 'SP']
relievers = ['RP', 'RP', 'RP', 'RP', 'RP', 'RP', 'RP', 'RP']

lf = [batter for batter in all_batters if batter.position == 'LF']
cf = [batter for batter in all_batters if batter.position == 'CF']
rf = [batter for batter in all_batters if batter.position == 'RF']
c = [batter for batter in all_batters if batter.position == 'C']
b1 = [batter for batter in all_batters if batter.position == '1B']
b2 = [batter for batter in all_batters if batter.position == '2B']
b3 = [batter for batter in all_batters if batter.position == '3B']
ss = [batter for batter in all_batters if batter.position == 'SS']
sp = [pitcher for pitcher in all_pitchers if pitcher.position == 'SP']
rp = [pitcher for pitcher in all_pitchers if pitcher.position == 'RP']

all_players = {
    'C': c,
    '1B': b1,
    '2B': b2,
    '3B': b3,
    'SS': ss,
    'LF': lf,
    'CF': cf,
    'RF': rf,
    'SP': sp,
    'RP': rp
}


on_team = []

# TODO: Figure out how to add players to teams
#       Create teams first
#       1 of each position, 1 extra catcher, 2inf, 2outf
#       for each team, pop a random player from each position list
#       and add them to a list. Then find the average rating of the
#       list and add that to the team's main rating. Then create a list
#       of all the player ids on the team and add them to the player_list.

# TODO: Create 30 teams for each league (5) 150 teams
#       Should I mass create teams and then pick 15 for each league
#       within the league constraints or should I create teams where
#       you filter the players into a certain range and then pick those players?
#
# for x in positions:

# 7min 27sec on M1 Pro Macbook Pro
for x in leagues:
    x_league = League(x)
    local_session.add(x_league)
    local_session.commit()
    # print(f"{x} league created")

for x in leagues:
    x_league = local_session.query(League).filter(League.name == x).all()[0]

    for y in range(30):
        team_name = f"{random.sample(cities_list, 1)[0]} {random.sample(animals_list, 1)[0]}"
        y_team = Team(team_name, x_league.id)
        local_session.add(y_team)
        local_session.commit()
        # print(f"{y_team.name} team created")

for x in leagues:
    x_league = local_session.query(League).filter(League.name == x).all()[0]
    league_rating = league_ratings[x]
    league_teams = local_session.query(Team).filter(Team.league_id == x_league.id).all()
    for team in league_teams:
        infield = ['C', 'C', '1B', '2B', '3B', 'SS', np.random.choice(infield_choices), np.random.choice(infield_choices)]
        for inf in infield:
            rating_inf = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                time1 = time.time()
                # print(f"Time up until crap {time.time() - time0}")
                rating_inf = [infielder for infielder in all_players[inf] if infielder.main_rating == rating]
                # print(f"Why is this so long ->> {time.time() - time1}")
                if len(rating_inf) > 0:
                    break

            player = random.choice(rating_inf)
            player.current_team = team.id
            on_team.append(player.id)
            all_players[inf].remove(player)

        # print(f"Infielders Created")

        outfield = ['LF', 'CF', 'RF', np.random.choice(outfield_choices), np.random.choice(outfield_choices)]
        for out in outfield:
            rating_outf = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_outf = [outfielder for outfielder in all_players[out] if outfielder.main_rating == rating]
                if len(rating_outf) > 0:
                    break

            player = random.choice(rating_outf)
            player.current_team = team.id
            on_team.append(player.id)
            all_players[out].remove(player)

        # print(f"Outfielders Created")

        for start in starters:
            rating_start = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_start = [starter for starter in all_players[start] if starter.main_rating == rating]
                if len(rating_start) > 0:
                    break

            player = random.choice(rating_start)
            player.current_team = team.id
            on_team.append(player.id)
            all_players[start].remove(player)

        # print(f"Starters Created")

        for relieve in relievers:
            rating_relieve = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_relieve = [reliever for reliever in all_players[relieve] if reliever.main_rating == rating]
                if len(rating_relieve) > 0:
                    break

            player = random.choice(rating_relieve)
            player.current_team = team.id
            on_team.append(player.id)
            all_players[relieve].remove(player)

        # print(f"Relievers Created")

        # print(f"Team {team.name} populated")

    local_session.commit()
    # print(f"{x} League populated")


# Set Default Lineup for teams

teams = local_session.query(Team).all()

# Add lineup spot for batters
# for team in teams:  # TODO: Ensure each team has a lineup filled with each position
#     batters = local_session.query(Batter).filter(Batter.current_team == team.id).all()
#     batter_weights = {batter.id: batter.attributes['contact'] * .5 + batter.attributes['power'] * .5 for batter in batters}
#     player_weights_sorted = {k: v for k, v in sorted(batter_weights.items(), key=lambda item: item[1], reverse=True)}
#     for count, batter_id in enumerate(player_weights_sorted.keys()):
#         batter = next(batter for batter in batters if batter.id == batter_id)
#         batter.num_in_lineup = count + 1

# groups = defaultdict(list)
# for obj in batters:
#     groups[obj.position].append(obj)
#
# gx = [groups[x] for x in groups.values()]

# df1 = pd.DataFrame([sum(list1).to_dict() for list1 in groups.values()])
# df1.sort_values('ops', ascending=False, inplace=True)
# print(df1.head(20))

for team in teams:
    batters = local_session.query(Batter).filter(Batter.current_team == team.id).all()
    batter_weights = {batter.id: [batter.attributes['contact'] * .5 + batter.attributes['power'] * .5, batter.position] for batter in batters}
    batter_weights_sorted = {k: v for k, v in sorted(batter_weights.items(), key=lambda item: item[1][0], reverse=True)}
    manditory_positions = ['C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF']
    count = 1
    dh = False
    for [batter_id, values] in batter_weights_sorted.items():
        if values[1] in manditory_positions:
            batter = next(batter for batter in batters if batter.id == batter_id)
            batter.num_in_lineup = count
            count += 1
            manditory_positions.remove(values[1])
        elif not dh:
            batter = next(batter for batter in batters if batter.id == batter_id)
            batter.num_in_lineup = count
            count += 1
            dh = True




# Add pitching priority for starters
for team in teams:
    pitchers = local_session.query(Pitcher).filter(Pitcher.current_team == team.id, Pitcher.position == 'SP').all()
    pitchers.sort(key=lambda x: x.main_rating, reverse=True)
    for count, pitcher in enumerate(pitchers):
        pitcher.pitcher_priority = count + 1

# Add pitching priority for relievers
for team in teams:
    pitchers = local_session.query(Pitcher).filter(Pitcher.current_team == team.id, Pitcher.position == 'RP').all()
    pitchers.sort(key=lambda x: x.main_rating, reverse=True)
    for count, pitcher in enumerate(pitchers):
        pitcher.pitcher_priority = count + 1

local_session.commit()

# TODO: Starting pitching and relievers
# TODO: Bench bats? What the point of an AI team that has bench bats?
