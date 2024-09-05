from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

import requests

from title_belt_nhl.models.nhl_team_schedule_response import ApiTeamScheduleResponse, Game
from title_belt_nhl.static.nhl_tms import nhl_team_abbvs


@lru_cache(maxsize=None)
def getTeamSchedule(tm_abv: str, season: str) -> ApiTeamScheduleResponse:
    """Gets the full season schedule for the given team."""
    url = f"https://api-web.nhle.com/v1/club-schedule-season/{tm_abv}/{season}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ConnectionError(
            f"Failed to retrieve data. Status code: {response.status_code}"
        )
    pass


def getFullSchedule(season: str) -> list[Game]:
    """
    Gets the full season schedule.  Have not found an endpoint that will
    do this in one call, so we're looping through all teams (in parallel)
    to get the full league schedule...
    """

    def process_team(tm):
        data = getTeamSchedule(tm, season)
        if data is not None:
            return {item["id"]: item for item in data["games"] if item["gameType"] == 2}
        return {}

    with ThreadPoolExecutor() as executor:
        future_to_team = {executor.submit(process_team, tm): tm for tm in nhl_team_abbvs}
        leagueSchedule = {}
        for future in as_completed(future_to_team):
            leagueSchedule.update(future.result())

    # Create an array of `Game` and sort
    gameList: list[Game] = [
        Game.from_dict(leagueSchedule[game_id]) for game_id in leagueSchedule
    ]

    gameList.sort(key=lambda game: game.gameDate)

    return gameList
