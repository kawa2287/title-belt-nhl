import csv
from datetime import date, datetime
from pathlib import Path
from textwrap import dedent
from typing import Union
from title_belt_nhl.service.nhl_api import getFullSchedule
from title_belt_nhl.models.nhl_team_schedule_response import Game

import click

EXCEL_EPOCH_DATE = date(1900, 1, 1)
SCHEDULE_FILE = Path(__file__).parent / "static" / "schedule_2024_2025.csv"
SEASON = '20242025'
INITIAL_BELT_HOLDER = 'FLA'

@click.command()
@click.option("--team", default="VAN", required=True)
def cli(team):
    click.echo(f"Calculating shortest path for {team} to challenge for the belt...")

    schedule = Schedule(team)
    holder = schedule.belt_holder

    path = schedule.find_nearest_path([holder], holder)
    games = path.split("vs")

    click.echo("=============================================================")
    click.echo(f"CURRENT BELT HOLDER: {holder}")
    click.echo(f"{len(games)-1} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
    click.echo(path)


class ExcelDate:
    date_obj: date
    serial_date: int

    def __init__(self, date_obj: date = None, serial_date: int = None):
        if not date_obj and not serial_date:
            raise ValueError("One of 'date_obj' or 'serial_date' is required to construct ExcelDate instance")

        if date_obj:
            self.date_obj = date_obj
            self.serial_date = (date_obj - EXCEL_EPOCH_DATE).days + 1
        elif serial_date:
            self.date_obj = date.fromordinal(EXCEL_EPOCH_DATE.toordinal() + serial_date - 1)
            self.serial_date = serial_date


class Match:
    home: str
    away: str
    date: int

    def __init__(self, home, away, date):
        self.home = home
        self.away = away
        self.date = date

    def __str__(self):
        return f"[{self.home} vs {self.away}]"


class Schedule():
    team: str
    belt_holder: str
    games: list[Match] = []
    from_date: ExcelDate = ExcelDate(date_obj=date.today())

    def __init__(self, team, from_date: Union[date, int] = None):
        self.team = team
        if from_date:
            self.set_from_date(from_date)

        # Get Schedule From API and determine current belt holder
        leagueSchedule = getFullSchedule(SEASON)
        self.belt_holder = Schedule.find_current_belt_holder(leagueSchedule)

        for game in leagueSchedule:
            game_date_obj = datetime.strptime(game['gameDate'],"%Y-%m-%d" )
            
            match = Match(
                game['homeTeam']['abbrev'], 
                game['awayTeam']['abbrev'],
                ExcelDate(date_obj=game_date_obj.date()).serial_date
            )
            self.games.append(match)
    
    def __str__(self):
        return dedent(f""" \
            Schedule of {len(self.games)} total games
            for Team [{self.team}] and Belt Holder [{self.belt_holder}]
            starting from date [{self.from_date.date_obj}] \
            """
        )

    def set_from_date(self, from_date: Union[date, int]):
        if type(from_date) is date:
            self.from_date = ExcelDate(date_obj=from_date)
        if type(from_date) is int:
            self.from_date = ExcelDate(serial_date=from_date)

    def games_after_date_inclusive(self, from_date: Union[date, int] = None) -> list[Match]:
        if from_date:
            self.set_from_date(from_date)
        return [g for g in self.games if g.date >= self.from_date.serial_date]

    def find_match(self, current_belt_holder, from_date) -> Match:
        for game in self.games_after_date_inclusive(from_date=from_date):
            if (
                game.away == current_belt_holder or game.home == current_belt_holder
            ) and self.from_date.serial_date < game.date:
                return game

    def find_nearest_path(self, teams, path_string, from_date=None) -> str:
        found = False
        newTeams = []
        if from_date:
            self.set_from_date(from_date)
        for tm in teams:
            splits = tm.split(" -> ")
            cur_match: Match = self.find_match(splits[-1], self.from_date)
            if cur_match and cur_match.away == self.team or cur_match.home == self.team:
                found = True
                path_string = f"{tm} -> {cur_match}"
                break
            else:
                newTeams.append(f"{tm} -> {cur_match} -> {cur_match.away}")
                newTeams.append(f"{tm} -> {cur_match} -> {cur_match.home}")

        if found:
            return path_string
        else:
            path_string = self.find_nearest_path(
                newTeams, path_string, cur_match.date
            )
        return path_string
    
    def is_game_complete(game: Game) -> bool:
        gameState = game['gameState'].upper()
        return gameState == 'OFF' or gameState == 'FINAL'
    
    def determine_winning_team(game: Game) -> str:
        homeScore = game['homeTeam']['score']
        awayScore = game['awayteam']['score']
        if homeScore > awayScore:
            return game['homeTeam']['abbrev']
        elif awayScore > homeScore:
            return game['awayteam']['abbrev']
        else:
            return None
    
    def find_current_belt_holder(leagueSchedule: list[Game]) -> str:
        cur_belt_holder = INITIAL_BELT_HOLDER
        completed_games: list[Game] = list(filter(lambda x: Schedule.is_game_complete(x), leagueSchedule))

        for cg in completed_games:
            winningTeam = Schedule.determine_winning_team(cg)
            if winningTeam is not None:
                cur_belt_holder = winningTeam
        return cur_belt_holder

if __name__ == "__main__":
    cli()
