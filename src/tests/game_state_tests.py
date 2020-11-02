import os
import unittest

from src.game_state import GameState, InningHalf
from src.team_state import TeamState
from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import BloodType, Team

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

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.home_team_state = TeamState(
            team_id="747b8e4a-7e50-4638-a973-ea7950a3e739",
            season=11,
            day=1,
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
            cur_batter_pos=1,
        )

        self.away_team_state = TeamState(
            team_id="f02aeae2-5e6a-4098-9842-02d2273f25c7",
            season=11,
            day=1,
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
            cur_batter_pos=1,
        )

        self.game_state = GameState(
            game_id="1",
            season=11,
            day=1,
            home_team=self.home_team_state,
            away_team=self.away_team_state,
            home_score=0,
            away_score=0,
            inning=1,
            half=InningHalf.TOP,
            outs=0,
            strikes=0,
            balls=0,
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



