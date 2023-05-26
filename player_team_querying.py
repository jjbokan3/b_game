from main import *
import time
import numpy as np
import random
import pandas as pd
import inquirer
import json
import os
from collections import defaultdict

# local_session = Session(bind=engine)

from contextlib import contextmanager
from rich.table import Table
from rich.console import Console

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    local_session = Session(bind=engine)
    try:
        yield local_session
    finally:
        local_session.rollback()
        local_session.close()


def print_dataframe(df):
    """Prints a pandas DataFrame using the rich package's Table format."""

    table = Table(show_header=True, header_style="bold magenta", show_lines=True)

    # Add columns
    for column in df.columns:
        table.add_column(column)

    # Add rows
    for _, row in df.iterrows():
        table.add_row(*row.astype(str).tolist())

    console = Console()
    console.print(table)

def print_dataframe_standings(df, user_team):
    """Prints a pandas DataFrame using the rich package's Table format."""

    table = Table(show_header=True, header_style="bold magenta", show_lines=True)

    # Add columns
    for column in df.columns:
        table.add_column(column)

    # Add rows
    for _, row in df.iterrows():
        if row["id"] == user_team:
            table.add_row(*row.astype(str).tolist(), style="bold green")
        else:
            table.add_row(*row.astype(str).tolist())

    console = Console()
    console.print(table)

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
            with session_scope() as local_session:
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
                # print(df1.head(20))
                print_dataframe(df1.head(20))
                input("Press Enter to continue...")

        case "Another team":
            pass
        case "Whole league":
            pass


def standings(data):

    # with open("vars.json", "r") as f:
        # data = json.load(f)
    with session_scope() as local_session:
        teams = local_session.query(Team).filter(Team.league_id == 1).all()

        df1 = pd.DataFrame([team.to_dict() for team in teams])
        df1.sort_values("wins", ascending=False, inplace=True)
        # print(df1.head(30))
        print_dataframe_standings(df1.head(30), data['user_info']['current_team'])

    input("Press Enter to continue...")
