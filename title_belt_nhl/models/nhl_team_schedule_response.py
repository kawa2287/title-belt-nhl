from dataclasses import dataclass
from typing import Optional


@dataclass
class Venue:
    default: str


@dataclass
class PlaceName:
    default: str
    fr: Optional[str] = None


@dataclass
class Team:
    id: int
    placeName: PlaceName
    placeNameWithPreposition: PlaceName
    abbrev: str
    logo: str
    darkLogo: str
    score: Optional[int] = None
    radioLink: str = ""


@dataclass
class PeriodDescriptor:
    periodType: str
    maxRegulationPeriods: int


@dataclass
class Game:
    id: int
    season: int
    gameType: int
    gameDate: str
    gameState: str
    awayTeam: Team
    homeTeam: Team
    venue: Optional[Venue] = None
    neutralSite: Optional[bool] = None
    startTimeUTC: Optional[str] = None
    easternUTCOffset: Optional[str] = None
    venueUTCOffset: Optional[str] = None
    venueTimezone: Optional[str] = None
    gameScheduleState: Optional[str] = None
    periodDescriptor: Optional[PeriodDescriptor] = None
    ticketsLink: Optional[str] = None
    ticketsLinkFr: Optional[str] = None
    gameCenterLink: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict):
        # Create instance by unpacking valid fields, ignoring extra ones
        return cls(**{k: data[k] for k in cls.__annotations__ if k in data})

    def is_game_complete(self) -> bool:
        """
        Checks if the given `Game` is complete.  I *believe* the only enums are
        `FINAL` and `OFF` per a quick check on previous completed season API responses.
        """
        return self.gameState.upper() == "OFF" or self.gameState.upper() == "FINAL"

    def determine_winning_team(self) -> str:
        homeScore = self.homeTeam["score"]
        awayScore = self.awayTeam["score"]
        if homeScore > awayScore:
            return self.homeTeam["abbrev"]
        elif awayScore > homeScore:
            return self.awayTeam["abbrev"]
        else:
            return None

    def is_title_belt_game(self, cur_belt_holder: str) -> bool:
        return (
            self.homeTeam["abbrev"] == cur_belt_holder
            or self.awayTeam["abbrev"] == cur_belt_holder
        )


@dataclass
class ApiTeamScheduleResponse:
    previousSeason: int
    currentSeason: int
    clubTimezone: str
    clubUTCOffset: str
    games: list[Game]
