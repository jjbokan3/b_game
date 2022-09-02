import datetime
import json
import os
import sys
import time
from art import *
from collections import defaultdict

import inquirer

from main import *

pd.set_option('display.max_columns', None)
pd.set_option('expand_frame_repr', False)
# facts = open('fun_facts.txt', 'r').read().split('\n')
#
# random.shuffle(facts)
#
# for fact in facts:
#     print(fact)
#     time.sleep(5)


local_session = Session(bind=engine)


# Aggregates each player's stats for a given year
bgs = local_session.query(BatterGameStats).filter(BatterGameStats.batter.has(current_team=26)).all()

# -------- Displys the batting stats for players on a given team --------

batter = local_session.query(Batter).filter(Batter.id == 10902).first()

groups = defaultdict(list)
for obj in bgs:
    groups[obj.batter_id].append(obj)

# -------- Displays the batting stats for an entire league --------

bgs1 = local_session.query(BatterGameStats).all()
bgs1 = [obj for obj in bgs1 if obj.at_bats != 0]

# TODO: Team not showing up correctly when looking from BatterGameStats.batter.player
# TODO: Player not showing up when looking from BatterGameStats.batter
# .filter(BatterGameStats.batter.player.team.has(league_id=1))

groups = defaultdict(list)
for obj in bgs1:
    groups[obj.batter_id].append(obj)

df1 = pd.DataFrame([sum(list1).to_dict() for list1 in groups.values()])


df1.sort_values('ops', ascending=False, inplace=True)
print(df1.head(20))

print(local_session.query(BatterGameStats).filter(BatterGameStats.batter_id == 5455).all())


# ------- Interface -------

current_time = datetime.datetime.now().hour

if 3 < current_time < 12:
    greeting = 'Good Morning'
elif 12 <= current_time < 16:
    greeting = 'Good Afternoon'
elif current_time >= 16 or current_time <= 3:
    greeting = 'Good Evening'
else:
    greeting = ''


with open('vars.json', 'r') as f:
    data = json.load(f)

data["last_login"] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

with open('vars.json', 'w') as f:
    json.dump(data, f)

os.system('clear')

# print(f'{greeting} {data["user_info"]["username"]}! WELCOME TO THE BASEBALL GAME!\n')

tprint('Welcome to BaseballSim!')


os.system('jp2a --colors --border --height=30 baseball.jpeg')

def menu():
    questions = [
        inquirer.List('Answer',
                      message="Choose from these options:",
                      choices=['View Standings', 'View League Leaders', 'View Player Stats', 'Change Lineup', 'Change Starting Precedence', 'Modify Team Settings', 'Exit'],
                      carousel=True),
    ]
    answers = inquirer.prompt(questions)

    match answers['Answer']:
        case 'View Standings':
            pass

        case 'View League Leaders':
            pass

        case 'View Player Stats':
            pass

        case 'Change Lineup':
            pass

        case 'Change Starting Precedence':
            pass

        case 'Modify Team Settings':
            questions = [
                inquirer.List('Answer',
                              message="Available options to modify:",
                              choices=['Change username', 'Change team name', 'Change team color', 'Change team logo'],
                              ),
            ]
            os.system('clear')
            answers = inquirer.prompt(questions)


            match answers['Answer']:
                case 'Change username':
                    os.system('clear')
                    new_username = input('Enter new username: ')
                    data['user_info']['username'] = new_username
                    with open('vars.json', 'w') as f:
                        json.dump(data, f)
                    print(f'Username changed to {new_username} successfully!')
                    time.sleep(3)
                    menu()

                case 'Change team name':
                    pass

                case 'Change team color':
                    pass

                case 'Change team logo':
                    pass

        case 'Exit':
            sys.exit()


menu()