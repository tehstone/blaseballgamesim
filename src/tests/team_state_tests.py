import os
import unittest

from src.team_state import TeamState


class TestTeamState(unittest.TestCase):
    def setUp(self):
        self.team_state = TeamState(
            id="id1",
            season=1,
            day=1,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup={1: "p1", 2: "p2", 3: "p3"},
            starting_pitcher="p4",
            stats={
                "p1": {"stat1": 0.0, "stat2": 3.0},
                "p2": {"stat1": 1.0, "stat2": 2.0},
                "p3": {"stat1": 2.0, "stat2": 1.0},
                "p4": {"stat1": 3.0, "stat2": 0.0},
            },
            blood={
                "p1": "b1",
                "p2": "b2",
                "p3": "b1",
                "p4": "b3",
            },
        )


class TestInit(TestTeamState):
    def test_initial_state(self):
        self.assertEqual(self.team_state.id, "id1")
        self.assertEqual(self.team_state.season, 1)
        self.assertEqual(self.team_state.day, 1)
        self.assertEqual(self.team_state.num_bases, 4)
        self.assertEqual(self.team_state.balls_for_walk, 4)
        self.assertEqual(self.team_state.strikes_for_out, 3)
        self.assertEqual(self.team_state.outs_for_inning, 3)
        self.assertEqual(len(self.team_state.lineup), 3)
        self.assertEqual(self.team_state.starting_pitcher, "p4")
        self.assertEqual(self.team_state.stats["p4"]["stat1"], 3.0)
        self.assertEqual(self.team_state.blood["p3"], "b1")


class TestSerialization(TestTeamState):
    def test_serialize_state(self):
        self.team_state.save("./foo.test")
        self.assertTrue(os.path.exists("./foo.test"))
        os.remove("./foo.test")
        self.assertFalse(os.path.exists("./foo.test"))

    def test_load_state(self):
        self.team_state.save("./foo.test")
        new_state = TeamState.load("./foo.test")
        self.assertEqual(new_state.id, self.team_state.id)
        self.assertEqual(new_state.stats["p4"]["stat1"], self.team_state.stats["p4"]["stat1"])
        os.remove("./foo.test")
