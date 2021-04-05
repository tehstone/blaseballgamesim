import os
import unittest

from src.team_state import TeamState
from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import AdditiveTypes, BloodType, PlayerBuff, Team, Weather
from src.stadium import Stadium

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
)

class TestTeamState(unittest.TestCase):
    def setUp(self):
        self.team_state = TeamState(
            team_id="747b8e4a-7e50-4638-a973-ea7950a3e739",
            season=1,
            day=1,
            stadium=default_stadium,
            weather=Weather.SUN2,
            is_home=False,
            num_bases=4,
            balls_for_walk=4,
            strikes_for_out=3,
            outs_for_inning=3,
            lineup={1: "p1", 2: "p2", 3: "p3"},
            rotation={1: "p4"},
            starting_pitcher="p4",
            cur_pitcher_pos=1,
            stlats={
                "p1": {
                    FK.BASE_THIRST: 3.0,
                    FK.CONTINUATION: 0.0,
                    FK.GROUND_FRICTION: 0.0,
                    FK.INDULGENCE: 0.0,
                    FK.LASERLIKENESS: 0.0,
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
                    FK.PATHETICISM: 2.0,
                    FK.THWACKABILITY: 0.0,
                    FK.TRAGICNESS: 0.0,
                    FK.COLDNESS: 0.0,
                    FK.OVERPOWERMENT: 0.0,
                    FK.RUTHLESSNESS: 0.0,
                    FK.SHAKESPEARIANISM: 0.0,
                    FK.SUPPRESSION: 0.0,
                    FK.UNTHWACKABILITY: 0.0,
                    FK.PRESSURIZATION: 0.0,
                    FK.CINNAMON: 0.0,
                },
                "p2": {
                    FK.BASE_THIRST: 2.0,
                    FK.CONTINUATION: 0.0,
                    FK.GROUND_FRICTION: 0.0,
                    FK.INDULGENCE: 0.0,
                    FK.LASERLIKENESS: 0.0,
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
                    FK.PATHETICISM: 1.0,
                    FK.THWACKABILITY: 1.0,
                    FK.TRAGICNESS: 0.0,
                    FK.COLDNESS: 0.0,
                    FK.OVERPOWERMENT: 0.0,
                    FK.RUTHLESSNESS: 0.0,
                    FK.SHAKESPEARIANISM: 0.0,
                    FK.SUPPRESSION: 0.0,
                    FK.UNTHWACKABILITY: 0.0,
                    FK.PRESSURIZATION: 0.0,
                    FK.CINNAMON: 0.0,
                },
                "p3": {
                    FK.BASE_THIRST: 1.0,
                    FK.CONTINUATION: 0.0,
                    FK.GROUND_FRICTION: 0.0,
                    FK.INDULGENCE: 0.0,
                    FK.LASERLIKENESS: 0.0,
                    FK.ANTICAPITALISM: 6.0,
                    FK.CHASINESS: 3.0,
                    FK.OMNISCIENCE: 3.0,
                    FK.TENACIOUSNESS: 3.0,
                    FK.WATCHFULNESS: 3.0,
                    FK.BUOYANCY: 0.0,
                    FK.DIVINITY: 0.0,
                    FK.MARTYRDOM: 0.0,
                    FK.MOXIE: 0.0,
                    FK.MUSCLITUDE: 0.0,
                    FK.PATHETICISM: 0.2,
                    FK.THWACKABILITY: 2.0,
                    FK.TRAGICNESS: 0.0,
                    FK.COLDNESS: 0.0,
                    FK.OVERPOWERMENT: 0.0,
                    FK.RUTHLESSNESS: 0.0,
                    FK.SHAKESPEARIANISM: 0.0,
                    FK.SUPPRESSION: 0.0,
                    FK.UNTHWACKABILITY: 0.0,
                    FK.PRESSURIZATION: 3.0,
                    FK.CINNAMON: 3.0,
                },
                "p4": {
                    FK.BASE_THIRST: 1.0,
                    FK.CONTINUATION: 0.0,
                    FK.GROUND_FRICTION: 0.0,
                    FK.INDULGENCE: 0.0,
                    FK.LASERLIKENESS: 0.0,
                    FK.ANTICAPITALISM: 6.0,
                    FK.CHASINESS: 3.0,
                    FK.OMNISCIENCE: 3.0,
                    FK.TENACIOUSNESS: 3.0,
                    FK.WATCHFULNESS: 3.0,
                    FK.BUOYANCY: 0.0,
                    FK.DIVINITY: 0.0,
                    FK.MARTYRDOM: 0.0,
                    FK.MOXIE: 0.0,
                    FK.MUSCLITUDE: 0.0,
                    FK.PATHETICISM: 0.01,
                    FK.THWACKABILITY: 3.0,
                    FK.TRAGICNESS: 0.0,
                    FK.COLDNESS: 0.0,
                    FK.OVERPOWERMENT: 0.0,
                    FK.RUTHLESSNESS: 0.0,
                    FK.SHAKESPEARIANISM: 0.0,
                    FK.SUPPRESSION: 0.0,
                    FK.UNTHWACKABILITY: 0.0,
                    FK.PRESSURIZATION: 3.0,
                    FK.CINNAMON: 3.0,
                },
            },
            buffs={
                "p1": {},
                "p2": {},
                "p3": {},
                "p4": {},
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
            segmented_stats={
                0: {
                    "p1": {Stats.BATTER_AT_BATS: 1.0},
                    "p2": {Stats.BATTER_AT_BATS: 1.0},
                    "p3": {Stats.BATTER_AT_BATS: 1.0},
                    "p4": {Stats.BATTER_AT_BATS: 1.0},
                },
                3: {
                    "p1": {Stats.BATTER_AT_BATS: 1.0},
                    "p2": {Stats.BATTER_AT_BATS: 1.0},
                    "p3": {Stats.BATTER_AT_BATS: 1.0},
                    "p4": {Stats.BATTER_AT_BATS: 1.0},
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
        self.assertEqual(self.team_state.weather, Weather.SUN2)
        self.assertEqual(self.team_state.is_home, False)
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
        self.assertEqual(new_state.segmented_stats[0]["p4"][Stats.BATTER_AT_BATS],
                         self.team_state.segmented_stats[0]["p4"][Stats.BATTER_AT_BATS])
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


class TestTeamBuffs(TestTeamState):
    def test_travelling(self):
        self.team_state.is_home = True
        self.team_state.calc_additives()
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(2.0, new_p1[5])
        self.assertEqual(0.0, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        self.assertEqual(0.0, self.team_state.batting_addition)
        self.assertEqual(0.0, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)
        self.team_state.team_enum = Team.SHOE_THIEVES
        self.team_state.season = 12
        self.team_state.calc_additives()
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(2.0, new_p1[5])
        self.assertEqual(0.0, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        self.assertEqual(0.0, self.team_state.batting_addition)
        self.assertEqual(0.0, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)
        self.team_state.is_home = False
        self.team_state.calc_additives()
        self.assertEqual(0.05, self.team_state.batting_addition)
        self.assertEqual(0.05, self.team_state.pitching_addition)
        self.assertEqual(0.05, self.team_state.defense_addition)
        self.assertEqual(0.05, self.team_state.base_running_addition)
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(1.95, new_p1[5])
        self.assertEqual(0.05, new_p1[6])
        self.assertEqual(3.05, new_p1[8])
        new_p1 = self.team_state.get_batter_feature_vector("p4")
        self.assertEqual(0.001, new_p1[5])

    def test_sinking_ship(self):
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(2.0, new_p1[5])
        self.assertEqual(0.0, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        self.assertEqual(0.0, self.team_state.batting_addition)
        self.assertEqual(0.0, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)
        self.team_state.team_enum = Team.FRIDAYS
        self.team_state.season = 14
        self.team_state.calc_additives()
        self.assertEqual(0.1, self.team_state.batting_addition)
        self.assertEqual(0.1, self.team_state.pitching_addition)
        self.assertEqual(0.1, self.team_state.defense_addition)
        self.assertEqual(0.1, self.team_state.base_running_addition)
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(1.9, new_p1[5])
        self.assertEqual(0.1, new_p1[6])
        self.assertEqual(3.1, new_p1[8])
        new_p1 = self.team_state.get_batter_feature_vector("p4")
        self.assertEqual(0.001, new_p1[5])

    def test_crows(self):
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(2.0, new_p1[5])
        self.assertEqual(0.0, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        self.assertEqual(0.0, self.team_state.batting_addition)
        self.assertEqual(0.0, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)
        self.team_state.team_enum = Team.PIES
        self.team_state.weather = Weather.BIRD
        self.team_state.season = 14
        self.team_state.calc_additives()
        self.assertEqual(0.5, self.team_state.batting_addition)
        self.assertEqual(0.5, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(1.5, new_p1[5])
        self.assertEqual(0.5, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        new_p1 = self.team_state.get_batter_feature_vector("p4")
        self.assertEqual(0.001, new_p1[5])

        self.team_state.weather = Weather.SUN2
        self.team_state.reset_team_state()
        new_p1 = self.team_state.get_batter_feature_vector("p1")
        self.assertEqual(2.0, new_p1[5])
        self.assertEqual(0.0, new_p1[6])
        self.assertEqual(3.0, new_p1[8])
        self.assertEqual(0.0, self.team_state.batting_addition)
        self.assertEqual(0.0, self.team_state.pitching_addition)
        self.assertEqual(0.0, self.team_state.defense_addition)
        self.assertEqual(0.0, self.team_state.base_running_addition)



class TestHitBuffModifiers(TestTeamState):
    def test_reset_hit_buff(self):
        self.team_state.player_buffs["p1"][PlayerBuff.SPICY] = 4
        self.assertEqual(4, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.team_state.reset_hit_buffs("p1")
        self.assertEqual(1, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])

    def test_spicy_buff(self):
        self.team_state.player_buffs["p1"][PlayerBuff.SPICY] = 1
        self.assertEqual(1, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.apply_hit_to_buffs("p1")
        self.assertEqual(2, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.apply_hit_to_buffs("p1")
        self.assertEqual(3, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.apply_hit_to_buffs("p1")
        self.assertEqual(4, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.5, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.apply_hit_to_buffs("p1")
        self.assertEqual(4, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.5, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.reset_hit_buffs("p1")
        self.assertEqual(1, self.team_state.player_buffs["p1"][PlayerBuff.SPICY])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])


class TestPreloadModifiers(TestTeamState):
    def test_chunky(self):
        self.team_state.player_buffs["p1"][PlayerBuff.CHUNKY] = 1
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.weather = Weather.SUN2
        self.team_state.reset_preload_additives()
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.team_state.weather = Weather.PEANUTS
        self.team_state.reset_preload_additives()
        self.assertEqual(1.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])

    def test_smooth(self):
        self.team_state.player_buffs["p1"][PlayerBuff.SMOOTH] = 1
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.team_state.weather = Weather.SUN2
        self.team_state.reset_preload_additives()
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.team_state.weather = Weather.PEANUTS
        self.team_state.reset_preload_additives()
        self.assertEqual(1.0, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])

    def test_homebody(self):
        self.team_state.player_buffs["p1"][PlayerBuff.HOMEBODY] = 1
        self.team_state.is_home = False
        self.team_state.reset_preload_additives()
        self.assertEqual(-0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(-0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(-0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(-0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.team_state.is_home = True
        self.team_state.reset_preload_additives()
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])

    def test_perk(self):
        self.team_state.player_buffs["p1"][PlayerBuff.PERK] = 1
        self.team_state.weather = Weather.SUN2
        self.team_state.reset_preload_additives()
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(1, self.team_state.player_buffs["p1"][PlayerBuff.PERK])
        self.team_state.player_buffs["p1"][PlayerBuff.PERK] = 1
        self.team_state.weather = Weather.COFFEE
        self.team_state.reset_preload_additives()
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(2, self.team_state.player_buffs["p1"][PlayerBuff.PERK])
        self.team_state.player_buffs["p1"][PlayerBuff.PERK] = 1
        self.team_state.weather = Weather.COFFEE2
        self.team_state.reset_preload_additives()
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(2, self.team_state.player_buffs["p1"][PlayerBuff.PERK])
        self.team_state.player_buffs["p1"][PlayerBuff.PERK] = 1
        self.team_state.weather = Weather.COFFEE3
        self.team_state.reset_preload_additives()
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(2, self.team_state.player_buffs["p1"][PlayerBuff.PERK])
        self.team_state.player_buffs["p1"][PlayerBuff.PERK] = 1
        self.team_state.weather = Weather.SUN2
        self.team_state.reset_preload_additives()
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.0, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(1, self.team_state.player_buffs["p1"][PlayerBuff.PERK])

    def test_under_over(self):
        self.team_state.player_buffs["p1"][PlayerBuff.UNDER_OVER] = 1
        self.team_state.reset_preload_additives()
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BASE_RUNNING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.BATTING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.PITCHING])
        self.assertEqual(0.2, self.team_state.player_additives["p1"][AdditiveTypes.DEFENSE])
        self.assertEqual(2, self.team_state.player_buffs["p1"][PlayerBuff.UNDER_OVER])

