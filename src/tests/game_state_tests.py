import os
import unittest
from decimal import Decimal
from typing import Any, Dict, List, Optional

from game_state import (
    BASE_INSTINCT_PRIORS,
    GameState,
    InningHalf,
)
import game_state
from team_state import TeamState, TEAM_ID, PlayerBuff
from common import BlaseballStatistics as Stats
from common import ForbiddenKnowledge as FK
from common import MachineLearnedModel as Ml
from common import BloodType, Team, Weather
from stadium import Stadium

DEFAULT_FKS = {
    FK.BASE_THIRST: 0.0,
    FK.CONTINUATION: 0.0,
    FK.GROUND_FRICTION: 0.0,
    FK.INDULGENCE: 0.0,
    FK.LASERLIKENESS: 0.0,
    FK.THWACKABILITY: 0.0,
    FK.ANTICAPITALISM: 0.0,
    FK.CHASINESS: 0.0,
    FK.OMNISCIENCE: 0.0,
    FK.TENACIOUSNESS: 0.0,
    FK.WATCHFULNESS: 0.0,
    FK.BUOYANCY: 0.0,
    FK.DIVINITY: 0.0,
    FK.MARTYRDOM: 0.0,
    FK.MOXIE: 0.0,
    FK.MUSCLITUDE: 0.0,
    FK.PATHETICISM: 0.0,
    FK.TRAGICNESS: 0.0,
    FK.COLDNESS: 0.0,
    FK.OVERPOWERMENT: 0.0,
    FK.RUTHLESSNESS: 0.0,
    FK.SHAKESPEARIANISM: 0.0,
    FK.SUPPRESSION: 0.0,
    FK.UNTHWACKABILITY: 0.0,
    FK.PRESSURIZATION: 0.0,
    FK.CINNAMON: 0.0,
}

SBA_PRIORS = [0.5, 0.5]
SB_PRIORS = [0.5, 0.5]
PITCH_PRIORS = [0.2, 0.2, 0.2, 0.2, 0.2]
IS_HIT_PRIORS = [0.33, 0.33, 0.34]
HIT_PRIORS = [0.25, 0.25, 0.25, 0.25]
ADVANCE_HIT_PRIORS = [0.5, 0.5]
ADVANCE_OUT_PRIORS = [0.5, 0.5]
OUT_PRIORS = [0.5, 0.5]

default_stadium = Stadium(
    "team_id",
    "stadium_id",
    "stadium_name",
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    [],
)

def new_generic_model_roll(self, model: Ml, feature_vector: List[float]) -> int:
    probs: List[float] = []
    if model == Ml.SB_ATTEMPT:
        probs = SBA_PRIORS
    if model == Ml.SB_SUCCESS:
        probs = SB_PRIORS
    if model == Ml.PITCH:
        probs = PITCH_PRIORS
    if model == Ml.IS_HIT:
        probs = IS_HIT_PRIORS
    if model == Ml.HIT_TYPE:
        probs = HIT_PRIORS
    if model == Ml.RUNNER_ADV_HIT:
        probs = ADVANCE_HIT_PRIORS
    if model == Ml.RUNNER_ADV_OUT:
        probs = ADVANCE_OUT_PRIORS
    if model == Ml.OUT_TYPE:
        probs = OUT_PRIORS

    # generate random float between 0-1
    roll = self._random_roll()
    total = 0
    for i in range(len(probs)):
        # add the odds of the next outcome to the running total
        total += probs[i]
        # if the random roll is less than the new total, return this outcome
        if roll < total:
            return i


class TestGameState(unittest.TestCase):
    def setUp(self):
        self.home_team_state = TeamState(
            team_id="747b8e4a-7e50-4638-a973-ea7950a3e739",
            season=10,
            day=1,
            stadium=default_stadium,
            weather=Weather.SUN2,
            is_home=True,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup={1: "p1", 2: "p2", 3: "p3"},
            starting_pitcher="p4",
            stlats={
                "p1": DEFAULT_FKS,
                "p2": DEFAULT_FKS,
                "p3": DEFAULT_FKS,
                "p4": DEFAULT_FKS,
            },
            game_stats={
                "p1": {},
                "p2": {},
                "p3": {},
                "p4": {},
            },
            buffs={
                "p1": {},
                "p2": {},
                "p3": {},
                "p4": {},
            },
            segmented_stats={
                0:{
                    "p1": {},
                    "p2": {},
                    "p3": {},
                    "p4": {},
                },
            },
            blood={
                "p1": BloodType.O,
                "p2": BloodType.GRASS,
                "p3": BloodType.LOVE,
                "p4": BloodType.ELECTRIC,
            },
            player_names={
                "p1": "HomePlayer 1",
                "p2": "HomePlayer 2",
                "p3": "HomePlayer 3",
                "p4": "HomePlayer 4",
            },
            rotation={1: "p4"},
            cur_batter_pos=1,
            cur_pitcher_pos=1
        )

        self.away_team_state = TeamState(
            team_id="f02aeae2-5e6a-4098-9842-02d2273f25c7",
            season=10,
            day=1,
            stadium=default_stadium,
            weather=Weather.SUN2,
            is_home=False,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup={1: "p11", 2: "p12", 3: "p13"},
            starting_pitcher="p14",
            stlats={
                "p11": DEFAULT_FKS,
                "p12": DEFAULT_FKS,
                "p13": DEFAULT_FKS,
                "p14": DEFAULT_FKS,
            },
            buffs={
                "p11": {},
                "p12": {},
                "p13": {},
                "p14": {},
            },
            game_stats={
                "p11": {},
                "p12": {},
                "p13": {},
                "p14": {},
            },
            segmented_stats={
                0: {
                    "p11": {},
                    "p12": {},
                    "p13": {},
                    "p14": {},
                },
            },
            blood={
                "p11": BloodType.O,
                "p12": BloodType.GRASS,
                "p13": BloodType.LOVE,
                "p14": BloodType.ELECTRIC,
            },
            player_names={
                "p11": "AwayPlayer 11",
                "p12": "AwayPlayer 12",
                "p13": "AwayPlayer 13",
                "p14": "AwayPlayer 14",
            },
            rotation={1: "p14"},
            cur_batter_pos=1,
            cur_pitcher_pos=1
        )
        self.home_team_state.reset_team_state()
        self.away_team_state.reset_team_state()
        self.home_team_state.player_buffs = {
            "p1": {},
            "p2": {},
            "p3": {},
            "p4": {},
        }
        self.away_team_state.player_buffs = {
            "p11": {},
            "p12": {},
            "p13": {},
            "p14": {},
        }
        GameState.generic_model_roll = new_generic_model_roll
        self.game_state = GameState(
            game_id="1",
            season=11,
            day=1,
            stadium=default_stadium,
            home_team=self.home_team_state,
            away_team=self.away_team_state,
            home_score=Decimal("0.0"),
            away_score=Decimal("0.0"),
            inning=1,
            half=InningHalf.TOP,
            outs=0,
            strikes=0,
            balls=0,
            weather=Weather.SUN2,
        )
        # FORCE RANDOMNESS OFF UNTIL WE TEST IT
        game_state.BIG_BUCKET_PERCENTAGE = 0.0
        game_state.FRIEND_OF_CROWS_PERCENTAGE = 0.0
        self.game_state.reset_game_state()


class TestInit(TestGameState):
    def test_initial_state(self):
        self.assertEqual(self.game_state.game_id, "1")
        self.assertEqual(self.game_state.season, 11)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.home_team.team_enum, Team.TIGERS)
        self.assertEqual(self.game_state.away_team.team_enum, Team.SUNBEAMS)


    def test_season_buff_initial_state(self):
        self.game_state.home_team.team_enum = Team.WORMS
        self.game_state.season = 17
        self.game_state.reset_game_state()
        self.assertEqual(self.game_state.game_id, "1")
        self.assertEqual(self.game_state.season, 17)
        self.assertEqual(self.game_state.home_score, Decimal("1.0"))
        self.assertEqual(self.game_state.away_score, Decimal("0.0"))
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.home_team.team_enum, Team.WORMS)
        self.assertEqual(self.game_state.away_team.team_enum, Team.SUNBEAMS)


class TestBaseAdvancement(TestGameState):
    def test_no_runners(self):
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.cur_base_runners, {})

    def test_one_runner(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(3)
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

    def test_two_runners_consec(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(3)
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

    def test_two_runners_split(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[3] = "p12"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.game_state.advance_all_runners(3)
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

    def test_three_runners(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.game_state.advance_all_runners(4)
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 3)


class TestForcedBaseAdvancement(TestGameState):
    def test_no_runners(self):
        self.assertEqual(self.game_state.cur_base_runners, {})
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.cur_base_runners, {})

    def test_one_runner(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    def test_two_runners_consec(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.cur_base_runners[1] = "p13"
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p13")
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

    def test_two_runners_split(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[3] = "p12"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    def test_three_runners(self):
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.game_state.advance_all_forced_runners()
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

class TestInningAdvancement(TestGameState):
    def testTopToBottom(self):
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 1)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertEqual(self.game_state.inning, 1)
        self.assertEqual(self.game_state.half, InningHalf.BOTTOM)
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)

    def testBottomToTop(self):
        self.game_state.half = InningHalf.BOTTOM
        self.game_state.refresh_game_status()
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 1)
        self.assertEqual(self.game_state.half, InningHalf.BOTTOM)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertEqual(self.game_state.inning, 2)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)

    def testTopNineNotEnding(self):
        self.game_state.half = InningHalf.TOP
        self.game_state.inning = 9
        self.game_state.away_score = Decimal("4.0")
        self.game_state.home_score = Decimal("3.0")
        self.game_state.refresh_game_status()
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 9)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.home_score, 3)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertEqual(self.game_state.inning, 9)
        self.assertEqual(self.game_state.half, InningHalf.BOTTOM)
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.home_score, 3)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)

    def testTopNineWithEnding(self):
        self.game_state.half = InningHalf.TOP
        self.game_state.inning = 9
        self.game_state.away_score = Decimal("4.0")
        self.game_state.home_score = Decimal("5.0")
        self.game_state.refresh_game_status()
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 9)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.home_score, 5)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertTrue(self.game_state.is_game_over)

    def testBottomNineNotEnding(self):
        self.game_state.half = InningHalf.BOTTOM
        self.game_state.inning = 9
        self.game_state.away_score = Decimal("4.0")
        self.game_state.home_score = Decimal("4.0")
        self.game_state.refresh_game_status()
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 9)
        self.assertEqual(self.game_state.half, InningHalf.BOTTOM)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.home_score, 4)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertEqual(self.game_state.inning, 10)
        self.assertEqual(self.game_state.half, InningHalf.TOP)
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.home_score, 4)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)

    def testBottomNineWithEnding(self):
        self.game_state.half = InningHalf.BOTTOM
        self.game_state.inning = 9
        self.game_state.away_score = Decimal("4.0")
        self.game_state.home_score = Decimal("5.0")
        self.game_state.refresh_game_status()
        self.game_state.strikes = 2
        self.game_state.outs = 3
        self.assertEqual(self.game_state.inning, 9)
        self.assertEqual(self.game_state.half, InningHalf.BOTTOM)
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.home_score, 5)
        self.assertEqual(self.game_state.away_score, 4)
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.assertFalse(self.game_state.is_game_over)
        self.game_state.attempt_to_advance_inning()
        self.assertEqual(self.game_state.inning, 9)
        self.assertTrue(self.game_state.is_game_over)


class TestONO(TestGameState):
    def testNonONoTeam(self):
        self.assertFalse(self.game_state.resolve_o_no())
        self.game_state.strikes = 2
        self.assertFalse(self.game_state.resolve_o_no())

    def testONoTeamNonBlood(self):
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.game_state.cur_batting_team.blood["p11"] = BloodType.GRASS
        self.game_state.strikes = 2
        self.game_state.balls = 1
        self.assertFalse(self.game_state.resolve_o_no())

    def testONoTrigger(self):
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.game_state.cur_batting_team.blood["p11"] = BloodType.O_NO
        self.game_state.strikes = 2
        self.game_state.balls = 1
        self.assertFalse(self.game_state.resolve_o_no())
        self.game_state.strikes = 1
        self.game_state.balls = 0
        self.assertFalse(self.game_state.resolve_o_no())
        self.game_state.strikes = 2
        self.assertTrue(self.game_state.resolve_o_no())


class TestFiery(TestGameState):
    def testNonFieryTeam(self):
        game_state.FIERY_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_pitching_team.team_enum = Team.MAGIC
        self.assertEquals(1, self.game_state.resolve_fiery())

    def testFieryTrigger(self):
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
        game_state.FIERY_TRIGGER_PERCENTAGE = 1.0
        self.assertEquals(2, self.game_state.resolve_fiery())


class TestPsychic(TestGameState):
    def testNonPsychicTeam(self):
        game_state.PSYCHIC_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.assertEquals(False, self.game_state.resolve_psychic_batter())
        self.assertEquals(False, self.game_state.resolve_psychic_pitcher())

    def testPsychicTrigger(self):
        self.game_state.cur_batting_team.team_enum = Team.SPIES
        self.game_state.season = 16
        game_state.FIERY_TRIGGER_PERCENTAGE = 1.0
        self.assertEquals(True, self.game_state.resolve_psychic_batter())
        self.assertEquals(False, self.game_state.resolve_psychic_pitcher())
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.SPIES
        self.assertEquals(False, self.game_state.resolve_psychic_batter())
        self.assertEquals(True, self.game_state.resolve_psychic_pitcher())


class TestAAA(TestGameState):
    def testAAATrigger(self):
        global HIT_PRIORS
        # test triple
        game_state.AAA_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.STEAKS
        self.game_state.season = 16
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertTrue(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])

    def testNoAAATrigger(self):
        global HIT_PRIORS
        # test triple
        game_state.AAA_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.WORMS
        self.game_state.season = 16
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])

        game_state.AAA_TRIGGER_PERCENTAGE = 0.0
        self.game_state.cur_batting_team.team_enum = Team.SPIES
        self.game_state.season = 16
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])


class TestAA(TestGameState):
    def testAATrigger(self):
        global HIT_PRIORS
        # test double
        game_state.AA_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.PIES
        self.game_state.season = 17
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertTrue(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])

    def testNoAATrigger(self):
        global HIT_PRIORS
        # test double
        game_state.AA_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.WORMS
        self.game_state.season = 17
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])

        game_state.AA_TRIGGER_PERCENTAGE = 0.0
        self.game_state.cur_batting_team.team_enum = Team.PIES
        self.game_state.season = 17
        self.game_state.reset_game_state()
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertFalse(PlayerBuff.OVER_PERFORMING in self.game_state.cur_batting_team.player_buffs["p11"])


class TestBaseInstinct(TestGameState):

    def testNonBITeam(self):
        new_priors = {3: 1.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        self.assertEqual(self.game_state.resolve_base_instincts(), 3)
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.assertEqual(self.game_state.resolve_base_instincts(), 1)

    def testBITrigger(self):
        new_priors = {3: 1.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_batting_team.blood["p11"] = BloodType.BASE
        self.assertEqual(self.game_state.resolve_base_instincts(), 3)
        new_priors = {3: 0.0, 2: 1.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        self.assertEqual(self.game_state.resolve_base_instincts(), 2)


class TestStolenBase(TestGameState):

    def testNoAttempt(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [1.0, 0.0]
        SB_PRIORS = [0.0, 1.0]
        self.assertFalse(self.game_state.stolen_base_sim())
        self.game_state.cur_base_runners[1] = "p11"
        self.assertFalse(self.game_state.stolen_base_sim())

    def testSBAttemptCaughtStealing(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [1.0, 0.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)

    def testSBAttemptSuccess(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")

    def testSBAttemptSuccessHome(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.away_score, 1)

    def testSBAttemptSuccessTwoOpen(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.away_score, 1)

    def testSBAttemptSuccessOneOpen(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, 0)


class TestPrePitchEvents(TestGameState):
    def testNonPrePitchTeam(self):
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())

    def testFriendOfCrows(self):
        game_state.FRIEND_OF_CROWS_PERCENTAGE = 1.0
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.weather = Weather.BIRD
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_pitching_team.player_buffs[self.game_state.cur_pitching_team.starting_pitcher][PlayerBuff.FRIEND_OF_CROWS] = 1
        self.game_state.weather = Weather.SUN2
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.weather = Weather.BIRD
        self.game_state.strikes = 0
        self.game_state.balls = 0
        self.game_state.outs = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p12")
        game_state.FRIEND_OF_CROWS_PERCENTAGE = 0.0
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p12")

    def testCharmPitcher(self):
        game_state.CHARM_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_pitching_team.team_enum = Team.LOVERS
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.LOVE
        self.game_state.strikes = 0
        self.game_state.balls = 0
        self.game_state.outs = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p12")
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.GRASS
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.LOVE
        self.game_state.season = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.season = 10
        self.game_state.strikes = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 3)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p11")

    def testCharmBatter(self):
        game_state.CHARM_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.LOVERS
        self.game_state.cur_pitching_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_batting_team.blood["p11"] = BloodType.LOVE
        self.game_state.strikes = 0
        self.game_state.balls = 0
        self.game_state.outs = 0
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p12")
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.cur_batting_team.blood["p12"] = BloodType.GRASS
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_batting_team.blood["p12"] = BloodType.LOVE
        self.game_state.season = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.season = 10
        self.game_state.strikes = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p11")

    def testZapBatter(self):
        game_state.ZAP_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_batting_team.team_enum = Team.DALE
        self.game_state.cur_pitching_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_batting_team.blood["p11"] = BloodType.ELECTRIC
        self.game_state.strikes = 0
        self.game_state.balls = 0
        self.game_state.outs = 0
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 2
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.strikes, 1)
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.cur_batting_team.blood["p11"] = BloodType.GRASS
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_batting_team.blood["p11"] = BloodType.ELECTRIC
        self.game_state.season = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.season = 10
        self.game_state.strikes = 0
        self.game_state.balls = 3
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 2
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())

    def testFloodingNotTriggering(self):
        game_state.FLOODING_TRIGGER_PERCENTAGE = 1.0
        self.game_state.weather = Weather.SUN2
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())

    def testFloodingWipesEveryoneAway(self):
        game_state.FLOODING_TRIGGER_PERCENTAGE = 1.0
        self.game_state.weather = Weather.FLOODING
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")

        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())

        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    def testFloodingScores1(self):
        game_state.FLOODING_TRIGGER_PERCENTAGE = 1.0
        self.game_state.weather = Weather.FLOODING
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.SWIM_BLADDER: 1}
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")

        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())

        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

    def testFloodingScores1Leaves1(self):
        game_state.FLOODING_TRIGGER_PERCENTAGE = 1.0
        self.game_state.weather = Weather.FLOODING
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.SWIM_BLADDER: 1}
        self.game_state.cur_batting_team.player_buffs["p12"] = {PlayerBuff.EGO1: 1}
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")

        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())

        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.game_state.cur_batting_team.player_buffs["p12"] = {PlayerBuff.EGO2: 1}

        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())

        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)


class TestRunnerAdvancementHit(TestGameState):

    def testNoOneOnBase(self):
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [0.0, 1.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.attempt_to_advance_runners_on_hit()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    def testFailureWithRunnerOnThird(self):
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_hit()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithRunnerOnThird(self):
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_hit()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithTwoRunners(self):
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_hit()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, 1)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithAcidic(self):
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_hit(acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))
        self.assertEqual(self.game_state.home_score, 0)


class TestRunnerAdvancementOut(TestGameState):

    def testNoOneOnBase(self):
        global ADVANCE_OUT_PRIORS
        ADVANCE_OUT_PRIORS = [0.0, 1.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.attempt_to_advance_runners_on_flyout()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    def testFailureWithRunnerOnThird(self):
        global ADVANCE_OUT_PRIORS
        ADVANCE_OUT_PRIORS = [1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_flyout()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithRunnerOnThird(self):
        global ADVANCE_OUT_PRIORS
        ADVANCE_OUT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_flyout()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.away_score, 1)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithTwoRunners(self):
        global ADVANCE_OUT_PRIORS
        ADVANCE_OUT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_flyout()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, 1)
        self.assertEqual(self.game_state.home_score, 0)

    def testSuccessWithAcidic(self):
        global ADVANCE_OUT_PRIORS
        ADVANCE_OUT_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.game_state.attempt_to_advance_runners_on_flyout(acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))
        self.assertEqual(self.game_state.home_score, 0)


class TestHitSim(TestGameState):

    def testNoOneOnBase(self):
        global HIT_PRIORS
        # test single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

        # test double
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

        # test triple
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test acidic hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))

    def testRunnerOnThird(self):
        global HIT_PRIORS
        # test single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test acidic single driving a run in
        self.game_state.reset_game_state()
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))

        # test double
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test triple
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

        # test acidic hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("1.8"))

    def testRunnerOnFirstAndThirdNoAdvance(self):
        global HIT_PRIORS
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [1.0, 0.0] # never advance on hit
        # test single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p13")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test double
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test triple
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

        # test acidic triple
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("1.8"))

        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 3)

    def testRunnerOnFirstAndThirdWithAdvance(self):
        global HIT_PRIORS
        global ADVANCE_HIT_PRIORS
        ADVANCE_HIT_PRIORS = [0.0, 1.0] # always advance on hit
        # test single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[3], "p13")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)

        # test double
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 1.0, 0.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

        # test triple
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 1.0, 0.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 2)

        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.cur_base_runners[3] = "p12"
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 3)


class TestBigBuckets(TestGameState):

    def testBigBuckets(self):
        global HIT_PRIORS
        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.stadium.has_big_buckets = True
        game_state.BIG_BUCKET_PERCENTAGE = 0.0
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 1)
        game_state.BIG_BUCKET_PERCENTAGE = 1.0
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 3)
        self.game_state.stadium.has_big_buckets = False
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 4)
        self.game_state.stadium.has_big_buckets = True
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.WIRED] = 1
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 7)
        del self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.WIRED]
        self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.TIRED] = 1
        self.game_state.hit_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 8.0)
        game_state.BIG_BUCKET_PERCENTAGE = 0.0

    def testAcidicBigBuckets(self):
        global HIT_PRIORS
        # test hr
        self.game_state.reset_game_state()
        HIT_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.stadium.has_big_buckets = True
        game_state.BIG_BUCKET_PERCENTAGE = 0.0
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))
        game_state.BIG_BUCKET_PERCENTAGE = 1.0
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("2.7"))
        self.game_state.stadium.has_big_buckets = False
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("3.6"))
        self.game_state.stadium.has_big_buckets = True
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.WIRED] = 1
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("6.4"))
        del self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.WIRED]
        self.game_state.cur_batting_team.player_buffs[self.game_state.cur_batting_team.cur_batter][PlayerBuff.TIRED] = 1
        self.game_state.hit_sim([], acidic_pitcher_check=True)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, Decimal("7.2"))
        game_state.BIG_BUCKET_PERCENTAGE = 0.0


class TestInPlaySim(TestGameState):

    def testNoOneOnBase(self):
        global HIT_PRIORS
        global IS_HIT_PRIORS
        # always hit a single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        # test flyout
        IS_HIT_PRIORS = [1.0, 0.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.in_play_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 1)

        # test groundout
        self.game_state.reset_game_state()
        IS_HIT_PRIORS = [0.0, 1.0, 0.0]
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.in_play_sim([])
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 1)


class TestPitchSim(TestGameState):

    def testBall(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        #turn off base instincts
        new_priors = {3: 0.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors

        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 1)
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.balls, 3)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")

        # test runner advances on walk
        self.game_state.reset_game_state()
        self.game_state.cur_base_runners[1] = "p13"
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p13")

        # test runner scores on walk
        self.game_state.reset_game_state()
        self.game_state.cur_base_runners[1] = "p13"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p13")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, 1)

        # test runner scores on acidic walk
        self.game_state.reset_game_state()
        self.game_state.cur_pitching_team.team_enum = Team.TACOS
        self.game_state.season = 17
        game_state.ACIDIC_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_base_runners[1] = "p13"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p11"
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.cur_base_runners[2], "p13")
        self.assertEqual(self.game_state.cur_base_runners[3], "p12")
        self.assertEqual(self.game_state.away_score, Decimal("0.9"))

        #turn on base instincts
        new_priors = {3: 1.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        # test runner scores on walk
        self.game_state.reset_game_state()
        self.game_state.cur_pitching_team.team_enum = Team.WORMS
        self.game_state.cur_base_runners[1] = "p13"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.blood["p11"] = BloodType.BASE
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.cur_base_runners[3], "p11")
        self.assertEqual(self.game_state.away_score, 3)

    def testStrikeSwinging(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]

        # test outs advance on strike
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.GEORGIAS
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 1)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 1)

        # test oh no wont trigger an out
        self.game_state.reset_game_state()
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.game_state.cur_batting_team.blood["p11"] = BloodType.O_NO
        self.game_state.strikes = 2
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 0)

    def testStrikeLooking(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        # test outs advance on strike
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.GEORGIAS
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 1)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 0)
        self.assertEqual(self.game_state.outs, 1)

        # test oh no wont trigger an out
        self.game_state.reset_game_state()
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.game_state.cur_batting_team.blood["p11"] = BloodType.O_NO
        self.game_state.strikes = 2
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.assertEqual(self.game_state.outs, 0)

    def testFoul(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [0.0, 0.0, 1.0, 0.0, 0.0, 0.0]

        # test strike increase on foul
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.GEORGIAS
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 1)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)
        self.game_state.pitch_sim()
        self.assertEqual(self.game_state.strikes, 2)

    def testFlinchStrike(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.FLINCH: 1}
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.GEORGIAS
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 1)

        PITCH_PRIORS = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        self.game_state.strikes = 0
        self.assertEqual(self.game_state.strikes, 0)
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.balls, 0)
        self.assertEqual(self.game_state.strikes, 1)

        PITCH_PRIORS = [0.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        global HIT_PRIORS
        # test single
        HIT_PRIORS = [1.0, 0.0, 0.0, 0.0]
        self.game_state.pitch_sim()
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.home_score, 0)
        self.assertEqual(self.game_state.away_score, 0)

    class TestSun2Blackhole(TestGameState):
        def testSun2(self):
            self.game_state.home_score = Decimal("9.0")
            self.game_state.away_score = Decimal("9.0")
            self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
            self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
            self.game_state.increase_batting_team_runs(Decimal("0.9"))
            self.assertEqual(Decimal("9.9"), self.game_state.away_score)
            self.game_state.increase_batting_team_runs(Decimal("1.0"))
            self.assertEqual(Decimal("0.9"), self.game_state.away_score)
            self.assertEqual(1.0, self.game_state.cur_batting_team.game_stats[TEAM_ID][Stats.TEAM_SUN2_WINS])
            self.game_state.home_score = Decimal("9.0")
            self.game_state.away_score = Decimal("9.0")

            self.game_state.half = InningHalf.BOTTOM
            self.game_state.cur_batting_team = self.game_state.home_team
            self.game_state.cur_pitching_team = self.game_state.away_team
            self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
            self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
            self.game_state.increase_batting_team_runs(Decimal("0.9"))
            self.assertEqual(Decimal("9.9"), self.game_state.home_score)
            self.game_state.increase_batting_team_runs(Decimal("1.0"))
            self.assertEqual(Decimal("0.9"), self.game_state.home_score)
            self.assertEqual(1.0, self.game_state.cur_batting_team.game_stats[TEAM_ID][Stats.TEAM_SUN2_WINS])

    def testBlackhole(self):
        self.game_state.home_score = Decimal("9.0")
        self.game_state.away_score = Decimal("9.0")
        self.game_state.weather = Weather.BLACKHOLE
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.away_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.home_team.team_enum)
        self.game_state.increase_batting_team_runs(Decimal("0.9"))
        self.assertEqual(Decimal("9.9"), self.game_state.away_score)
        self.game_state.increase_batting_team_runs(Decimal("1.0"))
        self.assertEqual(Decimal("0.9"), self.game_state.away_score)
        self.assertEqual(Decimal("1.0"), self.game_state.cur_pitching_team.game_stats[TEAM_ID][Stats.TEAM_BLACK_HOLE_CONSUMPTION])
        self.game_state.home_score = Decimal("9.0")
        self.game_state.away_score = Decimal("9.0")

        self.game_state.half = InningHalf.BOTTOM
        self.game_state.cur_batting_team = self.game_state.home_team
        self.game_state.cur_pitching_team = self.game_state.away_team
        self.assertEqual(self.game_state.cur_batting_team.team_enum, self.game_state.home_team.team_enum)
        self.assertEqual(self.game_state.cur_pitching_team.team_enum, self.game_state.away_team.team_enum)
        self.game_state.increase_batting_team_runs(Decimal("0.9"))
        self.assertEqual(Decimal("9.9"), self.game_state.home_score)
        self.game_state.increase_batting_team_runs(Decimal("1.0"))
        self.assertEqual(Decimal("0.9"), self.game_state.home_score)
        self.assertEqual(1.0, self.game_state.cur_pitching_team.game_stats[TEAM_ID][Stats.TEAM_BLACK_HOLE_CONSUMPTION])


class TestUnavailability(TestGameState):
    def testShelledBatter(self):
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.SHELLED: 1}
        self.game_state.cur_batting_team.player_buffs["p12"] = {PlayerBuff.SHELLED: 1}
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
        self.assertEqual("p11", self.game_state.cur_batting_team.cur_batter)
        self.game_state.validate_current_batter_state()
        self.assertEqual("p13", self.game_state.cur_batting_team.cur_batter)

    def testElsewhereBatter(self):
        self.game_state.cur_batting_team.reset_team_state()
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.ELSEWHERE: 1}
        self.game_state.cur_batting_team.player_buffs["p12"] = {PlayerBuff.ELSEWHERE: 1}
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
        self.assertEqual("p11", self.game_state.cur_batting_team.cur_batter)
        self.game_state.validate_current_batter_state()
        self.assertEqual("p13", self.game_state.cur_batting_team.cur_batter)


class TestBlaserunning(TestGameState):
    def testSBAttemptSuccess(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.BLASERUNNING] = 1
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.cur_base_runners[2], "p11")
        self.assertEqual(Decimal("0.2"), self.game_state.away_score)

    def testSBAttemptSuccessHome(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.game_state.cur_batting_team.player_buffs["p13"][PlayerBuff.BLASERUNNING] = 1
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.away_score, Decimal("0"))
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.away_score, Decimal("1.2"))


class TestCoffeePrimeScoring(TestGameState):
    def testGenericWiredAdvancement(self):
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.WIRED] = 1
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("1.5"), self.game_state.away_score)

    def testAcidicGenericWiredAdvancement(self):
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.WIRED] = 1
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.advance_all_runners(1, acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("1.4"), self.game_state.away_score)

    def testGenericTiredAdvancement(self):
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.TIRED] = 1
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("0.5"), self.game_state.away_score)

    def testAcidicGenericTiredAdvancement(self):
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.TIRED] = 1
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.advance_all_runners(1, acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("0.4"), self.game_state.away_score)

    def testSBAttemptSuccessHome(self):
        global SBA_PRIORS
        global SB_PRIORS
        SBA_PRIORS = [0.0, 1.0]
        SB_PRIORS = [0.0, 1.0]
        self.game_state.weather = Weather.COFFEE
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p12"
        self.game_state.cur_base_runners[3] = "p13"
        self.game_state.cur_batting_team.player_buffs["p13"][PlayerBuff.WIRED] = 1
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(self.game_state.away_score, Decimal("0"))
        self.assertEqual(len(self.game_state.cur_base_runners), 3)
        self.assertTrue(self.game_state.stolen_base_sim())
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_base_runners[2], "p12")
        self.assertEqual(self.game_state.cur_base_runners[1], "p11")
        self.assertEqual(self.game_state.away_score, Decimal("1.5"))


class TestCoffee2Out(TestGameState):
    def testGenericRefillAdvancement(self):
        self.game_state.weather = Weather.COFFEE2
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.COFFEE_RALLY] = 1
        self.game_state.outs = 1
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("1.0"), self.game_state.away_score)
        self.assertFalse(PlayerBuff.COFFEE_RALLY in self.game_state.cur_batting_team.player_buffs["p11"])


    def testGenericRefillNoOutAdvancement(self):
        self.game_state.weather = Weather.COFFEE2
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.cur_batting_team.player_buffs["p11"][PlayerBuff.COFFEE_RALLY] = 1
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.assertEqual(len(self.game_state.cur_base_runners), 1)
        self.assertEqual(self.game_state.outs, 0)
        self.game_state.advance_all_runners(1)
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(len(self.game_state.cur_base_runners), 0)
        self.assertEqual(Decimal("1.0"), self.game_state.away_score)
        self.assertTrue(PlayerBuff.COFFEE_RALLY in self.game_state.cur_batting_team.player_buffs["p11"])

class TestCoffee3Unruns(TestGameState):
    def testConditionUnmet(self):
        self.game_state.weather = Weather.COFFEE2
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_pitching_team.player_buffs["p1"][PlayerBuff.TRIPLE_THREAT] = 1
        self.game_state.outs = 0
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(Decimal("0"), self.game_state.away_score)

    def testGenericConditionMet(self):
        self.game_state.weather = Weather.COFFEE2
        self.game_state.cur_pitching_team.player_buffs["p4"][PlayerBuff.TRIPLE_THREAT] = 1
        # strikeout with 3 balls
        self.game_state.balls = 3
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.3"), self.game_state.away_score)

        # strikeout with person on 3rd
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.3"), self.game_state.away_score)

        # strikeout with person on 3rd and 3 balls
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.balls = 3
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.6"), self.game_state.away_score)

        # strikeout with bases loaded (by definition player on 3rd)
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p11"
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.6"), self.game_state.away_score)

        # strikeout with all 3
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p11"
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.balls = 3
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=False)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.9"), self.game_state.away_score)

    def testAcidicGenericConditionMet(self):
        self.game_state.weather = Weather.COFFEE2
        self.game_state.cur_pitching_team.player_buffs["p4"][PlayerBuff.TRIPLE_THREAT] = 1
        # strikeout with 3 balls
        self.game_state.balls = 3
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.4"), self.game_state.away_score)

        # strikeout with person on 3rd
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.4"), self.game_state.away_score)

        # strikeout with person on 3rd and 3 balls
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.balls = 3
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.8"), self.game_state.away_score)

        # strikeout with bases loaded (by definition player on 3rd)
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p11"
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-0.8"), self.game_state.away_score)

        # strikeout with all 3
        self.game_state.cur_base_runners[1] = "p11"
        self.game_state.cur_base_runners[2] = "p11"
        self.game_state.cur_base_runners[3] = "p11"
        self.game_state.outs = 0
        self.game_state.balls = 3
        self.game_state.away_score = Decimal("0.0")
        self.assertEqual(self.game_state.outs, 0)
        self.assertEqual(Decimal("0"), self.game_state.away_score)
        self.game_state.resolve_strikeout(acidic_pitcher_check=True)
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(Decimal("-1.2"), self.game_state.away_score)

