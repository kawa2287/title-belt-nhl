import requests
from title_belt_nhl.static.nhl_tms import nhl_team_abbvs
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

@lru_cache(maxsize=None)
def getTeamSchedule(team:str, season:str):
    url = f'https://api-web.nhle.com/v1/club-schedule-season/{team}/{season}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
    pass

def getFullSchedule(season:str='20242025'):
    def process_team(tm):
        data = getTeamSchedule(tm, season)
        if data is not None:
            return {item["id"]: item for item in data['games'] if item['gameType'] == 2}
        return {}

    with ThreadPoolExecutor() as executor:
        future_to_team = {executor.submit(process_team, tm): tm for tm in nhl_team_abbvs}
        leagueSchedule = {}
        for future in as_completed(future_to_team):
            leagueSchedule.update(future.result())

    return leagueSchedule