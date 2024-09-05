from datetime import date, datetime
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

from title_belt_nhl.models.nhl_team_schedule_response import Game
from title_belt_nhl.service.nhl_api import getFullSchedule
from title_belt_nhl.utils import ExcelDate

INITIAL_BELT_HOLDER = "FLA"
SCHEDULE_FILE = Path(__file__).parent / "static" / "schedule_2024_2025.csv"


class TitleBelt:
    team: str
    belt_holder: str

    def __init__(self, team, belt_holder):
        self.team = team
        self.belt_holder = belt_holder


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


class Schedule:
    team: str
    belt_holder: str
    games: list[Match] = []
    from_date: ExcelDate = ExcelDate(date_obj=date.today())
    season: str

    def __init__(
        self, team, season: Optional[str] = None, from_date: Union[date, int] = None
    ):
        self.team = team
        if from_date:
            self.set_from_date(from_date)

        if season is None:
            base_year = (
                date.today().year if date.today().month > 6 else date.today().year - 1
            )
            season = f"{base_year}{base_year+1}"
        self.season = season

        # Get Schedule From API and determine current belt holder
        leagueSchedule = getFullSchedule(season)
        self.belt_holder = Schedule.find_current_belt_holder(
            leagueSchedule, INITIAL_BELT_HOLDER
        )

        for game in leagueSchedule:
            game_date_obj = datetime.strptime(game.gameDate, "%Y-%m-%d")

            match = Match(
                game.homeTeam["abbrev"],
                game.awayTeam["abbrev"],
                ExcelDate(date_obj=game_date_obj.date()).serial_date,
            )
            self.games.append(match)

    def __str__(self):
        return dedent(f""" \
            Schedule of {len(self.games)} total games
            for Team [{self.team}] and Belt Holder [{self.belt_holder}]
            starting from date [{self.from_date.date_obj}] \
            """)

    def set_from_date(self, from_date: Union[date, int]):
        if type(from_date) is date:
            self.from_date = ExcelDate(date_obj=from_date)
        if type(from_date) is int:
            self.from_date = ExcelDate(serial_date=from_date)

    def games_after_date_inclusive(
        self, from_date: Union[date, int] = None
    ) -> list[Match]:
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
            newTeams.append(f"{tm} -> {cur_match} -> {cur_match.away}")
            newTeams.append(f"{tm} -> {cur_match} -> {cur_match.home}")

        if found:
            return path_string
        else:
            path_string = self.find_nearest_path(newTeams, path_string, cur_match.date)
        return path_string

    @classmethod
    def find_current_belt_holder(
        cls, leagueSchedule: list[Game], start_belt_holder: str
    ) -> str:
        """
        Given an array of `Game` and the Abbreviation of the season start belt holder,
        Return the current belt holder based off of game results.  This assumes the list of games is
        pre-sorted by date.
        """
        cur_belt_holder = start_belt_holder
        completed_games: list[Game] = list(
            filter(lambda x: x.is_game_complete(), leagueSchedule)
        )

        for cg in completed_games:
            winningTeam = cg.determine_winning_team()
            if winningTeam is not None and cg.is_title_belt_game(cur_belt_holder):
                cur_belt_holder = winningTeam
        return cur_belt_holder
