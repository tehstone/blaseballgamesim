import os
import unittest
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.game_state import (
    BASE_INSTINCT_PRIORS,
    GameState,
    InningHalf,
)
import src.game_state
from src.team_state import TeamState, TEAM_ID, PlayerBuff
from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import MachineLearnedModel as Ml
from src.common import BloodType, Team, Weather

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
PITCH_PRIORS = [0.25, 0.25, 0.25, 0.25]
IS_HIT_PRIORS = [0.33, 0.33, 0.34]
HIT_PRIORS = [0.25, 0.25, 0.25, 0.25]
ADVANCE_HIT_PRIORS = [0.5, 0.5]
ADVANCE_OUT_PRIORS = [0.5, 0.5]
OUT_PRIORS = [0.5, 0.5]


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
            season=11,
            day=1,
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
            segmented_stats={
                "p1": {},
                "p2": {},
                "p3": {},
                "p4": {},
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
        )

        self.away_team_state = TeamState(
            team_id="f02aeae2-5e6a-4098-9842-02d2273f25c7",
            season=11,
            day=1,
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
            game_stats={
                "p11": {},
                "p12": {},
                "p13": {},
                "p14": {},
            },
            segmented_stats={
                "p11": {},
                "p12": {},
                "p13": {},
                "p14": {},
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
        )
        self.home_team_state.reset_team_state()
        self.away_team_state.reset_team_state()
        self.home_team_state.player_buffs = {
            "p1": {},
            "p2": {PlayerBuff.SWIM_BLADDER: 1},
            "p3": {PlayerBuff.SPICY: 1},
            "p4": {PlayerBuff.TRIPLE_THREAT: 1},
        }
        self.away_team_state.player_buffs = {
            "p11": {},
            "p12": {PlayerBuff.SWIM_BLADDER: 1},
            "p13": {PlayerBuff.SPICY: 1},
            "p14": {PlayerBuff.TRIPLE_THREAT: 1},
        }
        GameState.generic_model_roll = new_generic_model_roll
        self.game_state = GameState(
            game_id="1",
            season=11,
            day=1,
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


class TestBaseInstinct(TestGameState):

    def testNonBITeam(self):
        self.assertEqual(self.game_state.resolve_base_instincts(), 1)
        self.game_state.cur_batting_team.team_enum = Team.MAGIC
        self.assertEqual(self.game_state.resolve_base_instincts(), 1)

    def testBITeamNonBlood(self):
        new_priors = {3: 1.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_batting_team.blood["p11"] = BloodType.GRASS
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

    def testCharmPitcher(self):
        src.game_state.CHARM_TRIGGER_PERCENTAGE = 1.0
        self.game_state.cur_pitching_team.team_enum = Team.LOVERS
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.LOVE
        self.game_state.strikes = 0
        self.game_state.balls = 0
        self.game_state.outs = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 1)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p12")
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.GRASS
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_pitching_team.blood["p4"] = BloodType.LOVE
        self.game_state.season = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.season = 10
        self.game_state.strikes = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(self.game_state.outs, 2)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p13")

    def testCharmBatter(self):
        src.game_state.CHARM_TRIGGER_PERCENTAGE = 1.0
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
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.cur_batting_team.blood["p12"] = BloodType.LOVE
        self.game_state.season = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.season = 10
        self.game_state.strikes = 1
        self.assertFalse(self.game_state.resolve_team_pre_pitch_event())
        self.game_state.strikes = 0
        self.assertTrue(self.game_state.resolve_team_pre_pitch_event())
        self.assertEqual(len(self.game_state.cur_base_runners), 2)
        self.assertEqual(self.game_state.cur_batting_team.cur_batter, "p13")

    def testZapBatter(self):
        src.game_state.ZAP_TRIGGER_PERCENTAGE = 1.0
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
        PITCH_PRIORS = [1.0, 0.0, 0.0, 0.0]

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

        #turn on base instincts
        new_priors = {3: 1.0, 2: 0.0}
        BASE_INSTINCT_PRIORS[4] = new_priors
        # test runner scores on walk
        self.game_state.reset_game_state()
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

    def testStrike(self):
        global PITCH_PRIORS
        PITCH_PRIORS = [0.0, 1.0, 0.0, 0.0]

        # test outs advance on strike
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
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
        PITCH_PRIORS = [0.0, 0.0, 1.0, 0.0]

        # test strike increase on foul
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
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
        PITCH_PRIORS = [0.0, 0.0, 0.0, 1.0]
        self.game_state.cur_batting_team.player_buffs["p11"] = {PlayerBuff.FLINCH: 1}
        self.game_state.cur_batting_team.team_enum = Team.SUNBEAMS
        self.game_state.cur_pitching_team.team_enum = Team.TIGERS
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
