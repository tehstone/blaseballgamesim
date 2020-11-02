from typing import Any, Dict, Optional, Tuple
from enum import Enum


class BlaseballStatistics(Enum):
    # stolen base stats
    STOLEN_BASE_ATTEMPTS = 1
    STOLEN_BASES = 2
    CAUGHT_STEALINGS = 3

    # batting stats
    BATTER_STRIKEOUTS = 10
    BATTER_HITS = 11
    BATTER_SINGLES = 12
    BATTER_DOUBLES = 13
    BATTER_TRIPLES = 14
    BATTER_HRS = 15
    BATTER_PLATE_APPEARANCES = 16
    BATTER_WALKS = 17
    BATTER_RBIS = 18
    BATTER_RUNS_SCORED = 19
    BATTER_PITCHES_FACED = 20
    BATTER_FOUL_BALLS = 21
    BATTER_FLYOUTS = 22
    BATTER_GROUNDOUTS = 23
    BATTER_AT_BATS = 24

    # pitcher stats
    PITCHER_WALKS = 30
    PITCHER_EARNED_RUNS = 31
    PITCHER_HITS_ALLOWED = 32
    PITCHER_HRS_ALLOWED = 33
    PITCHER_XBH_ALLOWED = 34
    PITCHER_PITCHES_THROWN = 35
    PITCHER_INNINGS_PITCHED = 36
    PITCHER_STRIKEOUTS = 37
    PITCHER_SHUTOUTS = 38
    PITCHER_BALLS_THROWN = 39
    PITCHER_STRIKES_THROWN = 40
    PITCHER_WINS = 41
    PITCHER_LOSSES = 42
    PITCHER_FLYOUTS = 43
    PITCHER_GROUNDOUTS = 44
    PITCHER_BATTERS_FACED = 45

    # Defense stats
    DEFENSE_STOLEN_BASE_ATTEMPTS = 50
    DEFENSE_STOLEN_BASES = 51
    DEFENSE_CAUGHT_STEALINGS = 52

    # Convenience stats  DO NOT USE
    GENERIC_ADVANCEMENT = 100


class ForbiddenKnowledge(Enum):
    # Base running
    BASE_THIRST = 1
    CONTINUATION = 2
    GROUND_FRICTION = 3
    INDULGENCE = 4
    LASERLIKENESS = 5

    # Defense
    ANTICAPITALISM = 10
    CHASINESS = 11
    OMNISCIENCE = 12
    TENACIOUSNESS = 13
    WATCHFULNESS = 14

    # Batting
    BUOYANCY = 20
    DIVINITY = 21
    MARTYRDOM = 22
    MOXIE = 23
    MUSCLITUDE = 24
    PATHETICISM = 25
    THWACKABILITY = 26
    TRAGICNESS = 27

    # Pitching
    COLDNESS = 30
    OVERPOWERMENT = 31
    RUTHLESSNESS = 32
    SHAKESPEARIANISM = 33
    SUPPRESSION = 34
    UNTHWACKABILITY = 35
    CINNAMON = 36
    PRESSURIZATION = 37


class MachineLearnedModel(Enum):
    PITCH = 1
    IS_HIT = 2
    HIT_TYPE = 3
    RUNNER_ADV_OUT = 4
    RUNNER_ADV_HIT = 5
    SB_ATTEMPT = 6
    SB_SUCCESS = 7


class BloodType(Enum):
    A = 1
    AA = 2
    AAA = 3
    ACID = 4
    BASE = 5
    ELECTRIC = 6
    WATER = 7
    FIRE = 8
    GRASS = 9
    H2O = 10
    LOVE = 11
    O = 12
    O_NO = 13
    PSYCHIC = 14


class PitchEventTeamBuff(Enum):
    BASE_INSTINCTS = 1
    CHARM = 2
    ELECTRIC = 3
    O_NO = 4
    ZAP = 5


class Team(Enum):
    LOVERS = 1
    TACOS = 2
    STEAKS = 3
    BREATH_MINTS = 4
    FIREFIGHTERS = 5
    SHOE_THIEVES = 6
    FLOWERS = 7
    FRIDAYS = 8
    MAGIC = 9
    MILLENNIALS = 10
    CRABS = 11
    SPIES = 12
    PIES = 13
    SUNBEAMS = 14
    WILD_WINGS = 15
    TIGERS = 16
    MOIST_TALKERS = 17
    DALE = 18
    GARAGES = 19
    JAZZ_HANDS = 20
    LIFT = 21


team_id_map: Dict[str, Team] = {
    "b72f3061-f573-40d7-832a-5ad475bd7909": Team.LOVERS,
    "878c1bf6-0d21-4659-bfee-916c8314d69c": Team.TACOS,
    "b024e975-1c4a-4575-8936-a3754a08806a": Team.STEAKS,
    "adc5b394-8f76-416d-9ce9-813706877b84": Team.BREATH_MINTS,
    "ca3f1c8c-c025-4d8e-8eef-5be6accbeb16": Team.FIREFIGHTERS,
    "bfd38797-8404-4b38-8b82-341da28b1f83": Team.SHOE_THIEVES,
    "3f8bbb15-61c0-4e3f-8e4a-907a5fb1565e": Team.FLOWERS,
    "979aee4a-6d80-4863-bf1c-ee1a78e06024": Team.FRIDAYS,
    "7966eb04-efcc-499b-8f03-d13916330531": Team.MAGIC,
    "36569151-a2fb-43c1-9df7-2df512424c82": Team.MILLENNIALS,
    "8d87c468-699a-47a8-b40d-cfb73a5660ad": Team.CRABS,
    "9debc64f-74b7-4ae1-a4d6-fce0144b6ea5": Team.SPIES,
    "23e4cbc1-e9cd-47fa-a35b-bfa06f726cb7": Team.PIES,
    "f02aeae2-5e6a-4098-9842-02d2273f25c7": Team.SUNBEAMS,
    "57ec08cc-0411-4643-b304-0e80dbc15ac7": Team.WILD_WINGS,
    "747b8e4a-7e50-4638-a973-ea7950a3e739": Team.TIGERS,
    "eb67ae5e-c4bf-46ca-bbbc-425cd34182ff": Team.MOIST_TALKERS,
    "b63be8c2-576a-4d6e-8daf-814f8bcea96f": Team.DALE,
    "105bc3ff-1320-4e37-8ef0-8d595cb95dd0": Team.GARAGES,
    "a37f9158-7f82-46bc-908c-c9e2dda7c33b": Team.JAZZ_HANDS,
    "c73b705c-40ad-4633-a6ed-d357ee2e2bcf": Team.LIFT,
}

blood_id_map: Dict[int, BloodType] = {
    0: BloodType.A,
    1: BloodType.AAA,
    2: BloodType.AA,
    3: BloodType.ACID,
    4: BloodType.BASE,
    5: BloodType.O,
    6: BloodType.O_NO,
    7: BloodType.WATER,
    8: BloodType.ELECTRIC,
    9: BloodType.LOVE,
    10: BloodType.FIRE,
    11: BloodType.PSYCHIC,
    12: BloodType.GRASS,
}

# TODO(kjc9): determine how to use this properly in the sim code
team_pitch_event_map: Dict[Team, Tuple[PitchEventTeamBuff, int, Optional[int], Optional[BloodType]]] = {
    # team: Tuple[Team buff, season start, season end]
    Team.FLOWERS: (PitchEventTeamBuff.O_NO, 11, None, BloodType.O_NO),
    Team.LOVERS: (PitchEventTeamBuff.CHARM, 10, None, BloodType.LOVE),
    Team.DALE: (PitchEventTeamBuff.ZAP, 8, None, BloodType.ELECTRIC),
    Team.SUNBEAMS: (PitchEventTeamBuff.BASE_INSTINCTS, 9, None, BloodType.BASE),
}

fk_key: Dict[ForbiddenKnowledge, str] = {
    ForbiddenKnowledge.BASE_THIRST: "baseThirst",
    ForbiddenKnowledge.CONTINUATION: "continuation",
    ForbiddenKnowledge.GROUND_FRICTION: "groundFriction",
    ForbiddenKnowledge.INDULGENCE: "indulgence",
    ForbiddenKnowledge.LASERLIKENESS: "laserlikeness",
    ForbiddenKnowledge.ANTICAPITALISM: "anticapitalism",
    ForbiddenKnowledge.CHASINESS: "chasiness",
    ForbiddenKnowledge.OMNISCIENCE: "omniscience",
    ForbiddenKnowledge.TENACIOUSNESS: "tenaciousness",
    ForbiddenKnowledge.WATCHFULNESS: "watchfulness",
    ForbiddenKnowledge.BUOYANCY: "buoyancy",
    ForbiddenKnowledge.DIVINITY: "divinity",
    ForbiddenKnowledge.MARTYRDOM: "martyrdom",
    ForbiddenKnowledge.MOXIE: "moxie",
    ForbiddenKnowledge.MUSCLITUDE: "musclitude",
    ForbiddenKnowledge.PATHETICISM: "patheticism",
    ForbiddenKnowledge.THWACKABILITY: "thwackability",
    ForbiddenKnowledge.TRAGICNESS: "tragicness",
    ForbiddenKnowledge.COLDNESS: "coldness",
    ForbiddenKnowledge.OVERPOWERMENT: "overpowerment",
    ForbiddenKnowledge.RUTHLESSNESS: "ruthlessness",
    ForbiddenKnowledge.SHAKESPEARIANISM: "shakespearianism",
    ForbiddenKnowledge.SUPPRESSION: "suppression",
    ForbiddenKnowledge.UNTHWACKABILITY: "unthwackability",
    ForbiddenKnowledge.CINNAMON: "cinnamon",
    ForbiddenKnowledge.PRESSURIZATION: "pressurization",
}

stat_key: Dict[BlaseballStatistics, str] = {
    BlaseballStatistics.STOLEN_BASE_ATTEMPTS: "Stolen base attempts",
    BlaseballStatistics.STOLEN_BASES: "Stolen bases",
    BlaseballStatistics.CAUGHT_STEALINGS: "Caught stealing",
    BlaseballStatistics.BATTER_STRIKEOUTS: "Batter strikeouts",
    BlaseballStatistics.BATTER_HITS: "Batter hits",
    BlaseballStatistics.BATTER_SINGLES: "Batter singles",
    BlaseballStatistics.BATTER_DOUBLES: "Batter doubles",
    BlaseballStatistics.BATTER_TRIPLES: "Batter triples",
    BlaseballStatistics.BATTER_HRS: "Batter home runs",
    BlaseballStatistics.BATTER_PLATE_APPEARANCES: "Batter plate appearances",
    BlaseballStatistics.BATTER_WALKS: "Batter walks",
    BlaseballStatistics.BATTER_RBIS: "Batter runs batted in",
    BlaseballStatistics.BATTER_RUNS_SCORED: "Batter runs scored",
    BlaseballStatistics.BATTER_PITCHES_FACED: "Batter pitches faced",
    BlaseballStatistics.BATTER_FOUL_BALLS: "Batter foul balls",
    BlaseballStatistics.PITCHER_WALKS: "Pitcher walks",
    BlaseballStatistics.PITCHER_EARNED_RUNS: "Pitcher earned runs",
    BlaseballStatistics.PITCHER_HITS_ALLOWED: "Pitcher hits allowed",
    BlaseballStatistics.PITCHER_HRS_ALLOWED: "Pitcher home runs allowed",
    BlaseballStatistics.PITCHER_XBH_ALLOWED: "Pitcher extra base hits allowed",
    BlaseballStatistics.PITCHER_PITCHES_THROWN: "Pitcher pitches thrown",
    BlaseballStatistics.PITCHER_INNINGS_PITCHED: "Pitcher innings pitched",
    BlaseballStatistics.PITCHER_STRIKEOUTS: "Pitcher strikeouts",
    BlaseballStatistics.PITCHER_SHUTOUTS: "Pitcher shutouts",
    BlaseballStatistics.PITCHER_BALLS_THROWN: "Pitcher balls thrown",
    BlaseballStatistics.PITCHER_STRIKES_THROWN: "Pitcher strikes thrown",
    BlaseballStatistics.PITCHER_WINS: "Pitcher wins",
    BlaseballStatistics.PITCHER_LOSSES: "Pitcher losses",
    BlaseballStatistics.DEFENSE_STOLEN_BASE_ATTEMPTS: "Defense stolen base attempts",
    BlaseballStatistics.DEFENSE_STOLEN_BASES: "Defense stolen bases",
    BlaseballStatistics.DEFENSE_CAUGHT_STEALINGS: "Defense caught stealing",
}