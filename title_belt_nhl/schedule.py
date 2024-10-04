from datetime import date, datetime
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

from title_belt_nhl.models.nhl_team_schedule_response import Game
from title_belt_nhl.service.nhl_api import getFullSchedule
from title_belt_nhl.utils import ExcelDate

INITIAL_BELT_HOLDER = "FLA"
SCHEDULE_FILE = Path(__file__).parent / "static" / "schedule_2024_2025.csv"


class Match:
    home: str
    away: str
    serial_date: int
    date_obj: date
    belt_holder: str = None
    home_last: str = None
    away_last: str = None

    def __init__(self, home, away, serial_date=None, date_obj=None):
        self.home = home
        self.away = away
        self.serial_date = serial_date
        self.date_obj = date_obj or ExcelDate(serial_date=serial_date).date_obj

    def __str__(self):
        return f"[{self.home} vs {self.away}]"


def traverse_matches_backwards(
    matches: list[list[Match]] | None = None, match: Match | None = None
):
    """Traverse a tree/graph of matches backwards to find the path to the top.

    Parameters:
    - matches: list[list[Match]] (optional)
      - each index of matches represents a depth into the tree/graph of matches
      - index 0 and last index should each contain a single match
      - index 0 represents the upcoming match for the current belt holder
      - last index represents the first match in the graph where the current team
        can play for the belt
    - match: Match (optional)
      - basically same as above, but only pass the last match that we can work up from

    ASSUMPTIONS:
    - each match specifies either home_last or away_last, matching with the
      match's belt_holder (home_last if belt_holder is home, or vice versa)
    """
    if not matches and not match:
        raise ValueError("Either matches or match must be provided!")
    path_matches = []
    cur_match = match or matches[-1][0]
    while cur_match:
        path_matches.insert(0, cur_match)

        # this line assumes that only away_last *or* home_last is set
        # and it matches the belt_holder
        last_match = cur_match.away_last or cur_match.home_last

        if not last_match:
            break
        cur_match = last_match

    return path_matches


class Schedule:
    team: str
    belt_holder: str
    matches: list[Match] = []
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

        self.matches = []
        for game in leagueSchedule:
            game_date_obj = datetime.strptime(game.gameDate, "%Y-%m-%d").date()

            match = Match(
                game.homeTeam["abbrev"],
                game.awayTeam["abbrev"],
                serial_date=ExcelDate(date_obj=game_date_obj).serial_date,
                date_obj=game_date_obj,
            )
            self.matches.append(match)

    def __str__(self):
        return dedent(f""" \
            Schedule of {len(self.matches)} total matches
            for Team [{self.team}] and Belt Holder [{self.belt_holder}]
            starting from date [{self.from_date.date_obj}] \
            """)

    def get_season_pretty(self):
        """Convert yyyyYYYY to yyyy-YY (20242025 --> 2024-25)."""
        if self.season:
            return f"{self.season[:4]}-{self.season[6:]}"

    def set_from_date(self, from_date: Union[date, int]):
        if type(from_date) is date:
            self.from_date = ExcelDate(date_obj=from_date)
        if type(from_date) is int:
            self.from_date = ExcelDate(serial_date=from_date)

    def matches_after_date_inclusive(
        self, from_date: Union[date, int] = None
    ) -> list[Match]:
        if from_date:
            self.set_from_date(from_date)
        return [g for g in self.matches if g.serial_date >= self.from_date.serial_date]

    def find_match(self, current_belt_holder, from_date) -> Match:
        for match in self.matches_after_date_inclusive(from_date=from_date):
            if (
                match.away == current_belt_holder or match.home == current_belt_holder
            ) and self.from_date.serial_date < match.serial_date:
                match.belt_holder = current_belt_holder
                return match

    def find_nearest_path_str(self, teams, path_string, from_date=None) -> str:
        newTeams = []
        if from_date:
            self.set_from_date(from_date)
        for tm in teams:
            splits = tm.split(" -> ")
            cur_match: Match = self.find_match(splits[-1], self.from_date)
            if cur_match:
                if cur_match.away == self.team or cur_match.home == self.team:
                    return f"{tm} -> {cur_match}"
                newTeams.append(f"{tm} -> {cur_match} -> {cur_match.away}")
                newTeams.append(f"{tm} -> {cur_match} -> {cur_match.home}")

        path_string = self.find_nearest_path_str(
            newTeams, path_string, cur_match.serial_date
        )
        return path_string

    def find_nearest_path_games(self):
        """Find the shortest path from the current belt holder's next game until
        self.team has a chance to play for the belt. May involve the belt changing
        hands in between.

        Requires
        """
        first_match: Match = self.find_match(self.belt_holder, self.from_date)
        matches = [[first_match]]
        depth = 0
        while matches[depth]:
            cur_matches = matches[depth]
            next_matches = []
            for m in cur_matches:
                if m.away == self.team or m.home == self.team:
                    return traverse_matches_backwards(match=m)
                else:
                    next_match_home = self.find_match(m.home, m.date_obj)
                    if next_match_home:
                        # else no more matches for home team
                        next_match_home.away_last = m
                        next_matches.append(next_match_home)

                    next_match_away = self.find_match(m.away, m.date_obj)
                    if next_match_away:
                        # else no more matches for away team
                        next_match_away.home_last = m
                        next_matches.append(next_match_away)
            depth += 1
            if len(next_matches) > 0:
                matches.append(next_matches)

        # didn't find a path (raise an Exception or something?)
        return None

    def get_matches_for_team(self, team):
        team_matches: list[Match] = [
            match for match in self.matches if match.away == team or match.home == team
        ]
        team_matches.sort(key=lambda m: m.serial_date)
        for i, m in enumerate(team_matches):
            last_match = team_matches[i - 1]
            if m.away == team and i > 0:
                m.away_last = last_match
            elif m.home == team and i > 0:
                m.home_last = last_match

        return team_matches

    @classmethod
    def find_current_belt_holder(
        cls, leagueSchedule: list[Game], start_belt_holder: str
    ) -> str:
        """
        Given an array of `Game` and the Abbreviation of the season start belt holder,
        Return the current belt holder based off of game results. This assumes the list
        of games is pre-sorted by date.
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
