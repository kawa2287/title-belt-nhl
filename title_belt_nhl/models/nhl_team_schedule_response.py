from dataclasses import dataclass, field
from typing import List, Optional, Dict

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
    venue: Venue
    neutralSite: bool
    startTimeUTC: str
    easternUTCOffset: str
    venueUTCOffset: str
    venueTimezone: str
    gameState: str
    gameScheduleState: str
    awayTeam: Team
    homeTeam: Team
    periodDescriptor: PeriodDescriptor
    ticketsLink: str
    ticketsLinkFr: str
    gameCenterLink: str

@dataclass
class ApiTeamScheduleResponse:
    previousSeason: int
    currentSeason: int
    clubTimezone: str
    clubUTCOffset: str
    games: List[Game]