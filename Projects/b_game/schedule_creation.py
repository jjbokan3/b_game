from random import shuffle

from sqlalchemy import desc
from main import *
local_session = Session(bind=engine)
local_session.add(Season())
local_session.commit()
current_season = local_session.query(Season).order_by(desc(Season.year)).limit(1)[0]

all_teams = local_session.query(Team).all()

all_leagues = local_session.query(League).all()
all_leagues.sort(key=lambda x: x.id, reverse=True)

leagues = {
    1: [team.id for team in all_teams if team.league == 1],
    2: [team.id for team in all_teams if team.league == 2],
    3: [team.id for team in all_teams if team.league == 3],
    4: [team.id for team in all_teams if team.league == 4],
    5: [team.id for team in all_teams if team.league == 5],
}

num_weeks = 162


def create_schedule(team_list, num_weeks):
    """
    Create a schedule for the given teams
    Args:
        team_list: List of team ids
        num_weeks:

    Returns:

    """
    schedule = []
    for week in range(num_weeks):
        shuffle(team_list)
        schedule.append([team_list[i::int(len(team_list)/2)] for i in range(int(len(team_list) / 2))])
    return schedule


for count, (league, teams) in enumerate(leagues.items()):
    local_session.add(LeagueSeasonSchedule(league, current_season.year, create_schedule(teams, num_weeks)))

local_session.commit()


# TODO: Add place in lineup for players on teams and energy for pitchers