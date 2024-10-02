import json
from datetime import date
from unittest.mock import Mock

import pytest

from title_belt_nhl.models.nhl_team_schedule_response import Game
from title_belt_nhl.schedule import Match, Schedule

MOCK_DATA_PATH = "./title_belt_nhl/tests/test_files/mock_league_schedule.json"


@pytest.fixture()
def league_schedule():
    # Open the file and load the JSON data
    with open(MOCK_DATA_PATH, "r") as file:
        data = json.load(file)
        return [Game.from_dict(game) for game in data]


class TestSchedule:
    def test_current_title_belt_holder(self, league_schedule):
        league_schedule.sort(key=lambda x: x.gameDate)
        cur_belt_holder = Schedule.find_current_belt_holder(league_schedule, "CHI")
        assert cur_belt_holder == "PIT"

    def test_find_match(self, monkeypatch, league_schedule):
        m = Mock()
        m.return_value = league_schedule
        monkeypatch.setattr("title_belt_nhl.schedule.getFullSchedule", m)
        monkeypatch.setattr("title_belt_nhl.schedule.INITIAL_BELT_HOLDER", "CHI")

        schedule = Schedule("VAN", from_date=date(2023, 9, 29))
        assert schedule.belt_holder == "PIT"
        assert len(schedule.matches) == 6

        match = schedule.find_match(schedule.belt_holder, date(2023, 9, 29))
        expected = Match("DAL", "PIT", date_obj=date(2023, 9, 30))
        assert str(match) == str(expected)
        assert match.date_obj == expected.date_obj

    def test_find_nearest_path_str(self, monkeypatch, league_schedule):
        m = Mock()
        m.return_value = league_schedule
        monkeypatch.setattr("title_belt_nhl.schedule.getFullSchedule", m)

        monkeypatch.setattr("title_belt_nhl.schedule.INITIAL_BELT_HOLDER", "CHI")

        schedule = Schedule("VAN", from_date=date(2023, 9, 29))
        assert schedule.belt_holder == "PIT"
        assert len(schedule.matches) == 6

        path = schedule.find_nearest_path_str(
            [schedule.belt_holder], schedule.belt_holder
        )
        assert len(path.split("vs")) - 1 == 2

        expected = "PIT -> [DAL vs PIT] -> DAL -> [VAN vs DAL]"
        assert path == expected

    def test_find_nearest_path_games(self, monkeypatch, league_schedule):
        m = Mock()
        m.return_value = league_schedule
        monkeypatch.setattr("title_belt_nhl.schedule.getFullSchedule", m)

        monkeypatch.setattr("title_belt_nhl.schedule.INITIAL_BELT_HOLDER", "CHI")

        schedule = Schedule("VAN", from_date=date(2023, 9, 29))
        assert schedule.belt_holder == "PIT"
        assert len(schedule.matches) == 6

        path_matches = schedule.find_nearest_path_games()
        assert len(path_matches) == 2

        m1 = Match("DAL", "PIT", date_obj=date(2023, 9, 30))
        m2 = Match("VAN", "DAL", date_obj=date(2023, 10, 1))
        expected = [m1, m2]
        for i, m in enumerate(expected):
            assert str(path_matches[i]) == str(m)
            assert path_matches[i].date_obj == m.date_obj
