from copy import deepcopy
from datetime import date, datetime, timedelta
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
    home_last: "Match" = None
    away_last: "Match" = None
    home_next: "Match" = None
    away_next: "Match" = None
    home_score: int = None
    away_score: int = None
    on_shortest_path: bool = False

    def __init__(
        self,
        home,
        away,
        serial_date=None,
        date_obj=None,
        belt_holder=None,
        home_score=None,
        away_score=None,
    ):
        self.home = home
        self.away = away
        self.serial_date = serial_date
        self.date_obj = date_obj or ExcelDate(serial_date=serial_date).date_obj
        self.belt_holder = belt_holder
        self.home_score = home_score
        self.away_score = away_score

    def __str__(self):
        return f"[{self.home} vs {self.away}]"

    def __eq__(self, other: "Match"):
        """Determines whether two Match objects are the same.

        We consider two Matches to be equal if they occur on the same date
        and between the same teams.
        """
        date_equals = (
            self.serial_date == other.serial_date or self.date_obj == other.date_obj
        )
        teams_equal = self.home == other.home and self.away == other.away
        return date_equals and teams_equal

    @classmethod
    def from_game(cls, game: Game):
        game_date_obj = datetime.strptime(game.gameDate, "%Y-%m-%d").date()

        return Match(
            game.homeTeam["abbrev"],
            game.awayTeam["abbrev"],
            serial_date=ExcelDate(date_obj=game_date_obj).serial_date,
            date_obj=game_date_obj,
            home_score=getattr(game.homeTeam, "score", None),
            away_score=getattr(game.awayTeam, "score", None),
        )


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
        last_match.on_shortest_path = True
        last_match.home_next = (
            cur_match if last_match.home in [cur_match.home, cur_match.away] else None
        )
        last_match.away_next = (
            cur_match if last_match.away in [cur_match.home, cur_match.away] else None
        )
        cur_match = last_match

    return path_matches


class Schedule:
    team: str
    belt_holder: str
    matches: list[Match] = []
    from_date: ExcelDate = ExcelDate(date_obj=date.today() - timedelta(days=1))
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
            self.matches.append(Match.from_game(game))

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

    def find_match(self, current_belt_holder, from_date) -> Match | None:
        for match in self.matches_after_date_inclusive(from_date=from_date):
            if (
                match.away == current_belt_holder or match.home == current_belt_holder
            ) and self.from_date.serial_date < match.serial_date:
                match.belt_holder = current_belt_holder
                return deepcopy(match)
        return None

    def find_nearest_path_v2(
        self, scenarios: list[list[Match]] | None = None
    ) -> list[Match]:
        """Find the shortest path from current belt holder to self.team. This is a
        recursive function that branches out at a rate of 2^x by exploring each match
        outcome of either home team winning or away team winning.  Recursion ends when
        self.team is found, or when no further matches can be found"""

        newScenarios: list[list[Match]] = []

        # Handle initial function call and find next match of the current belt holder
        if scenarios is None:
            scenarios = [[self.find_match(self.belt_holder, self.from_date)]]

        # Handle when no further matches can be found
        if len(scenarios) == 0:
            return None

        for s in scenarios:
            cur_match = s[-1]
            if cur_match:
                if cur_match.away == self.team or cur_match.home == self.team:
                    # found a path to team
                    return s

                # Add new Scenario branches
                newScenarios.append(
                    self.create_new_scenario_branch(
                        cur_match.home, cur_match.serial_date, s
                    )
                )
                newScenarios.append(
                    self.create_new_scenario_branch(
                        cur_match.away, cur_match.serial_date, s
                    )
                )

        shortestPath = self.find_nearest_path_v2(newScenarios)
        return shortestPath

    def create_new_scenario_branch(
        self, team: str, matchDate: int, scenario: list[Match]
    ):
        scenario_copy = deepcopy(scenario)
        next_match = self.find_match(team, matchDate)
        scenario_copy.append(next_match)
        return scenario_copy

    def find_nearest_path_games(self) -> list[set[Match]]:
        """Find the shortest path from the current belt holder's next game until
        self.team has a chance to play for the belt. May involve the belt changing
        hands in between.

        Requires
        """
        first_match: Match = self.find_match(self.belt_holder, self.from_date)
        matches = [[first_match]]
        depth = 0
        found = False
        while matches[depth] and not found:
            cur_matches = matches[depth]
            next_matches = []
            for m in cur_matches:
                if m.away == self.team or m.home == self.team:
                    # this updates the on_shortest_path for all relevant matches
                    # and home_next and away_next
                    traverse_matches_backwards(match=m)
                    m.on_shortest_path = True
                    found = True
                    # don't break if we want all shortest paths
                    break
                # else:  # need else if we want all shortest paths
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

            # `if found` instead of `else` here if we want all shortest paths
            else:
                depth += 1
                if len(next_matches) > 0:
                    matches.append(next_matches)

        if found:
            return matches
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

    @classmethod
    def find_belt_path(
        cls,
        league_schedule: list[Game],
        schedule: "Schedule" = None,
        start_belt_holder: str = INITIAL_BELT_HOLDER,
    ) -> str:
        """
        Given an array of `Game` and the Abbreviation of the season start belt holder,
        Return the path that the belt has taken so far, based off of game results.
        This assumes the list of games is pre-sorted by date.

        If schedule is provided, will also include the next title belt match.
        """
        cur_belt_holder = start_belt_holder
        completed_games: list[Game] = list(
            filter(lambda x: x.is_game_complete(), league_schedule)
        )

        last_date = None
        matches = []

        for cg in completed_games:
            winning_team = cg.determine_winning_team()
            if winning_team is not None and cg.is_title_belt_game(cur_belt_holder):
                m = Match.from_game(cg)
                m.belt_holder = cur_belt_holder
                matches.append(m)

                cur_belt_holder = winning_team
                last_date = m.date_obj

        if schedule and last_date:
            matches.append(schedule.find_match(cur_belt_holder, last_date))

        return matches
