from main import *
import pandas as pd
import random
import time

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
    'Gold': 80,
    'Silver': 70,
    'Bronze': 60,
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

t0 = time.time()
all_batters = local_session.query(Batter).all()
all_pitchers = local_session.query(Pitcher).all()
t1 = time.time()

total = t1-t0
print(total)
print(all_batters[0].name)

positions = ['C', 'C', '1B', '2B', '2B', '3B', 'SS', 'SS', 'LF', 'LF', 'CF', 'CF', 'RF']
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

infielders = [c, b1, b2, b3, ss]
outfielders = [lf, cf, rf]
pitchers = [sp, rp]

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
t0 = time.time()
on_team = []

# 7min 27sec on M1 Pro Macboob Pro
for x in leagues:
    league_rating = league_ratings[x]
    x_league = League(x)
    local_session.add(x_league)
    local_session.commit()
    x_league = local_session.query(League).filter(League.name == x).all()[0]
    for y in range(30):
        team_name = f"{random.sample(cities_list, 1)[0]} {random.sample(animals_list, 1)[0]}"
        y_team = Team(team_name, x_league.id)
        local_session.add(y_team)
        local_session.commit()
        y_team = local_session.query(Team).filter(Team.name == y_team.name).all()[0]


        for count, inf in enumerate(infielders):
            t0 = time.time()
            rating_inf = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_inf = [infielder for infielder in inf if infielder.main_rating == rating]
                if len(rating_inf) > 0:
                    break

            player = random.choice(rating_inf)
            player.current_team = y_team.id
            on_team.append(player.id)
            infielders[count].remove(player)

        print(f"Infielders Created")

        for count, inf in enumerate(outfielders):
            rating_outf = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_outf = [outfielder for outfielder in inf if outfielder.main_rating == rating]
                if len(rating_outf) > 0:
                    break

            player = random.choice(rating_outf)
            player.current_team = y_team.id
            on_team.append(player.id)
            outfielders[count].remove(player)

        print(f"Outfielders Created")

        for start in range(5):
            rating_start = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_start = [starter for starter in sp if starter.main_rating == rating]
                if len(rating_start) > 0:
                    break

            player = random.choice(rating_start)
            player.current_team = y_team.id
            on_team.append(player.id)
            sp.remove(player)

        print(f"Starters Created")

        for start in range(8):
            rating_relieve = []
            while True:
                rating = np.around(np.random.normal(league_rating, 1.5))
                rating_relieve = [reliever for reliever in rp if reliever.main_rating == rating]
                if len(rating_relieve) > 0:
                    break

            player = random.choice(rating_relieve)
            player.current_team = y_team.id
            on_team.append(player.id)
            rp.remove(player)

        print(f"Relievers Created")

        print(f"Team {y} created")

    local_session.commit()
    print(f"{x} League Created")


t1 = time.time()
print(t1-t0)




