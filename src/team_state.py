from typing import Any, Dict, List, Tuple
import json
import logging
import statistics

from src.common import BlaseballStatistics as Stats
from src.common import ForbiddenKnowledge as FK
from src.common import Team, team_id_map

DEF_ID = "DEFENSE"


class TeamState(object):
    def __init__(
        self,
        team_id: str,
        season: int,
        day: int,
        num_bases: int,
        balls_for_walk: int,
        strikes_for_out: int,
        outs_for_inning: int,
        lineup: Dict[int, str],
        starting_pitcher: str,
        stlats: Dict[str, Dict[FK, float]],
        game_stats: Dict[str, Dict[Stats, float]],
        blood: Dict[str, int],
        cur_batter_pos: int,
    ) -> None:
        """ A container class that holds the team state for a given game """
        self.team_id: str = team_id
        self.team_enum: Team = team_id_map[team_id]
        self.season: int = season
        self.day: int = day
        self.num_bases: int = num_bases
        self.balls_for_walk: int = balls_for_walk
        self.strikes_for_out: int = strikes_for_out
        self.outs_for_inning: int = outs_for_inning
        self.lineup: Dict[int, str] = lineup
        self.starting_pitcher: str = starting_pitcher
        self.stlats: Dict[str, Dict[FK, float]] = stlats
        self.game_stats: Dict[str, Dict[Stats, float]] = game_stats
        self.blood: Dict[str, int] = blood
        self.cur_batter_pos: int = cur_batter_pos
        self.cur_batter: str = lineup[cur_batter_pos]
        self._calculate_defense()

    def _calculate_defense(self):
        """Calculate the average team defense and store it in the stlats dict under DEF_ID"""
        anticapitalism: List[float] = []
        chasiness: List[float] = []
        omniscience: List[float] = []
        tenaciousness: List[float] = []
        watchfulness: List[float] = []
        defense_pressurization: List[float] = []
        defense_cinnamon: List[float] = []
        for pos in self.lineup.keys():
            cur_id: str = self.lineup[pos]
            anticapitalism.append(self.stlats[cur_id][FK.ANTICAPITALISM])
            chasiness.append(self.stlats[cur_id][FK.CHASINESS])
            omniscience.append(self.stlats[cur_id][FK.OMNISCIENCE])
            tenaciousness.append(self.stlats[cur_id][FK.TENACIOUSNESS])
            watchfulness.append(self.stlats[cur_id][FK.WATCHFULNESS])
            defense_pressurization.append(self.stlats[cur_id][FK.PRESSURIZATION])
            defense_cinnamon.append(self.stlats[cur_id][FK.CINNAMON])

        def_anticapitalism = statistics.mean(anticapitalism)
        def_chasiness = statistics.mean(chasiness)
        def_omniscience = statistics.mean(omniscience)
        def_tenaciousness = statistics.mean(tenaciousness)
        def_watchfulness = statistics.mean(watchfulness)
        def_defense_pressurization = statistics.mean(defense_pressurization)
        def_defense_cinnamon = statistics.mean(defense_cinnamon)

        self.stlats[DEF_ID][FK.ANTICAPITALISM] = def_anticapitalism
        self.stlats[DEF_ID][FK.CHASINESS] = def_chasiness
        self.stlats[DEF_ID][FK.OMNISCIENCE] = def_omniscience
        self.stlats[DEF_ID][FK.TENACIOUSNESS] = def_tenaciousness
        self.stlats[DEF_ID][FK.WATCHFULNESS] = def_watchfulness
        self.stlats[DEF_ID][FK.PRESSURIZATION] = def_defense_pressurization
        self.stlats[DEF_ID][FK.CINNAMON] = def_defense_cinnamon

    def to_dict(self) -> Dict[str, Any]:
        """ Gets a dict representation of the state for serialization """
        serialization_dict = {
            "team_id": self.team_id,
            "season": self.season,
            "day": self.day,
            "num_bases": self.num_bases,
            "balls_for_walk": self.balls_for_walk,
            "strikes_for_out": self.strikes_for_out,
            "outs_for_inning": self.outs_for_inning,
            "lineup": self.lineup,
            "starting_pitcher": self.starting_pitcher,
            "stlats": self.stats,
            "game_stats": self.game_stats,
            "blood": self.blood,
            "cur_batter_pos": self.cur_batter_pos,
        }
        return serialization_dict

    def save(self, storage_path: str) -> None:
        """ Persist a serialized json of the team state """
        with open(storage_path, "w") as json_file:
            json.dump(self.to_dict(), json_file)

    @classmethod
    def load(cls, storage_path: str):
        with open(storage_path, "r") as team_state_file:
            team_state_json = json.load(team_state_file)
            try:
                return TeamState.from_config(team_state_json)
            except KeyError:
                logging.warning(
                    "Unable to load team state file: " + storage_path
                )
                return None

    @classmethod
    def from_config(cls, team_state: Dict[str, Any]):
        """Reconstructs a team state from a json file."""
        team_id: str = team_state["team_id"]
        season: int = team_state["season"]
        day: int = team_state["day"]
        num_bases: int = team_state["num_bases"]
        balls_for_walk: int = team_state["balls_for_walk"]
        strikes_for_out: int = team_state["strikes_for_out"]
        outs_for_inning: int = team_state["outs_for_inning"]
        lineup: Dict[int, str] = team_state["lineup"]
        starting_pitcher: str = team_state["starting_pitcher"]
        stlats: Dict[str, Dict[FK, float]] = team_state["stlats"]
        game_stats: Dict[str, Dict[Stats, float]] = team_state["game_stats"]
        blood: Dict[str, int] = team_state["blood"]
        cur_battter_pos: int = team_state["cur_batter_pos"]
        return cls(
            team_id,
            season,
            day,
            num_bases,
            balls_for_walk,
            strikes_for_out,
            outs_for_inning,
            lineup,
            starting_pitcher,
            stlats,
            game_stats,
            blood,
            cur_battter_pos,
        )

    def get_batter_stats_by_position(self, position: int) -> Tuple[str, Dict[str, float]]:
        batter = self.lineup[position]
        stats = self.stats[batter]
        return batter, stats

    def get_player_stats_by_id(self, player_id: str) -> Dict[str, float]:
        return self.stats[player_id]

    def next_batter(self) -> None:
        if len(self.lineup) == self.cur_batter:
            self.cur_batter_pos = 1
        else:
            self.cur_batter_pos += 1
        self.cur_batter = self.lineup[self.cur_batter_pos]

    def update_stat(self, player_id: str, stat_id: Stats, value: float) -> None:
        self.game_stats[player_id][stat_id] += value

    def get_defense_feature_vector(self) -> List[float]:
        return []

    def get_pitcher_feature_vector(self) -> List[float]:
        return []

    def get_batter_feature_vector(self, player_id: str) -> List[float]:
        return []

    def get_runner_feature_vector(self, player_id: str) -> List[float]:
        return []

    def get_cur_batter_feature_vector(self) -> List[float]:
        return self.get_batter_feature_vector(self.cur_batter)
