from main import *
import time
import numpy as np
import random
import pandas as pd
import inquirer
import json
import os
from collections import defaultdict

local_session = Session(bind=engine)


def main_query():
    questions = [
        inquirer.List(
            "Answer",
            message="What scope would you like to query in?",
            choices=["My team", "Another team", "Whole league"],
            carousel=True,
        ),
    ]
    answers = inquirer.prompt(questions)

    with open("vars.json", "r") as f:
        data = json.load(f)

    match answers["Answer"]:
        case "My team":
            bgs1 = (
                local_session.query(BatterGameStats)
                .filter(
                    BatterGameStats.batter.has(
                        current_team=data["user_info"]["current_team"]
                    )
                )
                .all()
            )

            groups = defaultdict(list)
            for obj in bgs1:
                groups[obj.batter_id].append(obj)

            df1 = pd.DataFrame([sum(list1).to_dict() for list1 in groups.values()])
            df1.sort_values("ops", ascending=False, inplace=True)
            pd.options.display.float_format = '{:.3f}'.format
            print(df1.head(20))
            input("Press Enter to continue...")

        case "Another team":
            pass
        case "Whole league":
            pass


def standings():
    teams = local_session.query(Team).filter(Team.league_id == 1).all()

    df1 = pd.DataFrame([team.to_dict() for team in teams])
    df1.sort_values("wins", ascending=False, inplace=True)
    print(df1.head(30))
    input("Press Enter to continue...")
