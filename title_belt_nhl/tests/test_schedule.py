import json

from title_belt_nhl.main import Schedule
from title_belt_nhl.models.nhl_team_schedule_response import Game


def test_current_title_belt_holder():
    mock_data_path = "./title_belt_nhl/tests/test_files/mock_league_schedule.json"

    # Open the file and load the JSON data
    with open(mock_data_path, "r") as file:
        data = json.load(file)
        leagueSchedule: list[Game] = [Game.from_dict(game) for game in data]

    leagueSchedule.sort(key=lambda x: x.gameDate)
    cur_belt_holder = Schedule.find_current_belt_holder(leagueSchedule, "CHI")
    assert cur_belt_holder == "PIT"
