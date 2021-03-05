import os
import unittest

from src.team_state import TeamState
from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import BloodType, Team


class TestTeamState(unittest.TestCase):
    def setUp(self):
        self.team_state = TeamState(
            team_id="747b8e4a-7e50-4638-a973-ea7950a3e739",
            season=1,
            day=1,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup={1: "p1", 2: "p2", 3: "p3"},
            rotation={1: "p4"},
            starting_pitcher="p4",
            stlats={
                "p1": {
                    FK.THWACKABILITY: 0.0,
                    FK.BASE_THIRST: 3.0,
                    FK.ANTICAPITALISM: 0.0,
                    FK.CHASINESS: 0.0,
                    FK.OMNISCIENCE: 0.0,
                    FK.TENACIOUSNESS: 0.0,
                    FK.WATCHFULNESS: 0.0,
                    FK.PRESSURIZATION: 0.0,
                    FK.CINNAMON: 0.0,
                },
                "p2": {
                    FK.THWACKABILITY: 1.0,
                    FK.BASE_THIRST: 2.0,
                    FK.ANTICAPITALISM: 0.0,
                    FK.CHASINESS: 0.0,
                    FK.OMNISCIENCE: 0.0,
                    FK.TENACIOUSNESS: 0.0,
                    FK.WATCHFULNESS: 0.0,
                    FK.PRESSURIZATION: 0.0,
                    FK.CINNAMON: 0.0,
                },
                "p3": {
                    FK.THWACKABILITY: 2.0,
                    FK.BASE_THIRST: 1.0,
                    FK.ANTICAPITALISM: 6.0,
                    FK.CHASINESS: 3.0,
                    FK.OMNISCIENCE: 3.0,
                    FK.TENACIOUSNESS: 3.0,
                    FK.WATCHFULNESS: 3.0,
                    FK.PRESSURIZATION: 3.0,
                    FK.CINNAMON: 3.0,
                },
                "p4": {
                    FK.THWACKABILITY: 3.0,
                    FK.BASE_THIRST: 0.0,
                    FK.ANTICAPITALISM: 0.0,
                    FK.CHASINESS: 0.0,
                    FK.OMNISCIENCE: 0.0,
                    FK.TENACIOUSNESS: 0.0,
                    FK.WATCHFULNESS: 0.0,
                    FK.PRESSURIZATION: 0.0,
                    FK.CINNAMON: 0.0,
                },
            },
            game_stats={
                "p1": {
                    Stats.BATTER_AT_BATS: 1.0,
                },
                "p2": {
                    Stats.BATTER_AT_BATS: 1.0,
                },
                "p3": {
                    Stats.BATTER_AT_BATS: 1.0,
                },
                "p4": {
                    Stats.BATTER_AT_BATS: 1.0,
                },
            },
            blood={
                "p1": BloodType.O,
                "p2": BloodType.GRASS,
                "p3": BloodType.LOVE,
                "p4": BloodType.ELECTRIC,
            },
            player_names={
                "p1": "Player 1",
                "p2": "Player 2",
                "p3": "Player 3",
                "p4": "Player 4",
            },
            cur_batter_pos=1,
        )


class TestInit(TestTeamState):
    def test_initial_state(self):
        self.assertEqual(self.team_state.team_enum, Team.TIGERS)
        self.assertEqual(self.team_state.season, 1)
        self.assertEqual(self.team_state.day, 1)
        self.assertEqual(self.team_state.num_bases, 4)
        self.assertEqual(self.team_state.balls_for_walk, 4)
        self.assertEqual(self.team_state.strikes_for_out, 3)
        self.assertEqual(self.team_state.outs_for_inning, 3)
        self.assertEqual(len(self.team_state.lineup), 3)
        self.assertEqual(self.team_state.starting_pitcher, "p4")
        self.assertEqual(self.team_state.stlats["p4"][FK.THWACKABILITY], 3.0)
        self.assertEqual(self.team_state.blood["p3"], BloodType.LOVE)


class TestSerialization(TestTeamState):
    def test_serialize_state(self):
        self.team_state.save("./foo.test")
        self.assertTrue(os.path.exists("./foo.test"))
        os.remove("./foo.test")
        self.assertFalse(os.path.exists("./foo.test"))

    def test_load_state(self):
        self.team_state.save("./foo.test")
        new_state = TeamState.load("./foo.test")
        self.assertEqual(new_state.team_id, self.team_state.team_id)
        self.assertEqual(new_state.team_enum, self.team_state.team_enum)
        self.assertEqual(new_state.stlats["p4"][FK.THWACKABILITY], self.team_state.stlats["p4"][FK.THWACKABILITY])
        os.remove("./foo.test")


class TestBatterAdvancement(TestTeamState):
    def test_batter_advancement(self):
        cur_batter = self.team_state.cur_batter
        cur_batter_pos = self.team_state.cur_batter_pos
        self.assertEqual(cur_batter, "p1")
        self.assertEqual(cur_batter_pos, 1)
        self.team_state.next_batter()
        cur_batter = self.team_state.cur_batter
        cur_batter_pos = self.team_state.cur_batter_pos
        self.assertEqual(cur_batter, "p2")
        self.assertEqual(cur_batter_pos, 2)
        self.team_state.next_batter()
        self.team_state.next_batter()
        cur_batter = self.team_state.cur_batter
        cur_batter_pos = self.team_state.cur_batter_pos
        self.assertEqual(cur_batter, "p1")
        self.assertEqual(cur_batter_pos, 1)
