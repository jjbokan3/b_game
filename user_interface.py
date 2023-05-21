import datetime
import json
import os
import sys
import time
import subprocess
from art import *
from collections import defaultdict

import psycopg2
from psycopg2 import sql
import inquirer

from main import *
from play import simulate_play
from player_team_querying import main_query, standings

# from play import *

pd.set_option("display.max_columns", None)
pd.set_option("expand_frame_repr", False)

facts = open("fun_facts.txt", "r").read().split("\n")
#
random.shuffle(facts)

db_params = {
    'host': 'db',
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '354820'
}

# local_session = Session(bind=engine)


# Aggregates each player's stats for a given year
# bgs = local_session.query(BatterGameStats).filter(BatterGameStats.batter.has(current_team=26)).all()
#
# # -------- Displys the batting stats for players on a given team --------
#
# batter = local_session.query(Batter).filter(Batter.id == 10902).first()
#
# groups = defaultdict(list)
# for obj in bgs:
#     groups[obj.batter_id].append(obj)
#
# # -------- Displays the batting stats for an entire league --------
#
# bgs1 = local_session.query(BatterGameStats).all()
# bgs1 = [obj for obj in bgs1 if obj.at_bats != 0]
#
# # TODO: Team not showing up correctly when looking from BatterGameStats.batter.player
# # TODO: Player not showing up when looking from BatterGameStats.batter
# # .filter(BatterGameStats.batter.player.team.has(league_id=1))
#
# groups = defaultdict(list)
# for obj in bgs1:
#     groups[obj.batter_id].append(obj)
#
# df1 = pd.DataFrame([sum(list1).to_dict() for list1 in groups.values()])
#
#
# df1.sort_values('ops', ascending=False, inplace=True)
# print(df1.head(20))
#
# print(local_session.query(BatterGameStats).filter(BatterGameStats.batter_id == 5455).all())

def main():
    with open("vars.json", "r") as f:
        data = json.load(f)

    if not data["onboard_complete"]:
        onboard(data)
        menu(data)
    else:
        menu(data)

# -------- Onboard --------


def onboard(data):
    tprint("Welcome to BaseballSim!")
    time.sleep(2.5)
    questions = [
        inquirer.List(
            "Answer",
            message="Choose from these options:",
            choices=["Create New League", "View Description", "Exit"],
            carousel=True,
        ),
    ]
    answers = inquirer.prompt(questions)

    match answers["Answer"]:
        case "Create New League":
            print("Creating New League (This may take up to 5 minutes)\n")
            print(f"Fun Fact:\n{random.choice(facts)}\n")

            from rich.console import Console
            database = 'postgres'
            user = 'postgres'
            tasks = {
                "python create_db.py": "Creating Database",
                "python create_players.py": "Creating Players",
                "python create_teams_leagues_test.py": "Creating Teams and Leagues",
                "python schedule_creation.py": "Creating Team Schedules",
            }

            # Connect to the PostgreSQL server
            conn = psycopg2.connect(**db_params)
            print(1)

            # Create a new cursor
            cur = conn.cursor()

            print(2)
            # Execute an SQL command
            try:
                cur.execute(sql.SQL("drop schema public cascade; create schema public;"))

                print(3)
            # Commit the transaction
                conn.commit()

                print(4)

            except psycopg2.DatabaseError as e:
                print(e.pgcode)
            # Close the cursor and the connection
            cur.close()
            conn.close()

            print(5)

            console = Console()
            for task in tasks:
                with console.status(
                    f"[bold green]{tasks[task]}...", spinner="aesthetic"
                ) as status:
                    try:
                        subprocess.run(
                            task,
                            shell=True,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        console.print(
                            f"[bold green]{tasks[task]}[bold green] :thumbsup:"
                        )  # TODO: Find checkmark emoji
                        continue
                    except subprocess.CalledProcessError:
                        console.print(f"[bold red]{tasks[task]} :thumbsdown:")
                        sys.exit(2)

            print("League created successfully!")
            username = input("Enter your chosen username: ")
            teamname = input("Enter your chosen team name: ")

            data["user_info"]["username"] = username
            data["user_info"]["team_name"] = teamname
            data["user_info"]["current_team"] = random.randint(1, 31)
            data["current_week"] = 1
            data["onboard_complete"] = True
            with open("vars.json", "w") as f:
                json.dump(data, f)

            print(
                f"Onboarding was succesful!\nUsername: {data['user_info']['username']}\nTeam Name: {data['user_info']['team_name']}"
            )
            time.sleep(5)

        case "View Description":
            pass

        case "Exit":
            sys.exit()


# ------- Interface -------

current_time = datetime.datetime.now().hour

if 3 < current_time < 12:
    greeting = "Good Morning"
elif 12 <= current_time < 16:
    greeting = "Good Afternoon"
elif current_time >= 16 or current_time <= 3:
    greeting = "Good Evening"
else:
    greeting = ""


# with open('vars.json', 'r') as f:
#     data = json.load(f)
#
# data["last_login"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

# with open('vars.json', 'w') as f:
#     json.dump(data, f)

os.system("clear")

# print(f'{greeting} {data["user_info"]["username"]}! WELCOME TO THE BASEBALL GAME!\n')


def menu(data):
    while True:
        subprocess.run("clear", shell=True)
        tprint("Welcome to BaseballSim!")
        os.system("jp2a --colors --border --height=30 baseball.jpeg")

        questions = [
            inquirer.List(
                "Answer",
                message="Choose from these options:",
                choices=[
                    "Simulate PLay",
                    "View Standings",
                    "View League Leaders",
                    "View Player Stats",
                    "Change Lineup",
                    "Change Starting Precedence",
                    "Modify Team Settings",
                    "Restart League",
                    "Exit",
                ],
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)

        match answers["Answer"]:
            case "Simulate PLay":
                num_weeks = int(input("Enter the number of weeks to simulate: "))
                simulate_play(num_weeks, 1)
            case "View Standings":
                standings()
            case "View League Leaders":
                pass
            case "View Player Stats":
                main_query()
            case "Change Lineup":
                pass
            case "Change Starting Precedence":
                pass
            case "Modify Team Settings":
                # ... Your code here ...
                pass
            case "Restart League":
                data["onboard_complete"] = False
                with open("vars.json", "w") as f:
                    json.dump(data, f)
                os.system("clear")
                onboard(data)
                # continue back to the start of the loop
                continue
            case "Exit":
                return



if __name__ == "__user_interface__":
    main()

