import json
from title_belt_nhl.main import Schedule

def test_current_title_belt_holder():
    mock_data_path = './title_belt_nhl/tests/test_files/mock_league_schedule.json'

    # Open the file and load the JSON data
    with open(mock_data_path, 'r') as file:
        leagueSchedule = json.load(file)
    
    leagueSchedule.sort(key=lambda x: x['gameDate'])
    print(leagueSchedule)
    cur_belt_holder = Schedule.find_current_belt_holder(leagueSchedule, 'CHI')
    assert cur_belt_holder == 'PIT'

